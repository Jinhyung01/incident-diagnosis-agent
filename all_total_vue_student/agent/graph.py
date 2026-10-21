"""Improved v2: scope -> collect -> retrieve -> choose -> validate -> render.

Original implementation is preserved under day1/baseline/original_v2.
"""

from functools import partial
from typing import TypedDict
from langgraph.graph import END, StateGraph
from . import nodes


class AgentState(TypedDict, total=False):
    query: str
    thread_id: str
    history: list[dict]
    route: str
    targets: list[str]
    unknown: list[str]
    tasks: list[dict]
    needs_analysis: bool
    collected: list[dict]
    retry_count: int
    analysis_note: str
    draft: str | None
    choices: list[dict]
    validation_attempts: int
    validation_feedback: str | None
    validation_issues: list[str]
    write_error: str
    answer_status: str
    final: str
    evidence: dict
    last_prompt: str
    cost_usd: float
    events: list[dict]


def build_graph(deps):
    g = StateGraph(AgentState)
    for name in (
        "scope",
        "chat",
        "plan",
        "monitoring",
        "retrieval",
        "analysis",
        "write",
        "validate",
        "finalize",
    ):
        g.add_node(name, partial(getattr(nodes, name + "_node"), deps=deps))
    g.set_entry_point("scope")
    g.add_conditional_edges(
        "scope", lambda s: s["route"], {"chat": "chat", "incident": "plan"}
    )
    g.add_edge("chat", END)
    for a, b in [
        ("plan", "monitoring"),
        ("monitoring", "retrieval"),
        ("retrieval", "analysis"),
        ("analysis", "write"),
        ("write", "validate"),
    ]:
        g.add_edge(a, b)
    g.add_conditional_edges(
        "validate",
        lambda s: "write" if s.get("validation_feedback") else "finalize",
        {"write": "write", "finalize": "finalize"},
    )
    g.add_edge("finalize", END)
    return g.compile()
