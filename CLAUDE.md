# Claude Code Instructions for zenn-content

## Project Overview

This repository contains published, author-voiced Zenn / Dev.to articles and note / Substack essays about
AI agents, Claude Code workflows, and LLM engineering. Study drafts without an author voice do not belong.
The repository is public; nothing load-bearing depends on a publishing platform remaining available.

Reception metrics in `scripts/metrics/snapshots.jsonl` may inform **what to write**, cadence, and language
placement. They must not deform an idea, doctrine decision, or existing article body.

## Publications index

README is a routing page, not an article list. The exhaustive generated index is `docs/PUBLICATIONS.md`.

- source: `articles/*.md` frontmatter, `scripts/schedule.json`, `scripts/corpus.yml`, `scripts/reading_paths.yml`
- generate after article / URL / essay / paper changes: `npm run generate:index`
- verify drift before handoff: `npm run check:index`
- do not hand-maintain article titles or counts in README / llms files

## Writing harness

Human-primary prose has one entrypoint, resident in this repository:
`.claude/skills/writing-ecosystem/SKILL.md` (the
review agents `editor` / `essay-reviewer` / `prose-clarity-reviewer` / `theme-reviewer` / `title-reviewer` /
`fact-checker` and the skills `quality-gate` / `session-theme-mining` live in `.claude/` too).
Platform and repository values live only in `.claude/rules/publishing-channels.md`.
For article work in another repository, add this repo with `claude --add-dir ~/MyAI_Lab/zenn-content`
or start the session here.

Do not restate the shared flow here. `writing-ecosystem` owns the editorial brief, central thesis, causal
spine, evidence selection, revision return conditions, common review order, and the boundary that excludes
ADRs / memory / raw session history from writing-time rules.

## Channel and format boundaries

- Zenn: `articles/`; format and syntax are owned by `zenn-format`
- Dev.to: `articles-en/`; translation method is global `prose-translation`, platform conversion is `devto-translator`
- note JA canonical: `note/`; no frontmatter
- Substack EN translation: `substack/`; no frontmatter
- note / Substack HTML paste and corpus mirroring: `substack-publishing`
- Zenn / Dev.to publishing pipeline: `publish-article`

Exact register, audience promise, reviewer panel, title limit, `published_at`, cadence, terminology, and
publish handoff are defined in `.claude/rules/publishing-channels.md`; do not duplicate their values here.

Drafting stays in the orchestrator. Review and acceptance follow `writing-ecosystem` (resident in
`.claude/skills/`) plus the local channel contract.

## Post-publication measurement

`article-stocktake` is project-local instrumentation. It collects and reports reception differences, then
stops. It does not generate or rank themes and does not call `session-theme-mining` automatically.

## Verification and publishing

Pipeline details: `docs/CODEMAPS/scripts.md`.

1. `/quality-gate <file>`
2. author publication GO
3. `/publish-article <file>` for Zenn / Dev.to, or `substack-publishing` for note / Substack
4. `npm run generate:index`
5. `npm run validate` and `npm run check:index`

If article, `schedule.json`, or generated-index changes are committed, remind the user to push. An unpushed
commit does not reach Zenn scheduling or the Dev.to cross-post job.

## Public-repository safety

Never commit personal file paths, API keys, credentials, unsanitized raw logs, or sensitive screenshots.
