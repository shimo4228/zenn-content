<!-- origin: original -->
# Translate Article Skill

**Purpose:** Zenn 記事を高品質な英語に翻訳し、Dev.to への投稿準備を行う。

> **Note:** 翻訳→タグ付け→投稿を一気通貫で行う場合は `devto-translator` エージェントが推奨。このスキルは手動翻訳やカスタマイズが必要な場合に使う。

---

## Usage

```
/translate-article articles/ARTICLE_NAME.md
```

引数なしの場合は `articles/` 内の記事一覧を表示し、対象を選択させる。

---

## Translation Flow

### Step 1: ソース記事の読み込み

記事を読み込み、構造を把握する:
- frontmatter（title, emoji, type, topics）
- 本文の構成（セクション数、コードブロック数）
- 使用されている技術用語

### Step 2: グロッサリーの読み込み

`docs/translation-glossary.json` を読み込み、用語の翻訳ルールを確認する。

### Step 3: 翻訳の実行

以下のルールに従って記事全体を英語に翻訳する。

#### 翻訳品質ガイドライン

**必須ルール:**
- コードブロック（```で囲まれた部分）は**絶対に翻訳しない**
- インラインコード（`backtick`）内も翻訳しない
- Markdown 構文（#, -, |, [], ![] 等）をそのまま保持
- frontmatter の構造を保持（title のみ翻訳）
- 画像リンク（`/images/xxx`）はそのまま保持
- グロッサリーの `never_translate` 用語はそのまま保持

**文体ルール:**
- 技術的で明快な英語（対象読者: ソフトウェアエンジニア）
- 直訳ではなく、英語として自然な表現にする
- 著者の個性と洞察を保持する
- 日本特有の文化的文脈は、英語圏の読者向けに簡潔に説明を補足する
- AI スロップ禁止: "powerful", "seamless", "revolutionary", "game-changer" は使わない
- 謙遜表現は英語の技術文書の慣習に合わせて調整する

**frontmatter の翻訳ルール:**
```yaml
---
title: "英語タイトル（原文の意味を保持、60文字以内）"
emoji: "📚"           # そのまま
type: "tech"           # そのまま
topics: ["claude", "ai", "automation"]  # 英語タグに変換
published: true        # そのまま
---
```

topics の変換例:
- "開発ツール" → "devtools"
- "チートシート" → "cheatsheet"
- "自動化" → "automation"
- "テスト" → "testing"
- "設計" → "architecture"

### Step 4: 品質チェック

翻訳完了後、以下を自己検証する:

1. **コードブロック完全性**: 原文と翻訳文のコードブロック数が一致するか
2. **リンク完全性**: すべてのURL、画像パスが保持されているか
3. **用語一貫性**: グロッサリーの用語が正しく使われているか
4. **AI スロップ**: 汎用的な AI 表現が混入していないか
5. **技術的正確性**: 技術用語が正しく翻訳されているか

### Step 5: 保存

翻訳結果を `articles-en/` ディレクトリに保存する。

```bash
# ディレクトリがなければ作成
mkdir -p articles-en

# 同じファイル名で保存
articles-en/ARTICLE_NAME.md
```

### Step 6: Dev.to クロスポスト提案

翻訳完了後、ユーザーに Dev.to への投稿を提案する:

```bash
# Dev.to dry-run
cd scripts && uv run python publish.py ../articles-en/ARTICLE_NAME.md \
  --platform devto \
  --dry-run
```

> **Note:** EN 記事には canonical_url を設定しない（言語が異なるため Zenn canonical は無意味）。

---

## Translation Prompt Template

記事の翻訳時に、以下のシステムプロンプトを内部的に使用する:

```
You are a professional technical translator specializing in Japanese→English
translation for software engineering articles.

Target audience: Software engineers who read Dev.to.

## Glossary
{glossary_json}

## Rules
1. Preserve ALL markdown syntax exactly
2. Do NOT translate content inside code blocks or inline code
3. Translate the frontmatter title; keep other metadata as-is
4. Convert Japanese topics to English equivalents
5. Adapt cultural context for English-speaking engineers
6. Use glossary terms consistently
7. NO AI slop: "powerful", "seamless", "revolutionary", "game-changer"
8. Maintain technical depth and author's voice
9. When Japanese concepts need context, add a brief parenthetical explanation

## Output
Provide ONLY the translated markdown. No preamble, no explanations.
```

---

## Error Recovery

| 問題 | 対応 |
|------|------|
| コードブロックが翻訳されてしまった | 原文からコードブロックを抽出して差し替え |
| 用語が不統一 | グロッサリーを参照して一括置換 |
| frontmatter が壊れた | 原文から frontmatter をコピーして title のみ翻訳 |
| 文体が硬すぎる | 「技術ブログ」のトーンで書き直し |

---

## Quick Reference

```
翻訳のみ:
  /translate-article articles/my-article.md

翻訳 + Dev.to 投稿:
  /translate-article articles/my-article.md
  → 翻訳後に publish.py --platform devto を実行

全記事の翻訳状況確認:
  ls articles/ articles-en/ で未翻訳記事を特定
```
