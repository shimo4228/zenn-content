# 判断の経緯（Decision History）

zenn-content の執筆系で何を決め、なぜそうしたかの記録。1 件 1 ファイル、番号は連番、過去形で書く。
記録は書かれた日の判断で、現行は `.claude/rules/`・skills・agents・scripts と著者の今の指示が決める。旧記録の
Status 欄と日付つき注記もその日の状態。新しい判断は旧記録と衝突してよく、旧記録はそのまま置く。

| # | Title | Date |
|---|-------|------|
| [0001](0001-content-integrity-principle.md) | Content Integrity 原則 | 2026-04-13 |
| [0002](0002-writing-team-orchestration.md) | 執筆チームオーケストレーション | 2026-04-13 |
| [0003](0003-zenn-practical-channel-axis.md) | Zenn/Dev.to の実用軸チャンネルへの一本化 | 2026-07-05 |
| [0004](0004-zenn-clarity-reviewer-addition.md) | zenn-clarity-reviewer の追加 — 「新レビューエージェント禁止」の部分 supersede | 2026-07-27 |
| [0005](0005-post-publication-eval-loop.md) | 実測ベースの事後 Eval ループ — 予測型エンゲージメントレビュアーの不採用 | 2026-07-27 |
| [0006](0006-authorial-values-and-editorial-judgment-skills.md) | 著者の判断・価値観の 2 スキル正本化（values / editorial-judgment） | 2026-07-28 |
| [0007](0007-kaguura-writing-principles-intake.md) | 外部ライティング原則（Kaguura 2026）の優先取り込み — 引き込み構成への統合 | 2026-07-30 |
| [0008](0008-two-tier-eval-and-revision-loop.md) | 二本立て評価関数（テーマ / 記事品質）と改稿ループの導入 | 2026-08-12 |
| [0009](0009-readme-routing-page-and-generated-publications-index.md) | README をルーティングページにし、網羅一覧を生成索引 1 つへ集約する | 2026-08-18 |
| [0010](0010-channel-values-in-the-resident-layer.md) | チャンネルの値は常駐層に 1 箇所だけ置く | 2026-08-23 |
| [0011](0011-dismantle-the-eval-layer.md) | eval 層を解体し、テーマはレビュアーに戻す | 2026-08-23 |
| [0012](0012-zenn-review-deterministic-layer.md) | Zenn レビューの決定論層を evidence script へ降ろす | 2026-08-27 |
| [0013](0013-first-contact-read-on-codex.md) | 初見の読みを Codex に移し、cross-model review を兼ねさせる | 2026-09-27 |
| [0014](0014-writing-backbone-in-resident-rules.md) | 執筆の背骨を常駐 rule に置き、writing-ecosystem の細則を原理へ畳む | 2026-09-29 |
| [0015](0015-persona-read-loop-before-freeze.md) | Zenn 稿の構造凍結前に、記事ごとのペルソナ読みで見せ方を改稿するループを置く | 2026-10-09 |

## Template

新しい記録の節: Date / Context / Decision / Review-when / Alternatives Considered / Consequences。
Decision は過去形（何をしたかと理由）で書く。Review-when は任意で、無ければ「無し — 記録」と書く。
ファイル名は `NNNN-kebab-case-title.md`。
