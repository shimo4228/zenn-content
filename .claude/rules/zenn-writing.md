<!-- origin: original -->
# Zenn Writing Rules (プロジェクト overlay)

> このファイルは `~/.claude/skills/writing-ecosystem/SKILL.md` の Zenn プロジェクト向け overlay。
> global base の AI slop 禁止リスト・Voice ルール・タイトル原則は **再掲しない**。
> 本ファイルは Zenn プラットフォーム固有の追加ルールのみを定義する。

## タイトル文字数上限

- **50 文字以内**（Zenn UI で切れずに表示される目安）
- 概念を正確に伝えるために必要な場合は **60 文字まで許容**
- 基本原則（煽り禁止・問いの形 OK など）は writing-ecosystem skill の Title Conventions を参照

## Zenn Frontmatter 規約

```yaml
---
title: "記事タイトル（50-60 文字）"
emoji: "📚"           # 1 字、記事内容を象徴
type: "tech"          # "tech" | "idea"
topics: ["claude"]    # 1-5 個（Zenn タグ仕様）
published: true       # false で下書き
published_at: 2026-04-15 07:00  # JST、予約投稿
---
```

### `published_at` フォーマット注意

- **正**: `YYYY-MM-DD HH:MM`（例: `2026-04-15 07:00`）
- **誤**: スラッシュ区切り（`2026/04/15`）、秒付き（`07:00:00`）
- JST 固定、省略で即公開
- push 後、指定時刻まで公開されない（レートリミットに計上されない）

## Zenn 記法特有の注意

### `:::message` ブロック

- textlint が `:::` 閉じタグを「句点なし文」として誤検出
- 回避: 該当箇所を `<!-- textlint-disable -->` ... `<!-- textlint-enable -->` で囲む
- 刃牙リファレンス・ダミーデータの明示にも使う（zenn-writer skill 参照）

### 内部リンク

- **誤**: `/articles/xxx`（textlint の no-dead-link がローカルファイル扱いしてエラー）
- **正**: フル URL `https://zenn.dev/shimo4228/articles/xxx`

### だ/である調の textlint 設定

- textlint `no-mix-dearu-desumasu`: 「だ」と「である」は別カテゴリ扱い
- 「だ」調で統一していても、「である」が 1 箇所混入すると発火する
- 統一するならどちらか一方に揃える

## プロジェクト固有用語（書き換え禁止ワード）

| ✅ 正 | ❌ 誤 |
|------|------|
| pdf2anki | PDF2Anki, pdf-to-anki, Pdf2Anki |
| Claude-Native | Claude-first, Claude based |
| CLI-First | CLI first, command-line first |
| 半自動 (Semi-automated) | semi-automatic, partially automated |
| Anki card | flashcard, card (alone) |
| LLM critique | AI critique, model critique |
| TDD (Test-Driven Development) | test driven, test-first |

詳細: プロジェクト CLAUDE.md の Terminology Consistency を参照。

## Zenn 投稿ペース方針

- **週 2-3 本ペース**（毎日投稿は 2026/3 の Zenn AI コンテンツ乱造対策で凍結リスクあり）
- バズタイム: 火〜水 7:00-9:00（JST）に集中
- 詳細: MEMORY.md の「投稿ペース方針」参照

## Dev.to クロスポスト規約（EN 記事）

- `description:` を frontmatter に含める（Dev.to API の description フィールドに渡される）
- `topics:` は YAML リスト、`tags:` はカンマ区切り文字列の両方を parser が読む
- カバー画像: `images/covers/{slug}.png` → GitHub raw URL で自動参照
- canonical_url は設定しない（JP と EN で言語が異なるため Zenn canonical は無意味）

詳細: `.claude/refs/translation-rules.md` と MEMORY.md の「クロスポスト・公開パイプライン」を参照。

---

## Related

- `~/.claude/skills/writing-ecosystem/SKILL.md` — global base（AI slop / Voice / タイトル原則）
- `~/.claude/agents/editor.md` — tech 記事レビュー（global）
- `~/.claude/agents/essay-reviewer.md` — idea 記事レビュー（global）
- `~/.claude/agents/fact-checker.md` — 事実検証（global）
- `.claude/agents/zenn-drafter.md` — Zenn 固有執筆エージェント（project）
- `.claude/agents/devto-translator.md` — Dev.to 翻訳・投稿（project）
- `.claude/rules/content-integrity.md` — Content Integrity 原則（project）
