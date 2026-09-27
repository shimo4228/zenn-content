# 委譲プラン: 全記事への zenn-content 正本リンク追加（新規 Opus セッション）

## Context

LLM 動線の強化のため、公開記事から Markdown 正本 repo への直接リンクを張る。Zenn 記事ページは HTML だが、repo には Markdown 正本・生成索引（docs/PUBLICATIONS.md）・llms ファイルが揃っており、記事 1 本を読んだ LLM がコーパス全体へ 1 hop で届くようになる。著者は本タスクの設計方針を承認済みで、**実装は新セッションの Opus に委譲する**（本セッション = Fable は判断層。tier 規約に従う）。

## 本セッションがやること（委譲のみ）

1. skill: `spawn-session` で新規 detached セッションを起動する
   - project: zenn-content（cwd = `~/MyAI_Lab/zenn-content`）
   - model: **opus**
   - 初期 prompt: 下の「タスクパケット」を渡す（プランモードから開始させる）
2. 起動確認して報告する。実装・レビュー・commit は新セッション側の chain に任せる

## タスクパケット（新セッションへ渡す内容）

### 要求

公開済み Zenn 記事の末尾「関連リンク」節に、その記事の Markdown 正本への定型行を 1 行追加する。

- リンク形式: `https://github.com/shimo4228/zenn-content/blob/main/articles/<slug>.md`（repo トップではなく記事自身の正本ファイルへ）
- 定型文言はプラン時に 1 案決めて著者確認（例:「この記事の Markdown 正本（GitHub）」）
- 対象: `articles/*.md` の `published: true` 全件（下書きは公開時に入るので対象外でも可、実装側判断）
- 「関連リンク」節が無い記事の扱い（節を新設 or スキップ）はプラン時に件数を実測して著者に確認
- 遡及は **1 commit の機械編集**（script 可）。既公開記事の本文更新は公開登録に数えられずレートリミット非消費、フィード再浮上もしない
- 今後の新規記事用に `.claude/rules/publishing-channels.md` の「Related links」節へ定型行の規約を 1 行追記
- EN（articles-en/）: 既公開 Dev.to 記事は update 手段がないため**遡及対象外**。新規 EN 稿へ prospective に入れる規約追記のみ検討

### 制約

- 本文（関連リンク節以外）を変更しない（Content Integrity — 配信最適化で本文を変形しない）
- 検証: `npm run validate` / `npm run check:index` が通ること、追加リンクの実在（サンプル数件を HTTP で確認）
- push すると Zenn 公開版に反映される。commit までで止めて push 前に著者へ確認
- 公開 repo 安全規約: 秘密・個人 path を含めない

### 参照

- 関連リンク規約の正本: `.claude/rules/publishing-channels.md`「Related links」
- 既存記事の関連リンク節の形: `articles/ai-review-task-loop.md` 末尾が代表例
- 注意: 公開ミラーへのリンクで `claude-config`（private）を使わない事故が先例にある。今回のリンク先は zenn-content 自身なので対象外だが、リンク実在確認は必須

## Verification（本セッション側）

- spawn-session 実行後、新セッションが Claude モバイル / セッション一覧に現れることを確認
- 以後の検収は著者と新セッション間で行う（本セッションは介入しない）
