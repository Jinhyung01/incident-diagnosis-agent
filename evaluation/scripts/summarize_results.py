"""Create a factual Markdown summary of completed evaluation records."""
import argparse
import json
import statistics
from pathlib import Path


def percent(numerator, denominator):
    return f"{numerator}/{denominator} ({numerator / denominator:.1%})" if denominator else "N/A"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("directory", type=Path)
    args = p.parse_args()
    config = json.loads((args.directory / "config.json").read_text())
    path = args.directory / "results.json"
    results = json.loads(path.read_text()) if path.exists() else []
    expected_count = len(config["case_ids"]) * config["repeat"]
    failures = sum(r["error"] for r in results)
    scope = sum(r["metrics"]["target_scope_pass"] for r in results)
    scope_completed = sum(r["metrics"]["target_scope_pass"] and not r["error"] for r in results)
    matched = sum(r["metrics"]["matched_targets"] for r in results)
    targets = sum(r["metrics"]["expected_target_count"] for r in results)
    single = [r for r in results if r["metrics"]["runbook_top1_correct"] is not None]
    top1 = sum(r["metrics"]["runbook_top1_correct"] for r in single)
    top1_completed = sum(r["metrics"]["runbook_top1_correct"] and not r["error"] for r in single)
    no_books = [r for r in results if r["metrics"]["runbook_none_pass"] is not None]
    no_book_pass = sum(r["metrics"]["runbook_none_pass"] and not r["error"] for r in no_books)
    completed_successes = [r for r in results if not r["error"]]
    timing = (f"{statistics.median(r['elapsed_seconds'] for r in completed_successes):.2f}초"
              if completed_successes else "N/A (성공한 요청 없음)")
    lines = [
        "# 개선 전 평가 실행 요약", "",
        f"- 백엔드: `{config['backend']}`",
        f"- 모델: `{config['fast_model']}` / `{config['quality_model']}`",
        f"- 완료 기록: {len(results)}/{expected_count}; 실행 오류: {failures}",
        f"- 최종 응답 완료: {percent(len(results) - failures, len(results))}",
        "- 평가 범위: 원본 v2 그래프 + 고정 데이터 MCP 어댑터. 실제 MCP 전송 및 웹 UI는 이 실험의 검증 대상이 아님.",
        "- 토큰 수는 Ollama 응답에서 수집. cost_usd는 가상 비교값이며 실제 청구액이 아님.",
        "- 타임아웃 난 LLM 호출은 토큰 사용량을 반환하지 않으므로 기록된 토큰 합계는 전체 생성량이 아님.",
        f"- 설정된 반복 횟수: 사례별 {config['repeat']}회. 작은 평가 세트의 결과이며 운영 전체의 성능을 대표하지 않음.",
        "- 의미·사실 정확성은 자동 채점하지 않았음. review 체크리스트에 따른 사람 검토 필요.", "",
    ]
    if config["backend"] == "fake":
        lines += ["**Fake 결과는 실행기 확인용이다. 실제 모델의 성능 결과로 사용하지 않는다.**", ""]
    if len(results) != expected_count:
        lines += ["**부분 실행이다. 전체 20개 질문의 성능으로 해석하지 않는다.**", ""]
    if results:
        lines += [
            "| 자동 지표 | 결과 |", "|---|---|",
            f"| 요청한 등록 대상 수집률 | {percent(matched, targets)} |",
            f"| 조회 단계의 대상 범위 일치 | {percent(scope, len(results))} |",
            f"| 대상 범위 일치 + 최종 응답 완료 | {percent(scope_completed, len(results))} |",
            f"| 검색 단계의 단일 정답 매뉴얼 Top-1 | {percent(top1, len(single))} |",
            f"| 단일 정답 매뉴얼 적중 + 최종 응답 완료 | {percent(top1_completed, len(single))} |",
            f"| 매뉴얼 불필요 사례의 불필요 검색 방지 | {percent(no_book_pass, len(no_books))} |",
            f"| 성공한 사례의 처리 시간 중앙값 | {timing} |", "",
            "대상 수집률은 대상 개수로, 대상 범위 일치는 사례 수로 계산한다. 대상 범위는 수집에 성공한 서비스 집합 기준이며 실패한 호출 시도는 별도 확인한다.",
            "단일 정답 Top-1은 정답 문서가 하나인 사례만 포함한다. 검색·수집 뒤 응답이 실패할 수 있어 단계별 지표와 완료 지표를 나눴다.",
            "매뉴얼 불필요 사례에는 일반 대화도 포함된다. 이 값은 정상 서비스 처리만의 성공률이 아니다.", "",
            "| 데이터 구분 | 기록 | 최종 응답 완료 | 시간 초과 등 오류 |",
            "|---|---:|---:|---:|",
        ]
        for split in ("development", "evaluation", "supplemental"):
            group = [r for r in results if r['split'] == split]
            if group:
                errors = sum(r['error'] for r in group)
                lines.append(f"| {split} | {len(group)} | {len(group) - errors} | {errors} |")
        lines += ["",
            "| ID | 실제 조회 대상 | 매뉴얼 | 시간(초) | 오류 |",
            "|---|---|---|---:|---|",
        ]
        for r in results:
            m = r["metrics"]
            lines.append(f"| {r['id']} | {', '.join(m['actual_targets']) or '없음'} | "
                         f"{', '.join(m['actual_runbooks']) or '없음'} | {r['elapsed_seconds']:.2f} | "
                         f"{'있음' if r['error'] else '없음'} |")
    else:
        lines += ["완료된 사례가 없어 품질 지표를 산출하지 않았다."]
    (args.directory / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    print(args.directory / "SUMMARY.md")


if __name__ == "__main__":
    main()
