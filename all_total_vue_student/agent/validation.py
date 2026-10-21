"""Validate model-selected report fields before any incident text is published."""

import json
from .evidence import sections_from, runbook_steps


REPORT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "system_name": {"type": "string"},
                    "cpu_percent": {"type": "number"},
                    "memory_percent": {"type": "number"},
                    "runbook_id": {"type": "string"},
                    "step_ids": {"type": "array", "items": {"type": "integer"}},
                    "cause_confirmed": {"type": "boolean"},
                },
                "required": [
                    "system_name",
                    "cpu_percent",
                    "memory_percent",
                    "runbook_id",
                    "step_ids",
                    "cause_confirmed",
                ],
            },
        }
    },
    "required": ["sections"],
}


def validate_draft(draft, collected):
    try:
        doc = json.loads(draft)
        if (
            not isinstance(doc, dict)
            or set(doc) != {"sections"}
            or not isinstance(doc["sections"], list)
        ):
            raise ValueError("sections JSON 필요")
        expected = {s["system_name"]: s for s in sections_from(collected)}
        rows = doc["sections"]
        names = [s.get("system_name") for s in rows]
        if len(names) != len(set(names)) or set(names) != set(expected):
            return False, ["서비스 목록 누락·중복·범위 밖 대상"], None
        problems = []
        fields = {
            "system_name",
            "cpu_percent",
            "memory_percent",
            "runbook_id",
            "step_ids",
            "cause_confirmed",
        }
        for row in rows:
            s = expected[row["system_name"]]
            name = s["system_name"]
            if set(row) != fields:
                problems.append(f"{name}: 허용되지 않은 필드")
            for metric in ("cpu_percent", "memory_percent"):
                value = row.get(metric)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or value != s[metric]
                ):
                    problems.append(f"{name}: {metric} 관측값 불일치")
            if row.get("cause_confirmed") is not False:
                problems.append(f"{name}: 원인 확정 근거 없음")
            book = s["book"]
            if row.get("runbook_id") != (book["id"] if book else ""):
                problems.append(f"{name}: 매뉴얼 연결 불일치")
            ids = row.get("step_ids")
            steps = runbook_steps(book["body"]) if book else {}
            if (
                not isinstance(ids, list)
                or any(type(n) is not int or n not in steps for n in ids)
                or len(ids) != len(set(ids))
            ):
                problems.append(f"{name}: 원문에 없는 절차")
            elif book and not ids:
                problems.append(f"{name}: 절차 선택 없음")
            if not book and ids:
                problems.append(f"{name}: 문서 없이 조치 선택")
        return not problems, problems, doc
    except (ValueError, TypeError, KeyError, AttributeError):
        return False, ["구조화 답변 JSON 형식 오류"], None
