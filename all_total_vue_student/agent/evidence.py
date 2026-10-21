"""Build service-scoped evidence and preserve runbook conditions verbatim."""

import math
import re


def monitoring_state(data):
    if data.get("status") not in {"healthy", "degraded", "down"}:
        return "unknown"
    for key in ("cpu_percent", "memory_percent"):
        n = data.get(key)
        if (
            isinstance(n, bool)
            or not isinstance(n, (int, float))
            or not math.isfinite(n)
            or not 0 <= n <= 100
        ):
            return "unknown"
    if data["status"] == "healthy" and not data.get("alerts"):
        return "healthy"
    if not data.get("alerts"):
        return "insufficient"
    return "investigate"


def runbook_steps(body):
    return {int(n): text for n, text in re.findall(r"(?m)^(\d+)\.\s+(.+)$", body)}


def sections_from(collected):
    books = {
        c.get("service"): c["data"] for c in collected if c.get("source") == "runbook"
    }
    sections = []
    for c in collected:
        if c.get("source") == "monitoring":
            d = c["data"]
            sections.append(
                {
                    "system_name": d["system_name"],
                    "cpu_percent": d["cpu_percent"],
                    "memory_percent": d["memory_percent"],
                    "state": monitoring_state(d),
                    "book": books.get(d["system_name"]),
                    "data": d,
                }
            )
    return sections


def evidence_payload(collected, targets=(), unknown=()):
    sections = sections_from(collected)
    observed = {s["system_name"] for s in sections}
    return {
        "services": [
            {
                "system_name": s["system_name"],
                "state": s["state"],
                "monitoring": s["data"],
                "runbook": s["book"],
            }
            for s in sections
        ],
        "unregistered": list(unknown),
        "unconfirmed_targets": [s for s in targets if s not in observed],
        "limitations": [
            "교육용 모의 모니터링",
            "실제 로그·배포 이력·의존 관계·시계열 미수집",
            "서버 조치는 실행하지 않음",
        ],
        "errors": [c["data"] for c in collected if c.get("source") == "error"],
    }


def render_report(collected, targets=(), unknown=(), choices=None, notice=None):
    sections = sections_from(collected)
    lines = []
    if notice:
        lines += [notice, ""]
    if not targets:
        if unknown:
            lines.append(
                "미등록 서비스: "
                + ", ".join(unknown)
                + ". 등록된 다른 서비스로 바꾸어 조회하지 않았습니다."
            )
            lines.append("확인할 등록 서비스 이름을 알려주세요.")
        else:
            lines.append("어느 서비스를 확인할까요? 서비스 이름을 알려주세요.")
        return "\n".join(lines)
    choice_map = {c["system_name"]: c for c in (choices or [])}
    for section in sections:
        d = section["data"]
        name = d["system_name"]
        lines += [f"### {name}"]
        if section["state"] == "unknown":
            lines.append(
                "모니터링 정보가 유효하지 않아 CPU·메모리를 확인할 수 없습니다."
            )
        else:
            lines.append(
                f"확인된 상태: {d['status']} · CPU {d['cpu_percent']}% · 메모리 {d['memory_percent']}%"
            )
        lines.append(f"조회 시각: {d['last_checked']}")
        if d.get("alerts"):
            lines.append("활성 알림: " + "; ".join(d["alerts"]))
        if section["state"] == "healthy":
            lines.append(
                "현재 관측은 정상이며 활성 알림이 없습니다. 장애 매뉴얼을 적용하지 않았습니다."
            )
        elif section["state"] in {"unknown", "insufficient"}:
            lines.append(
                "상태 판단에 필요한 정보가 부족합니다. 추가 지표와 알림 확인이 필요합니다."
            )
        elif section["book"]:
            b = section["book"]
            steps = runbook_steps(b["body"])
            selected = choice_map.get(name, {}).get("step_ids") or list(steps)[:3]
            lines.append(f"참고 매뉴얼: {b['title']} ({b['id']})")
            lines.append("확인·대응 절차 (매뉴얼 원문, 조치 미실행):")
            lines.extend(f"- {steps[n]}" for n in selected if n in steps)
        else:
            lines.append(
                "관련 매뉴얼을 확보하지 못했습니다. 임의의 장애 유형으로 대체하지 않았습니다."
            )
        lines += [""]
    observed = {s["system_name"] for s in sections}
    missing = [t for t in targets if t not in observed]
    if missing:
        lines.append("조회 실패·미확인: " + ", ".join(missing))
    if unknown:
        lines.append("미등록·미조회: " + ", ".join(unknown))
        lines.append("미등록 대상 대신 확인할 등록 서비스 이름을 알려주세요.")
    lines += [
        "추가 확인: 실제 로그·배포 이력·시계열은 수집하지 않아 근본 원인과 조치 조건의 지속 여부는 확인하지 못했습니다."
    ]
    if len(targets) > 1:
        lines.append(
            "공통 원인: 서비스별 상태는 확인했으나 의존 관계·동시 변화 자료가 없어 확정할 수 없습니다."
        )
    return "\n".join(lines)
