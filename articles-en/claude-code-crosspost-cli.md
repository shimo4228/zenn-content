---
title: "Cross-Post from Zenn to Qiita to Dev.to in One Command with Claude Code"
emoji: "🔄"
type: "tech"
topics: ["claudecode", "zenn", "qiita", "python"]
published: true
---

After writing an article on Zenn and copy-pasting it to Qiita, I noticed the next day that `:::message` blocks were rendering as raw text. A reader left a comment saying "the layout is broken" before I scrambled to fix it. The `:::details` blocks and `/images/` paths were all broken too.

Manually converting platform-specific syntax for every cross-post is not sustainable. I asked Claude Code to "build a system that reliably converts Zenn syntax and cross-posts articles," and it generated `scripts/publish.py`.

## Usage

```bash
# Post to Qiita (new article)
python scripts/publish.py articles/my-article.md --platform qiita

# Update an existing Qiita article (auto-search by title)
python scripts/publish.py articles/my-article.md --platform qiita --update auto

# Post to Dev.to (with canonical URL — marks the original for SEO)
python scripts/publish.py articles/my-article.md --platform devto \
  --canonical-url https://zenn.dev/shimo4228/articles/my-article

# Preview the converted output with dry-run
python scripts/publish.py articles/my-article.md --platform qiita --dry-run
```

## Zenn Syntax Conversion

The script converts three types of Zenn-specific syntax into standard Markdown.

**:::message to blockquote**

```markdown
<!-- Before (Zenn) -->
:::message
This is a note.
:::

<!-- After -->
> This is a note.
```

**:::details to HTML details tag**

```markdown
<!-- Before (Zenn) -->
:::details Click to expand
Detailed content here.
:::

<!-- After -->
<details><summary>Click to expand</summary>

Detailed content here.

</details>
```

**/images/ to GitHub raw URL**

```markdown
<!-- Before -->
![Diagram](/images/diagram.png)

<!-- After -->
![Diagram](https://raw.githubusercontent.com/user/zenn-content/main/images/diagram.png)
```

Zenn's `/images/` paths only resolve within Zenn. On other platforms, the script replaces them with raw URLs from the GitHub repository.

## How --update auto Works

When you pass `--update auto`, the script searches for an existing article by title.

```python
def find_qiita_item_by_title(title: str, token: str) -> str | None:
    """タイトル完全一致で Qiita 記事を検索（簡略版）"""
    page = 1
    while page <= 5:
        resp = httpx.get(
            f"{QIITA_API_BASE}/authenticated_user/items",
            headers={"Authorization": f"Bearer {token}"},
            params={"page": page, "per_page": 20},
            timeout=30,
        )
        # エラーハンドリング省略（実装では status_code チェックあり）
        for item in resp.json():
            if item.get("title") == title:
                return item["id"]
        page += 1
    return None
```

It matches by exact title. If you change the title on the Zenn side, use `--update <article-id>` to specify the ID directly.

## English Article Guard

Dev.to and Hashnode are English-language platforms. If you try to post directly from the `articles/` directory (which contains Japanese articles), the script stops with an error.

```bash
$ python scripts/publish.py articles/my-article.md --platform devto
Warning: No English translation found at articles-en/my-article.md
Run /translate-article first, or pass --force to publish in Japanese.
```

Translated articles go in `articles-en/`, and you post from there. If you want to publish in Japanese anyway, pass the `--force` flag to bypass the guard.

## Setup

### Dependencies

```bash
pip install httpx python-frontmatter
```

### API Tokens

Set your platform tokens in `scripts/.env`.

```text
QIITA_ACCESS_TOKEN=xxxxx
DEVTO_API_KEY=xxxxx
HASHNODE_API_TOKEN=xxxxx
HASHNODE_PUBLICATION_ID=xxxxx
```

Add `.env` to your `.gitignore`. The script automatically loads `scripts/.env` at startup using a lightweight custom loader (not `python-dotenv`) to keep dependencies minimal.

**Image path configuration**: The `GITHUB_RAW_BASE` constant in the script has the GitHub username and repository name hardcoded. Update it to match your environment.

```python
# Change this constant in scripts/publish.py to your repository
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/<your-user>/zenn-content/main/images"
```

## Design Decisions

**Why build it from scratch?**

Existing cross-posting tools (zenn-to-qiita, cross-post-cli, etc.) had incomplete Zenn syntax conversion. Most of them left `:::message` and `:::details` untouched, which meant manual fixes were still necessary. By asking Claude Code to "reliably convert Zenn syntax," I got a script tailored to my exact use case.

**Why add --update auto?**

Having to look up the Qiita article ID from the admin dashboard every time I update an article is tedious. With title-based auto-matching, the workflow becomes: update on Zenn, then run `--update auto` to sync Qiita -- all in one command.

## Summary

- Automatically converts Zenn-specific syntax (`:::message`, `:::details`, `/images/`) for cross-posting
- `--update auto` enables automatic updates of existing articles via title search
- Built-in guard prevents accidental posting of Japanese content to English-language platforms
- Claude Code generated a working script in about 30 minutes

Hashnode does not yet support `--update auto`, so use `--update <article-id>` directly when updating.
