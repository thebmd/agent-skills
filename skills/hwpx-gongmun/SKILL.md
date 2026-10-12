---
name: hwpx-gongmun
description: hwpx 공문/기안문 양식을 첨부하면 주제에 맞춰 공문 내용을 자동 작성. 작성 전 반드시 사용자에게 ①목표 분량(페이지 수) ②문체(개조식/서술식) ③내용 중점 방향을 3단계로 질문·확정한 뒤, 확정값에 근사하게 본문을 설계·검증한다. 파일 조작 규칙·스크립트는 hwpx-core 스킬을 따른다 (v5.2, 2026-10-12 — 공통 조작을 hwpx-core로 분리)
---

# HWPX 공문/기안문 자동 채우기 스킬 (v5.2)

> **먼저 `hwpx-core` 스킬을 읽는다.** 파일 해제·텍스트 읽기(Shift+Enter 줄바꿈)·lineseg 삭제·문단 복제·
> 표 행 추가·내어쓰기·재패키징·렌더링 검증은 모두 hwpx-core 규칙과 `hwpx_tool.py`를 따른다.
> 이 스킬은 **공문/기안문 고유 규칙**(사전 질문, 분량 설계, 섹션 교체, 제목·자리표시 처리, 문체)만 다룬다.

## 0단계: 3단계 사전 질문 (★★★ 반드시 가장 먼저, 순서대로 실행)

> **아래 3개 질문을 모두 확정하기 전에는 본문 작성을 시작하지 않는다.**
> 질문은 반드시 **한 번에 하나씩, ①→②→③ 순서로** 진행한다 (한 턴에 몰아서 묻지 않는다).
> 사용자가 이미 답을 명시한 항목은 질문을 생략하고 그 값으로 확정한다.
> 3개 항목이 모두 확정되면 **"목표 N페이지 · ○○식 · 중점: ○○ 기준으로 본문 약 M개 문단을 설계합니다"라고 선언**하고 작업을 시작한다.

### 0-1. 질문 ① — 목표 분량 (페이지 수)

- "완성본을 **총 몇 페이지** 분량으로 만들까요? (예: 1p 요약 / 3p 보고 / 5p 상세 / 10p 계획서)"
- 필요 시 추가로: 섹션별 비중(개요는 짧게, 방안은 길게 등) 선호 여부

사용자가 이미 분량을 명시했다면(예: "5p 내외", "10페이지짜리") 질문 없이 그 값을 목표로 확정한다.

### 0-2. 질문 ② — 문체 (개조식 vs 서술식)

분량 확정 후 다음을 질문한다:

- "본문 문체는 **개조식**과 **서술식** 중 어떤 방식으로 작성할까요?"
  - **개조식**: 명사형 종결("~함", "~추진", "~필요"), 짧은 요점 나열 — 공공기관 보고서 표준
  - **서술식**: 완결형 문장("~합니다", "~할 계획입니다") — 대외 공문·설명 자료에 적합

**문체별 작성 규칙:**

| 구분 | 개조식 | 서술식 |
|------|--------|--------|
| 종결 | 명사형(~함/~임/~됨/~추진/~마련) 또는 체언 종결 | 경어체(~합니다/~습니다) 완결 문장 |
| 문장 길이 | 1문단 = 1행 내외의 핵심 요지 | 1문단 = 1~2문장의 완결 서술 |
| 조사·수식어 | 최소화, 핵심 명사 중심 | 자연스러운 문장 흐름 유지 |
| 분량 환산 영향 | 문단당 줄 수가 짧아짐 → 같은 페이지에 문단 수 +10~20% 필요 | 0-4 환산표 기본값 적용 |

> 개조식 확정 시 0-4의 목표 문단 수에 **+10~20%를 가산**하여 설계한다.

### 0-3. 질문 ③ — 내용 중점 방향

문체 확정 후 다음을 질문한다:

- "내용은 **어느 쪽에 중점**을 둘까요? (예: ⑴ 추진 배경·필요성 논리 강화 / ⑵ 실행 방안·운영 계획 구체화 / ⑶ 기대효과·성과지표 부각 / ⑷ 예산·일정 등 관리 정보 중심)"
- 문서 주제에 맞게 선택지를 조정하되, 2~4개의 상호배타적 방향을 제시한다

**중점 방향은 0-5 섹션별 문단 배분에 직접 반영한다:**
- 선택된 중점 영역의 섹션에 전체 본문 문단의 **35~45%를 배분** (최대 배분 섹션으로 지정)
- 나머지 섹션은 잔여 분량을 논리 흐름에 따라 안배
- 중점 섹션은 □ 소제목을 더 세분화하고 ―/※ 세부 문단을 우선 확장한다

### 0-4. 페이지 → 문단 수 환산 (분량 설계표)

한글 보고서 양식(A4, 상하 여백 표준, 휴먼명조 15pt, 문단 위 간격 포함) 기준 실측 환산:

| 요소 | 1페이지당 분량 |
|------|---------------|
| □ 소제목(헤드라인M 16) | 문단 위 여백 포함 약 2줄 점유 |
| ○/―/※ 본문(15pt/13pt) | 1문단 = 1~2줄 (긴 문장은 2줄로 계산) |
| **본문 문단 수 환산치** | **1페이지 ≈ 본문 10~13문단** (표지·목차 제외) |

**목표 문단 수 공식:**
```
본문 목표 문단 수 = (목표 페이지 수 - 표지/목차 페이지 수) × 11  (±10%)
```

예시:
- 5p 요청, 표지 없음 → 약 **55문단** (□ 8~10개 + ○/―/※ 45개 내외)
- 10p 요청, 표지+목차 2p → 본문 8p → 약 **88문단** (□ 12~16개 + ○/―/※ 70개 내외)
- 1p 요약 → 약 11문단

### 0-5. 섹션별 문단 배분 계획 수립 (★ 질문 ③의 중점 방향 반영)

본문 작성 전에 **섹션별 문단 배분표를 먼저 작성**하고 나서 content_list를 만든다:

```
예: 10p 계획서(본문 88문단) 배분
Ⅰ. 개요        : 10문단 (□2, ○3, ―4, ※1)
Ⅱ. 추진배경    : 14문단 (□3, ○4, ―5, ※2)
Ⅲ. 현황및문제점 : 22문단 (□4, ○6, ―8, ※4)
Ⅳ. 개선방안    : 28문단 (□5, ○8, ―10, ※5)  ← 질문 ③에서 확정한 중점 섹션에 최대(35~45%) 배분
Ⅴ. 향후계획    : 14문단 (□3, ○4, ―5, ※2)
```

**분량을 늘리는 올바른 방법** (같은 말 반복 금지):
- (개조식 확정 시) 목표 문단 수에 +10~20% 가산분을 먼저 반영
- □ 소제목 자체를 세분화 (예: "교육 운영" → "기수 편성", "실습 인프라", "교수진 구성" 3개로 분리)
- ○ 항목마다 ― 세부 근거 2~3개씩 확장 (수치·일정·대상·방법을 각각 별도 ― 로)
- ※ 참고·유의사항·기대효과를 섹션마다 1~2개 추가
- 원문(PDF 등)에 있는 구체적 수치·사례·고유명사를 빠짐없이 활용 (요약하며 버리지 말 것)

---

## 1단계: HWPX 파일 해제

`python hwpx_tool.py unpack 원본.hwpx original/` (hwpx-core). 본문 section 파일이 여러 개일 수 있으니 `content.hpf`로 확인한다.
mimetype, META-INF/, BinData/, Preview/는 수정하지 않는다.

---

## 2단계: section XML 구조 분석 (★ 반드시 실행)

단순히 텍스트를 순회하는 것이 아니라, **문단의 부모 구조(parent tag)** 를 함께 파악해야 한다.
한글 보고서 양식에서 본문 단락(□,○,―,※)은 흔히 **모든 섹션이 동일한 `<sec>` 요소의 직계 자식**으로 연결된다.
이 구조를 무시하면 섹션 경계 탐색이 실패하여 전체 본문이 삭제되는 치명적 오류가 발생한다.

```python
from lxml import etree

with open('original/Contents/section0.xml', 'rb') as f:
    tree = etree.parse(f)
root = tree.getroot()

# ★ sec 요소 찾기
sec_elem = None
for elem in root.iter():
    if etree.QName(elem.tag).localname == 'sec':
        sec_elem = elem
        break

# ★ sec 직계 자식 인덱스 맵핑 (구조 파악 필수)
sec_children = list(sec_elem)
print(f"sec 직계 자식 수: {len(sec_children)}")
for i, child in enumerate(sec_children):
    local = etree.QName(child.tag).localname
    if local == 'p':
        texts = [t.text for t in child.iter()
                 if etree.QName(t.tag).localname == 't' and t.text and t.text.strip()]
        if texts:
            print(f"sec_child[{i}] p: {'|'.join(texts)[:70]}")
    else:
        print(f"sec_child[{i}] {local}")
```

이 출력으로 **각 섹션 본문의 정확한 start/end 인덱스**를 확인한 뒤 다음 단계로 진행한다.

---

## 3단계: XML 수정

### ★★★ 가장 중요한 규칙: linesegarray 삭제 ★★★

텍스트를 수정한 `<hp:p>` **직계의** `linesegarray`만 삭제한다 (hwpx-core 3절, `remove_own_lineseg`).
텍스트를 읽을 때는 `hwpx_tool.t_text()`를 써서 lineBreak(Shift+Enter)를 놓치지 않는다 (hwpx-core 2절).

### 절대 금지 사항

- 절대로 XML을 문자열(f-string, concat, replace)로 조합하지 않는다.
- 절대로 XML 선언(<?xml ...?>)을 수동으로 추가하지 않는다.
- 절대로 section0.xml 전체를 새로 작성하지 않는다.
- 절대로 .replace()나 re.sub()로 XML을 조작하지 않는다.
- **절대로 텍스트 내용으로 섹션 경계를 탐색하지 않는다 → 2단계의 인덱스 맵핑을 사용한다.**

---

## 4단계: 섹션 본문 교체 (★★★ sec 공유 구조 대응)

### 핵심 헬퍼 함수

```python
import copy

def clone_para(ref_p, run_texts):
    """
    ref_p를 깊은 복사하여 각 run의 텍스트를 교체.
    run_texts: ['run0에 넣을 텍스트', 'run1에 넣을 텍스트', ...]
    여분의 run은 제거. linesegarray 삭제 필수.
    """
    new_p = copy.deepcopy(ref_p)
    remove_own_lineseg(new_p)   # hwpx-core
    runs = [c for c in new_p if etree.QName(c.tag).localname == 'run']
    for i, txt in enumerate(run_texts):
        if i < len(runs):
            for t in runs[i]:
                if etree.QName(t.tag).localname == 't':
                    t.text = txt
                    break
    for r in runs[len(run_texts):]:
        new_p.remove(r)
    return new_p


def replace_section_body(sec_elem, body_start_idx, body_end_idx,
                          ref_box, ref_circle, ref_dash, ref_note,
                          content_list):
    """
    sec_elem      : 모든 본문 단락의 공통 부모 sec 요소
    body_start_idx: 교체 시작 자식 인덱스 (첫 □ 위치)
    body_end_idx  : 교체 끝 자식 인덱스 + 1 (exclusive)
    ref_box       : □ 두 run 구조 참조 단락 (deepcopy 원본)
    ref_circle    : ○ 단락 참조
    ref_dash      : ― 단락 참조
    ref_note      : ※ 단락 참조
    content_list  : [("box"|"circle"|"dash"|"note", "텍스트"), ...]
    """
    to_remove = list(sec_elem)[body_start_idx:body_end_idx]
    for child in to_remove:
        sec_elem.remove(child)

    sym_map = {
        "box":    (" □  ", True),
        "circle": ("  ○ ", False),
        "dash":   ("   ― ", False),
        "note":   ("     ※ ", False),
    }
    ref_map = {
        "box": ref_box, "circle": ref_circle,
        "dash": ref_dash, "note": ref_note,
    }

    insert_pos = body_start_idx
    for typ, text in content_list:
        sym, two_run = sym_map[typ]
        ref_p = ref_map[typ]
        if two_run:
            new_p = clone_para(ref_p, [sym, text])
        else:
            new_p = clone_para(ref_p, [sym + text])
        sec_elem.insert(insert_pos, new_p)
        insert_pos += 1
```

### ★★★ 반드시 역순(Ⅳ→Ⅲ→Ⅱ→Ⅰ)으로 처리

여러 섹션을 순서대로(Ⅰ→Ⅱ→...) 처리하면 삽입/삭제로 인해 이후 섹션 인덱스가 틀어진다.
**반드시 마지막 섹션부터 역순으로 호출한다.**

```python
# 2단계 출력으로 확인한 실제 인덱스를 아래에 입력
# 참조 단락은 수정 전에 반드시 deepcopy로 저장
sec_children = list(sec_elem)
ref_box    = copy.deepcopy(sec_children[23])  # □ 두 run 구조 (실제 인덱스로 교체)
ref_circle = copy.deepcopy(sec_children[24])  # ○
ref_dash   = copy.deepcopy(sec_children[25])  # ―
ref_note   = copy.deepcopy(sec_children[31])  # ※ (있는 섹션에서 가져옴)

# ★ 역순 처리 (Ⅳ → Ⅲ → Ⅱ → Ⅰ)
replace_section_body(sec_elem, sec4_start, sec4_end, ref_box, ref_circle, ref_dash, ref_note, sec4_content)
replace_section_body(sec_elem, sec3_start, sec3_end, ref_box, ref_circle, ref_dash, ref_note, sec3_content)
replace_section_body(sec_elem, sec2_start, sec2_end, ref_box, ref_circle, ref_dash, ref_note, sec2_content)
replace_section_body(sec_elem, sec1_start, sec1_end, ref_box, ref_circle, ref_dash, ref_note, sec1_content)
```

> **순서 처리가 불가피한 경우**: 각 호출 후 `delta = len(content) - (end - start)`를 계산하여
> 이후 섹션 인덱스에 누적 합산한다.

---

## 5단계: 단순 텍스트 교체 (제목·날짜·기관명 등)

> **★ 제목 작성 원칙**: 보고서 제목은 **15자 내외**로 간결하게 작성한다.
> 핵심 키워드 중심으로 압축하되, 20자를 초과하지 않도록 한다.
> (예: "2026년 AI교육 추진계획" → O / "2026년도 인공지능 디지털 교육 추진 및 운영 계획" → X)

### ★★★ 5-0. 교체 전 반드시 텍스트의 실제 위치(depth) 확인

**교체 필수 대상 (누락 금지):**

| 위치 | 자리표시 텍스트 예 | 비고 |
|------|-------------------|------|
| 표지 제목 | "보고서 양식(제목)" | 통상 표 내부 |
| 표지 날짜 | "2026. 1. 1." | 통상 직계 run |
| 표지 기관명 | "기관명" | 통상 직계 run |
| **본문 1p 상단 제목 박스** | **"제 목"** | **통상 표 내부 — 누락 빈발, 반드시 확인** |
| 섹션 헤더(Ⅰ~) | " 추진 배경" 등 | 표 내부 |
| 목차 항목 | "Ⅰ. 개요" 등 | 표 내부 |

> 2단계 구조 분석 출력에서 위 자리표시 텍스트가 나타나는 **모든 인덱스**를 교체 대상 목록으로 만들고,
> 하나라도 빠뜨리지 않았는지 교체 후 전체 스캔(5-3)으로 검증한다.

**표지 제목·섹션 헤더는 문단의 직계 run이 아니라 `tbl > tr > tc > subList > p` 내부에 들어 있는 양식이 흔하다.**
이 경우 직계 run만 수정하는 `set_run_text`를 쓰면 ① 표 안의 자리표시 텍스트("보고서 양식(제목)" 등)는 그대로 남고
② 새 텍스트가 표 바깥에 이중으로 삽입되는 치명적 오류가 발생한다.

### ★★★ 5-0-1. 표지 제목 문단에서 run 삭제 절대 금지 (붉은 테두리 소실 방지)

표지/1p 상단의 제목 문단(통상 sec_children[0])은 다음과 같은 복합 구조인 경우가 대부분이다:

```
p
 ├─ run: secPr(페이지 설정) + ctrl(colPr)   ← 삭제 시 페이지 레이아웃 파괴
 ├─ run: ctrl(pageNum)                      ← 삭제 시 쪽번호 소실
 └─ run: tbl(borderFillIDRef=N)             ← ★ 제목을 감싸는 "붉은 테두리 박스" 표
          └─ tr > tc > subList > p > run > t: "제목 자리표시"
```

**따라서 제목 문단에는 `set_run_text(..., remove_extra_runs=True)`를 절대 사용하지 않는다.**
run을 삭제하면 붉은 테두리 표(tbl) 자체가 통째로 사라져 제목 박스가 소실된다 (실제 발생한 치명 오류).

**제목 교체의 유일한 허용 방식**: `replace_text_anywhere`(targeted lineseg 방식)로 표 내부 `t` 노드의 텍스트만 교체한다.
run·tbl·secPr·ctrl 등 구조 요소는 어떤 경우에도 추가·삭제하지 않는다.

**run 삭제가 필요해 보이는 문단은 먼저 run 구성을 감사(audit)한다:**

```python
def audit_runs(p_elem):
    """각 run에 t 외의 구조 요소(secPr/ctrl/tbl 등)가 있는지 보고.
    구조 요소가 하나라도 있으면 그 run은 절대 삭제 금지."""
    for i, r in enumerate(c for c in p_elem if etree.QName(c.tag).localname == 'run'):
        kinds = sorted({etree.QName(c.tag).localname for c in r})
        protected = bool(set(kinds) - {'t'})
        print(f"run[{i}] children={kinds} {'★삭제금지' if protected else ''}")
```

교체 후 아래 검증을 반드시 실행한다 (5-3 스캔과 별도):

```python
# 제목 테두리 표 + run 구조 보존 검증 (필수)
p0 = list(sec_elem)[0]  # 제목 문단 인덱스는 2단계 출력 기준
tbls = [c for c in p0.iter() if etree.QName(c.tag).localname == 'tbl']
assert tbls, "제목 테두리 표(tbl)가 사라짐 — run 삭제 금지 규칙 위반"
runs_now = sum(1 for c in p0 if etree.QName(c.tag).localname == 'run')
assert runs_now == RUNS_ORIGINAL, f"제목 문단 run 수 변동({RUNS_ORIGINAL}→{runs_now}) — 구조 훼손"
# RUNS_ORIGINAL: 2단계 분석 시점에 기록해 둔 원본 run 수
```

**검증 실패 시 복구**: 수정본을 고치려 들지 말고, 원본 section0.xml에서 해당 문단을 통째로 가져와
`sec_elem.replace(손상된_p, 원본_p_deepcopy)` 후 텍스트 교체만 다시 수행한다.

교체 전 아래로 **해당 텍스트가 직계 run에 있는지, 표 내부에 있는지 반드시 확인**한다:

```python
def locate_text(p_elem, needle):
    """needle 텍스트가 직계 run에 있는지, tbl 내부에 있는지 판별"""
    for r in p_elem:
        if etree.QName(r.tag).localname != 'run':
            continue
        for c in r:
            local = etree.QName(c.tag).localname
            if local == 't' and c.text and needle in c.text:
                return 'direct'       # 직계 run → set_run_text 사용
            if local == 'tbl':
                for t in c.iter():
                    if etree.QName(t.tag).localname == 't' and t.text and needle in t.text:
                        return 'nested_tbl'   # 표 내부 → replace_text_anywhere 사용
    return None
```

### 5-1. 위치별 교체 함수

**(A) 직계 run에 있을 때** — 기존 방식:

```python
def set_run_text(p_elem, run_idx, new_text, remove_extra_runs=False):
    """p_elem의 run_idx번째 run에 텍스트 설정. linesegarray 삭제."""
    runs = [c for c in p_elem if etree.QName(c.tag).localname == 'run']
    if run_idx < len(runs):
        for t in runs[run_idx]:
            if etree.QName(t.tag).localname == 't':
                t.text = new_text
                break
    if remove_extra_runs:
        for r in runs[run_idx+1:]:
            p_elem.remove(r)
    remove_own_lineseg(p_elem)   # hwpx-core
```

**(B) 표 내부(subList/tc)에 있을 때** — 자리표시 텍스트를 기준으로 t 노드를 직접 찾아 교체:

> ★★★ **linesegarray는 "실제 텍스트를 수정한 최소 단위 hp:p의 직계"만 삭제**한다 (targeted 방식).
> p_elem 하위 전체를 재귀 삭제하면 안 된다 — 제목 표의 얇은 셀 등 **미수정 문단의 음수 spacing lineseg 캐시**
> (예: `spacing=-240`)까지 지워져 줄 높이가 재계산되면서 빨간 줄 양식이 깨지는 치명 오류가 실제 발생했다.

```python
def remove_own_lineseg(p):
    """해당 p의 '직계' linesegarray만 삭제 (하위 표 내부는 건드리지 않음)"""
    for c in list(p):
        if etree.QName(c.tag).localname == 'linesegarray':
            p.remove(c)

def nearest_p(elem):
    cur = elem.getparent()
    while cur is not None and etree.QName(cur.tag).localname != 'p':
        cur = cur.getparent()
    return cur

def replace_text_anywhere(p_elem, old_text, new_text):
    """p_elem 하위 전체(표 내부 포함)에서 old_text와 일치하는 t 노드만 교체.
    lineseg 캐시는 '그 t가 속한 최소 단위 p'의 직계만 삭제하고,
    미수정 문단(빈 셀·장식 셀 등)의 캐시는 반드시 보존한다."""
    replaced = 0
    for t in p_elem.iter():
        if etree.QName(t.tag).localname == 't' and t.text and old_text in t.text:
            t.text = t.text.replace(old_text, new_text)
            replaced += 1
            host = nearest_p(t)
            if host is not None:
                remove_own_lineseg(host)
    assert replaced > 0, f"'{old_text}' 를 찾지 못함 — 자리표시 텍스트를 2단계 출력에서 재확인할 것"
    return replaced
```

### 5-2. 사용 예 (인덱스는 2단계 출력으로 확인)

```python
# ① 위치 판별 후 ② 알맞은 함수 선택
loc = locate_text(sec_children[5], "보고서 양식(제목)")
if loc == 'nested_tbl':
    replace_text_anywhere(sec_children[5], "보고서 양식(제목)", "보고서 제목")
else:
    set_run_text(sec_children[5], 0, "보고서 제목", remove_extra_runs=True)

set_run_text(sec_children[11], 0, "2026. 7. 1.")   # 날짜: 통상 직계 run
set_run_text(sec_children[16], 0, "기관명")          # 기관명: 통상 직계 run
```

### 5-3. ★ 교체 후 자리표시 잔존 전체 스캔 (필수)

개별 문단 검증에 더해, **저장 직전 문서 전체를 스캔**하여 양식의 자리표시 텍스트가 하나라도 남아있으면 실패 처리한다:

```python
PLACEHOLDERS = ["보고서 양식(제목)", "제 목", "기관명", "헤드라인M 폰트",
                "휴면명조", "중고딕", "세부내용"]  # 양식에 따라 2단계 출력 기준으로 보완

leftover = []
for p in sec_elem.iter():
    if etree.QName(p.tag).localname == 't' and p.text:
        for ph in PLACEHOLDERS:
            if ph in p.text:
                leftover.append((ph, p.text[:50]))
assert not leftover, f"자리표시 텍스트 잔존: {leftover} — 교체 누락, 5-0 대상 목록 재확인"
```

또한 새로 넣은 제목이 이중 삽입되지 않았는지 확인한다:

```python
texts = [t.text for t in sec_children[5].iter()
         if etree.QName(t.tag).localname == 't' and t.text and t.text.strip()]
assert texts.count("보고서 제목") == 1, "제목이 없거나 중복 삽입됨"
```

> "세부내용"은 목차의 [붙 임]/[참 고] 항목에 쓰이는 자리표시다. 실제 붙임이 없으면 잔존을 허용하되,
> 그 외 자리표시는 잔존 시 반드시 교체 후 재패키징한다.

### 5-4. 목차(TOC) 교체 시 주의

목차 문단도 표 내부 구조인 경우가 많다. 항목별 교체 시 **치환 문자열이 서로 겹치지 않는지** 반드시 확인한다.
(예: '. 추진배경'과 '. 현황 및 문제점'을 각각 다른 제목으로 치환할 때, 앞선 치환 결과가 뒤 치환 패턴과 겹치면 중복 제목이 발생)
안전한 방식: 목차의 `t` 노드를 **순서대로 순회하며 번호(Ⅰ,Ⅱ,...) 기준으로 매핑**하여 교체하고,
본문 섹션 수보다 목차 항목이 많으면 초과 항목(번호+제목)의 텍스트를 비운다.
교체 후 목차 전체 텍스트를 출력해 중복·불일치가 없는지 검증한다.

---

## 6·7단계: XML 저장과 재패키징

`hwpx_tool.save(tree, 경로)`로 저장하고 `python hwpx_tool.py pack original/ 결과물.hwpx --order-from 원본.hwpx`로 묶는다 (hwpx-core 7절).

---

## 8단계: 검증 (무결성 + ★분량 검증)

### 8-1. 파일 무결성과 렌더링

`python hwpx_tool.py check 결과물.hwpx` 통과 후, 가능하면 `render_request.py`로 한글 렌더링을 확인한다 (hwpx-core 8절).
렌더링을 못 했으면 못 했다고 보고한다.

### 8-2. ★★★ 분량 검증 (미달 시 반드시 보강 후 재패키징)

0단계에서 확정한 목표 문단 수와 실제 생성 문단 수를 비교한다.
**목표 대비 85% 미만이면 결과물을 전달하지 말고 본문을 보강**한다.

```python
root = tree.getroot()
sec = next(e for e in root.iter() if etree.QName(e.tag).localname == 'sec')

body_count = 0
for p in sec:
    texts = ''.join(t.text or '' for t in p.iter()
                    if etree.QName(t.tag).localname == 't')
    s = texts.strip()
    # 본문 문단만 카운트 (□/○/ㅇ/―/-/※/* 로 시작하는 실질 내용 문단)
    if s and s[0] in '□○ㅇ―-※*':
        body_count += 1

TARGET = 55           # ← 0단계에서 확정한 목표 문단 수 입력
ratio = body_count / TARGET
print(f"본문 문단: {body_count} / 목표: {TARGET} ({ratio:.0%})")
assert ratio >= 0.85, (
    f"분량 미달({ratio:.0%}) — 0-5 배분표로 돌아가 ―/※ 세부 문단을 추가하고 "
    f"재작성할 것. 미달 상태로 사용자에게 전달 금지")
```

보강 방법은 0-5의 "분량을 늘리는 올바른 방법"을 따른다 (소제목 세분화, ― 세부근거 확장, ※ 추가).
글자 수 늘리기용 중복 서술이나 미사여구 반복은 금지.

---

## 9단계: 공문 작성 원칙

- **문체는 0-2에서 확정한 값을 따른다** (개조식: 명사형 종결 / 서술식: 합니다·습니다체)
- 문체 미확정 상태로 이 단계에 도달하는 것 자체가 오류 — 0단계로 돌아가 질문할 것
- 두괄식 서술 (결론 → 배경 → 세부내용)
- 본문 순서: 목적/배경 → 세부 내용 → 요청/협조 사항 → 붙임
- 관용 표현: "~와 관련하여", "아래와 같이", "~하여 주시기 바랍니다"

---

## ★ 작업 체크리스트

| 순서 | 확인 항목 |
|------|-----------|
| ⓪ | **3단계 사전 질문 완료** — ①분량 ②문체(개조식/서술식) ③내용 중점을 순서대로 질문·확정, 확정 선언 후 문단 수 환산·배분표 작성 |
| ① | 2단계 구조 분석 실행 → `sec` 직계 자식 인덱스 맵 출력 확인 |
| ② | 참조 단락(`ref_box`, `ref_circle`, `ref_dash`, `ref_note`)을 수정 전에 `deepcopy`로 저장 |
| ③ | content_list 길이가 0-3 배분표와 일치하는지 확인 후 섹션 본문 교체는 **역순(마지막 섹션부터)** 처리 |
| ④ | 텍스트를 수정한 모든 `<hp:p>`에서 `linesegarray` 삭제 확인 |
| ④-1 | **제목·헤더 교체 전 `locate_text`로 위치 판별** — 표 내부(nested_tbl)면 `replace_text_anywhere` 사용 |
| ④-1a | **제목 문단에서 run 삭제 절대 금지(5-0-1)** — 붉은 테두리 표(tbl) 보존 assert 통과 확인 |
| ④-2 | **5-0 교체 대상표의 전 항목 처리** — 특히 본문 1p 상단 "제 목" 박스 누락 여부 확인 |
| ④-3 | **저장 직전 자리표시 잔존 전체 스캔(5-3) 통과** — 잔존·중복 삽입 시 재작업 |
| ④-4 | 목차 교체 시 치환 패턴 겹침 확인(5-4) — 번호 기준 순차 매핑, 초과 항목 비우기, 교체 후 전체 출력 검증 |
| ⑤ | `hwpx_tool.py check` 통과 (mimetype 무압축 첫 항목 포함) |
| ⑥ | 렌더링 확인 또는 미확인 사실 보고 (hwpx-core 8절) |
| ⑦ | **분량 검증(8-2) 통과** — 목표 문단 수 대비 85% 이상, 미달 시 보강 후 재패키징 |
