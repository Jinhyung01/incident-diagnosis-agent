"""Render actual test records as clearly labelled capture/report pages."""
import argparse
import html
import json
from pathlib import Path

LABELS = {
    "original_target_selection": "원래 기준의 대상 선택",
    "original_runbook_selection": "원래 기준의 매뉴얼 선택",
    "prompt_label_is_gateway": "대표 라벨 gateway",
    "plan_needs_analysis": "분석 필요 플래그",
    "analysis_task_retained": "분석 작업 유지",
    "analysis_completed": "분석 호출 완료",
    "chat_route": "일반 대화 직접 분기",
    "no_monitoring_or_runbook": "불필요한 도구 조회 없음",
    "answer_tokens_before_final": "최종 답변 전 토큰 수신",
    "process_pid_changed": "새 서버 프로세스로 재시작",
    "sqlite_rows_preserved": "재시작 전후 DB 이력 보존",
    "user_name_persisted": "DB에 사용자 이름 보존",
    "history_in_final_prompt": "재시작 후 프롬프트에 이전 이름 전달",
    "answer_contains_name": "답변에 민수 포함(역할 정확성 별도 검토)",
    "token_concat_matches_final": "토큰 합계와 최종 답변 일치",
    "prompt_label_is_auth": "원래 정책의 대표 라벨 auth",
    "plan_target_clamped_to_auth": "원래 정책의 조사 대상 auth 보정",
}
STYLE = """
body{font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo',sans-serif;background:#f3f5f8;color:#192839;margin:0;padding:30px;line-height:1.55}
main{max-width:1250px;margin:auto}header{border-bottom:3px solid #1f5eaa;padding-bottom:15px;margin-bottom:18px}h1{font-size:27px;margin:5px 0}h2{font-size:18px;margin:0 0 10px}h3{font-size:15px;margin:12px 0 6px}.meta{font-size:13px;color:#56687c}.query{font-size:19px;font-weight:650;padding:14px;background:#e7eef8;border-radius:8px}.grid{display:grid;grid-template-columns:1fr 1.3fr;gap:16px;margin-top:16px}.box{background:white;border:1px solid #dce2eb;border-radius:8px;padding:18px;margin:14px 0}.grid .box{margin:0}p{margin:8px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-family:inherit;font-size:14px;margin:0}.badge{display:inline-block;border-radius:5px;padding:3px 9px;font-size:13px;margin:3px 4px 3px 0}.yes{background:#dff1e7;color:#165338}.no{background:#ffe4df;color:#8c2e22}.info{background:#e8edf3;color:#425367}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #e0e6ed;text-align:left;padding:9px;vertical-align:top}th{background:#edf2f8}a{color:#1f5eaa}.note{font-size:12px;color:#5d6c7c}footer{margin-top:16px;font-size:12px;color:#5d6c7c}.status{font-weight:650}
"""


def esc(value):
    return html.escape(str(value))


def seconds(value):
    return '없음' if value is None else f'{value:.2f}'


def document(title, body):
    return f'<!doctype html><html lang="ko"><meta charset="utf-8"><title>{esc(title)}</title><style>{STYLE}</style><main>{body}</main></html>'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);args=parser.parse_args()
    out=args.directory
    results=json.loads((out/'results.json').read_text())
    config=json.loads((out/'config.json').read_text())
    reviews=json.loads((out/'review.json').read_text()) if (out/'review.json').exists() else {}
    rows=[];md=['# 원본 쿼리 목적별 통합 검증','',
        '- 실행일: 2026-10-21 (Asia/Seoul)',
        '- 원본 v2 + 원본 HTTP 프록시 + 실제 MCP subprocess + 로컬 Ollama(qwen3:0.6b / qwen3:8b)',
        '- 별도 포트 8201/8701, 별도 session.db. 실행용 .env와 기존 서버·DB는 사용하지 않음.',
        '- 모니터링은 교육용 모의 데이터이며 원본의 무작위 변동을 유지. 실제 운영 서비스의 장애 진단 결과가 아니며, 고정 데이터 전후 비교 결과와 구분.',
        '- 캡처는 이 시험 기록 페이지의 화면이며 원본 채팅 UI 캡처와 구분.',
        '- 의미 정확성 검토는 AI 보조 검토. 자동 통과 항목은 아래에 표시한 구체적 조건만 뜻함.',
        '- 원래 목적 출처: all_total_vue_student/doc/regression_test_queries.md',
        '', '## 기존 계획에 미치는 영향', '',
        '주요 개선 4개와 추가 기능 3개의 방향은 유지한다. 대상 미명시·미등록 요청의 auth-service 기본 처리는 원본의 의도된 정책이므로, 이를 바꾸는 작업은 오류 수정이 아닌 정책 변경으로 설명한다. 스트리밍과 서버 재시작 후 대화 유지는 회귀 검증 범위에 포함한다.',
        '', '이 기록은 개선 전 원본의 단일 실행 결과다. 모델 응답과 원본 모니터링의 무작위 변동 때문에 이전 실행과 수치가 다를 수 있다. 개선 전후 정량 비교는 별도 고정 데이터 평가로 수행한다.', '']
    for c in results:
        review=reviews.get(c['id'],{})
        status='응답 완료' if c['response_complete'] else '응답 미완료'
        badges=''.join(f'<span class="badge {"yes" if v else "no"}">{esc(LABELS.get(k,k))}: {"확인" if v else "미충족"}</span>' for k,v in c['original_purpose_checks'].items())
        mon=''.join(f'<tr><td>{esc(m["system_name"])}</td><td>{esc(m["status"])}</td><td>{esc(m["cpu_percent"])}%</td><td>{esc(m["memory_percent"])}%</td></tr>' for m in c['monitoring'])
        replies=''.join(f'<h3>{esc(t["message"])}</h3><pre>{esc(t["reply"] or "최종 답변 없음")}</pre>'+(f'<p class="badge no">{esc(t["error"])}</p>' if t['error'] else '') for t in c['turns'])
        streams=''.join(f'<p>{i+1}턴: 토큰 이벤트 {t["stream_checks"]["token_events"]}개 · 첫 토큰 {seconds(t["stream_checks"]["first_token_seconds"])}초 · 최종 답변 {seconds(t["stream_checks"]["final_seconds"])}초 · 토큰 합계와 최종 답변 일치: {"예" if t["stream_checks"]["joined_tokens_match_final"] else "아니오"}</p>' for i,t in enumerate(c['turns']))
        body=f'''<header><div class="meta">AI Mini-project · 2026-10-21 · 원본 기능 통합 검증</div><h1>{esc(c['id'])} · 쿼리별 결과 기록</h1><div class="meta">실제 HTTP/SSE · MCP · Ollama / 원본 코드 수정 없음</div></header>
<div class="query">{esc(c['query'])}</div><p><b>원래 테스트 목적:</b> {esc(c['purpose'])}</p>
<p><span class="badge {"yes" if c['response_complete'] else "no"}">{status}</span><span class="badge info">총 {c['elapsed_seconds']:.2f}초</span><span class="badge info">매뉴얼: {esc(', '.join(c['runbooks']) or '조회 없음')}</span></p>
<div class="grid"><section class="box"><h2>목적별 확인 결과</h2>{badges}<h3>실제 수집 대상</h3><table><tr><th>대상</th><th>상태</th><th>CPU</th><th>메모리</th></tr>{mon or '<tr><td colspan="4">모니터링 조회 없음</td></tr>'}</table><h3>스트리밍 기록</h3>{streams}</section>
<section class="box"><h2>실제 응답</h2>{replies}</section></div>
<section class="box"><h2>결과 해석 · 개선 연결</h2><p>{esc(review.get('interpretation','AI 보조 검토 대기'))}</p><p><b>개선 연결:</b> {esc(review.get('improvement','미정'))}</p></section>
<footer>시험 기록 화면입니다. 원본 채팅 UI 화면이 아닙니다. 수치·답변·시간은 실제 호출 기록에서 가져왔습니다. <a href="{c['id']}.json">전체 JSON</a> · <a href="index.html">전체 결과</a></footer>'''
        (out/f"{c['id']}.html").write_text(document(c['id'],body))
        rows.append(f'<tr><td><a href="{c["id"]}.html">{c["id"]}</a></td><td>{esc(c["purpose"])}</td><td>{status}</td><td>{esc(", ".join(c["targets"]) or "없음")}</td><td>{c["elapsed_seconds"]:.2f}초</td><td><a href="captures/{c["id"]}.jpg">캡처</a></td></tr>')
        md += [f"## {c['id']}. {c['query']}",'',f"- 원래 목적: {c['purpose']}",f"- 응답: {status}, {c['elapsed_seconds']:.2f}초",f"- 조회: {', '.join(c['targets']) or '없음'}",f"- 매뉴얼: {', '.join(c['runbooks']) or '없음'}"]
        md += [f"- {LABELS.get(k,k)}: {'확인' if v else '미충족'}" for k,v in c['original_purpose_checks'].items()]
        md += [f"- 해석: {review.get('interpretation','AI 보조 검토 대기')}",f"- 개선 연결: {review.get('improvement','미정')}",f"- 캡처: captures/{c['id']}.jpg",'']
        for t in c['turns']:
            sc=t['stream_checks']
            md += [f"입력: {t['message']}", '', '```text', t['reply'] or '최종 답변 없음', '```', '', f"토큰 이벤트 {sc['token_events']}개 / 첫 토큰 {seconds(sc['first_token_seconds'])}초 / 최종 답변 {seconds(sc['final_seconds'])}초 / 토큰 합계 일치 {sc['joined_tokens_match_final']}", '']
    intro='<header><div class="meta">2026-10-21 · 원본 기능 확인</div><h1>쿼리별 통합 검증 결과</h1></header><section class="box"><p>원본 테스트 목적과 변경할 정책을 구분한 실제 호출 기록입니다.</p><p>실제 MCP·로컬 모델·HTTP 스트리밍을 사용하고, 이름 테스트는 별도 SQLite DB로 서버를 재시작했습니다.</p><p class="note">아래 캡처는 시험 기록 페이지의 화면입니다. 원본 채팅 UI 화면과 구분합니다. 원래 실행 스크립트의 DB 삭제 동작은 실행하지 않았고 코드로 확인했습니다.</p></section>'
    (out/'index.html').write_text(document('원본 쿼리 검증 결과',intro+'<section class="box"><table><tr><th>ID</th><th>원래 목적</th><th>응답</th><th>수집 대상</th><th>시간</th><th>기록</th></tr>'+''.join(rows)+'</table></section>'))
    (out/'REPORT.md').write_text('\n'.join(md).rstrip()+'\n')
    print(f'Rendered {len(results)} case pages and index.')


if __name__=='__main__':main()
