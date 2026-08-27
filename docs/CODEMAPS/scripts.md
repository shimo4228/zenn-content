<!-- Generated: 2026-08-27 | Files: 5 Python scripts | Token estimate: ~800 -->
# Scripts (Publishing Pipeline)

## Entry Point

`devto_crosspost.py` is one self-contained file — a per-article scheduled Dev.to
cross-poster. Dev.to has **no future-publish API**, so each EN article is posted
by a **one-shot launchd agent** that fires at the datetime you give on the command
line (tuned to the overseas buzz window), posts it, records the URL, and removes
itself. The post time is an argument, never stored in schedule.json.

| Command | Purpose |
|---------|---------|
| `schedule <slug> --at "<datetime [Tz]>"` | Arm a one-shot launchd job at that datetime |
| `post <slug> [--dry-run]` | Post the article to Dev.to now (what launchd runs) |
| `list` | Show each EN article's launchd state / Dev.to URL |
| `unschedule <slug>` | Cancel a pending launchd job |

`<slug>` is the `articles-en/<slug>.md` basename. **Zenn (JP) publishing is NOT
scripted** — Zenn schedules natively via `published_at` frontmatter.

Consolidated 2026-07 from five modules (`publish.py` / `_schedule_utils.py` /
`plan_schedule.py` / `generate_cover.py` + this) once the pipeline collapsed to
"post one article at its scheduled time." Cover images are managed by hand.

## Key Functions

- `cmd_schedule()` → `parse_publish_at()` (parses the `--at` datetime, tz-aware →
  JST) → `render_plist()` + `install_agent()` — writes a plist to
  `~/Library/LaunchAgents/` and `launchctl load`s it. Refuses past times.
- `cmd_post()` — idempotency guard (`find_existing_devto_url()` title search +
  the entry's `devto` field) → `convert_to_devto()` → `post_to_devto()` → write
  URL back to schedule.json → `remove_agent()` (one-shot self-cleanup).
- `parse_zenn_article()` / `strip_zenn_syntax()` / `resolve_devto_tags()` —
  Zenn markdown → Dev.to payload (`:::message`→blockquote, `:::details`→
  `<details>`, `/images/…`→GitHub raw URL). The proven transform core.
- `render_plist()` — uses `sys.executable` / `__file__`, so **no username is
  hard-coded**; the rendered file lives only in the user's untracked LaunchAgents.

## schedule.json Schema

```json
{
  "articles": [
    {
      "file": "articles-en/slug.md",
      "devto": null,
      "devto_tags": ["tag1", "tag2"],
      "cover_image": "https://..."
    }
  ]
}
```

schedule.json is a **posted-URL ledger**, not a schedule — the post time is passed
to `schedule --at`, never stored here. Only `articles-en/…` entries are
cross-posted; `articles/…` (JP) entries are record-keeping placeholders. `devto`:
URL = posted (auto-recorded), else pending. Schema source of truth:
`.claude/refs/schedule-schema.md`.

## Automation

- **Per-article one-shot launchd** (2026-07). `schedule <slug>` installs a job at
  the article's exact datetime into `~/Library/LaunchAgents/`; it fires once,
  posts, and self-removes. No committed plist, no recurring poll. If the Mac is
  asleep at the fire time, launchd runs the missed job once at next wake.
- **No cron.** The old GitHub Actions `scheduled-publish.yml` was retired
  2026-05; `.github/workflows/` holds only `validate.yml`. `DEVTO_API_KEY` stays in
  `scripts/.env` (gitignored), never in a plist.

## Publication index generator

`generate_article_index.py` renders `docs/PUBLICATIONS.md` (every article / essay /
paper / research line, newest first) and the `<!-- reading-paths:start/end -->`
blocks in `README.md` / `README.ja.md`. Deterministic (no clock, no git), so
`--check` is safe in CI (`validate.yml` runs `npm run check:index`; no bot commit).

| Input | Owns |
|---|---|
| `articles/*.md` frontmatter | JP membership (`published: true`), title, topics, slug, `published_at` (**required**) |
| `articles-en/<slug>.md` / `<slug>-en.md` | EN title, EN source link |
| `schedule.json` | Dev.to URL only (enrichment, never membership) |
| `corpus.yml` | note/Substack essays, deposited papers (Zenodo + SSRN), research lines |
| `reading_paths.yml` | README curated routes (author judgment, ~yearly) |

Run: `npm run generate:index` (write) / `npm run check:index` (exit 1 on drift, 2 on
source errors such as a published article without `published_at`). ADR-0009.

## zenn_evidence.py

`zenn_evidence.py` extracts deterministic evidence from `articles/*.md` — the
structure, format, existence and consistency checks a reviewer would otherwise
count by eye. Evidence, not a verdict: JSON out, no threshold, always exit 0.

| Output layer | Meaning |
|---|---|
| `deviations` | A rule the channel contract states, broken by this article |
| `grandfathered` | The same rule, broken by an article published before the check existed — reported, never counted as a deviation |
| `signals` | Hybrid counts a reviewer interprets: register mixing, self-link placement, paragraph density |
| `info` | Neutral facts: topics, title length, first heading level, related-link count |

Covers frontmatter fields / `published_at` presence and format / topics count and
case / type enum / single emoji / title limits / relative internal links / code
fence balance and language / `:::` balance / body heading level / image existence
/ personal paths and secrets / canonical-source link and author hub in the related
links section / project terminology. `--online` adds external URL liveness and is
the only path that touches the network.

Run: `npm run evidence -- articles/<slug>.md` (or a directory, `--text` for a
human-readable summary). Wired into the channel table's deterministic checks,
`zenn-format` Step 0, and `publish-article` Validate target — deliberately not
into a commit hook. ADR-0012.

Other script: `metrics_snapshot.py` writes Zenn / Dev.to reception snapshots to
`metrics/snapshots.jsonl`. The publishing pipeline has no prose linter; global reviewers and
`quality-gate` own semantic acceptance.

## Tests

- `tests/test_devto_crosspost.py` — respx-mocked Dev.to API, launchctl stubbed: `--at` tz conversion, conversion rules, tag resolution, POST
  success/failure/no-url, idempotency skip, one-shot self-cleanup, plist render,
  agent lifecycle, schedule/env/path helpers, command dispatch.
- `tests/test_generate_article_index.py` — tmp repo fixture: membership /
  ordering / EN resolution / Dev.to enrichment, `published_at` required, essays /
  papers / lines rendering, corpus validation, marker splice, `--check` semantics.
- `tests/test_metrics_snapshot.py` — record building, Zenn / Dev.to pagination,
  fail-soft collection when an API key or endpoint is missing.
- `tests/test_zenn_evidence.py` — tmp repo fixture: every check above, the
  grandfathered / deviation split, `--online` behind a stubbed opener (and a test
  asserting the default never opens a socket), plus false-positive regressions
  pinned from the real corpus: placeholder `/Users/you/` paths, a shell comment
  inside a fence reading as an H1, and wrong terminology quoted in a config example.
- Run: `cd scripts && uv run pytest --cov=. --cov-report=term-missing` (≥ 80%).
