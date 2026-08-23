# Architecture Decision Records

Design decisions for the zenn-content writing ecosystem. Each ADR records the
context, the decision, the alternatives considered, and the consequences.

| # | Title | Status | Date |
|---|-------|--------|------|
| [0001](0001-content-integrity-principle.md) | Content Integrity 原則 | Accepted | 2026-04-13 |
| [0002](0002-writing-team-orchestration.md) | 執筆チームオーケストレーション | Accepted | 2026-04-13 |
| [0003](0003-zenn-practical-channel-axis.md) | Zenn/Dev.to の実用軸チャンネルへの一本化 | Accepted | 2026-07-05 |
| [0004](0004-zenn-clarity-reviewer-addition.md) | zenn-clarity-reviewer の追加 — 「新レビューエージェント禁止」の部分 supersede | Accepted | 2026-07-27 |
| [0005](0005-post-publication-eval-loop.md) | 実測ベースの事後 Eval ループ — 予測型エンゲージメントレビュアーの不採用 | Accepted | 2026-07-27 |
| [0006](0006-authorial-values-and-editorial-judgment-skills.md) | 著者の判断・価値観の 2 スキル正本化（values / editorial-judgment） | Accepted | 2026-07-28 |
| [0007](0007-kaguura-writing-principles-intake.md) | 外部ライティング原則（Kaguura 2026）の優先取り込み — 引き込み構成への統合 | Accepted | 2026-07-30 |
| [0008](0008-two-tier-eval-and-revision-loop.md) | 二本立て評価関数（テーマ / 記事品質）と改稿ループの導入 | Accepted | 2026-08-12 |
| [0009](0009-readme-routing-page-and-generated-publications-index.md) | README をルーティングページにし、網羅一覧を生成索引 1 つへ集約する | Accepted | 2026-08-18 |
| [0010](0010-channel-values-in-the-resident-layer.md) | チャンネルの値は常駐層に 1 箇所だけ置く | Accepted | 2026-08-23 |

ADR-0003 partially supersedes ADR-0001 (zenn-writer row) and ADR-0002 §2
(`writing-standards.md` reference) — see its Consequences section.
ADR-0004 partially supersedes ADR-0002 §1 and ADR-0003 §5 (new-reviewer ban).
ADR-0010 partially supersedes ADR-0003 §2 (channel/文体 table) and ADR-0002 §2
(`translation-rules.md` reference) — both carry dated notes in place.
