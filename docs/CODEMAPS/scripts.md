<!-- Generated: 2026-07-05 | Files: 1 Python script | Token estimate: ~420 -->
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

## Tests

- `tests/test_devto_crosspost.py` — 56 tests (respx-mocked Dev.to API, launchctl
  stubbed): `--at` tz conversion, conversion rules, tag resolution, POST
  success/failure/no-url, idempotency skip, one-shot self-cleanup, plist render,
  agent lifecycle, schedule/env/path helpers, command dispatch.
- Run: `cd scripts && uv run pytest --cov=. --cov-report=term-missing` (≥ 80%).
