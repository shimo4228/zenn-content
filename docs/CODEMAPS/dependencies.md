<!-- Generated: 2026-05-24 | Token estimate: ~320 -->
# Dependencies

## Node.js (preview & validation)
| Package | Purpose |
|---------|---------|
| zenn-cli | Local preview + frontmatter validation (`npm run validate` = `zenn list:articles`) |

> The prose/markdown lint stack (textlint, prh, no-dead-link, markdownlint-cli2,
> husky + lint-staged) was removed 2026-07. After the ja-technical-writing preset
> was dropped (2026-04-29), what remained was terminology vowel-mark nits +
> whitespace checks — low signal, high false-positive friction. Only Zenn
> frontmatter validation is kept.

## Python (publishing)
| Package | Purpose |
|---------|---------|
| httpx (>=0.28.1) | HTTP client for the Dev.to API |
| python-frontmatter | Parse/write Zenn frontmatter |
| respx (dev) | httpx mock for tests |
| (uv managed) | See `scripts/pyproject.toml` |

## External Services
| Service | Usage | Auth |
|---------|-------|------|
| Zenn | Primary platform (git-deploy, native `published_at` scheduling) | GitHub integration |
| Dev.to | EN cross-post (manual) | DEVTO_API_KEY |
| GitHub Actions | Validate CI (`validate.yml`, push/PR to main) | Automatic |

## Secrets Location
`scripts/.env` — DEVTO_API_KEY (gitignored)
