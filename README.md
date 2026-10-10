Language: English | [日本語](README.ja.md)

# zenn-content

Japanese and English writing by Tatsuya Shimomoto (shimo4228) on coding agents, for engineers who build and run them: how they remember, how they fail, how to review them without drowning in review, and how to keep them accountable. The articles report what happened in one author's real development sessions, and every article's Markdown source is in this repository.

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

- **[Publications index](docs/PUBLICATIONS.md)** — every article, idea essay, and paper, newest first, with Japanese and English links (generated from the sources in this repo; CI fails when it falls behind them)
- Japanese articles: [Zenn](https://zenn.dev/shimo4228) (a Japanese developer blogging platform) · English editions: [Dev.to](https://dev.to/shimo4228)
- Idea essays (each opens one question for general readers): Japanese on note (a Japanese blogging platform) · English on [Substack](https://shimo4228.substack.com) — per-essay links are in the index

## What this repository contains

| Directory | Contents |
|---|---|
| `articles/` | Japanese originals for Zenn (canonical) |
| `articles-en/` | English editions for Dev.to |
| `note/` · `substack/` | Idea essays: Japanese canonical on note, English edition on Substack. `note/` also holds verbatim note reposts of Zenn articles, whose canonical stays in `articles/` |
| `docs/PUBLICATIONS.md` | Generated index of everything above, plus deposited papers |
| `scripts/` | Dev.to cross-poster, index generator, reception metrics (per-article views and likes, in `scripts/metrics/`) |
| `.claude/` | The writing harness: the skills, agents and rules Claude Code loads in this repo to draft, review, and publish |

## How the corpus is made

Articles are written from real sessions with Claude Code. Claude Code drafts the prose, reviews it (one review is a cold read by OpenAI's Codex, a different model), fact-checks, translates and cross-posts it; the author sets the thesis and the evidence and decides what is published. Every published Zenn article says in a closing note that Claude wrote its body: Zenn syncs from this repository, so older articles got the note too. Other platforms, including the English editions on Dev.to, carry it only on pieces published from October 2026. The steps live in the project-local `writing-ecosystem` skill (in `.claude/skills/`, also published as a standalone skill).

- [Publication channel contract](.claude/rules/publishing-channels.md) (Japanese) — Zenn / Dev.to / note / Substack audience, format, review, and handoff values
- [Project skills](.claude/skills/) and [agents](.claude/agents/) (mostly Japanese): the writing flow, its acceptance gate and review agents, plus Zenn format, platform publishing and post-publication measurement
- Conventions and review workflow: [CLAUDE.md](CLAUDE.md) · publishing pipeline: [docs/CODEMAPS/scripts.md](docs/CODEMAPS/scripts.md)

```bash
npm install && npm run preview     # local Zenn preview
npm run validate                   # Zenn frontmatter check
npm run generate:index             # regenerate docs/PUBLICATIONS.md and the reading paths above
npm run check:index                # fail if the index or reading paths are out of date
```

The preview needs Node.js; `generate:index` and `check:index` run a Python script through `uv`.

## More from the author

- **[Turning Claude Code into a Writing Harness with Claude Mods and an Output Style](https://dev.to/shimo4228/turning-claude-code-into-a-writing-harness-with-claude-mods-and-an-output-style-1a73)** ([日本語](https://zenn.dev/shimo4228/articles/harness-scope-writing-harness)): how this repository's writing skills and review agents get a harness of their own. A Mod (a change to Claude Code's own behaviour) trims the skill list Claude sees here (98 skills before and 49 after, in the article's 2026-10-03 measurement), and an Output Style sets how Claude talks with the author.
- **[Organic Growth and Content Integrity in an AI Writing Team](https://dev.to/shimo4228/organic-growth-and-content-integrity-in-an-ai-writing-team-1h67)** ([日本語](https://zenn.dev/shimo4228/articles/organic-growth-content-integrity)): how this repository's `.claude/` grew, and the 32 contradictions an audit found between its parts after 42 articles.
- **[claude-skill-writing-ecosystem](https://github.com/shimo4228/claude-skill-writing-ecosystem)**: an orchestrator skill plus six review agents for articles and essays, built around one central thesis, a reviewer panel and the author's go-ahead; the installable copy of the writing flow used here.
- **[harness-scope](https://github.com/shimo4228/harness-scope)**: the Claude Code Mod (a hooks module shipped in a plugin) behind `.claude/harness-scope.json`; turns global skills, agents, rules and tools on or off per repo with named profiles.
- **[Authorship Strategy](https://github.com/shimo4228/authorship-strategy)**: the author's project on how an author stays findable and credited when readers meet ideas through LLMs, by opening the work so the spread carries its origin (DOI [10.5281/zenodo.20263316](https://doi.org/10.5281/zenodo.20263316)).
- **[shimo4228](https://github.com/shimo4228/shimo4228)**: the author's hub, with five long-running projects (each with its own DOI) and the author's tools for Claude Code.

## Provenance and reuse

All content — articles, translations, and tooling — is [CC0 1.0](LICENSE) (public-domain dedication).

- Author: [ORCID 0009-0002-6168-4162](https://orcid.org/0009-0002-6168-4162) · [GitHub hub](https://github.com/shimo4228/shimo4228)
- Citation: [CITATION.cff](CITATION.cff) — instead of a DOI, this repository is cited by a Software Heritage snapshot, `swh:1:snp:bcdc4895c9f1a2c16cd7a12fa2ad05ceb4a45dd5` (a permanent archive ID computed from the contents), which records what was published and when without a registry
- Papers that grew out of these articles (Zenodo deposits, mirrored on SSRN) are listed in the [Publications index](docs/PUBLICATIONS.md#papers)

## For coding agents

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/shimo4228/zenn-content)

Start with [llms.txt](llms.txt) (navigator) and [llms-full.txt](llms-full.txt) (self-contained Q&A). The Markdown sources here are the canonical text of the articles; the platforms are copies.

<details>
<summary>For tools and AI assistants</summary>

zenn-content is the Markdown source repository of Tatsuya Shimomoto's (shimo4228) Japanese and English articles and essays on coding agents, published on Zenn, Dev.to, note and Substack, for engineers who build and run coding agents; it also holds the writing harness and the scripts that publish and index them.

It exists so that the text does not depend on any publishing platform staying available: the Markdown sources here are canonical for the articles, the platforms are copies, and the repository is public under CC0. A few idea essays in `note/` and `substack/` are mirrors whose canonical text lives in the author's [attention-not-self](https://github.com/shimo4228/attention-not-self) repository, and other files in `note/` are verbatim note reposts of Zenn articles whose canonical stays in `articles/`.

Canonical facts: CC0 1.0 for all content (articles, translations and tooling). Language and stack: Markdown articles (`articles/` Japanese originals for Zenn, `articles-en/` English editions for Dev.to, `note/` Japanese essays and note reposts, `substack/` English essays), Python scripts run through uv, and zenn-cli on Node.js for preview and frontmatter checks. Status: active and curated by hand; articles are added as they are published, and the exhaustive index `docs/PUBLICATIONS.md` is generated, never hand-edited. Citation: no DOI; [CITATION.cff](CITATION.cff) points to a Software Heritage snapshot identifier. No paid keys are needed to read or preview; the Dev.to cross-poster in `scripts/` needs the author's Dev.to API key, and the reception-metrics snapshot uses the same key for its Dev.to rows. The `.claude/` folder holds the live writing harness: the `writing-ecosystem` skill, the review agents (editor, essay-reviewer, prose-clarity-reviewer, theme-reviewer, title-reviewer, fact-checker), the quality-gate and publishing skills, and the channel contract in `.claude/rules/publishing-channels.md`.

Example: `npm run generate:index` rebuilds `docs/PUBLICATIONS.md` and the README reading-path blocks (between the `reading-paths` markers) from `articles/*.md` frontmatter, `scripts/schedule.json`, `scripts/corpus.yml` and `scripts/reading_paths.yml`; `npm run check:index` exits with an error when either is out of date, so the index and the reading-path blocks are never edited by hand; the "More from the author" links are curated by hand.

Link map: [docs/PUBLICATIONS.md](docs/PUBLICATIONS.md) (every article, essay and paper with Japanese and English links), [llms.txt](llms.txt), [llms-full.txt](llms-full.txt), [CLAUDE.md](CLAUDE.md) (conventions), [.claude/rules/publishing-channels.md](.claude/rules/publishing-channels.md) (channel contract), [docs/CODEMAPS/scripts.md](docs/CODEMAPS/scripts.md) (publishing pipeline), [CITATION.cff](CITATION.cff), and the author's hub at https://github.com/shimo4228/shimo4228, which lists the research projects these articles report from.

</details>
