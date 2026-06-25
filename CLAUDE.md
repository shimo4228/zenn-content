# Claude Code Instructions for zenn-content

## Project Overview

This repository contains **Zenn articles and books** for AI agent development, Claude Code workflows, and LLM engineering experiments. All content follows the **"Build in Public"** principle, documenting real development sessions and design decisions.

## Governed essay corpus (membership)

This repository is governed as the **essay-corpus artifact** of a five-line research ecosystem (see `CITATION.cff` and the README "Research ecosystem" section). The governed corpus is **author-voiced + published** essays: pieces written in the author's own voice and actually published (Zenn / Dev.to / Substack mirror). Study or learning drafts without an author voice — for example Claude-written study drafts that were never published — are **not** part of the governed corpus and are kept out of this repository. This is a membership criterion, not a churn rule: it describes what belongs, and is not enforced by reshuffling files.

The corpus rests its priority claim on the **intrinsic content-derived identifier** (the Software Heritage snapshot in `CITATION.cff`), not a registry DOI — this is the essay genre's substitute priority-claim mechanism under the ecosystem's genre-split placement model (authorship-strategy ADR-0016 / ADR-0013). A load-bearing essay idea is promoted to a concept-DOI deposit only when it graduates into a paper.

## Git Push Reminder (CRITICAL)

記事の作成・編集・schedule.json の更新をコミットしたら、**必ずユーザーに push を促すこと**。未 push のコミットがあると、Zenn の `published_at` 予約投稿が反映されず、Dev.to のクロスポストスクリプトも動かない。

## Writing Guidelines

### Zenn Article Format

All articles MUST use Zenn frontmatter:

```markdown
---
title: "Article Title (50-60 characters)"
emoji: "📚"
type: "tech"  # or "idea"
topics: ["claude", "anki", "ai"]  # 1-5 tags
published: true  # or false for draft
published_at: 2026-04-15 07:00  # 予約投稿（JST、省略で即公開）
---

# Article content starts here
```

### Content Standards

1. **Technical Depth**
   - Explain **"why"** decisions were made, not just **"what"** was implemented
   - Include real code examples from the repository
   - Discuss trade-offs and alternatives considered

2. **Code Examples**
   - All code snippets MUST be executable and tested
   - Include file paths for context (e.g., `src/pdf2anki/quality.py:322-329`)
   - Use syntax highlighting: ` ```python `, ` ```typescript `, ` ```bash `
   - Add comments for clarity

3. **Terminology Consistency**
   - Use consistent terms across articles:
     - "pdf2anki" (not "PDF2Anki" or "pdf-to-anki")
     - "Claude-Native" (design philosophy)
     - "CLI-First" (architecture principle)
     - "半自動 (Semi-automated)" (workflow approach)

4. **Tone and Style**
   - **Technical but approachable** - Assume readers are engineers
   - **Honest** - Discuss failures and challenges, not just successes
   - **Human insights** - AI-assisted writing, but human perspective
   - **No AI slop** - Avoid generic phrases like "powerful tool", "revolutionize", "seamless"

5. **Structure**
   - **Introduction** - Hook reader with a problem or insight
   - **Context** - Background and motivation
   - **Implementation** - Technical details with code examples
   - **Lessons Learned** - Reflections and takeaways
   - **Conclusion** - Summary and next steps

### Image Guidelines

- Store images in `images/` directory
- Use descriptive filenames: `tokenization-flow.png` not `image1.png`
- Embed with Zenn syntax: `![Alt text](/images/filename.png)`
- Sanitize screenshots: no file paths like `/Users/username/`, no API keys

## `substack/` フォルダ（Zenn 規約の適用外）

`substack/` は他媒体（Substack 等）で初出した human essay の mirror 置き場（public GitHub 上の .md として LLM クローラーに読ませる corpus 拡張用）。**Zenn 記事ではないので、本 repo の記事規約は適用しない**:

- Zenn frontmatter 必須・`published` フラグ・`published_at` は不要（Zenn は `articles/` のみ同期するため `substack/` は公開されない）
- lint-staged / textlint / markdownlint の対象外（lint glob は記事フォルダ系のみ。実際 `substack/` 追加時に lint-staged は "no matching files" を返す）
- `schedule.json` に載せない（dev.to クロスポストしない）
- canonical は初出媒体（Substack 等）。ここはあくまでミラー

公開〜ミラーの手順は global skill `substack-publishing` を参照。

## Editor Agent Usage

Before publishing, run review agents. For tech articles use `editor`, for idea articles use `essay-reviewer`. Run `fact-checker` in parallel to verify factual claims.

```bash
# tech 記事
claude --agent=editor --prompt="Review: articles/ARTICLE_NAME.md"
# idea 記事
claude --agent=essay-reviewer --prompt="Review: articles/ARTICLE_NAME.md"
# ファクトチェック（並列実行可）
claude --agent=fact-checker --prompt="Fact-check: articles/ARTICLE_NAME.md"
```

Available agents:
- `editor` — tech 記事の構造・品質・AI slop 検出（4段階評価）
- `essay-reviewer` — idea 記事の論理・トーン・過積載検出
- `fact-checker` — 事実主張の Web 検索検証（ACCURATE/PARTIALLY/INACCURATE/UNVERIFIABLE）
- `devto-translator` — JP→EN 翻訳 + Dev.to タグ付け + 投稿
- `zenn-drafter` — 記事執筆（分析→執筆→セルフレビュー）

## zenn-writer Skill

Use the `zenn-writer` skill for article-specific guidance:

```bash
claude skill zenn-writer
```

This skill provides:
- Zenn frontmatter templates
- Article structure patterns
- SEO best practices
- Code embedding formats
- Image embedding formats

## Testing Workflow

See `docs/RUNBOOK.md` for the full testing and publishing workflow.

## Publishing Checklist

Full procedure: `docs/RUNBOOK.md`

- [ ] Code snippets have no API keys
- [ ] Screenshots have no sensitive information (file paths, usernames)
- [ ] File paths are anonymized
- [ ] All code examples are tested and executable
- [ ] Editor/essay-reviewer レビュー完了
- [ ] fact-checker でファクトチェック完了（idea 記事は必須）
- [ ] Lint passes (`npm run lint`)
- [ ] Dead-link チェック (`npm run lint:links`) — 公開前のみ。CI では走らない（外部 URL の rate limit / redirect 偽陽性で止まらないようにするため）
- [ ] Preview looks good (`npm run preview`)
- [ ] `published_at` を設定（`YYYY-MM-DD HH:MM` 形式、JST）
- [ ] English translation created in `articles-en/`
- [ ] `schedule.json` updated with both Japanese and English entries
- [ ] Cross-post target scheduled: Dev.to (English)

---

**IMPORTANT**: This repository is PUBLIC. Never commit:
- Personal file paths (`/Users/username/`)
- API keys or credentials
- Sensitive screenshots
