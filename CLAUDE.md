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

All articles MUST use Zenn frontmatter. Field-by-field spec is canonical in `.claude/skills/zenn-format/SKILL.md`; the `published_at` scheduling field is documented in `.claude/rules/zenn-writing.md`.

> **執筆スタイルの既定は実用軸**（読者が数秒で何かわかり、すぐ使える）。tech は `zenn-practical-writing`、frontmatter・記法は `zenn-format`、Zenn 固有ルールは `.claude/rules/zenn-writing.md` が正本。以下の Technical Depth は「why を冗長に語る」ではなく、必要な深さを低認知負荷で（詳細は `:::details` に）という意味。

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
   - **No AI slop** - Avoid generic phrases like "powerful tool", "revolutionize", "seamless"（禁止リストの正本は global `writing-ecosystem` skill）

5. **Structure**
   - **Introduction** - Hook reader with a problem or insight
   - **Context** - Background and motivation
   - **Implementation** - Technical details with code examples
   - **Lessons Learned** - Reflections and takeaways
   - **Conclusion** - Summary and next steps
   - **Environment-dependent changes** - When commands depend on local paths, existing settings, symlinks, or authentication, finish the human-facing narrative first, then provide a standalone read-only planning prompt for the reader's coding agent. The agent must stop for human approval before implementation. Canonical rules: `zenn-practical-writing`.

### Image Guidelines

- Store images in `images/` directory
- Use descriptive filenames: `tokenization-flow.png` not `image1.png`
- Embed with Zenn syntax: `![Alt text](/images/filename.png)`
- Sanitize screenshots: no file paths like `/Users/username/`, no API keys

### 関連リンク：著者ハブ（毎回必須）

記事末尾に「関連リンク」節を置くとき（本文で著者自身のリポジトリ/ツールに言及した記事）は、紹介した repo が **1つでも**、著者の GitHub ハブ [github.com/shimo4228](https://github.com/shimo4228) を**必ず含める**。ハブは読者を著者の全リポジトリへ送る導線なので、言及 repo の数に依らず付ける。これが canonical。skill 側（`zenn-practical-writing`）はここを参照する。

## `substack/` フォルダ（Zenn 規約の適用外）

`substack/` は他媒体（Substack 等）で初出した human essay の mirror 置き場（public GitHub 上の .md として LLM クローラーに読ませる corpus 拡張用）。**Zenn 記事ではないので、本 repo の記事規約は適用しない**:

- Zenn frontmatter 必須・`published` フラグ・`published_at` は不要（Zenn は `articles/` のみ同期するため `substack/` は公開されない）
- `schedule.json` に載せない（dev.to クロスポストしない）
- canonical は初出媒体（Substack 等）。ここはあくまでミラー

公開〜ミラーの手順は global skill `substack-publishing` を参照。

## Editor Agent Usage

記事の執筆はサブエージェントに委譲せず、Claude Code 本体が `zenn-practical-writing` に従って直接執筆する。Before publishing, run review agents in parallel: `editor`（全 Zenn/Dev.to 記事共通）+ `fact-checker`（事実主張の検証）+ `zenn-clarity-reviewer`（初見読者の明瞭性、project agent）+ codex-review（公開記事の cross-model レビュー、prompt-driven）。

```bash
claude --agent=editor --prompt="Review: articles/ARTICLE_NAME.md"
# ファクトチェック（並列実行可）
claude --agent=fact-checker --prompt="Fact-check: articles/ARTICLE_NAME.md"
```

Available agents:
- `editor` — Zenn/Dev.to 記事の構造・品質・AI slop 検出（4段階評価）。type 分岐なしで全記事に使用
- `essay-reviewer` — Substack essay corpus 専用（Zenn/Dev.to のミッションでは使わない）
- `fact-checker` — 事実主張の Web 検索検証（ACCURATE/PARTIALLY/INACCURATE/UNVERIFIABLE）
- `zenn-clarity-reviewer` — 初見読者の明瞭性（造語予算・タイトル軸・内部文脈依存。project agent、JP/EN 両対応。FAIL は公開ブロック）
- `devto-translator` — JP→EN 翻訳 + Dev.to タグ付け + 投稿

## Writing skills

Zenn/Dev.to の記事執筆は**チャンネル独自の実用軸**が既定 —「読者が数秒で何かわかり、そのまま手を動かして再現できる」。**tech/idea の type で声を分けない**（frontmatter の `type` は platform 要件として残るが、voice は分岐しない）。

| 用途 | 使うスキル |
|---|---|
| **Zenn/Dev.to の記事執筆（既定・全記事）** | `zenn-practical-writing` — 実用軸（ですます・即実用・実コード/図・低認知負荷）。環境依存の変更記事は「人間向けナラティブ → エージェント向け実装契約」の二層構成 |
| **執筆前のタイプ判定・軸ずれ検出・改稿時の構造自己審問・レビュー採否** | `zenn-editorial-judgment` — 著者の編集判断ゲート集（構成案の前に Phase 0 タイプ判定、ADR-0006） |
| **著者の価値観・ペルソナ規約・内容ランク A/B/C 基準** | `zenn-authorial-values` — 実セッション引用付き価値観リファレンス（ADR-0006） |
| **記法・frontmatter** | `zenn-format`（正本） |
| **任意の personality flavor** | `zenn-idea-voice`（毒humor / 刃牙。type 非依存の opt-in） |
| **公開後の実測 Eval ループ** | `article-stocktake` — 実測メトリクス × 品質ランクの乖離棚卸し（月次目安、ADR-0005） |
| **genuine な思索エッセイ** | `~/.claude/skills/writing-ecosystem/SKILL.md`（だ/である × 発見調）。Substack corpus 専用、Zenn には出さない |

genre 中立 canon（AI slop 禁止・タイトル原則・ネタ 3 軸）は global `writing-ecosystem` が正本。根拠: `docs/adr/0003-zenn-practical-channel-axis.md`。

## Testing Workflow

See `docs/CODEMAPS/scripts.md` for the publishing pipeline (single `devto_crosspost.py`, launchd agent, tests).

## Publishing Checklist

Pipeline reference: `docs/CODEMAPS/scripts.md`

- [ ] Code snippets have no API keys
- [ ] Screenshots have no sensitive information (file paths, usernames)
- [ ] File paths are anonymized
- [ ] All code examples are tested and executable
- [ ] Editor レビュー完了（Zenn/Dev.to は type 分岐なく editor に一本化。essay-reviewer は Substack 専用）
- [ ] タイトル最適化済み（`/seo-optimizer` → global `headline-craft` 経由で候補提示・確定。英訳より前に確定させる）
- [ ] fact-checker でファクトチェック完了（事実主張を含む記事は必須）
- [ ] zenn-clarity-reviewer の verdict が PASS（初見読者の明瞭性。FAIL のままなら公開不可）
- [ ] Zenn frontmatter validates (`npm run validate`)
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
