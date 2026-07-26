# ADR-0004: zenn-clarity-reviewer の追加 — 「新レビューエージェント禁止」の部分 supersede

## Status

Accepted (2026-07-27)

本 ADR は ADR-0002 §1「新しいエージェントは作らない」および ADR-0003 §5「新しいレビューエージェントは作らない」を一部 supersede する。

## Context

Claude 5 世代の rules 棚卸し記事の公開前レビューで、既存チェーン（editor / fact-checker / codex-review）が拾えない不備が実地で露出した: 記事がハーネス内の造語・過去記事の文脈・編集過程の知識を前提にしており、フィードや検索から来た初見読者には冒頭数秒で伝わらない。editor の観点（構造・コード正確性・AI slop・用語一貫性）はこれと直交しており、「初見読者が最後まで追えるか」を検査するレビュアーが不在だった。

ADR-0003 §5 は「新しいレビューエージェントは作らない。実用軸の客観チェック項目は `quality-gate` の客観チェックリストに集約する」と定めていた。しかし初見読者明瞭性（造語予算・タイトル軸の貫通・内部文脈依存・一文テスト）は、runnable code や 図表 ≥1 のような機械検査可能な構造的性質ではなく、**意味理解を要する性質**であり、チェックリスト（code 側）では検査できない（global `rules/common/patterns.md` の Code vs LLM 判定）。

なお学術論文向けには同型の `clarity-reviewer` agent（global）が既に存在し、paper-ecosystem の 4 並列レビューで実績がある。本 agent はその Zenn/Dev.to 版である。

## Decision

1. **`zenn-clarity-reviewer` agent を project（`.claude/agents/`）に新設する**。観点は初見読者の明瞭性のみ（造語予算 / タイトル軸の貫通 / 編集メタ語り / 内部文脈依存 / 冒頭数秒理解 / 一文テスト / EN 版の translationese）。editor / fact-checker と観点が直交するため、writing-team Mission A/B の並列レビューブロックに 4 本目として追加する。
2. **ブロッキングゲートとする**。agent は PASS|FAIL の verdict を返し、`quality-gate` の必須条件に「verdict が PASS」を追加（editor CRITICAL 0 と同格）。FAIL のままの記事は公開できない。
3. **配置は project とする**。判定基準は global `rules/common/skills.md` の Knowledge Placement「Global vs Project」（本件を機に正本化 — global ADR-0025）: 2+ の repo / channel で使う資産は global、単一 platform / channel 固有は project overlay。本 agent は Zenn/Dev.to チャンネル専用（学術論文は global `clarity-reviewer` が担当し、両者は When-NOT-to-Use 節で相互に defer 済み）のため project が正しい。editor / fact-checker が global なのは複数チャンネル共有だからであり、基準は一貫している。

## Alternatives Considered

- **global `clarity-reviewer` を Zenn にも流用する** — 読者モデルが違う（論文: 分野は知るが companion repo を知らない読者 / Zenn: フィードから来たエンジニア）。基準の分岐を 1 agent に押し込むと両方の精度が落ちるため不採用。
- **quality-gate のチェックリストに項目追加（ADR-0003 §5 の路線維持）** — 意味的性質はチェックリストでは検査できない。「未説明概念なし」の既存項目が実際には効いていなかったのが今回の起点。不採用。
- **editor の観点に統合** — editor は既に 5 観点を持ち、観点を足すほど各観点の検出力が薄まる。paper-ecosystem が観点直交の並列レビュアー分割で成功している前例に従い不採用。

## Consequences

- writing-team Mission A/B のレビューは 4 本並列になる（editor / fact-checker / zenn-clarity-reviewer / codex-review）。レビュー時間はほぼ不変（並列）、トークンコストは agent 1 本分増。
- 公開ゲートが 1 条件増える（verdict PASS）。初見読者に伝わらない記事が editor PASS だけで公開される経路が塞がる。
- ADR-0002 §1 / ADR-0003 §5 の「新レビューエージェント禁止」は「機械検査できない直交観点が実地で露出した場合は agent 追加可（本 ADR が前例）」に緩和される。
- 参照更新箇所: `writing-team` / `quality-gate` / `publish-article` / `CLAUDE.md` / `rules/zenn-writing.md` / `docs/CODEMAPS/skills.md`
