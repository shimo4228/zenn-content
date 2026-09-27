# Zenn 記事計画: LLM-as-judge はスコアを集計しない

## Context

LLM-as-judge の評価設計で、著者は初期（skill-stocktake / learn-eval の設計過程）から
ルーブリックの数値スコアを採らず「二値チェック＝証拠、判定＝ホリスティック verdict」方式を
採用してきた。後発の論文（BinEval "Ask, Don't Judge" 等）がこの選択を裏付け、スキル側の
References に編入済み。この設計判断と実運用の証拠を、読者が自分の judge 設計に今日
適用できる実用パターン記事として Zenn に公開する。

/grill-me インタビューで確定した決定（すべてユーザー承認済み）:

| 決定点 | 結論 |
|---|---|
| 核の主張 | **実用パターン軸**: 「LLM-as-judge にルーブリックスコアを使うな。二値チェックで証拠を集め、判定はホリスティックな verdict で出させる」 |
| スコープ | 二値スクリーン + **反証プレッシャーテスト** + 名前付き verdict 設計まで。aggregate cost は脚注 |
| 論文の深度 | **limitations まで読む**: BinEval 自身の limitations（過剰分解はホリスティック品質次元で相関劣化）を逆読みの根拠に使う |
| AKC 素材 | **原則 + 転記ミス事件**: Evaluation scales with model capability 原則を紹介し、Promote トリガー数値閾値の転記ミス→無言変異（places→times）事件を「数値は複製中に意味が壊れる」実例として 3-4 文で添える |
| コード例 | **実物断片 + 汎用テンプレ**: skill-stocktake / learn-eval の実物断片 + 読者移植用の汎用 judge プロンプト構造（verdict enum + 証拠配列の JSON 出力例） |
| タイトル | **設計原則型**: 「LLM-as-judge はスコアを集計しない — チェックは証拠、判定はホリスティック」系（50 字以内、執筆時に磨く） |

## 種別と chain（planning.md Writing Chain）

- 種別: `writing` / doc 分類: 記事 → orchestrator は `writing-ecosystem`（voice は `zenn-practical-writing` 実用軸・ですます調）
- 執筆はサブエージェント委譲せず本体が直接書く（プロジェクト CLAUDE.md 規約）
- Parallel Group 1: [editor, fact-checker, codex-review(prompt-driven)] — ドラフト完成後に並列
- Sequential: 修正 → 人間 gate（ユーザーの記事内容確認）→ 予約設定 → commit → push 促し → EN 翻訳（devto-translator）
- 早期停止: MAJOR ISSUES / ❌ INACCURATE → 停止して報告

## 素材（一次ソース、全て確認済み）

1. **skill-stocktake** `~/.claude/skills/skill-stocktake/SKILL.md`
   - L14-24: 設計ノート（1M context 時代にバッチ分割は有害 → 全件単一 context のホリスティック評価）
   - L75-117: Phase 2 二段設計 — Stage 1 二値スクリーン（No のみ表面化）→ Stage 2 反証プレッシャーテスト（非 Keep 候補のみ、draft verdict を叩く動的質問 1-3 個）
   - L104-106: 「holistic judgment, not a numeric rubric — satisfaction ratio は単一の致命的 No を薄める」
   - L199-206: References（BinEval / CheckEval / TICK、スコア不採用の理由）
2. **learn-eval** `~/.claude/skills/learn-eval/SKILL.md`
   - L56-104: 同型の二層設計（checklist + holistic verdict、集計禁止、No を verdict の根拠に必ず列挙）
   - L168-174: References（+ FActScore, UniEval）
   - 非対称の設計: learn-eval は N=1 ドラフトに無条件で動的質問生成 / skill-stocktake はライブラリ規模なので非 Keep のみ — 「同じ原則、規模で運用が変わる」素材
3. **AKC** `~/MyAI_Lab/agent-knowledge-cycle/`
   - Design Principle #5「Evaluation scales with model capability」（ADR-0010 L47 に列挙、llms-full.txt L24）
   - 転記ミス事件: CHANGELOG v2.2.0 (2026-06-06) Fixed 節。2026-03-29 rules 化初稿で「3+ places」数値閾値が混入 → README phase 表複製時に「3+ times」へ無言変異 → ホリスティック判定に復元。git 証拠: `6ac29e2`（混入）/ `81692fa`（復元）
   - ADR-0008 judge パターン: 「LLM は code が用意した名前付き選択肢から選ぶ、実行は code」— verdict enum 設計の理論的裏付け
4. **verdict の実例**: Keep/Improve/Update/Retire/Merge（stocktake）、Save/Improve/Merge/Drop（learn-eval）

## 執筆ステップ

1. **素材ファイル作成**: `drafts/article-context_llm-judge-checks-2026-07-13.md` に上記ソース断片を出典付きで集約（zenn-writing rules の素材置き場規約）
2. **ドラフト執筆**: `articles/llm-judge-checks-not-scores.md`（slug 仮）
   - 構成案: 読者の問題（judge のスコアが不安定/判定が信用できない）→ パターン提示（チェック=証拠・verdict=ホリスティック・集計禁止）→ 反証プレッシャーテスト → 汎用テンプレ（JSON 出力例）→ 実運用実例（stocktake/learn-eval 断片）→ なぜスコアでないか（AKC 原則 + 転記ミス事件 + BinEval limitations 逆読み）→ まとめ
   - frontmatter: `type: tech`、emoji/topics は zenn-format に従い執筆時決定
   - 関連リンク節: AKC repo・skill repo（公開版 URL 要確認）+ **著者ハブ github.com/shimo4228 必須**
3. **並列レビュー**: editor + fact-checker + codex-review（prompt-driven）
   - fact-check 重点: BinEval arXiv:2606.27226 の主張と limitations の記述、CheckEval/TICK の位置づけ、AKC CHANGELOG 引用の正確性
4. **修正 → ユーザー確認（人間 gate）**
5. **公開設定**: `published: true` + `published_at: 2026-07-21 09:00`（火曜バズ枠。今週は 7/13・7/14 で埋まっているため翌週）。**7/17 までに push**（レートリミット 3 日ルール）
6. **EN 翻訳**: devto-translator で `articles-en/` 作成 → `devto_crosspost.py schedule <slug> --at "2026-07-20 22:00 Asia/Tokyo"` → schedule.json 更新
7. **commit → ユーザーに push を促す**（CRITICAL 規約）

## Verify（writing 版）

- `npm run validate`（frontmatter 検証）
- fact-checker verdict の出典編入確認
- `git status` — 意図しないファイルなし
- 人間 gate: 公開前 diff 承認

## 外部調査（Phase 0 相当）

writing 種別のため Chain Matrix の Phase 0 は非該当。ただし fact-checker が
論文 3 本（arXiv:2606.27226 / 2403.18771 / 2410.03608）を Web 検証する。
既存 Zenn 記事に同テーマなし（articles/ 全件確認済み、重複なし）。
