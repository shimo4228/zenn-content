Language: English | [日本語](README.ja.md)

# zenn-content

Japanese and English writing by Tatsuya Shimomoto (shimo4228) on coding agents, for engineers who build and run them: how they remember, how they fail, how to review them without drowning in review, and how to keep them accountable. Everything here comes from real development sessions, and every article's Markdown source is in this repository.

If you arrived from one article, pick a path below for the next useful piece — or browse the [complete index](docs/PUBLICATIONS.md).

## Choose your next path

<!-- reading-paths:start -->

### Make coding agents remember

Where an agent's knowledge should live, and when structured memory beats memory RAG.

- [Where to Put a Coding Agent's Knowledge — and How to Make It Stick](https://dev.to/shimo4228/where-to-put-a-coding-agents-knowledge-and-how-to-make-it-stick-161g)
- [Claude Code's Memory Has No Vectors — Try ADRs Before Memory RAG](https://dev.to/shimo4228/claude-codes-memory-has-no-vectors-try-adrs-before-memory-rag-4kik)

### Review agents without creating endless work

LLM-as-judge design, cross-model review, and the failure mode where every review spawns another task.

- [LLM-as-Judge Shouldn't Aggregate Scores: Binary Checks as Evidence, One Holistic Verdict](https://dev.to/shimo4228/llm-as-judge-shouldnt-aggregate-scores-binary-checks-as-evidence-one-holistic-verdict-822)
- [I Built a Skill for Easy Codex Reviews from Claude Code](https://dev.to/shimo4228/i-built-a-skill-for-easy-codex-reviews-from-claude-code-4h89)
- [AI Review Kept Creating Work: Why I Deleted 4,541 Lines](https://dev.to/shimo4228/ai-review-kept-creating-work-why-i-deleted-4541-lines-22ec)

### Make autonomous behavior reconstructable

Accountability architecture and practical observability for agents that act on their own.

- [A Sign on a Climbable Wall: Why AI Agents Need Accountability, Not Just Guardrails](articles-en/ai-agent-accountability-wall-en.md) (English source in this repo — not yet on Dev.to)
- [Why Did My Agent Decide That? 3 Observability Patterns](https://dev.to/shimo4228/why-did-my-agent-decide-that-3-observability-patterns-ami)

<!-- reading-paths:end -->

## Browse everything

- **[Publications index](docs/PUBLICATIONS.md)** — every article, idea essay, and paper, newest first, with Japanese and English links (generated from the sources in this repo and checked by CI, so it stays in step with the profiles below)
- Japanese articles: [Zenn](https://zenn.dev/shimo4228) · English editions: [Dev.to](https://dev.to/shimo4228)
- Idea essays: Japanese on note (a Japanese blogging platform) · English on [Substack](https://shimo4228.substack.com) — per-essay links are in the index

## What this repository contains

| Directory | Contents |
|---|---|
| `articles/` | Japanese originals for Zenn (canonical) |
| `articles-en/` | English editions for Dev.to |
| `note/` · `substack/` | Idea essays — Japanese canonical on note, English edition on Substack |
| `docs/PUBLICATIONS.md` | Generated index of everything above, plus deposited papers |
| `scripts/` | Dev.to cross-poster, index generator, reception-metrics snapshot |
| `.claude/` | The writing harness: skills and agents that draft, review, and publish with Claude Code |

## How the corpus is made

Articles are written from real sessions with Claude Code as collaborator — it reviews, fact-checks, translates, and cross-posts; the author writes and decides. The harness that does this is in `.claude/` and is itself part of what the articles describe:

- [`zenn-practical-writing`](.claude/skills/zenn-practical-writing/SKILL.md) — the default voice for every article (practical axis: usable in seconds, reproducible by hand)
- [`writing-team`](.claude/skills/writing-team/SKILL.md) — orchestrates the review loop (editor · fact-checker · clarity reviewer · article judge)
- [`theme-eval`](.claude/skills/theme-eval/SKILL.md) — rates the theme before and after drafting, because a weak question caps the article
- Conventions and review workflow: [CLAUDE.md](CLAUDE.md) · publishing pipeline: [docs/CODEMAPS/scripts.md](docs/CODEMAPS/scripts.md)

```bash
npm install && npm run preview     # local Zenn preview
npm run validate                   # Zenn frontmatter check
npm run generate:index             # regenerate docs/PUBLICATIONS.md and the reading paths above
```

## Provenance and reuse

All content — articles, translations, and tooling — is [CC0 1.0](LICENSE) (public-domain dedication).

- Author: [ORCID 0009-0002-6168-4162](https://orcid.org/0009-0002-6168-4162) · [GitHub hub](https://github.com/shimo4228/shimo4228) — the author's other research projects, which these articles draw on and report from, each with its own DOI
- Citation: [CITATION.cff](CITATION.cff) — instead of a DOI, this repository is cited by a content-derived identifier (a Software Heritage snapshot), which records what was published and when without a registry
- Papers that grew out of these articles are listed in the [Publications index](docs/PUBLICATIONS.md#papers)

## For coding agents

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/shimo4228/zenn-content)

Start with [llms.txt](llms.txt) (navigator) and [llms-full.txt](llms-full.txt) (self-contained Q&A). The Markdown sources here are the canonical text; the platforms are copies.
