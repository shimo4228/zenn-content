<!-- Generated: 2026-07-05 | Skills: 11 + learned/, Project agents: 1 | Token estimate: ~430 -->
# Claude Code Skills & Agents

## Project Skills (.claude/skills/)

| Skill | Purpose |
|-------|---------|
| `writing-team` | Orchestrator (PM): mission triage → team assembly → quality gate |
| `zenn-writer` | Article writing core (voice, structure, Zenn format, 刃牙 references) |
| `ideation` | Theme exploration & ideation |
| `chatlog-to-article` | Convert chat logs to articles |
| `content-research-writer` | Research-driven writing with Zenn context |
| `publish-article` | Pre-publish checklist + cross-post procedure |
| `schedule-publish` | Discoverability scoring + schedule.json date assignment |
| `seo-optimizer` | Title / tag / emoji optimization (Content Integrity: no intro rewrites) |
| `series-checker` | Cross-article series consistency |
| `quality-gate` | Unified quality standard across all paths |
| `zenn-format` | Zenn markdown format reference |
| `learned/` | Auto-extracted patterns (e.g. `concept-before-use-rule`) |

## Project Agents (.claude/agents/)

| Agent | Purpose |
|-------|---------|
| `zenn-drafter` | Article writer (analyze → write → self-review) |
| `devto-translator` | JP→EN translation + Dev.to publishing |

> `editor`, `essay-reviewer`, `fact-checker` were **promoted to global** (`~/.claude/agents/`) on 2026-04-18 and are no longer project agents. Shared writing standards live in the global `writing-ecosystem` skill.

## Workflow

```
Draft → writing-team (orchestrate) → editor / essay-reviewer + fact-checker (parallel review)
      → human approval → published_at → git push (Zenn native schedule)
      → devto-translator (EN) → manual Dev.to cross-post
```
