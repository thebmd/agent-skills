---
name: example-skill
description: 예시 스킬. 사용자가 "예시 스킬 테스트"라고 하면 사용한다. 실제 스킬로 교체할 것.
---

# Example skill

이 폴더를 복사해서 실제 스킬을 만든다.

- SKILL.md 의 `name` 은 폴더 이름과 같아야 한다.
- 스크립트는 `scripts/` 에 두고, 본문에서 `scripts/xxx.py` 처럼 상대경로로 언급한다.
- frontmatter 는 name, description, license, compatibility, metadata, allowed-tools 만 사용한다.
  (Claude Code 전용 필드를 넣으면 claude.ai 업로드와 다른 도구에서 실패할 수 있음)
