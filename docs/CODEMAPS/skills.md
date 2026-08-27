<!-- Generated: 2026-08-23 | Project skills: 4 | Project agents: 1 -->
# Writing Harness Skills & Agents

## Global writing layer (`~/.claude`)

| Asset | Responsibility |
|---|---|
| `writing-ecosystem` | Sole human-prose orchestrator: theme → one-thesis brief → draft → title → review → acceptance |
| `session-theme-mining` | Finds 0–3 evidence-backed questions from past sessions; author selects |
| `collect-context` | Builds the evidence dossier; does not choose what enters the draft |
| `headline-craft` / `title-reviewer` | Generate title candidates / review them against the frozen draft (findings only) |
| `quality-gate` | Aggregates the project channel contract into PASS / FAIL / BLOCKED |
| `theme-reviewer` | Pre-write findings and deepening questions; no verdict |
| `editor` / `essay-reviewer` | Practical-channel / essay-channel review |
| `prose-clarity-reviewer` | First-contact clarity, title-axis, and insider-context review |
| `fact-checker` | Web verification of factual claims |

## Project-local layer

| Asset | Responsibility |
|---|---|
| `publishing-channels.md` | Path, audience, register, panel, validator, title constraint, publish handoff |
| `zenn-format` | Zenn frontmatter, topics / emoji, Zenn Markdown |
| `publish-article` | Zenn / Dev.to preview, scheduling, index, and push boundary |
| `substack-publishing` | note / Substack HTML paste, publication, and corpus mirror |
| `article-stocktake` | Zenn / Dev.to reception measurement; reports and stops |
| `devto-translator` | Dev.to-specific translation conversion; stops before review, gate, and publishing |

## Data flow

```text
session-theme-mining (optional) → author selection → theme-reviewer
  → collect-context (optional evidence dossier)
  → writing-ecosystem editorial brief: one thesis + causal spine + selected evidence + cut list
  → orchestrator draft → headline-craft → title-reviewer
  → channel editor + prose-clarity-reviewer + fact-checker + codex-review
  → quality-gate reads publishing-channels.md → author GO
  → project-local publisher

Post-publication:
  metrics_snapshot.py → article-stocktake → author-facing observation report (stop)
```

A structural review fix invalidates the brief and title verdict. Copy edits do not. ADRs, memory, and raw
session history are not writing-time rules.
