<!-- Generated: 2026-03-06 | Skills: 10, Agents: 1 | Token estimate: ~400 -->
# Claude Code Skills & Agents

## Project Skills (.claude/skills/)

| Skill | Purpose |
|-------|---------|
| `zenn-writer` | Article writing guide (voice, structure, Zenn format) |
| `publish-article` | Pre-publish checklist + cross-post procedure |
| `schedule-publish` | Schedule articles in schedule.json |
| `translate-article` | JP→EN article translation |
| `catchify` | Transform report-style openings to incident-first narrative |
| `content-research-writer` | Research-driven writing with Zenn context |
| `chatlog-to-article` | Convert chat logs to articles |
| `seo-optimizer` | SEO optimization for articles |
| `zenn-format` | Zenn markdown format reference |
| `learned/` | Auto-extracted patterns (concept-before-use-rule) |

## Project Agent (.claude/agents/)

| Agent | Purpose |
|-------|---------|
| `editor` | Rigorous 4-tier article review (ACCEPT/MINOR/REVISE/REJECT) |

## Workflow

```
Draft → catchify → editor review → human review → lint → publish
```
