<!-- Generated: 2026-03-06 | Files: 4 Python scripts | Token estimate: ~500 -->
# Scripts (Publishing Pipeline)

## Entry Points

| Script | Lines | Trigger | Purpose |
|--------|-------|---------|---------|
| `zenn_publish.py` | 275 | launchd 07:00 JST | Set published:true → commit → push |
| `scheduled_publish.py` | 528 | launchd 09:00 JST | Cross-post to Qiita/Dev.to/Hashnode |
| `publish.py` | 676 | CLI manual | API client for cross-posting |
| `plan_schedule.py` | 257 | CLI manual | Generate schedule.json entries |

## Key Functions

### zenn_publish.py
- `_git_add_commit_push()` — git add → commit → pull --rebase → push
- `_publish_zenn_article(entry)` — frontmatter rewrite (published: true)
- Assumes local/remote are in sync (breaks if unpushed commits exist)

### scheduled_publish.py
- Phase 1: Zenn publish (delegates to zenn_publish)
- Phase 2: Cross-post with 15-min delay (Zenn deploy lead time)
- Handles `depends_on` chains (EN waits for JP)
- Incremental schedule.json saves after each entry

### publish.py
- `_post_qiita(article_path)` — Zenn→Qiita markdown conversion + API POST
- `_post_devto(article_path, canonical_url)` — Dev.to API with canonical
- `_post_hashnode(article_path, canonical_url)` — Hashnode GraphQL mutation
- Strips Zenn-specific syntax (:::message, :::details)

## schedule.json Schema
```json
{
  "file": "articles/slug.md",
  "canonical_url": "https://zenn.dev/shimo4228/articles/slug",
  "zenn_date": "YYYY-MM-DD",
  "date": "YYYY-MM-DD",
  "qiita": "URL | pending | n/a",
  "devto": "URL | pending | n/a",
  "hashnode": "URL | pending | n/a",
  "zenn_published": true,
  "depends_on": "articles/slug.md (optional, for EN translations)"
}
```

## launchd Plist
- `com.shimomoto.zenn-auto-publish` → zenn_publish.py at 07:00
- `dev.shimo4228.crosspost` → scheduled_publish.py at 09:00
- Logs: `~/Library/Logs/zenn-auto-publish.log`, `scripts/publish.log`

## Tests
- `test_publish.py` — publish.py unit tests
- `test_scheduled_publish.py` — orchestrator tests
- `test_zenn_publish_manual.py` — manual publish flow
- `test_crosspost_delay.py` — timing/delay tests
