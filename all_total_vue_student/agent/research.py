"""Collect every requested service; a failed lookup does not cancel its peers."""

import asyncio
from datetime import datetime, timezone
from .evidence import monitoring_state
from .retry import with_retry


async def collect_monitoring(targets, mcp, timeout):
    async def one(target):
        try:
            data, retries = await asyncio.wait_for(
                with_retry(
                    mcp.call_tool, "get_monitoring_status", {"system_name": target}
                ),
                timeout,
            )
            if data.get("system_name") != target:
                raise ValueError("모니터링 응답 대상 불일치")
            return {
                "source": "monitoring",
                "service": target,
                "data": data,
                "retries": retries,
            }
        except Exception as exc:
            return {
                "source": "error",
                "service": target,
                "data": {
                    "service": target,
                    "stage": "monitoring",
                    "reason": type(exc).__name__,
                },
                "retries": 0,
            }

    return await asyncio.gather(*(one(t) for t in targets))


async def collect_runbooks(collected, searcher, mcp, timeout):
    results = []
    # Search per service. Do not mix CPU and memory alerts into a first-match label.
    for item in collected:
        if (
            item.get("source") != "monitoring"
            or monitoring_state(item["data"]) != "investigate"
        ):
            continue
        data = item["data"]
        target = data["system_name"]
        query = f"상태 {data['status']}. 증상: " + "; ".join(data.get("alerts", []))
        try:
            found = await asyncio.wait_for(searcher.search(query), timeout)
            matches = found.get("matches", [])
            results.append(
                {
                    "source": "search",
                    "service": target,
                    "data": {
                        "query": query,
                        "model": found.get("model"),
                        "matches": [
                            {k: v for k, v in m.items() if k != "body"} for m in matches
                        ],
                    },
                }
            )
            if not matches:
                raise LookupError("검색 임계값을 넘는 매뉴얼 없음")
            match = matches[0]
            server, template = await mcp.find_resource_template("get_incident_runbook")
            uri = template.format(incident_type=match["id"])
            body = await asyncio.wait_for(mcp.read_resource(uri, server), timeout)
            if body.startswith("# Runbook Not Found"):
                raise LookupError("매뉴얼 원문 없음")
            results.append(
                {
                    "source": "runbook",
                    "service": target,
                    "data": {
                        "id": match["id"],
                        "title": match["title"],
                        "uri": uri,
                        "score": match["score"],
                        "body": body,
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "embedding_model": found.get("model"),
                    },
                }
            )
        except Exception as exc:
            results.append(
                {
                    "source": "error",
                    "service": target,
                    "data": {
                        "service": target,
                        "stage": "runbook",
                        "reason": type(exc).__name__,
                    },
                }
            )
    return results
