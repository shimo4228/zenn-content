# Runbook

> Auto-generated from project configuration — 2026-02-15

## Deployment (Publishing Articles)

### Manual Publish

```bash
# 1. Verify article passes lint
npm run lint:all

# 2. Preview locally
npm run preview

# 3. Set published: true in frontmatter
# 4. Commit and push to main
git add articles/xxx.md && git commit -m "feat: publish xxx" && git push

# 5. Cross-post (optional)
cd scripts && source .venv/bin/activate
python publish.py ../articles/xxx.md --platform qiita
python publish.py ../articles-en/xxx.md --platform devto --canonical-url URL
python publish.py ../articles-en/xxx.md --platform hashnode --canonical-url URL
```

### Scheduled Publish (launchd)

A macOS launchd job runs daily at **18:00 JST** (09:00 UTC).

**Config**: `scripts/dev.shimo4228.crosspost.plist`

```bash
# Install the launchd job
cp scripts/dev.shimo4228.crosspost.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/dev.shimo4228.crosspost.plist

# Unload
launchctl unload ~/Library/LaunchAgents/dev.shimo4228.crosspost.plist

# Check status
launchctl list | grep crosspost
```

**Schedule file**: `scripts/schedule.json`
- `date`: Target publish date (YYYY-MM-DD)
- `null`: Not yet posted (will be attempted)
- URL string: Already posted (skip)
- `"n/a"`: Not applicable for this platform

```bash
# Check schedule status
python scripts/scheduled_publish.py --status

# Dry run
python scripts/scheduled_publish.py --dry-run
```

**Logs**:
- stdout: `scripts/launchd-out.log`
- stderr: `scripts/launchd-err.log`
- app log: `scripts/publish.log`

## Monitoring

### Check Launchd Job Health

```bash
# Is it loaded?
launchctl list | grep crosspost

# Recent output
tail -20 scripts/launchd-out.log
tail -20 scripts/launchd-err.log

# App-level log
tail -20 scripts/publish.log
```

### Check Schedule Progress

```bash
python scripts/scheduled_publish.py --status
```

Output shows per-article status: `posted`, `DUE`, or `scheduled`.

## Common Issues and Fixes

### 1. textlint fails on commit

**Symptom**: Pre-commit hook blocks commit with textlint errors.

**Fix**:
```bash
# See errors
npm run lint

# Auto-fix what's possible
npm run lint:fix

# Manual fix for remaining issues, then re-commit
```

### 2. markdownlint fails on commit

**Symptom**: Pre-commit hook blocks commit with markdownlint errors.

**Fix**:
```bash
npm run lint:md
# Fix reported issues manually
```

**Common causes**:
- Missing blank lines before/after lists inside `:::message` / `:::details` (MD032)
- Bare URLs without angle brackets (MD034)

### 3. Cross-post API token expired

**Symptom**: `publish.py` returns 401/403 errors.

**Fix**:
1. Regenerate token on the platform
2. Update `scripts/.env`
3. Retry

| Platform | Token Location |
|----------|---------------|
| Qiita | Settings > Applications > Personal access tokens |
| Dev.to | Settings > Extensions > DEV Community API Keys |
| Hashnode | Settings > Developer > Personal Access Tokens |

### 4. launchd job not running

**Symptom**: `schedule.json` shows `DUE` articles but they weren't posted.

**Fix**:
```bash
# Check if loaded
launchctl list | grep crosspost

# Check logs for errors
tail -50 scripts/launchd-err.log

# Reload
launchctl unload ~/Library/LaunchAgents/dev.shimo4228.crosspost.plist
launchctl load ~/Library/LaunchAgents/dev.shimo4228.crosspost.plist

# Manual run
cd scripts && source .venv/bin/activate && python scheduled_publish.py
```

### 5. prh pattern causes regex error

**Symptom**: `Error: Invalid regular expression` on Node.js 20+.

**Cause**: Hyphen-containing patterns (e.g., `Node-js`) produce `\-` which is invalid in unicode regex.

**Fix**: Do NOT add hyphenated patterns to `prh.yml`. Use alternative patterns without hyphens.

### 6. markdownlint lints ALL files (not just staged)

**Symptom**: Pre-commit hook reports errors in unstaged files.

**Cause**: Glob patterns in `.markdownlint-cli2.jsonc` conflict with lint-staged.

**Fix**: Keep `.markdownlint-cli2.jsonc` free of glob patterns. File filtering is handled by lint-staged.

## Rollback Procedures

### Unpublish an Article

Set `published: false` in frontmatter, commit, and push:

```bash
# Edit the article frontmatter: published: false
git add articles/xxx.md && git commit -m "chore: unpublish xxx" && git push
```

Zenn removes it from public listing within a few minutes.

### Revert a Cross-Post

- **Qiita**: Delete from Qiita dashboard, then set the field in `schedule.json` back to `null`
- **Dev.to**: Unpublish from Dev.to dashboard (edit > unpublish)
- **Hashnode**: Delete from Hashnode dashboard

### Revert a Bad Commit

```bash
git log --oneline -10          # Find the commit to revert
git revert <commit-hash>       # Create a revert commit
git push
```
