"""Identify request scope independently of the model's plan."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TargetSelection:
    known: tuple[str, ...]
    unknown: tuple[str, ...]


def select_targets(query: str, registered) -> TargetSelection:
    text = query.lower()
    known = sorted(
        (
            s
            for s in registered
            if re.search(rf"(?<![a-z0-9_-]){re.escape(s)}(?![a-z0-9_-])", text)
        ),
        key=text.index,
    )
    candidates = re.findall(
        r"(?<![a-z0-9_-])(?:[a-z0-9]+(?:[-_][a-z0-9]+)*-service|web-\d+)(?![a-z0-9_-])",
        text,
    )
    return TargetSelection(
        tuple(known), tuple(dict.fromkeys(s for s in candidates if s not in registered))
    )


def repair_plan(tasks, targets, needs_analysis):
    # The model may omit or invent a target. Only the explicit request is authority.
    result = [
        {
            "id": f"monitor-{s}",
            "agent": "research",
            "kind": "monitoring",
            "target": s,
            "status": "pending",
        }
        for s in targets
    ]
    if needs_analysis:
        result.append(
            {
                "id": "analysis",
                "agent": "analysis",
                "kind": "pattern-analysis",
                "status": "pending",
            }
        )
    return result


def remembered_name(history, query=""):
    messages = [m["content"] for m in history if m.get("role") == "user"] + [query]
    name = None
    for text in messages:
        found = re.search(
            r"(?:제|내)\s*이름(?:은|이)\s*([가-힣A-Za-z]{1,20}?)(?:입니다|이에요|예요|라고 합니다|라고 해요)(?:[.!]|\s|$)",
            text,
        )
        if found:
            name = found[1]
    return name
