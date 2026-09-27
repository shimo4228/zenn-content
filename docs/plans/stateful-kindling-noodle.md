# プロジェクトスキル改善プラン（skill-stocktake 監査結果の実行）

## Context

zenn-content のプロジェクトスキル（`.claude/skills/` 11 本 + learned 4 本）を skill-stocktake で全数監査した。7/5 の大規模整理（ADR-0003 の channel 軸再編・lint 全撤去・投稿ペア既定化 205d810）の後、**正本を更新した際の参照側スキルの追従漏れ**が 5 スキルに残っている。加えてユーザー判断で zenn-writer（純 router）の Retire と、タグ・emoji ガイドの zenn-format への一本化が確定した。

タスク種別: `chore`（スキル定義ファイルの整合修正。コード変更なし）。
Chain: Code Review 条件付き（settings/hooks 変更なし → 不要）、Verify は git status + 参照リンク確認のみ。

## 変更内容

### 1. zenn-writer を Retire（ユーザー承認済み）

- `.claude/skills/zenn-writer/` ディレクトリを削除
- 参照の repoint:
  - `CLAUDE.md:106` — 「`zenn-writer` skill は歴史的パス維持のための声のルーター」の一文を削除（振り分け表自体は既に zenn-practical-writing を直接指しているため、その行だけ落とす）
  - `docs/CODEMAPS/skills.md:9` — zenn-writer 行を削除し、現在のスキル構成（practical-writing / idea-voice / format の 3 層）に更新
  - `.claude/rules/zenn-writing.md` の Related 節に zenn-writer 言及があれば除去（本文確認の上）
- `docs/adr/0003-zenn-practical-channel-axis.md` に追記（Consequences 節）: 「router は参照導線消滅を確認し 2026-07-06 に削除」— 新規 ADR は立てない（0003 の決定の後日談）

### 2. zenn-format の修正（Improve）

- **L165 内部リンク例の修正（最重要・実害あり）**: `[前回の記事](/articles/previous-article-slug)` → フル URL 形式 `https://zenn.dev/shimo4228/articles/xxx` に修正し、「相対パスは Zenn 上で解決されない」の注記を添える（zenn-writing.md L 内部リンク規約と一致させる）
- L37 title の表現: 「50-60 chars optimal, 60 max」→「50 文字以内推奨・60 まで許容」（zenn-writing.md の優先関係に合わせる）
- L241: 公開前チェックのフロー列挙から「lint→」を除去（lint は 2026-07 撤去済み）
- **タグ・emoji の正本化（ユーザー承認済み）**: 既存の Tag guidelines / Emoji Selection 節を正本と明記（seo-optimizer から defer される受け側になる）

### 3. seo-optimizer の修正（Improve）

- **Step 3 Topics 最適化を全面書き換え**: 「高トラフィックタグ（ai/llm 等）を優先的に含める」戦略を削除し、「タグ選定基準は `zenn-format` の Tag guidelines が正本（ニッチ優先・`ai`/`llm` 単独禁止・定着確認）」のポインタ + 提案フロー（現タグとの diff 提示・理由付き）だけ残す
- **Step 4 Emoji 表を削除**: zenn-format の Emoji Selection へのポインタに置換
- **Step 1 の「冒頭文: フック力」行を削除**: 冒頭最適化は ADR-0001 で廃止済み。評価だけ残すのは残骸（Note 欄の廃止注記と矛盾）

### 4. schedule-publish の修正（Improve）

- **Readiness 軸（L51-58）の書き換え**: lint 前提のスコア基準を現行の品質ゲートに合わせる。案: 3 = editor レビュー済み CRITICAL なし / 2 = レビュー済み MEDIUM 残 / 1 = レビュー未実施 / 0 = CRITICAL 未修正
- **クロスポスト行（L86）の修正**: 「Zenn 公開当日または翌日」→「EN は JP の前日 22:00 JST（正本: `.claude/rules/zenn-writing.md` 投稿予約タイミング）」
- Step 3 / Cross-Post Timing の `America/New_York` 例 → `--at "<前日> 22:00 Asia/Tokyo"` に差し替え（zenn-writing.md の既定と一致）

### 5. publish-article の修正（Improve）

- Step 8 の予約例: `--at "2026-07-07 09:00 America/New_York"` → `--at "2026-07-07 22:00 Asia/Tokyo"` + 「日米ペア既定は zenn-writing.md 投稿予約タイミングが正本」の一行
- Quick Reference: `claude task --agent=editor` → `claude --agent=editor --prompt="..."`（CLAUDE.md の記法に統一）

### 6. writing-team の修正（Improve 小）

- 「品質ゲート」節の「全ミッションで `/quality-gate` を通す」を実態に合わせる: Mission A/B のフローに明記済み、C（翻訳）には quality-gate の「翻訳記事追加」チェックをフローに 1 行追加、D/E は品質ゲート対象外と明記（スケジューリングとアイデア出しに品質ゲートは意味を持たない）

### 7. learned/security-article-credibility の微修正

- 「publish-article フローの Step 4（セキュリティチェック）」→「Step 2」（番号ドリフト修正）

## 変更しないもの（Keep 確定）

zenn-practical-writing / zenn-idea-voice / quality-gate / ideation / series-checker / learned 3 本（concept-before-use-rule, reader-first-article-review, article-anonymization-pattern）— 現行・重複なし・defer 構造明確。

## Verify

1. `grep -rn "zenn-writer" CLAUDE.md .claude/ docs/` — ADR-0003 の履歴記述以外にゼロ
2. `grep -rn "lint" .claude/skills/*/SKILL.md` — 撤去済み lint への現在形参照がゼロ
3. `grep -rn "America/New_York" .claude/skills/` — ゼロ（JST 明示に統一）
4. `grep -rn "/articles/previous" .claude/skills/zenn-format/SKILL.md` — 相対パス例が残っていない
5. `git status` で意図しないファイルが含まれていないこと
6. コミット（1 コミット、type: chore）。**push はユーザーに促す**（CLAUDE.md の Git Push Reminder）

## 備考

- skill-stocktake の ledger（results.json）はグローバルスキル専用のため更新しない（プロジェクトスキルは毎回 fresh 読み）
- 全て既存ファイルの edit + 1 ディレクトリ削除。削除は zenn-writer のみでユーザー承認済み
