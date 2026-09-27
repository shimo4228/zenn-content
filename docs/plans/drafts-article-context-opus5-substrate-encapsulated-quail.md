# Zenn 記事執筆計画: Claude 5 世代の自作 rules 照合・棚卸し手順

## Context

2026-07-24 の Opus 5 ローンチと同時に Anthropic が公式に「context engineering の新ルール」を公開し（Thariq 記事、C1-C4）、旧世代向けに書いた自作 rules が公式の前提と衝突・ドリフトする状況が生まれた。著者は自分の `~/.claude` ハーネスで rules rightsize（照合→退役/反転/保持）を実施済みで、その証拠台帳が `drafts/article-context_opus5-substrate-conflict_2026-07-26.md` にある。この台帳から Zenn 記事（JP + EN Dev.to クロスポスト）を作る。

**速報性重視**（ユーザー判断）: 今日中に執筆→レビュー→push まで完了し、JP 7/27（日）09:00 公開。

## grill-me で確定した編集判断

| 項目 | 決定 |
|---|---|
| フレーム | **照合手順の how-to**。「公式の前提が変わったのに自作 rules が古いまま常駐している」読者が、照合手順と判定枠を持ち帰る。因果（競合を止めたから改善）は主張しない — 設定ドリフトの実例として書く（codex P1-2 準拠） |
| 骨格 | **Step ドリブン**。前提の表 1 枚 → Step 1 採取 → Step 2 突合 → Step 3 判定枠で処分 → 落とし穴 |
| C13（trailer のモデル依存観測） | `:::details` に格納。限界（統制比較でない自然観察・実害ゼロ）を明記 |
| タイトル方向 | **「ルールの書き方が公式に変わった」ことが伝わる形**。候補:「Claude 5 世代でルールの書き方は公式に変わった——自作 rules の棚卸し手順」（50 字以内で微調整） |
| 公開日 | JP **2026-07-27（日）09:00** / EN 目標 **07-26 22:00**（間に合わなければ 07-27 22:00） |
| 触れないこと | 過去記事との矛盾・セキュリティ層再編（T-006/ADR-0020）・human-gate 第 2 軸（ADR-0019）— 別記事素材として温存 |

## 記事構成（本文の設計）

- slug: `claude5-rules-official-shift-audit`（`articles/` に新規作成。emoji/topics は zenn-format に従い執筆時決定）
- 冒頭: 「この記事でわかること」1 行 + 読者の壁（例: 旧世代向けに書き溜めた CLAUDE.md / rules が Claude 5 で邪魔をしていないか分からない）+ 公式変化の事実（C1: system prompt 80% 削減、C3: Then→Now 6 対の表）
- **前提**: 照合相手は 2 層ある表 — runtime 層（system prompt + tool description、推論時ロード）vs guidance 層（公式 doc、ロードされない）。食い違いの名前も分ける: 競合 vs ドリフト（発見 1）
- **Step 1: 今の runtime 層を実セッションから採る** — repo だけ見ても分からない（C15: repo 外注入の実例）。tool description は ToolSearch 相当で実物取得、system prompt はセッション内で引用させる
- **Step 2: 自作 rules と突合し 3 分類** — 競合 2（plan mode = C10 逐語対比 / attribution = C12 幽霊設定）、冗長 1（スコープ厳守 = C11）、ドリフト 3（confidence 閾値 = C5 / Verify 足場 = C6 / Author-Reviewer = C7）。発見 4「rule は自分の根拠が消えたことを検知できない」をここに置く
- **Step 3: 「競合＝悪」とせず判定枠で処分** — 意図・根拠・鮮度・失効条件（発見 2）。処分例: plan mode rule 退役（鮮度失効）/ Author-Reviewer 保持（ADR 根拠が生存、C16 未検証は明記）/ git-workflow.md 退役（幽霊設定の結末。**台帳より後の 07-26 の退役なので HEAD で再確認**）
- **落とし穴**: 公式指摘の機械適用は誤診する（発見 6: Verify 8 項目 — モデル自己検証か決定論ゲートかで判定）/ 削除でなく反転が要る例（発見 3: confidence → Scope Filtering）
- `:::details`: C13 モデル依存観測（限界付き）
- まとめ + 関連リンク（Thariq 記事 / Opus 5 prompting doc / **著者 GitHub ハブ github.com/shimo4228 必須**）
- Before/After 数値（5,789→2,316 words 等）は「質が重心」の判断に従い脇役として 1 表まで。**執筆前に HEAD で再計測**（git-workflow 退役後は 13 ファイル / 2,321 words — 台帳 C9 は既に古い）

## 実行手順

1. **数値再計測**: 台帳のコマンドで `ef1bb95^` / `ef1bb95` / 現 HEAD の 3 点を取り直す（~/.claude repo、read-only）
2. **執筆**: Claude Code 本体が `zenn-practical-writing` に従い直接執筆（サブエージェント委譲しない）。ですます調・1 節 1 論点・図/表 ≥1・独立論点 ≤4。未検証事項（C15 注入元 / C16 / C13 限界）は正直に明記
3. **自己プリフライト**: zenn-practical-writing Phase 3 チェックリスト（AI-slop / 段落密度 / 用語初出定義 / 英語名詞句連結）
4. **レビュー並列**: `editor` + `fact-checker`（Claims Register C1-C17 が fact-checker 直行表）+ `codex-review`（cross-model）
5. **指摘反映後、ユーザー本文確認**（公開ドキュメント = 本文提示の human gate。published: true は確認後のみ）
6. **frontmatter 確定**: `published: true` + `published_at: 2026-07-27 09:00`、`npm run validate`
7. **EN 翻訳**: `devto-translator` agent（JP→EN 翻訳 + タグ + schedule.json 登録 + `devto_crosspost.py schedule <slug> --at "2026-07-26 22:00 Asia/Tokyo"`。時刻超過なら 07-27 22:00 に変更）
8. **コミット & push 促し**（push しないと予約が反映されない）
9. **Zenn デプロイ履歴の確認をユーザーに依頼** — 3 日前ルール違反の公開なので予約登録の拒否リスクあり。拒否時は空コミット push で再トリガー

## リスク（ユーザー判断で受容済み）

- 公開前日 push は「3 日以上前 push」の緩和策に反する → 手順 9 で必ず登録成功を確認
- 日曜 09:00 は火水バズタイム外 → 速報性優先の明示的判断

## Verification

- `npm run validate`（frontmatter 検証）が通る
- `npm run preview` で表示確認
- editor / fact-checker / codex-review の指摘がゼロまたは反映済み
- push 後 Zenn デプロイ履歴で予約登録成功（ユーザー確認）
