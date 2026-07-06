<!-- Generated: 2026-07-06 | Skills: 10 + learned/, Project agents: 1 | Token estimate: ~430 -->
# Claude Code Skills & Agents

## Project Skills (.claude/skills/)

| Skill | Purpose |
|-------|---------|
| `writing-team` | Orchestrator (PM): mission triage → team assembly → quality gate |
| `zenn-practical-writing` | Default voice for all Zenn/Dev.to articles (実用軸, ですます, no tech/idea split) |
| `zenn-idea-voice` | Opt-in personality flavor (毒humor / 刃牙 references) |
| `zenn-format` | Zenn frontmatter / markdown / emoji / topics — canonical reference |
| `ideation` | Theme exploration & ideation |
| `publish-article` | Pre-publish checklist + cross-post procedure |
| `schedule-publish` | Discoverability scoring + schedule.json date assignment |
| `seo-optimizer` | Title / tag / emoji optimization (Content Integrity: no intro rewrites) |
| `series-checker` | Cross-article series consistency |
| `quality-gate` | Unified quality standard across all paths |
| `learned/` | Auto-extracted patterns (e.g. `concept-before-use-rule`) |

> `zenn-writer` (voice router), `chatlog-to-article`, `content-research-writer` were retired — see ADR-0003 and its 2026-07-06 addendum.

## Project Agents (.claude/agents/)

| Agent | Purpose |
|-------|---------|
| `devto-translator` | JP→EN translation + Dev.to publishing (one-shot launchd scheduling) |

> `editor`, `essay-reviewer`, `fact-checker` were **promoted to global** (`~/.claude/agents/`) on 2026-04-18. `zenn-drafter` was retired (ADR-0003 — writing is done by the orchestrator itself). Shared writing standards live in the global `writing-ecosystem` skill.

## Workflow

```
Draft (orchestrator writes directly, per zenn-practical-writing)
  → editor + fact-checker + codex-review (parallel review)
  → human approval → published_at → git push (Zenn native schedule)
  → devto-translator (EN) → devto_crosspost.py schedule (one-shot launchd)
```
