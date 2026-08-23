# ADR-0002: 執筆チームオーケストレーション

## Status

Accepted (2026-04-13)

## Context

執筆チームのコンポーネント（エージェント5、スキル8）を段階的に構築してきた結果、以下の問題が蓄積した。

### 矛盾（監査で12件検出）

代表例:
- **タイトル文字数**: zenn-writer（50文字）、zenn-drafter（60文字）、zenn-format（50-60文字）で不一致
- **感情語**: zenn-writer は禁止、catchify は冒頭で推奨
- **数字の使用**: 「数字が主役にしない」（zenn-writer）〜「no numbers」（zenn-drafter）のスペクトラム
- **セクション長**: 30% ハードルール（zenn-drafter）vs 重要度に比例（essay-reviewer）

### 重複（8件）

- AI slop 禁止リスト: zenn-drafter, editor, essay-reviewer に同一リストがコピペ
- トーンルール: zenn-writer, zenn-drafter, essay-reviewer で同一内容
- 翻訳ルール・品質チェック: translate-article と devto-translator で逐語的重複

### 責務の曖昧さ（4件）

- **翻訳の所有者**: translate-article (skill), devto-translator (agent), publish-article (skill) の3者が翻訳に言及
- **schedule.json スキーマ**: devto-translator と schedule-publish で互換性のないスキーマを定義
- **canonical_url**: schedule-publish は EN 記事に設定、translate-article は設定しないと明記

### オーケストレーション不在

各コンポーネントの接続をユーザーが手動で行っている。zenn-drafter は「次は editor でレビューを」と伝えるが、実際の起動はユーザー任せ。

### 欠落（12件、重要なもの）

- 執筆前の ideation 支援なし
- シリーズ記事の整合性チェックなし
- 全パス（新規・改稿・翻訳）共通の品質基準なし
- fact-checker が必須化されていない（idea 記事でも任意）

## Decision

### 1. Claude Code 本体をオーケストレーター（PM）とする

新しいエージェントは作らない。`writing-team` スキルで Claude Code にミッション種別の判定とチーム編成のテンプレートを提供する。

**理由**: オーケストレーターは「判断と指揮」を行う。Claude Code 本体がすでにその能力を持っており、別エージェントにすると文脈の断絶が起きる。

### 2. 共有リファレンス（`.claude/refs/`）で DRY 化する

散在するルールを `.claude/refs/` に集約し、各エージェント・スキルから参照する。

| リファレンス | 集約内容 |
|------------|---------|
| ~~`writing-standards.md`~~ | ADR-0003 で無効化（ファイルは存在せず、canon は global `writing-ecosystem` skill へ移行済み） |
| ~~`translation-rules.md`~~ | 2026-08-23 に `devto-translator` agent へ吸収・退役（消費者が agent 1 つだけで、正本を外に置いたため逐語重複が発生していた）。汎用の JA→EN 手順は global `ja-to-en-translation` skill |
| `schedule-schema.md` | schedule.json の統一スキーマ、フィールド定義、状態遷移 |

**理由**: エージェントは自分の定義ファイルしか読まないため、参照先の内容をインライン展開する仕組みが要る。各エージェント・スキルには「詳細は refs/X を参照」と記載し、Claude Code（オーケストレーター）が必要に応じて refs/ を読んでエージェントに渡す。

### 3. 責務を明確に1つのコンポーネントに割り当てる

| 責務 | 所有者 | 理由 |
|------|-------|------|
| 翻訳ワークフロー | **devto-translator** (agent) | translate-article 自身が推奨。一気通貫の実行能力がある |
| schedule.json スキーマ | **refs/schedule-schema.md** | 中立的な正本。どのコンポーネントからも参照 |
| canonical_url 方針 | **refs/schedule-schema.md** | EN 記事には設定しない（言語が異なるため） |
| 品質基準 | **quality-gate** (新規 skill) | 全パス共通の品質チェックリスト |

### 4. 廃止・変更は ADR-0001 の Content Integrity 原則に基づく

catchify の廃止、seo-optimizer のスコープ縮小は ADR-0001 で決定済み。本 ADR は構造的な理由による変更（translate-article の重複廃止など）をカバーする。

## Consequences

### 新規作成

- `docs/adr/` — ADR ディレクトリ（このプロジェクト初）
- ~~`.claude/refs/writing-standards.md`~~ — 存在しない。正本は global `writing-ecosystem` skill（ADR-0003 で無効化）
- ~~`.claude/refs/translation-rules.md`~~ — 2026-08-23 に `devto-translator` agent へ吸収・退役
- `.claude/refs/schedule-schema.md`
- `.claude/skills/writing-team/SKILL.md` — オーケストレーター
- `.claude/skills/ideation/SKILL.md` — テーマ検討
- ~~`.claude/skills/series-checker/SKILL.md`~~ — 2026-08-23 に `zenn-editorial-judgment`「シリーズ記事の整合」へ吸収・退役
- `.claude/skills/quality-gate/SKILL.md` — 統一品質基準
- `.claude/rules/content-integrity.md` — Content Integrity ルール

### 廃止

- `.claude/skills/catchify/` — ADR-0001 による
- `.claude/skills/translate-article/` — devto-translator と完全重複

### 変更（refs/ 参照化 + 矛盾解消）

- `.claude/agents/zenn-drafter.md`
- `.claude/agents/editor.md`
- `.claude/agents/essay-reviewer.md`
- `.claude/agents/devto-translator.md`
- `.claude/skills/seo-optimizer/SKILL.md`
- `.claude/skills/publish-article/SKILL.md`
- `.claude/skills/schedule-publish/SKILL.md`
- `.claude/skills/zenn-format/SKILL.md`
- `CLAUDE.md`
- `docs/RUNBOOK.md`

## Notes

- refs/ はエージェントが直接読めない。Claude Code（オーケストレーター）がエージェント起動時にコンテキストとして渡す、または各エージェント定義内に要点を残し「正本は refs/」と明記する二段構えで運用
- この再設計は1回のセッションで完了する規模。ただし Mission A（新規記事1本の通し実行）で検証してから完了とする
