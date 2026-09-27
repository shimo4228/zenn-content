# 記事執筆プラン: ローカル判断モデル第 3 ラウンド

## Context

前記事「文章を書かないモデル Jev のスキル選択は、0.3 秒で Opus にどこまで近づくか」（9/21 公開）で
Jev の hosted 判断が skill selection で Opus 天井の半分まで到達した。Jev 公開後 1 週間で 30 本超の
オープン再実装が出ており（systemonemodels.org）、読者の「じゃあローカルで動くのは？」に答える記事。

contemplative-agent の RFC-0043 第 3 ラウンドで qwen3:8b / kev-0.8b / Laya を 150 行で測り、
全候補が品質・レイテンシ・安定性のいずれかで脱落。RFC-0040 は blocked に戻った。

## Editorial brief

```
Reader: 前記事を読んで「ローカルの判断モデルで同じことをやれないか」と考えている
        engineer。Ollama は使える。Apple Silicon のノート PC を持っている。
        Jev の hosted API は試したが、クローズドなので本番には入れにくいと感じている
Channel: Zenn（articles/*.md）
Central thesis: Jev が 0.3 秒で解いた skill selection の判断をローカルで再現するには、
  重みだけでなく、較正された確率・prefix cache が効く注意機構・12,000 字の入力窓が要る
  — 2026 年 9 月の 3 候補はいずれも 1 つ以上欠いた
Entry bridge: Jev 公開 1 週間で 30 本超のオープン代替が出た。3 種を同じ 150 行で測って、
  何が足りないかを数字で切り分けた
First-screen deliverable: 結果の比較表（Jev / gemma / qwen3:8b / Laya / kev × 一致率 /
  レイテンシ / 安定性）
Figure plan: [内容 GO 後に埋める]
Causal spine:
  観察: Jev の hosted 判断は有効だがクローズド。オープン代替が一気に登場
  → 緊張: 3 候補を同じ 150 行のリプレイで測ったら、最善でも無作為に近い
  → 機序: 失敗の原因は 3 つに分かれる — 較正（Laya ECE 0.469）、
    注意機構（qwen3.5 hybrid → prefix cache 不成立、kev → MPS OOM）、
    入力長（kev 384 token 学習 vs 12,000 字 prompt）
  → 読者の判断: ローカル判断モデルを選ぶとき、重み公開だけでなく
    この 3 条件を確かめる。DecisionBackend seam は作ったので、
    条件を満たすモデルが出たら差し替えられる
Selected evidence:
  - C1: Jev の天井値（前記事との接続）
  - C8: qwen3.5 vs qwen3 の prefix cache（注意機構の実証）
  - C10-C11: qwen3:8b logits の latency（レイテンシ脱落）
  - C12-C16: Laya の Jaccard / AUC / ECE（品質・較正の実証）
  - C21-C24: kev の MPS OOM と分割 probe（安定性脱落）
  - C19: Laya の未較正警告（較正ギャップの物証）
  - C31: DecisionBackend seam（正の成果）
  - C30: gemma の baseline 数字（比較基準）
Out of scope:
  - Jev のアーキテクチャ推測（C37: 未検証）
  - C9: qwen3.5 hybrid 注意の原因詳細（推測）
  - swap 圧力の詳細分析（C28-C29: 再現条件が著者環境依存）
  - seam の実装詳細（ADR-0112 の内容。記事の命題を進めない）
  - Ollama の同居モデル挙動（C26: 未検証部分あり）
```

## 構成（節構成案）

発見の順で書く。台帳の時系列をそのまま並べない。

1. **冒頭（見出し前）**: 比較表（First-screen deliverable）+ 1 文の結論
2. **「30 本のオープン代替と 3 つの問い」**: Jev クローズド → 代替急増 →
   「重みがあればローカルで動くか？」→ 3 候補の選定理由（approaches: logits / typed-decisions / specialized）
3. **「150 行のリプレイで測る」**: 測定方法を最小限に（前記事の replay framework への back-ref、
   基準は opus 天井、指標は Jaccard / AUC / calibration）
4. **「qwen3:8b — prefix cache が効く代わりに」**: logits アプローチ。54 コール × 150 行の
   latency が 43-74 秒で問題外。qwen3.5 は hybrid 注意で cache 不成立→ qwen3 に替えても遅すぎ
5. **「Laya — 較正という名の壁」**: typed-decisions 専用モデル。Jaccard 0.075（無作為 0.056）、
   ECE 0.469。確率が 0.5-0.7 に集中して hit rate 10-14%。公表の T4 33ms vs Apple Silicon 39 秒
6. **「kev — 0.8B が 12 GB を食いつくす」**: MPS OOM。分割で凌いでも allocator が 17 行で詰まる。
   CUDA 専用カーネルの reference fallback
7. **「3 つの条件」**: 較正・注意機構・入力長の整理。DecisionBackend seam は作った。
   RFC-0040 の再開条件 3 つ
8. **関連リンク**: 前記事、systemonemodels.org、各モデルの repo

## レビュー計画

全レビュアーを **Opus 4.6**（`claude-opus-4-6`）で実行する（ユーザー指示）。

| # | フェーズ | コンポーネント | model 指定 |
|---|---------|---------------|-----------|
| 1 | 構造凍結 → channel review | `editor` agent | opus |
| 2 | 構造凍結 → 初見明瞭性 | `prose-clarity-reviewer` agent | opus |
| 3 | 構造凍結 → 事実検証 | `fact-checker` agent（台帳 path 付き） | opus |
| 4 | cross-model | `codex-review` skill | opus（同一モデルになるため cross の意味が薄い。実行して記録するが、blocking にしない） |
| 5 | 著者の内容 GO | 通読 | — |
| 6 | 図 | eli5 × 3-4 枚（内容 GO 後） | — |
| 7 | タイトル | `headline-craft` → `title-reviewer` | opus |
| 8 | 受け入れ | `quality-gate` | — |

fact-checker には以下を dispatch prompt に含める:
- 証拠台帳: `drafts/article-context_local-decision-models-round3_2026-09-22.md`
- 一次資料: `contemplative-agent/docs/evidence/rfc-0043/README.md`,
  `skillsel-arm-replay-round3-20260922.json`
- 外部 URL: systemonemodels.org, TypeSafe MCA, kev/Laya/von の GitHub

## スケジュール

- schedule.json は 9/22〜月末が空。前回 9/21 に 2 本出しているので、最短 9/24（水）09:00 JST
- EN 版: `devto-translator` → Dev.to。JP 公開後

## 検証

1. `npm run validate` — frontmatter 検証
2. `npm run evidence -- articles/<slug>.md` — deviations 0
3. `npm run evidence -- articles/<slug>.md --online` — 公開直前
4. brief の First-screen deliverable と Figure plan が本文と一致（人手）
5. `npm run generate:index` → `npm run check:index`
