# agent-skills

Agent Skills 오픈 표준(agentskills.io) 형식의 개인 스킬 저장소.
스킬 본체는 `skills/<이름>/SKILL.md` 하나뿐이고, `.claude-plugin/` 은 Claude 쪽에서
마켓플레이스로 인식하게 하는 메타 파일이다. 다른 도구는 `.claude-plugin/` 을 무시한다.

## 구조

```
skills/<스킬이름>/SKILL.md     # 스킬 하나당 폴더 하나 (표준)
skills/<스킬이름>/scripts/     # 실행 코드 (선택)
.claude-plugin/marketplace.json  # Claude 전용 메타
.claude-plugin/plugin.json       # Claude 전용 메타
```

## 스킬 추가
`skills/` 아래에 폴더 + SKILL.md. 폴더 이름 = name. 커밋/푸시하면 끝.

## 등록

### Claude Code
```
/plugin marketplace add <github-id>/agent-skills
/plugin install my-skills@jeongmok-skills
```
갱신: `/plugin marketplace update jeongmok-skills` → `/plugin update my-skills@jeongmok-skills`

### Claude 데스크톱 / Cowork
Customize → Plugins → Add → Add marketplace → `<github-id>/agent-skills` → Sync.
(Settings → Capabilities 에서 코드 실행·파일 생성이 켜져 있어야 함)

### claude.ai 일반 채팅
플러그인 미지원. 필요한 스킬 폴더만 zip 으로 묶어 Customize → Skills 에 업로드.

### Codex / Cursor / Copilot 등 (Agent Skills 표준 지원 도구)
```
npx skills add <github-id>/agent-skills
```
스킬을 골라 각 도구의 skills 디렉토리에 설치·동기화한다.

### ChatGPT (Business/Enterprise)
Plugins → Skills 탭에서 스킬 폴더를 업로드. 같은 SKILL.md 그대로 사용.

## 검증
```
claude plugin validate .
```
