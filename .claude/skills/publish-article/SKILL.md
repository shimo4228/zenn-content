<!-- origin: original -->
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

### Step 1: textlint（日本語品質チェック）

```bash
npx textlint {article_path}
```

**チェック内容:**
- 日本語技術文書のルール（preset-ja-technical-writing）
- リンク切れ検出（no-dead-link）
- 用語統一（prh: pdf2anki, Claude-Native, CLI-First 等）

**エラーがある場合:** 自動修正可能なものは `npx textlint --fix {article_path}` で修正。残りは手動対応。

### Step 2: markdownlint（Markdown 構造チェック）

```bash
npx markdownlint-cli2 {article_path}
```

**チェック内容:**
- 見出しレベルの整合性
- リスト記法の統一
- 空行の適切な配置
- HTML 要素の妥当性

### Step 3: Editor エージェントによるレビュー

editor エージェントを起動して記事を包括的にレビューする。

**レビュー観点:**
1. 技術的正確性（コードスニペット、ファイルパス）
2. ナラティブフロー（導入→文脈→実装→学び→まとめ）
3. 用語の一貫性
4. AI スロップ検出
5. 対象読者の適切性

**結果が「MAJOR ISSUES」の場合:** 修正してから Step 3 を再実行。

### Step 4: セキュリティチェック

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

### Step 5: Frontmatter 検証

```bash
npx zenn list:articles
```

**チェック内容:**
- title が 60 文字以内
- emoji が単一の絵文字
- type が "tech" または "idea"
- topics が 1-5 個
- slug（ファイル名）が Zenn の規約に準拠

### Step 6: プレビュー確認

```bash
npm run preview
```

ユーザーに `http://localhost:8000` でのプレビュー確認を促す。

### Step 7: 公開

ユーザーの確認後:

1. `published: false` → `published: true` に変更
2. `git add {article_path}`
3. `git commit -m "feat: {article_title} を公開"`
4. `git push`

### Step 8: Qiita クロスポスト（オプション）

ユーザーに Qiita にもクロスポストするか確認する。

```bash
cd scripts && .venv/bin/python publish.py ../{article_path} --platform qiita --dry-run
```

dry-run の結果を確認後:

```bash
cd scripts && .venv/bin/python publish.py ../{article_path} --platform qiita
```

**publish.py が自動変換する差異:**

| Zenn | Qiita |
|------|-------|
| `:::message ... :::` | `> blockquote` |
| `:::details title ... :::` | `<details><summary>` |
| `topics` (frontmatter) | `tags` (API、最大5個) |

**手動対応が必要な差異:**

| 項目 | Zenn | Qiita |
|------|------|-------|
| CTA | 「いいね」のみ | 「いいね」+「ストック」 |
| 前回記事リンク | Zenn URL | Qiita URL に差し替え |

**クロスリンクの注意:** 前回記事リンクは公開済みプラットフォームの URL を使う。Zenn 側が `published: false` なら Qiita URL にフォールバック。

### Step 9: 英訳記事の作成（Dev.to / Hashnode 用）

ユーザーに英訳してクロスポストするか確認する。

```bash
# /translate-article スキルで英訳を作成
/translate-article {article_path}
```

英訳は `articles-en/` に同名で保存される。

### Step 10: Dev.to / Hashnode クロスポスト（オプション）

英訳記事が存在する場合、Dev.to と Hashnode にクロスポストする。

```bash
CANONICAL="https://zenn.dev/shimo4228/articles/{slug}"

# Dev.to
cd scripts && uv run python publish.py ../articles-en/{filename} --platform devto --canonical-url "$CANONICAL"

# Hashnode
cd scripts && uv run python publish.py ../articles-en/{filename} --platform hashnode --canonical-url "$CANONICAL"
```

> **Note:** `publish.py` は日本語記事（`articles/`）で Dev.to / Hashnode を指定するとガードが発動します。`--force` で回避可能。

---

## Error Recovery

| ステップ | 失敗時の対応 |
|----------|-------------|
| textlint | `--fix` で自動修正 → 残りを手動修正 |
| markdownlint | エラーメッセージに従い手動修正 |
| editor review | 指摘事項を修正して再レビュー |
| セキュリティ | 該当箇所を即座に削除/マスク |
| frontmatter | フィールドを修正 |
| Qiita投稿 | dry-run で原因確認 → 変換ロジック修正 |

---

## Quick Reference

```
全ステップ実行:
  /publish-article articles/my-article.md

lint のみ:
  npm run lint:all

editor レビューのみ:
  claude task --agent=editor --prompt="Review articles/my-article.md"
```
