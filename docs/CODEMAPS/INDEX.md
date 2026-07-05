<!-- Generated: 2026-05-24 | Codemaps: 4 | Token estimate: ~250 -->
# CODEMAPS Index

Token-lean architecture documentation for `zenn-content` — a bilingual (JP/EN)
Zenn content repository with manual Dev.to cross-posting. Start here, then open
the role-specific map you need.

| Codemap | Role | What it answers |
|---------|------|-----------------|
| [architecture.md](architecture.md) | Project shape | Directory layout, data flow, agents, toolchain |
| [scripts.md](scripts.md) | Publishing pipeline | Entry points, key functions, schedule.json schema, tests |
| [dependencies.md](dependencies.md) | Dependencies | Node lint stack, Python publishing deps, external services |
| [skills.md](skills.md) | Claude Code config | Project skills (11 + learned/), project agents (2), workflow |

## Quick facts

- **Content**: 65 JP articles in `articles/` (48 published), 57 EN in `articles-en/` (35 published)
- **Substack mirror**: `substack/` (out of Zenn convention scope)
- **JP publishing**: Zenn native `published_at` scheduling (no script)
- **EN publishing**: Dev.to cross-post via `devto_crosspost.py` — `schedule <slug> --at "<datetime>"` arms a per-article one-shot launchd job that fires at that datetime, posts, and self-removes — GitHub Actions cron retired 2026-05
- **CI**: `.github/workflows/validate.yml` only (Zenn frontmatter check)

## Related

- [scripts.md](scripts.md) — publishing pipeline & launchd automation
- [../../CLAUDE.md](../../CLAUDE.md) — writing conventions, frontmatter rules (Context role)
- [../adr/](../adr/) — design decision records (ADR)
- [../../llms.txt](../../llms.txt) / [../../llms-full.txt](../../llms-full.txt) — AI-facing navigation
