"""Small LangGraph nodes with injected scope, retrieval and validation boundaries."""

import asyncio
import re
from langgraph.config import get_stream_writer
from langsmith import traceable
from .targets import select_targets, repair_plan, remembered_name
from .research import collect_monitoring, collect_runbooks
from .retrieval import MCPRunbookSearch
from .evidence import render_report, evidence_payload, sections_from
from .validation import validate_draft


def events(state, *items):
    return state.get("events", []) + list(items)


@traceable(name="improved.scope")
async def scope_node(state, deps):
    selected = select_targets(state["query"], deps.catalog)
    incident = bool(
        selected.known
        or selected.unknown
        or re.search(
            r"장애|진단|다운|지연|급증|느려|느리|모니터링|응답|CPU|메모리|디스크|로그인|커넥션",
            state["query"],
            re.I,
        )
    )
    return {
        "route": "incident" if incident else "chat",
        "targets": list(selected.known),
        "unknown": list(selected.unknown),
        "collected": [],
        "cost_usd": 0.0,
        "events": events(
            state,
            {"type": "RouteDecided", "route": "incident" if incident else "chat"},
            {
                "type": "ScopeChecked",
                "targets": list(selected.known),
                "unknown": list(selected.unknown),
            },
        ),
    }


@traceable(name="improved.chat")
async def chat_node(state, deps):
    query = state["query"]
    writer = get_stream_writer()
    name = remembered_name(state.get("history", []), query)
    if re.search(r"이름.*(?:뭐|무엇|기억)", query):
        reply = (
            f"사용자님의 이름은 {name}입니다."
            if name
            else "아직 이름을 확인하지 못했어요. 이름을 알려주세요."
        )
        usage = {}
        writer({"type": "AnswerToken", "delta": reply})
    elif remembered_name([], query):
        reply = f"반갑습니다, {name}님. 이름을 기억해둘게요."
        usage = {}
        writer({"type": "AnswerToken", "delta": reply})
    elif re.search(r"안녕|누구|하이|hello", query, re.I):
        reply = "안녕하세요. 서비스 상태와 대응 매뉴얼을 확인하는 운영 장애 진단 비서입니다."
        usage = {}
        writer({"type": "AnswerToken", "delta": reply})
    else:
        reply, usage = await asyncio.wait_for(
            deps.fast_llm.chat(
                query,
                state.get("history", []),
                on_token=lambda p: writer({"type": "AnswerToken", "delta": p}),
            ),
            deps.call_timeout,
        )
    return {
        "final": reply,
        "last_prompt": usage.get("prompt"),
        "cost_usd": usage.get("usd", 0),
        "evidence": {},
        "answer_status": "chat",
        "events": events(state, {"type": "Finalize", "pipeline": "chat-direct"}),
    }


@traceable(name="improved.plan")
async def plan_node(state, deps):
    targets = state["targets"]
    needs = len(targets) > 1 or bool(re.search(r"공통|비교|패턴", state["query"]))
    proposed = []
    cost = state.get("cost_usd", 0)
    error = None
    if targets:
        try:
            server = await deps.mcp.find_prompt("incident_analysis_prompt")
            procedure = await deps.mcp.get_prompt(
                "incident_analysis_prompt",
                {"system_name": targets[0], "symptom": state["query"]},
                server=server,
            )
            result, usage = await asyncio.wait_for(
                asyncio.to_thread(deps.fast_llm.plan, state["query"], procedure),
                deps.call_timeout,
            )
            proposed = result.get("tasks", [])
            cost += usage.get("usd", 0)
        except Exception as exc:
            error = type(exc).__name__
    tasks = repair_plan(proposed, targets, needs)
    return {
        "tasks": tasks,
        "needs_analysis": needs,
        "cost_usd": cost,
        "events": events(
            state,
            {
                "type": "PlanCreated",
                "targets": targets,
                "task_count": len(tasks),
                "recovered_targets": [
                    t for t in targets if t not in [p.get("target") for p in proposed]
                ],
                "plan_error": error,
            },
            {
                "type": "GateApplied",
                "removed_analysis_tasks": 0
                if needs
                else sum(t.get("agent") == "analysis" for t in proposed),
            },
        ),
    }


@traceable(name="improved.monitoring")
async def monitoring_node(state, deps):
    collected = await collect_monitoring(state["targets"], deps.mcp, deps.call_timeout)
    evs = [
        {
            "type": "TaskCompleted" if c["source"] == "monitoring" else "TaskFailed",
            "source": c["source"],
            "target": c["service"],
            "retries": c.get("retries", 0),
        }
        for c in collected
    ]
    return {
        "collected": collected,
        "retry_count": sum(c.get("retries", 0) for c in collected),
        "events": events(state, *evs),
    }


@traceable(name="improved.retrieval")
async def retrieval_node(state, deps):
    searcher = deps.searcher or MCPRunbookSearch(deps.mcp)
    additions = await collect_runbooks(
        state.get("collected", []), searcher, deps.mcp, deps.call_timeout
    )
    evs = [
        {
            "type": "RunbookSelected",
            "target": c["service"],
            "incident_type": c["data"]["id"],
            "score": c["data"]["score"],
        }
        for c in additions
        if c["source"] == "runbook"
    ]
    evs += [
        {"type": "EvidenceMissing", **c["data"]}
        for c in additions
        if c["source"] == "error"
    ]
    if not additions:
        evs.append({"type": "RetrievalSkipped", "reason": "정상·미확인·대상 없음"})
    return {
        "collected": state.get("collected", []) + additions,
        "events": events(state, *evs),
    }


@traceable(name="improved.analysis")
async def analysis_node(state, deps):
    # No log/trace/dependency tools exist. A model cannot establish a common cause.
    note = "서비스별 관측만 수집함. 로그·시계열·의존 관계가 없어 공통 원인은 미확인."
    return {
        "analysis_note": note,
        "events": events(
            state,
            {
                "type": "AnalysisCompleted"
                if state.get("needs_analysis")
                else "AnalysisSkipped",
                "scope": "관측 비교 한계 확인",
                "cause_confirmed": False,
            },
        ),
    }


@traceable(name="improved.write")
async def write_node(state, deps):
    attempt = state.get("validation_attempts", 0) + 1
    if not sections_from(state.get("collected", [])) or not any(
        c["source"] == "runbook" for c in state.get("collected", [])
    ):
        return {
            "draft": None,
            "events": events(
                state,
                {
                    "type": "DraftSkipped",
                    "reason": "매뉴얼 선택 없음; 관측·확인 안내만 출력",
                },
            ),
        }
    try:
        draft, usage = await asyncio.wait_for(
            deps.quality_llm.write(
                state["query"],
                state.get("collected", []),
                attempt,
                state.get("validation_feedback"),
            ),
            deps.call_timeout,
        )
        return {
            "draft": draft,
            "last_prompt": usage.get("prompt"),
            "cost_usd": state.get("cost_usd", 0) + usage.get("usd", 0),
            "events": events(state, {"type": "DraftWritten", "attempt": attempt}),
        }
    except Exception as exc:
        return {
            "draft": "",
            "write_error": type(exc).__name__,
            "events": events(
                state, {"type": "GenerationFailed", "reason": type(exc).__name__}
            ),
        }


@traceable(name="improved.validate")
async def validate_node(state, deps):
    if state.get("draft") is None:
        return {
            "choices": [],
            "validation_feedback": None,
            "answer_status": "observation",
            "events": events(
                state, {"type": "Validation", "verdict": "관측·확인 안내", "attempt": 0}
            ),
        }
    ok, issues, doc = validate_draft(state["draft"], state.get("collected", []))
    attempts = state.get("validation_attempts", 0) + 1
    retry = not ok and attempts < deps.max_writes and not state.get("write_error")
    return {
        "choices": doc["sections"] if ok else [],
        "validation_attempts": attempts,
        "validation_feedback": "; ".join(issues) if retry else None,
        "validation_issues": issues,
        "answer_status": "validated" if ok else "fallback",
        "events": events(
            state,
            {
                "type": "Validation",
                "attempt": attempts,
                "verdict": "합격" if ok else "불합격",
                "issues": issues,
                "fallback": not ok and not retry,
            },
        ),
    }


@traceable(name="improved.finalize")
async def finalize_node(state, deps):
    notice = (
        "답변 생성·검증을 완료하지 못해 수집된 사실과 매뉴얼 원문만 안내합니다."
        if state.get("answer_status") == "fallback"
        else None
    )
    final = render_report(
        state.get("collected", []),
        state["targets"],
        state["unknown"],
        state.get("choices"),
        notice,
    )
    writer = get_stream_writer()
    for start in range(0, len(final), 80):
        writer(
            {
                "type": "AnswerToken",
                "delta": final[start : start + 80],
                "validated": True,
            }
        )
    return {
        "final": final,
        "evidence": evidence_payload(
            state.get("collected", []), state["targets"], state["unknown"]
        ),
        "events": events(
            state,
            {
                "type": "Finalize",
                "pipeline": "improved-v2",
                "answer_status": state.get("answer_status"),
            },
        ),
    }
