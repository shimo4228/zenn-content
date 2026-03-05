<!-- Generated: 2026-03-06 | Token estimate: ~300 -->
# Dependencies

## Node.js (lint & preview)
| Package | Purpose |
|---------|---------|
| zenn-cli | Local preview, article validation |
| textlint + preset-ja-technical-writing | Japanese prose linting |
| textlint-rule-prh | Terminology consistency (prh.yml) |
| textlint-rule-no-dead-link | Broken link detection |
| textlint-filter-rule-comments | textlint-disable regions |
| markdownlint-cli2 | Markdown structure linting |
| husky + lint-staged | Pre-commit hooks |

## Python (publishing)
| Package | Purpose |
|---------|---------|
| requests | HTTP client for cross-post APIs |
| python-frontmatter | Parse/write Zenn frontmatter |
| (uv managed) | See scripts/pyproject.toml |

## External Services
| Service | Usage | Auth |
|---------|-------|------|
| Zenn | Primary platform (git-deploy) | GitHub integration |
| Qiita | JP cross-post | QIITA_ACCESS_TOKEN |
| Dev.to | EN cross-post | DEVTO_API_KEY |
| Hashnode | EN cross-post | HASHNODE_API_TOKEN + PUBLICATION_ID |
| GitHub Actions | Lint CI | Automatic |
| macOS launchd | Scheduled publishing | Local |

## Secrets Location
`scripts/.env` — API tokens (gitignored)
