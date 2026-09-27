# 執筆プラン: 「memory RAG の前に ADR を」(rag-to-adr)

## Context

前セッション（contemplative-agent 7d4ce77d、2026-08-05）で A/B 実測と RAG/ADR 議論を行い、証拠台帳 `drafts/article-context_rag-to-adr_2026-08-05.md` が収集済み。中心主張はユーザー自身の発言として判断記録に固定されている:「メモリー RAG やグラフ RAG をする人は素直に ADR を試してほしい。大部分の問題が解決すると思う」。本プランは /grill-me（2026-08-05、本セッション）で収束した編集判断に基づく。執筆は台帳 + 索引されたセッションログのみを入力とし、台帳に無い記憶に頼らない。

## Grill で確定した編集判断

1. **対象**: rag-to-adr を先に書き切る。姉妹台帳（demo-vs-production-agent）は後続。
2. **主読者**: memory RAG / グラフ RAG の**既実装者**（乗り換え判断の材料を渡す）。これから選ぶ人は副読者として自然に拾う。
3. **主張範囲 — 判定基準で限定**:「LLM が読める規模の agent memory × frontier 級 LLM なら、検索（RAG）より読ませる方が勝つ」。境界の外側を明示する:
   - 大規模コーパス（LLM が読めない規模）
   - 曖昧想起（キーワードでヒットしない類似検索）
   - 弱いローカル LLM（C12: gemma4:e4b のコールド prefill 6.3〜7.1 ms/tok — 「読ませて判断」が払えない）
   - **自分自身が境界の外側で embedding を使っている事実（contemplative-agent ADR-0019）を隠さず境界実例として書く**
4. **「書き込み規律コストへの付け替え」反論への 2 段応答**:
   - (1) 規律は人間でなく agent が担う — Claude Code auto-memory（C1: plain .md 89 件 + 索引、frontmatter description、[[リンク]]、embedding 資産ゼロ）が実例
   - (2) 読み書き非対称性 — 書き込みは低頻度、読み出し時の関連性判断は毎回。RAG はその毎回の判断を弱い凍結判定者（embedding）に前倒し代行させる設計。コストを低頻度側へ移すのは付け替えでなく正しい側への移動
5. **シリーズ**: `articles/small-llm-by-choice.md`（ハブ）に**緩い所属**。タイトル・冒頭には出さない。記事末でハブへリンク + ハブ側の「このシリーズで扱う技術的な中身」節にリンク追加。境界実例（弱い LLM だから embedding）の節でハブ記事を根拠として内部リンク（フル URL 必須）。
6. **導入の掴み**: 保留 — 執筆時に `zenn-editorial-judgment` Phase 0 で決定（候補: Claude Code にベクトル無し / 実測数字 / 主張断言）。
7. **公開日**: 保留 — 書いてから決定。制約: JP 火水 09:00 JST、EN 前日 22:00 JST、push は公開 3 日以上前 + Zenn デプロイ履歴確認。

## ⚠ 未検証クレームの扱い（執筆前ゲート）

- **C10（agentic search 採用）**: 一次ソース特定済み（plan mode 中の WebSearch/WebFetch、2026-08-05）。**Anthropic 公式ブログではなく Boris Cherny（Claude Code 作者）の Hacker News コメント（item 43164253）+ X ポスト**（逐語: "Early versions of Claude Code used RAG + a local vector db, but we found pretty quickly that agentic search generally works better."）。執筆時に HN スレッドを直接 WebFetch して逐語確認し、「作者本人の発言」として正確に帰属させる。「公式見解」とは書かない。
- **C9（stocktake の embedding→LLM grouping 転換）**: contemplative-agent repo で `git log --grep="stocktake"`（2026-05-30 頃）+ ADR 本文確認。特定できなければ記事から落とす。
- **C11（memory 書式仕様）**: 公式 docs を確認し、未文書なら「観察された挙動」と明示して書く。
- **「RAG 幻覚の主因は矛盾チャンク同居」の一般論**: 無出典。外部文献が見つからなければ使わない。
- C5（ADR-0019）の分業定式は本文パラフレーズ注意 — 引用時は ADR 本文を直接読む。

## 執筆手順

1. **⚠ クレーム検証**（上記ゲート）— C10 逐語確認、C9 特定、C11 公式 docs 確認
2. **Phase 0**: `zenn-editorial-judgment` でタイプ判定 + 導入の掴み決定 → 構成案
3. **執筆**: `zenn-practical-writing` に従い本体（オーケストレーター直接執筆、サブエージェント委譲禁止）。新規ファイル `articles/<slug>.md`（slug は執筆時決定）。ですます調。frontmatter は `zenn-format` 準拠、`published: false` で開始。内部リンクはフル URL。数値は全て台帳の Claims Register の tier 一次のみ使用（C2 prefill 38.85s→0.061〜0.064s、C3 本番 p50 56.1s vs 28.3s は「選別側が遅い」方向を取り違えないこと、C8 の prompt_eval_count 罠は補強材）
4. **ハブ更新**: `articles/small-llm-by-choice.md` のシリーズ節に新記事リンクを追加
5. **レビュー（並列）**: editor + fact-checker + zenn-clarity-reviewer（FAIL は公開ブロック）+ codex-review
6. **タイトル確定**: `/seo-optimizer`（headline-craft 経由、50 字以内）。英訳より前に確定
7. **人間ゲート**: ユーザーの内容確認を取ってから published 化（自動公開しない）
8. **英訳・予約**: devto-translator で `articles-en/` + `schedule.json` 更新、公開日はここで質問して確定
9. **commit + push 催促**（未 push だと予約が反映されない）

## 成功基準

- 全レビューゲート通過（zenn-clarity-reviewer PASS 必須）+ fact-checker で Claims Register 12 件が ACCURATE
- 中心主張が「判定基準」として読者が自分のケースに適用できる形になっている（挑発でなく基準）
- 実測パフォーマンスは月次 `/article-stocktake` で追跡（repo 既定）

## Verification

- `npm run validate`（frontmatter 検証）
- `npm run preview` で表示確認
- push 後 Zenn デプロイ履歴で予約登録成功を確認（レートリミット拒否の検知）
