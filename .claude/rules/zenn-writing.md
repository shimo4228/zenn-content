<!-- origin: original -->
# Zenn Writing Rules (プロジェクト overlay)

> このファイルは Zenn/Dev.to プラットフォーム固有ルールの overlay。記事の**声（voice）は type（tech/idea）で分岐しない**:
> - **Zenn/Dev.to の全記事** → `.claude/skills/zenn-practical-writing/SKILL.md`（実用軸：ですます・即実用・実コード/図・低認知負荷）が既定
> - 任意の personality flavor → `.claude/skills/zenn-idea-voice/SKILL.md`（毒humor / 刃牙。type 非依存の opt-in）
> - genre 中立 canon（AI slop 禁止・タイトル原則・ネタ 3 軸）は `~/.claude/skills/writing-ecosystem/SKILL.md` が正本
> - genuine な思索エッセイ（だ/である × 発見調）は Zenn ではなく Substack corpus へ（`writing-ecosystem` skill）
>
> global base の AI slop 禁止リスト・タイトル原則は **再掲しない**。本ファイルは Zenn プラットフォーム固有ルールのみを定義する。

## タイトル文字数上限

- **50 文字以内**（Zenn UI で切れずに表示される目安）
- 概念を正確に伝えるために必要な場合は **60 文字まで許容**
- 基本原則（煽り禁止・問いの形 OK など）は writing-ecosystem skill の Title Conventions を参照

## Zenn Frontmatter 規約

基本フィールド（title/emoji/type/topics/published）の正本は [zenn-format](../skills/zenn-format/SKILL.md)。本節は Zenn 固有の追加フィールド `published_at`（予約投稿）のみを定義する。

```yaml
published_at: 2026-04-15 07:00  # JST、予約投稿
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
- 刃牙リファレンス・ダミーデータの明示にも使う（`zenn-idea-voice` skill 参照）

### 内部リンク

- **誤**: `/articles/xxx`（textlint の no-dead-link がローカルファイル扱いしてエラー）
- **正**: フル URL `https://zenn.dev/shimo4228/articles/xxx`

### 文体（channel で分ける。type では分けない）

- **Zenn/Dev.to の全記事**: ですます調（正本 `zenn-practical-writing`。tech/idea で分岐しない）
- **Substack essay corpus**: だ/である × 発見調（正本 `writing-ecosystem`。Zenn には出さない別 channel）
- **1 記事内で文体を混在させない**
- 注: textlint の `no-mix-dearu-desumasu` は preset-ja-technical-writing 廃止（2026-04-29）で無効。文体統一は機械検出でなく執筆時に守る

## 生ログ・素材の置き場所

- AI 対話などの**生ログ**は `articles/_context/{slug}-{source}-log.md` に置く（Zenn の同期対象外。`articles/` 直下でないため公開されない）
- 執筆前の構造化コンテキストは `drafts/article-context_<topic>-<date>.md`（素材集めフローの正本は `zenn-practical-writing` skill）

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

## Zenn 投稿ペース方針（投稿タイミングの正本）

> 投稿ペース・バズタイムは**このセクションを正本**とする。他スキル（`schedule-publish` / `publish-article` / `refs/schedule-schema.md`）はここを参照し、値を再掲しない。

- **週 2-3 本ペース**（毎日投稿は 2026/3 の Zenn AI コンテンツ乱造対策で凍結リスクあり）
- **バズタイム: 火〜水 7:00-9:00（JST）** に集中。他の日は執筆期間
- 背景: Zenn は投稿上限がユーザーごとに設定され、高頻度投稿は凍結リスク。書き溜め→分散投稿のストック型で 1 本の密度を上げる

## Dev.to クロスポスト規約（EN 記事）

- `description:` を frontmatter に含める（Dev.to API の description フィールドに渡される）
- `topics:` は YAML リスト、`tags:` はカンマ区切り文字列の両方を parser が読む
- カバー画像: `images/covers/{slug}.png` → GitHub raw URL で自動参照
- canonical_url は設定しない（JP と EN で言語が異なるため Zenn canonical は無意味）

詳細: `.claude/refs/translation-rules.md` を参照（クロスポスト・公開パイプラインの手順）。

---

## Related

- `~/.claude/skills/writing-ecosystem/SKILL.md` — global base（AI slop / essay Voice / タイトル原則）
- `.claude/skills/zenn-practical-writing/SKILL.md` — Zenn/Dev.to 全記事の既定の声（実用軸。type で分岐しない）
- `.claude/skills/zenn-idea-voice/SKILL.md` — idea/opinion の opt-in personality（毒humor / 刃牙）
- `.claude/skills/zenn-format/SKILL.md` — frontmatter・記法の正本
- `~/.claude/agents/editor.md` — Zenn/Dev.to 全記事のレビュー（global、type 分岐なし）
- `~/.claude/agents/essay-reviewer.md` — Substack essay corpus 専用（global。Zenn/Dev.to では使わない）
- `~/.claude/agents/fact-checker.md` — 事実検証（global）
- 記事執筆はサブエージェントに委譲せず、オーケストレーター本体が `zenn-practical-writing` に従って直接執筆する
- `.claude/agents/devto-translator.md` — Dev.to 翻訳・投稿（project）
- `.claude/rules/content-integrity.md` — Content Integrity 原則（project）
