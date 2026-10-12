#!/usr/bin/env python3
"""hwpx 파일 공통 조작 도구 (라이브러리 + CLI).

CLI:
  hwpx_tool.py unpack  <file.hwpx> <dir>
  hwpx_tool.py pack    <dir> <out.hwpx> [--order-from <원본.hwpx>]
  hwpx_tool.py dump    <section.xml>            # 문단·표 구조 (문단모양 ID 포함)
  hwpx_tool.py text    <file.hwpx|section.xml>  # 본문 텍스트 (lineBreak/tab 반영)
  hwpx_tool.py diff    <a.hwpx> <b.hwpx>        # 두 파일 본문 텍스트 비교
  hwpx_tool.py parapr  <header.xml> [id ...]    # 문단모양 정렬·여백·내어쓰기 값
  hwpx_tool.py check   <file.hwpx>              # 패키징·XML 무결성 검사

라이브러리 사용: sys.path에 이 폴더를 넣고 `import hwpx_tool as hx`.
필요: lxml
"""
import copy
import difflib
import os
import sys
import zipfile

from lxml import etree

HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'
HH = '{http://www.hancom.co.kr/hwpml/2011/head}'
HC = '{http://www.hancom.co.kr/hwpml/2011/core}'
NS = {'hp': HP[1:-1], 'hh': HH[1:-1], 'hc': HC[1:-1]}


# ---------------------------------------------------------------- 패키징
def unpack(hwpx, out_dir):
    with zipfile.ZipFile(hwpx) as z:
        z.extractall(out_dir)


def pack(src_dir, out_path, order_from=None):
    """mimetype을 무압축으로 맨 앞에, 디렉터리 항목 없이 묶는다.
    order_from이 있으면 그 파일의 항목 순서를 따른다 (한글 저장본 순서 유지)."""
    files = []
    for dp, _, fns in os.walk(src_dir):
        for fn in fns:
            files.append(os.path.relpath(os.path.join(dp, fn), src_dir).replace(os.sep, '/'))
    order = []
    if order_from:
        with zipfile.ZipFile(order_from) as z:
            order = [n for n in z.namelist() if not n.endswith('/')]
    rest = sorted(f for f in files if f not in order)
    seq = ['mimetype'] + [f for f in order + rest if f != 'mimetype' and f in files]
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w') as z:
        for f in seq:
            ct = zipfile.ZIP_STORED if f in ('mimetype', 'version.xml') else zipfile.ZIP_DEFLATED
            z.write(os.path.join(src_dir, f), f, compress_type=ct)


def check(hwpx):
    """패키징 규칙과 XML 파싱을 검사하고 문제 목록을 반환한다."""
    probs = []
    with zipfile.ZipFile(hwpx) as z:
        infos = z.infolist()
        if z.testzip() is not None:
            probs.append('ZIP CRC 오류')
        if not infos or infos[0].filename != 'mimetype':
            probs.append('mimetype이 첫 항목이 아님')
        elif infos[0].compress_type != zipfile.ZIP_STORED:
            probs.append('mimetype이 압축되어 있음')
        if any(i.filename.endswith('/') for i in infos):
            probs.append('디렉터리 항목 포함 (권장하지 않음)')
        for n in z.namelist():
            if n.endswith('.xml') or n.endswith('.hpf'):
                try:
                    etree.fromstring(z.read(n))
                except etree.XMLSyntaxError as e:
                    probs.append(f'{n}: XML 오류 {e}')
    return probs


# ---------------------------------------------------------------- 읽기
def load(path):
    return etree.parse(path)


def save(tree, path):
    d = tree.docinfo
    tree.write(path, xml_declaration=True, encoding=d.encoding or 'UTF-8',
               standalone=d.standalone if d.standalone is not None else True)


def t_text(t):
    """hp:t 하나의 텍스트. lineBreak(Shift+Enter)=\\n, tab=\\t, 공백류 제어문자 반영."""
    s = t.text or ''
    for c in t:
        name = etree.QName(c).localname
        if name == 'lineBreak':
            s += '\n'
        elif name == 'tab':
            s += '\t'
        elif name in ('fwSpace', 'nbSpace'):
            s += ' '
        s += c.tail or ''
    return s


def p_text(p, include_nested=False):
    """문단 텍스트. 기본은 표 안 문단을 제외한 그 문단 자신의 글자만."""
    out = []
    for t in p.iter(HP + 't'):
        if not include_nested and nearest_p(t) is not p:
            continue
        out.append(t_text(t))
    return ''.join(out)


def nearest_p(el):
    cur = el.getparent()
    while cur is not None and cur.tag != HP + 'p':
        cur = cur.getparent()
    return cur


def body_paras(root):
    """sec 직계 문단 목록."""
    return root.findall('hp:p', NS)


def iter_text_lines(root):
    """문서 순서대로 (경로표시, 텍스트) — 표 셀은 [r행 c열]로 표시."""
    for i, p in enumerate(body_paras(root)):
        own = p_text(p)
        yield (f'p{i}', own)
        for tbl in p.iter(HP + 'tbl'):
            if nearest_p(tbl) is not p:
                continue  # 중첩 표는 바깥 셀에서 처리
            for tc in tbl.iter(HP + 'tc'):
                a = tc.find('hp:cellAddr', NS)
                for q in tc.find('hp:subList', NS).findall('hp:p', NS):
                    yield (f'p{i}[r{a.get("rowAddr")} c{a.get("colAddr")}]', p_text(q))


def dump(section_path):
    root = load(section_path).getroot()
    for i, p in enumerate(body_paras(root)):
        runs = [r.get('charPrIDRef') for r in p.findall('hp:run', NS)]
        has_tbl = any(nearest_p(t) is p for t in p.iter(HP + 'tbl'))
        print(f'p{i} paraPr={p.get("paraPrIDRef")} runs={runs}{" TBL" if has_tbl else ""} '
              f'{p_text(p)[:70]!r}')
        for tbl in p.iter(HP + 'tbl'):
            if nearest_p(tbl) is not p:
                continue
            print(f'   tbl rows={tbl.get("rowCnt")} cols={tbl.get("colCnt")} '
                  f'size={tbl.find("hp:sz", NS).get("width")}x{tbl.find("hp:sz", NS).get("height")}')
            for tc in tbl.iter(HP + 'tc'):
                a, sp, sz = (tc.find('hp:cellAddr', NS), tc.find('hp:cellSpan', NS),
                             tc.find('hp:cellSz', NS))
                ps = tc.find('hp:subList', NS).findall('hp:p', NS)
                print(f'     r{a.get("rowAddr")} c{a.get("colAddr")} span={sp.get("colSpan")}x'
                      f'{sp.get("rowSpan")} w={sz.get("width")} '
                      + str([(q.get('paraPrIDRef'), p_text(q)[:28]) for q in ps][:6]))


# ---------------------------------------------------------------- 쓰기
def remove_own_lineseg(p):
    """그 문단 직계의 줄 배치 캐시만 삭제 (하위 표 안 문단은 건드리지 않음)."""
    for c in p.findall('hp:linesegarray', NS):
        p.remove(c)


def audit_runs(p):
    """run별 자식 종류. t 이외 요소(secPr/ctrl/tbl/pic 등)가 있는 run은 삭제 금지."""
    res = []
    for i, r in enumerate(p.findall('hp:run', NS)):
        kinds = sorted({etree.QName(c).localname for c in r})
        res.append((i, kinds, bool(set(kinds) - {'t'})))
    return res


def set_text(p, text):
    """문단 텍스트 교체. '\\n'은 lineBreak로 넣는다.
    첫 텍스트 run에 넣고, 나머지 텍스트 run의 t는 비운다.
    구조 요소(표·컨트롤)가 있는 run은 삭제하지 않는다."""
    runs = [r for r in p.findall('hp:run', NS) if r.find('hp:t', NS) is not None]
    if not runs:
        r = p.find('hp:run', NS)
        if r is None:
            r = etree.SubElement(p, HP + 'run', charPrIDRef='0')
            p.remove(r)
            ls = p.find('hp:linesegarray', NS)
            (ls.addprevious(r) if ls is not None else p.append(r))
        runs = [r]
        etree.SubElement(r, HP + 't')
    first = runs[0]
    ts = first.findall('hp:t', NS)
    _fill_t(ts[0], text)
    for t in ts[1:]:
        first.remove(t)
    for r in runs[1:]:
        for t in r.findall('hp:t', NS):
            r.remove(t)
        if len(r) == 0:
            p.remove(r)
    remove_own_lineseg(p)
    return p


def _fill_t(t, text):
    for c in list(t):
        t.remove(c)
    parts = text.split('\n')
    t.text = parts[0]
    for part in parts[1:]:
        br = etree.SubElement(t, HP + 'lineBreak')
        br.tail = part


def clone_para(ref, text, para_pr=None):
    """같은 파일 안의 참조 문단을 복제해 텍스트만 바꾼다 (서식 ID가 그 파일 기준으로 유효)."""
    q = copy.deepcopy(ref)
    q.set('id', '0')
    if para_pr is not None:
        q.set('paraPrIDRef', str(para_pr))
    return set_text(q, text)


def insert_after(ref, items):
    for it in items:
        ref.addnext(it)
        ref = it
    return ref


# ---------------------------------------------------------------- 표
def table_cells(tbl):
    return {(int(tc.find('hp:cellAddr', NS).get('rowAddr')),
             int(tc.find('hp:cellAddr', NS).get('colAddr'))): tc for tc in tbl.iter(HP + 'tc')
            if tc.getparent().getparent() is tbl}


def set_cell(tc, lines, tmpl=None, para_pr=None):
    """셀 내용을 lines(문단 목록)로 교체. 각 줄 안의 '\\n'은 lineBreak.
    tmpl: 복제할 문단 (기본: 셀의 첫 문단)."""
    sub = tc.find('hp:subList', NS)
    old = sub.findall('hp:p', NS)
    t = tmpl if tmpl is not None else old[0]
    new = [clone_para(t, s, para_pr) for s in lines]
    for p in old:
        sub.remove(p)
    for p in new:
        sub.append(p)
    tc.set('dirty', '1')


def add_rows(tbl, n, template_row_index=-1):
    """병합 없는 표에서 template 행을 복제해 끝에 n행 추가. rowAddr·rowCnt·표 높이 갱신."""
    rows = tbl.findall('hp:tr', NS)
    tmpl = rows[template_row_index]
    last = rows[-1]
    h = int(tmpl.find('hp:tc/hp:cellSz', NS).get('height'))
    for k in range(n):
        nr = copy.deepcopy(tmpl)
        for tc in nr.findall('hp:tc', NS):
            tc.find('hp:cellAddr', NS).set('rowAddr', str(len(rows) + k))
            for p in tc.iter(HP + 'p'):
                remove_own_lineseg(p)
        last.addnext(nr)
        last = nr
    tbl.set('rowCnt', str(len(rows) + n))
    sz = tbl.find('hp:sz', NS)
    sz.set('height', str(int(sz.get('height')) + h * n))


def set_col_widths(tbl, widths):
    """병합 없는 표의 열 너비(HWPUNIT) 지정, 표 전체 너비도 갱신."""
    for (r, c), tc in table_cells(tbl).items():
        tc.find('hp:cellSz', NS).set('width', str(widths[c]))
    tbl.find('hp:sz', NS).set('width', str(sum(widths)))


# ---------------------------------------------------------------- 서식(header)
def para_pr_info(header_root, ids=None):
    out = {}
    for p in header_root.iter(HH + 'paraPr'):
        if ids and p.get('id') not in ids:
            continue
        m = p.find('.//' + HH + 'margin')
        vals = {etree.QName(c).localname: int(c.get('value')) for c in m} if m is not None else {}
        out[p.get('id')] = (p.find(HH + 'align').get('horizontal'), vals)
    return out


def add_para_pr(header_root, base_id, intent=None, left=None):
    """base_id 문단모양을 복제해 새 ID로 추가하고 그 ID를 반환.
    intent < 0 이면 내어쓰기 (한글 저장 방식: left=0, intent 음수)."""
    props = header_root.find('.//' + HH + 'paraProperties')
    base = [p for p in props if p.get('id') == str(base_id)][0]
    new_id = str(max(int(p.get('id')) for p in props) + 1)
    q = copy.deepcopy(base)
    q.set('id', new_id)
    for m in q.iter(HH + 'margin'):  # switch/case 와 default 양쪽 모두
        if intent is not None:
            m.find(HC + 'intent').set('value', str(intent))
        if left is not None:
            m.find(HC + 'left').set('value', str(left))
    props.append(q)
    props.set('itemCnt', str(len(props)))
    return new_id


# ---------------------------------------------------------------- 비교
def doc_lines(path):
    """hwpx 또는 section xml에서 비교용 텍스트 줄 목록."""
    roots = []
    if path.endswith('.hwpx'):
        with zipfile.ZipFile(path) as z:
            for n in sorted(n for n in z.namelist() if n.startswith('Contents/section')):
                roots.append((n, etree.fromstring(z.read(n))))
    else:
        roots.append((os.path.basename(path), load(path).getroot()))
    lines = []
    for name, r in roots:
        for loc, txt in iter_text_lines(r):
            if txt.strip():
                lines.append(f'{name.split("/")[-1]}:{loc}: {txt}'.replace('\n', '⏎'))
    return lines


def diff(a, b):
    strip = lambda ls: [l.split(': ', 1)[1] for l in ls]
    la, lb = doc_lines(a), doc_lines(b)
    for l in difflib.unified_diff(strip(la), strip(lb), a, b, lineterm='', n=1):
        print(l)


# ---------------------------------------------------------------- CLI
def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd, args = argv[1], argv[2:]
    if cmd == 'unpack':
        unpack(*args)
    elif cmd == 'pack':
        order = None
        if '--order-from' in args:
            i = args.index('--order-from')
            order = args[i + 1]
            args = args[:i] + args[i + 2:]
        pack(args[0], args[1], order)
        probs = check(args[1])
        print('pack ok' if not probs else '\n'.join(probs))
    elif cmd == 'dump':
        dump(args[0])
    elif cmd == 'text':
        for l in doc_lines(args[0]):
            print(l)
    elif cmd == 'diff':
        diff(args[0], args[1])
    elif cmd == 'parapr':
        info = para_pr_info(load(args[0]).getroot(), set(args[1:]) or None)
        for k, (al, v) in sorted(info.items(), key=lambda x: int(x[0])):
            print(k, al, v)
    elif cmd == 'check':
        probs = check(args[0])
        print('ok' if not probs else '\n'.join(probs))
        return 1 if probs else 0
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
