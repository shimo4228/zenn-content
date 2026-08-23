<!-- origin: original -->
# Zenn Writing Rules (プロジェクト overlay)

> このファイルは publishing チャンネル固有ルールの overlay。**声（voice）は type（tech/idea）でなく
> チャンネルで分岐する** — 分岐の実値は下の「チャンネル表」が唯一の正本。
>
> genre 中立 canon（AI slop 禁止・タイトル原則・ネタ 3 軸・craft 規約）は
> `~/.claude/skills/writing-ecosystem/SKILL.md` が正本で、**ここには再掲しない**。
> 本ファイルはチャンネル固有の事実・配線・罠のみを定義する。

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
- push 後、指定時刻まで公開されない
- **⚠ 予約登録自体がレートリミット（投稿数上限）に計上される**（2026-07-06 実測。上限中は「投稿数の上限に達したためデプロイされませんでした」で登録自体が拒否される）。公開予定日の **3 日以上前に push** し、Zenn の「デプロイ履歴」で登録成功を確認する。拒否されたら解除後に空コミット push で deploy を再トリガー

## Zenn 記法特有の注意

### `:::message` ブロック

- 刃牙リファレンス・ダミーデータの明示に使う（`zenn-idea-voice` skill 参照）

### 内部リンク

- **誤**: `/articles/xxx`（相対パスは Zenn 上で正しく解決されない）
- **正**: フル URL `https://zenn.dev/shimo4228/articles/xxx`

## チャンネル表（チャンネルの値を持つ唯一の場所）

**このセクションが、文体・声・レビュー agent の実値を持つ唯一の場所。** skill / agent /
CLAUDE.md はここを指すだけで、値を再掲しない。rules は main loop にも全 agent プロセスにも
常駐するので、どの skill が発火してもこの表は context にある（配置根拠は ADR-0010）。

| チャンネル | 置き場 | 文体 | 声 | 既定 skill | レビュー agent |
|---|---|---|---|---|---|
| **Zenn** | `articles/` | ですます | 実用軸（即実用・低認知負荷） | `zenn-practical-writing` | `editor` |
| **Dev.to** | `articles-en/` | 英語（`ja-to-en-translation` の voice 規約） | 同上 | `zenn-practical-writing` → `devto-translator` | `editor` |
| **note**（JA 正本・初出） | `note/` | **ですます** | 発見調 | `writing-ecosystem` | `essay-reviewer` |
| **Substack**（EN 翻訳） | `substack/` | 英語 | 発見調 | `ja-to-en-translation` | `essay-reviewer` |

- **日本語の公開チャンネルはすべて ですます**（2026-08-06 著者指示）。**だ/である で書く
  日本語チャンネルは存在しない** — 規約のない場（研究 repo 内の下書き等）だけが例外
- **type（tech/idea）でレビュアーを分けない**（2026-07 廃止）。分岐軸は上表のチャンネルのみ
- **1 記事内で文体を混在させない**
- 注: prose lint（textlint/markdownlint）は 2026-07 に全撤去。文体統一・表記・書式は機械検出でなく執筆時に守る（残る機械チェックは `zenn list:articles` の frontmatter 検証のみ）

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

### 投稿予約タイミング（日米ペアの既定・正本）

JP と EN は **JST でペア予約**する。EN を前夜に、JP を翌朝に出す。

- **JP (Zenn `published_at`)**: 当日 **09:00 JST**（バズタイム。上の「Zenn 投稿ペース方針」に従う）
- **EN (Dev.to `--at`)**: その **前日 22:00 JST**（例: JP `2026-07-08 09:00` → EN は `2026-07-07 22:00`）。22:00 JST ≈ 米国 **09:00 ET** で、Dev.to の US 午前ピークにも当たる
- コマンド: `devto_crosspost.py schedule <slug> --at "<前日> 22:00 Asia/Tokyo"`（tz→JST 換算されるので JST を明示して渡す）

詳細: `.claude/agents/devto-translator.md`（翻訳・タグ付け・投稿の手順を保持）と `.claude/refs/schedule-schema.md`（台帳スキーマ）。

---

## Related

- `~/.claude/skills/writing-ecosystem/SKILL.md` — genre 中立 canon（AI slop / craft / タイトル原則 / エッセイ 4 段構成）
- `.claude/skills/zenn-practical-writing/SKILL.md` — Zenn/Dev.to の実用軸（文体はチャンネル表が正本）
- `.claude/skills/zenn-idea-voice/SKILL.md` — 任意の personality flavor（毒humor / 刃牙。type 非依存の opt-in）
- `.claude/skills/zenn-format/SKILL.md` — frontmatter・記法の正本
- `~/.claude/agents/editor.md` — Zenn/Dev.to のレビュー（global。担当チャンネルはチャンネル表）
- `~/.claude/agents/essay-reviewer.md` — note/Substack エッセイのレビュー（global。同上）
- `~/.claude/agents/fact-checker.md` — 事実検証（global）
- `.claude/agents/zenn-clarity-reviewer.md` — 初見読者の明瞭性レビュー（project。Zenn/Dev.to 専用、FAIL は公開ブロック。学術論文は global `clarity-reviewer`）
- 記事執筆はサブエージェントに委譲せず、オーケストレーター本体が `zenn-practical-writing` に従って直接執筆する
- `.claude/agents/devto-translator.md` — Dev.to 翻訳・投稿（project）
- `.claude/rules/content-integrity.md` — Content Integrity 原則（project）
