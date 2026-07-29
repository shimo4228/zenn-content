# ADR-0007: 外部ライティング原則（Kaguura 2026）の優先取り込み

## Status

Accepted (2026-07-30)

## Context

Kaguura Gichuru "How I Got 20,585 Substack Subscribers in 90 Days"（The Write Path, 2026-07-05）が提示するライティング原則 — 文の技術（craft）・構成（Hero's Journey）・結果駆動タイトル・配信ファネル — は、既存の執筆規約群（writing-ecosystem / zenn-practical-writing / public-comment / substack-publishing）と大部分で整合するが、いくつかの点で真っ向から衝突していた。

著者の判断: **衝突する部分は記事の原則を優先し、虚心坦懐に取り組む**。既存規約側を改定する。

議論の中で確定した重要な整理: how-to 記事でも「一瞬で何が書いてあるかわかること」は重要だが、**この記事の軸に照らして引き込まないと何も始まらない** — つまり「一瞬でわかる」と「引き込み」は排他ではなく両立させる（記事タイプで構成を二分しない）。

## Decision

記事の原則を層別に既存規約へ取り込み、衝突点は記事優先で既存規約を改定する。

### 取り込み範囲

- **取り込む**: craft（単数の読者・強い動詞・能動態・平易語・10% 編集・スペーシング・密度 > 字数・Input エンジン）、構成（Hero's Journey 4 段 + warm-up 削除）、タイトル（結果駆動ヘッダー・A/B テスト）、配信（Notes 3 型・net-giver コメント・organic recommendations・welcome email・無駄時間チェックリスト）
- **除外**: 収益化（sec.5 ペイウォール回避・高チケットバックエンド）— global `authorship-strategy` skill の「マネタイズ禁止」原則と衝突するため、取り込むなら別の意思決定として切り離す

### 撤回・改定した既存規約

| 旧規約 | 新規約 |
|---|---|
| 「個人的エピソード始まりは離脱要因」（zenn-practical-writing の一律禁止） | 撤回。全記事の既定構成を「一瞬でわかる → 引き込み（掴み = 具体的シーン）→ 緊張 → 解決 → Higher Ground」に統合。禁止対象は warm-up fluff（読者に接続しない前置き）に精密化。壁の箇条書きは掴みの一実装に降格 |
| 「数字が主役のタイトル禁止」（writing-ecosystem Title Conventions） | 「空の listicle 数字禁止」に限定。実測の裏付けある具体的数字は scroll-stopper として推奨 |
| Title Conventions に結果駆動の概念なし | 基本ルールに「結果駆動」を追加。詩的・教科書的タイトルの禁止を明文化 |
| 「わかること」1 行 blockquote の必須化（zenn-practical-writing） | 同日の追加決定で撤回。機能要件「第一画面（タイトル + 掴み）で読後価値が伝わる」に降格し、装置は任意（結果駆動タイトルが主役。全記事同一の定型行は corpus レベルのテンプレ臭、掴みの前のメタ行は warm-up fluff） |

### 配置（正本の割り当て）

| 原則 | 正本 |
|---|---|
| Craft 規約・エッセイ 4 段構成・タイトル改定 | global `writing-ecosystem` |
| 結果駆動ヘッダー技法・A/B テスト | global `headline-craft` |
| Zenn 全記事の導入設計（引き込み） | project `zenn-practical-writing`「導入の設計」 |
| net-giver コメント哲学 | global `public-comment` |
| Substack 配信ファネル（Notes 3 型・recommendations 等） | global `substack-publishing` §7 |

### Content Integrity（ADR-0001）との整理

執筆時の構成設計（掴み・緊張・Higher Ground などの引き込み設計）は **Content 層の著者判断**であり、ADR-0001 が禁じる「完成稿の事後 catchify」とは別物。ADR-0001 の改定は不要（Notes に整理を追記）。

## Alternatives Considered

- **記事タイプで構成を分岐**（how-to は従来の BLUF・壁の箇条書き、essay のみ Hero's Journey）— 著者が棄却。「一瞬でわかる」は維持しつつ、引き込みがなければ how-to でも読み始まらない。Zenn もフィード流入があり、両立が正しい
- **収益化層も含めた全量取り込み** — authorship-strategy の「マネタイズ禁止」見直しという別スコープの意思決定になるため除外
- **既存規約優先（記事は参考情報どまり）** — 著者の明示指示（虚心坦懐に記事優先）に反するため不採用

## Consequences

- 過去記事の導入（壁の箇条書き型）は旧規約準拠のまま — 遡及改稿はしない（Content Integrity: 事後の作り替えはしない）
- `quality-gate` が参照する受け入れチェックリストの導入項目は「具体的シーンの掴み + 緊張 → 解決」に置き換わった
- 撤回した旧規約の文言（「個人的エピソード始まりは離脱要因」等）は skill 群から除去済み。今後のレビューエージェントが旧規約で FAIL を出したら、このADR を根拠に採否を決める
- 出典: [How I Got 20,585 Substack Subscribers in 90 Days](https://kaguura.substack.com/p/90-days-20585-new-subscribers-heres)
