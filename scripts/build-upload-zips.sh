#!/usr/bin/env bash
# 스킬을 claude.ai 업로드용 zip으로 묶는다.
#   build-upload-zips.sh            # 마지막 커밋에서 바뀐 스킬만
#   build-upload-zips.sh --all      # 전체 스킬
#   build-upload-zips.sh --range A B # A..B 사이에 바뀐 스킬 (pull 후 사용)
#   build-upload-zips.sh <이름>...   # 지정한 스킬
# 출력: $SKILL_ZIP_DIR (기본 ~/shared/exchange/skills-upload)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${SKILL_ZIP_DIR:-$HOME/shared/exchange/skills-upload}"
cd "$REPO"

if [ "${1:-}" = "--all" ]; then
  names=$(ls skills)
elif [ "${1:-}" = "--range" ]; then
  names=$(git diff --name-only "$2" "$3" -- skills/ | awk -F/ '{print $2}' | sort -u)
elif [ $# -gt 0 ]; then
  names="$*"
else
  names=$(git diff-tree --no-commit-id --name-only -r HEAD -- skills/ 2>/dev/null \
          | awk -F/ '{print $2}' | sort -u)
fi
[ -z "$names" ] && exit 0

mkdir -p "$OUT"
built=()
for n in $names; do
  [ -f "skills/$n/SKILL.md" ] || continue   # 삭제된 스킬은 건너뜀
  rm -f "$OUT/$n.zip"
  (cd skills && zip -q -r "$OUT/$n.zip" "$n" -x '*/__pycache__/*' '*.pyc' '*/.DS_Store')
  built+=("$n")
done
[ ${#built[@]} -eq 0 ] && exit 0

{
  echo "갱신: $(date '+%Y-%m-%d %H:%M')  커밋: $(git log -1 --format='%h %s')"
  echo "claude.ai → Customize → Skills 에서 아래 zip을 다시 올리면 됩니다 (같은 이름 스킬은 교체)."
  for n in "${built[@]}"; do echo "  - $n.zip"; done
} > "$OUT/업로드할것.txt"
echo "[skills] 업로드용 zip 생성: ${built[*]} → $OUT"
