# LLM-as-judge 記事の執筆再開プラン（前段記事を踏まえた再構成版）

## Context

「LLM-as-judge はスコアを集計しない」記事は grill-me で 6 決定確定済み・単一コンテキスト希釈検証も完了済み。
計画正本: `drafts/article-plan_llm-judge-checks-not-scores_2026-07-13.md`、検証レポート: `drafts/verification_single-context-dilution_2026-07-13.md`。

**ユーザー指示による再構成**: 公開済み記事
[skill-stocktake-design-journey](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey)
（「AI の苦手な仕事をスクリプトに逃がす」）が**前段**になる。この記事は既に以下をカバー済み:

- V1→V4 の設計経緯: 6 次元ルーブリック廃止 → 「チェックリストで確認を強制、判定は AI のホリスティック判断」
- ルーブリックが AI に合わない理由（次元間相関 r>0.7、中心傾向バイアス、「AI は最初から判定を知っている」）
- 分業原則: 機械的処理はスクリプトに、品質判断は AI に
- AI の出力は外部入力として検証する（Danger Model）

## 再構成方針（前段との役割分担）

新記事は**続編**。重複を避け、以下の分担にする:

| 内容 | 置き場所 |
|---|---|
| ルーブリック廃止の経緯・理由（V1→V4） | 前段記事（リンクで委譲、再説明は 2-3 文の要約まで) |
| judge パターンの一般化（チェック=証拠 / verdict=ホリスティック / 集計禁止） | **新記事の核** |
| 反証プレッシャーテスト + verdict enum + 証拠配列 JSON テンプレ | 新記事（前段では未登場） |
| 論文裏付け（BinEval / CheckEval / TICK、limitations 逆読み） | 新記事（前段は経験則のみだった → 後発論文が裏付けた、という接続） |
| 単一コンテキスト希釈検証 → v3.0 ハイブリッド出荷 | 新記事の新エピソード。前段の分業原則の一歩先: **「検証の所有権」も code に降ろす**（決定論プリパス） |
| AKC 転記ミス事件（数値は複製中に意味が壊れる） | 新記事 |

続編としての物語軸: 前段は「Phase 1（インベントリ）を code に降ろした」話。新記事は
「Phase 2（判断）の内側にも code に降ろすべき決定論部分が隠れていた」ことを自分の検証で発見し、
当日 v3.0 を出荷した話。分業境界が 1 段深くなった、という進行。

## 構成案（再構成後）

1. 読者の問題: judge のスコアが不安定・判定が信用できない
2. 前段の要約 2-3 文 + フル URL リンク（スコア→チェックリスト化の経緯はそちらへ）
3. パターン提示: 二値チェック=証拠、判定=ホリスティック verdict、集計禁止
4. 反証プレッシャーテスト（draft verdict を動的質問で叩く）
5. 汎用テンプレ: verdict enum + 証拠配列の JSON 出力例（読者移植用）
6. 実運用実例: skill-stocktake / learn-eval 断片（同じ原則、規模で運用が変わる非対称）
7. **新設節「単一コンテキストは精度が落ちないのか」**: 検証レポート結論 4 点を骨子に
   （per-item 希釈は実在 16% / セットレベル判定は落ちない / 最大の教訓は検証の所有権 / v3.0 ハイブリッド）
8. なぜスコアでないか: BinEval limitations 逆読み + AKC 原則 #5 + 転記ミス事件（git 証拠 `6ac29e2`→`81692fa`）
9. まとめ

## 前提確認済み（このセッション）

- skill-stocktake SKILL.md は v3.0 化済み（Design note L19-、holistic L119、References L247-254 付近）。旧計画の行番号は素材収集時に現行で取り直す
- schedule.json に llm-judge エントリなし、articles/ に同テーマ記事なし
- 文体注意: 前段記事は だ/である調（旧規約）、新記事は ですます調（zenn-practical-writing 現行規約）。遡及変更しない

## 実行ステップ

1. **素材ファイル作成**: `drafts/article-context_llm-judge-checks-2026-07-13.md` — skill-stocktake v3.0（現行行番号）/ learn-eval / AKC / 検証レポート結論 4 点 / 前段記事の被リンク箇所を出典付き集約
2. **ドラフト執筆**: `articles/llm-judge-checks-not-scores.md` — 本体が直接執筆（サブエージェント委譲禁止）、`type: tech`、タイトル 50 字以内・設計原則型、関連リンクに前段記事 + AKC repo + skill repo + **著者ハブ github.com/shimo4228 必須**
3. **並列レビュー**: editor + fact-checker + codex-review（prompt-driven）
   - fact-check 重点: BinEval arXiv:2606.27226 / CheckEval 2403.18771 / TICK 2410.03608、AKC CHANGELOG 引用、前段記事との整合
   - 早期停止: MAJOR ISSUES / ❌ INACCURATE → 停止して報告
4. **修正 → 人間 gate**(ユーザーの記事内容確認。自動で published: true にしない)
5. **公開設定**: `published: true` + `published_at: 2026-07-21 09:00`（火曜バズ枠、7/17 までに push）
6. **EN 翻訳**: devto-translator → `devto_crosspost.py schedule llm-judge-checks-not-scores --at "2026-07-20 22:00 Asia/Tokyo"` → schedule.json 更新
7. **commit → ユーザーに push を促す**（CRITICAL 規約）

## Verify（writing 版）

- `npm run validate`（frontmatter 検証）
- fact-checker verdict の出典編入確認
- `git status` — 意図しないファイル混入なし（作業ツリーに前セッション由来の未コミット変更あり: zenn-writing.md / zenn-practical-writing SKILL.md / schedule.json。記事コミットに混ぜない）
- 人間 gate: 公開・push 前の diff 承認
