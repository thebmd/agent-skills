---
name: hwpx-core
description: 한글(hwpx) 파일을 읽고 고치고 검증하는 공통 기반 스킬. hwpx 양식 채우기·수정, 표 행 추가, 들여쓰기(내어쓰기) 조정, 사용자 수정본과의 비교, 한글 렌더링 확인 등 hwpx를 XML 수준에서 다루는 모든 작업 전에 읽는다. 공문·논문·계획서 같은 문서별 작업 스킬은 이 스킬의 규칙과 스크립트를 전제로 한다. 트리거: ".hwpx", "한글 파일", "한글 양식", "hwpx 수정", "한글 문서 만들어줘".
---

# hwpx-core — 한글 파일 공통 조작

hwpx는 XML 묶음(zip)이다. 이 스킬은 **문서 종류와 무관한 파일 조작 규칙**만 다룬다.
문서별 내용 규칙(공문 문체, 학회 서식 등)은 각 작업 스킬에 있다.

도구: `scripts/hwpx_tool.py` (lxml 필요), `scripts/render_request.py`

```bash
T=<이 스킬 폴더>/scripts/hwpx_tool.py
python $T unpack 원본.hwpx work/          # 해제
python $T dump   work/Contents/section0.xml   # 구조 (문단모양 ID·표 셀 주소)
python $T text   파일.hwpx                 # 본문 텍스트 (줄바꿈 ⏎ 표시)
python $T diff   이전.hwpx 새것.hwpx        # 본문 텍스트 비교
python $T parapr work/Contents/header.xml 57 58   # 문단모양 정렬·여백·내어쓰기
python $T pack   work/ 결과.hwpx --order-from 원본.hwpx
python $T check  결과.hwpx                 # 패키징·XML 무결성
```

## 1. 시작 전에

- **원본은 절대 덮어쓰지 않는다.** 결과는 `_v2`, `_초안`처럼 새 이름으로 저장한다.
- **사용자가 한글에서 고친 파일이 있으면 그 파일을 기준으로 삼는다.** 먼저 `diff`로 내 이전 결과물과 비교해, 사용자가 무엇을 바꿨는지 확인한 뒤 작업한다. 사용자 수정을 되돌리면 안 된다.
- 본문은 `Contents/section0.xml`만이 아니다. **section0, section1 … 여러 개**일 수 있다(예: section0=별표 흐름도, section1=본문). `content.hpf`에서 목록을 확인하고, 각각 `dump`로 무엇이 들어 있는지 본다.

## 2. 텍스트 읽기 — 줄바꿈을 놓치지 말 것

`<hp:t>` 안에는 글자만 있는 게 아니다.

| 요소 | 한글에서 | 텍스트로 |
|---|---|---|
| `<hp:lineBreak/>` | **Shift+Enter** (문단 안 줄바꿈) | 줄바꿈 |
| `<hp:tab/>` | Tab | 탭 |
| `<hp:fwSpace/>`, `<hp:nbSpace/>` | 전각·묶음 빈칸 | 공백 |

`''.join(t.text)`처럼 `.text`만 이으면 lineBreak 뒤 글자(tail)가 빠진다.
예: "한국철도기술⏎연구원"을 "한국철도기술"로 읽고 오탈자라고 잘못 보고하게 된다.
반드시 `hwpx_tool.t_text()` / `text` 명령을 쓴다.

## 3. 고치기 — 기본 규칙

- XML은 **lxml로 파싱해서** 고친다. 문자열 치환·정규식·f-string 조립 금지. section 파일 전체를 새로 쓰기 금지.
- 저장은 `hwpx_tool.save()` (XML 선언·인코딩·standalone 유지).
- **텍스트를 바꾼 문단은 그 문단 직계의 `linesegarray`(줄 배치 캐시)만 지운다.** 한글이 열 때 다시 계산한다. 하위 표 안 문단이나 안 고친 문단의 캐시까지 재귀 삭제하면 얇은 셀·음수 줄간격 양식이 깨진다. (`set_text`, `clone_para`가 이 규칙대로 동작)
- **run 삭제 전에 `audit_runs`로 확인.** t 말고 다른 자식(secPr·ctrl·tbl·pic)이 있는 run은 삭제 금지 — 쪽 설정, 쪽번호, 제목 테두리 표가 통째로 사라진다.
- 줄바꿈이 필요한 셀 텍스트는 `'\n'`을 넣으면 `set_text`가 lineBreak로 바꿔 넣는다.

## 4. 문단·표 늘리기 — 같은 파일 안에서 복제

- 새 문단은 **같은 파일의 비슷한 문단을 복제**해 텍스트만 바꾼다 (`clone_para`). 그래야 글꼴·문단모양 ID가 그 파일에서 유효하다.
- **다른 파일(예: 빈 양식)의 표·문단을 가져오지 않는다.** 파일마다 header.xml의 charPr/paraPr/borderFill 번호 체계가 달라서 서식이 엉뚱하게 바뀐다. 필요한 모양의 표가 없으면, 같은 파일 안에서 열 수가 같은 표를 복제해 셀 텍스트와 열 너비(`set_col_widths`)를 바꾼다.
- 표 행 추가: `add_rows(tbl, n)` — 마지막 행 복제, `rowAddr`·`rowCnt`·표 높이 갱신. **병합 셀이 있는 표에는 쓰지 않는다** (cellSpan·cellAddr를 직접 계산해야 함).
- 셀 내용 교체: `set_cell(tc, [문단1, 문단2...], para_pr=ID)`.
- 셀 높이(`cellSz height`)는 최소값 개념이다. 대략만 맞춰 두면 한글이 열 때 내용에 맞게 늘린다.

## 5. 들여쓰기 · 내어쓰기

번호 항목은 **내어쓰기**를 해야 둘째 줄이 번호 뒤 글자에 맞춰 정렬된다. 들여쓰기 없는 문단모양으로 일괄 복제하면 표가 지저분해진다.

- 한글은 내어쓰기를 `left=0`, **`intent` 음수**(HWPUNIT)로 저장한다. 한 문단모양에 `hp:switch/case`와 `default` 두 군데 margin이 있으니 **양쪽 다** 바꾼다 (`add_para_pr`가 처리).
- 필요한 내어쓰기 문단모양이 없으면 `add_para_pr(header, base_id, intent=-N)`로 새로 만들고 그 ID를 문단에 지정한다. 기존 문단모양 값을 고치면 같은 ID를 쓰는 다른 문단까지 바뀌므로 새로 만든다.
- 값 기준 (10pt 본문, 실제 양식에서 확인한 값):

| 머리 | intent |
|---|---|
| `(1) ` | 약 -1,840 (한글 실측 -1,770 ~ -1,940) |
| `1. ` | 약 -1,150 (추정) |
| ` - ` | 약 -1,770 |
| `○ ` | 약 -1,990 |

  글자 크기가 다르면 비례해서 조정한다. 정확한 값은 같은 양식에서 이미 내어쓰기된 문단의 `parapr`를 보고 따라 한다.

## 6. 한글이 다시 저장한 파일

사용자가 한글에서 열어 저장하면:
- header.xml의 **paraPr/charPr 번호가 다시 매겨진다** (안 쓰는 모양 정리). 이전 버전에서 알아둔 ID를 재사용하지 말고 **새 파일에서 `dump`·`parapr`로 다시 확인**한다.
- zip 압축 방식·파일 순서가 바뀐다. 다시 묶을 때 `--order-from <그 파일>`로 순서를 따른다.

## 7. 묶기

- `mimetype`은 **무압축(STORED)으로 첫 항목**. 디렉터리 항목은 넣지 않는다. (`pack`이 처리)
- 묶은 뒤 `check` 통과 확인.

## 8. 검증

1. `check` — zip·XML 무결성
2. `text` / `diff` — 의도한 텍스트만 바뀌었는지, 자리표시가 남았는지
3. **렌더링 확인** — Linux(ARM 포함)에서는 한글 렌더링이 안 된다.
   `python scripts/render_request.py 결과.hwpx` → 공유 폴더(`~/shared/papers/_render/`)를 통해 Windows 노트북의 한글 렌더 도우미(`hwp_render_watcher.py`, pyhwpx)가 PDF를 만들어 준다. PDF를 이미지로 바꿔 레이아웃을 본다.
   시간 초과(도우미 꺼짐)면 **확인 못 했다고 명시**하고, 사용자에게 한글에서 열어 확인할 곳(표 정렬, 내어쓰기, 쪽 넘김)을 구체적으로 알려준다. 검증 안 된 것을 된 것처럼 보고하지 않는다.

## 9. 보고할 때

- 무엇을 바꿨는지(섹션·표 단위), 어떤 파일을 기준으로 했는지, 무엇을 확인 못 했는지를 짧게.
- 값을 추정한 곳(내어쓰기 폭, 셀 높이 등)은 추정이라고 밝힌다.
