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

### Step 1: 品質保証は済んでいるか（このスキルは判定しない）

**本スキルは公開作業の手順であって、品質ゲートではない。**レビュー panel（editor +
fact-checker + zenn-clarity-reviewer + codex-review）とタイトル確定（title-eval →
zenn-format の提案フロー）と最終判定（article-judge）は、すべて **`writing-team` の責務**。

- 正本: `writing-team` Mission A の step 7（panel）/ step 9（binding 最終判定）/ step 11（タイトル）
- 公開可否の判定は `quality-gate` skill が行う。本スキルはその後に走る

`/publish-article` を単独で呼ぶ場合も、**品質は保証されない**。先に `writing-team` を
通すか、少なくとも `quality-gate` を通すこと。

### Step 2: セキュリティチェック

以下を**手動で**確認する:

- [ ] コードスニペットに API キーが含まれていないか
- [ ] `/Users/username/` のような個人パスが含まれていないか
- [ ] スクリーンショットに機密情報が映っていないか
- [ ] 生ログを引用した箇所がサニタイズされているか（生ログの置き場は `articles/_context/`。
      Zenn 同期対象外だが、本文へ引用するときは個人パス・キーを落とす）

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
- title が上限内（正本: `.claude/rules/zenn-writing.md`）
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
- **⚠ 予約登録自体がレートリミットに計上される** — 詳細と対処は
  `.claude/rules/zenn-writing.md`「`published_at` フォーマット注意」が正本

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

### Step 9.5: 公開索引の再生成（commit 前）

`docs/PUBLICATIONS.md` と README の読書経路ブロックは `articles/*.md` frontmatter + `schedule.json` + `scripts/corpus.yml` から生成する。記事の追加・`published_at` 設定・Dev.to URL 書き戻しのあと、**commit に含める前に**再生成する（CI は `--check` で drift を fail させるだけで、bot commit はしない — ADR-0009）:

```bash
npm run generate:index   # docs/PUBLICATIONS.md + README.md/README.ja.md の marker ブロックを更新
npm run check:index      # 生成物が最新か確認（CI と同じ）
```

- `published: true` の記事に `published_at` が無いと生成が止まる（日付は索引の正本。過去記事は 2026-08-18 に Zenn 実値でバックフィル済み）
- README の読書経路（3 経路 × 2〜3 本）は `scripts/reading_paths.yml` の著者判断。新記事を自動で足さない — 年単位で見直す
- note / Substack エッセイと論文は frontmatter が無いので `scripts/corpus.yml` に手で 1 エントリ追記してから再生成する

### Step 10: git push 確認（CRITICAL）

全コミット完了後、**必ず `git push` を確認する**。未 push だと:
- Zenn の `published_at` 予約投稿が反映されない
- Dev.to のクロスポストスクリプトも動かない
- CI の `check:index` は push 後に走るので、生成し忘れは push 後に赤で気づく

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
