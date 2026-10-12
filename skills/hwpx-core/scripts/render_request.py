#!/usr/bin/env python3
"""노트북 한글 렌더 도우미에 hwpx를 보내고 PDF 결과를 기다린다.

  render_request.py <file.hwpx> [--root ~/shared] [--timeout 120]

동작: <root>/papers/_render/requests/ 에 복사 → results/<이름>.pdf 또는 .error.txt 대기.
도우미(Windows 노트북의 hwp_render_watcher.py)가 꺼져 있으면 시간 초과로 끝난다.
그 경우 사용자에게 한글에서 직접 열어 확인해 달라고 요청한다.
종료코드: 0=PDF 생성, 2=도우미 오류, 3=시간 초과
"""
import argparse
import os
import shutil
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('hwpx')
    ap.add_argument('--root', default=os.path.expanduser('~/shared'))
    ap.add_argument('--timeout', type=int, default=120)
    a = ap.parse_args()
    req = os.path.join(a.root, 'papers', '_render', 'requests')
    res = os.path.join(a.root, 'papers', '_render', 'results')
    os.makedirs(req, exist_ok=True)
    os.makedirs(res, exist_ok=True)
    stem = os.path.splitext(os.path.basename(a.hwpx))[0]
    pdf, err = os.path.join(res, stem + '.pdf'), os.path.join(res, stem + '.error.txt')
    for f in (pdf, err):
        if os.path.exists(f):
            os.remove(f)
    shutil.copy(a.hwpx, os.path.join(req, os.path.basename(a.hwpx)))
    end = time.time() + a.timeout
    while time.time() < end:
        if os.path.exists(pdf):
            print(pdf)
            return 0
        if os.path.exists(err):
            print(open(err, encoding='utf-8', errors='replace').read())
            return 2
        time.sleep(3)
    print(f'시간 초과({a.timeout}s): 렌더 도우미가 꺼져 있을 수 있음')
    return 3


if __name__ == '__main__':
    sys.exit(main())
