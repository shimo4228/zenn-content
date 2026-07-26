---
name: publish-article
description: 記事公開前の全チェック（レビュー→セキュリティ→frontmatter→published_at→スケジュール→Dev.to クロスポスト→push）を順に実行する。
user-invocable: true
origin: shimo4228
---

# Publish Article Skill

**Purpose:** 記事公開前の全チェックを一連のフローで実行し、抜け漏れを防止する。

---

## Usage

```
/publish-article articles/ARTICLE_NAME.md
```

引数なしの場合は `published: false` の記事一覧を表示し、対象を選択させる。

---

## Publish Flow

以下のステップを**順番に**実行する。各ステップで問題が見つかった場合は修正してから次へ進む。

> **注:** 日本語品質チェック（textlint）・Markdown 構造チェック（markdownlint）は 2026-07 に撤去済み。frontmatter 検証（Step 3 の `npx zenn list:articles`）が唯一残る機械チェック。表記・文体統一は執筆時に守る（`zenn-practical-writing` / `.claude/rules/zenn-writing.md`）。

### Step 1: Editor エージェントによるレビュー

**`writing-team` Mission A/B から到達した場合はスキップ**（editor/fact-checker/zenn-clarity-reviewer/codex-review は writing-team 側で既に並列実行済み）。`/publish-article` を単独で直接呼んだ場合のみ、このステップで editor / zenn-clarity-reviewer エージェントを並列起動する。

editor エージェントを起動して記事を包括的にレビューする。並列で zenn-clarity-reviewer を起動し、初見読者の明瞭性（造語予算・タイトル軸の貫通・内部文脈依存）を検査する（verdict FAIL は公開ブロック — `quality-gate` の必須条件）。

**レビュー観点:**
1. 技術的正確性（コードスニペット、ファイルパス）
2. ナラティブフロー（導入→文脈→実装→学び→まとめ）
3. 用語の一貫性
4. AI スロップ検出
5. 対象読者の適切性

**結果が「MAJOR ISSUES」の場合:** 修正してから Step 1 を再実行。

### Step 2: セキュリティチェック

以下を**手動で**確認する:

- [ ] コードスニペットに API キーが含まれていないか
- [ ] `/Users/username/` のような個人パスが含まれていないか
- [ ] スクリーンショットに機密情報が映っていないか
- [ ] SpecStory ログがサニタイズされているか

**自動検出パターン:**
```
grep -n '/Users/' {article_path}
grep -n 'sk-proj-\|api_key\|password\|secret\|token' {article_path}
```

### Step 3: Frontmatter 検証

> frontmatter 仕様の正本は `zenn-format` skill。ここでは公開前の検証のみ。

```bash
npx zenn list:articles
```

**チェック内容:**
- title が 60 文字以内
- emoji が単一の絵文字
- type が "tech" または "idea"
- topics が 1-5 個
- slug（ファイル名）が Zenn の規約に準拠

### Step 4: プレビュー確認

```bash
npm run preview
```

ユーザーに `http://localhost:8000` でのプレビュー確認を促す。

### Step 5: published_at 設定

**Zenn 公開は `published_at` 予約投稿方式を使う。**

frontmatter に以下を設定:
```yaml
published: true
published_at: 2026-04-15 07:00  # JST、ハイフン区切り必須
```

- `published_at` を指定して `git push` すれば、指定時刻に自動公開される
- レートリミットにカウントされない
- 何本でも事前 push OK（`published_at` まで公開されない）

**参考タイミング:** `.claude/rules/zenn-writing.md`「投稿ペース方針」を参照（バズタイム：火〜水 7:00-9:00 JST）。

### Step 6: スケジュール登録

> **正本:** `.claude/refs/schedule-schema.md` を参照。

`scripts/schedule.json` に `refs/schedule-schema.md` のスキーマに従ってエントリを追加する。

### Step 7: 英訳記事の作成（Dev.to 用）

ユーザーに英訳してクロスポストするか確認する。

**推奨:** `devto-translator` エージェントで一気通貫（翻訳→タグ→投稿）。

英訳は `articles-en/` に同名で保存される。

### Step 8: Dev.to クロスポスト（予約 or 即時）

`{slug}` は `articles-en/{slug}.md` のベース名。投稿日時は `--at` 引数で渡す（tz 付き推奨。schedule.json には保存しない）。

```bash
# 変換プレビュー（実 POST しない）
cd scripts && uv run python devto_crosspost.py post {slug} --dry-run

# 予約: 指定日時に one-shot launchd 発火
# 日米ペア既定（EN = JP 公開の前日 22:00 JST）の正本は .claude/rules/zenn-writing.md「投稿予約タイミング」
cd scripts && uv run python devto_crosspost.py schedule {slug} --at "2026-07-07 22:00 Asia/Tokyo"

# 即時投稿したい場合
cd scripts && uv run python devto_crosspost.py post {slug}
```

### Step 9: schedule.json の最終更新（自動）

`post`（launchd 発火 or 即時）成功時に `devto` へ実 URL が自動書き戻しされ、one-shot ジョブは自己削除される。手動更新は不要。

### Step 10: git push 確認（CRITICAL）

全コミット完了後、**必ず `git push` を確認する**。未 push だと:
- Zenn の `published_at` 予約投稿が反映されない
- Dev.to のクロスポストスクリプトも動かない

---

## Error Recovery

| ステップ | 失敗時の対応 |
|----------|-------------|
| editor review | 指摘事項を修正して再レビュー |
| セキュリティ | 該当箇所を即座に削除/マスク |
| frontmatter | フィールドを修正 |
| Dev.to投稿 | dry-run で原因確認 → API エラー対応 |

---

## Quick Reference

```
全ステップ実行:
  /publish-article articles/my-article.md

frontmatter 検証のみ:
  npm run validate

editor レビューのみ:
  claude --agent=editor --prompt="Review: articles/my-article.md"
```
