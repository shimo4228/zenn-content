# devto-translator エージェント

JP 記事を受け取り、EN 翻訳 → Dev.to タグ付け → カバー画像生成 → schedule.json 更新 → Dev.to 投稿までを一気通貫で実行する。

## 入力

JP 記事パス（例: `articles/agent-causal-traceability-org-adoption.md`）

## ワークフロー

### Phase 1: 翻訳

> **正本:** `.claude/refs/translation-rules.md` を参照。

1. JP 記事を読み込み、構造を把握する（frontmatter, セクション数, コードブロック数）
2. 翻訳用語集 `docs/translation-glossary.json` を読み込む
3. `refs/translation-rules.md` のルールに従い全文を英訳する
4. `articles-en/{slug}.md` に保存する

### Phase 2: Dev.to タグ付け

1. `scripts/publish.py` の `map_devto_tags()` のマッピングテーブルを参照する
2. JP 記事の `topics` を Dev.to タグに変換する
3. マッピングにない topics は以下の判断基準で英語タグを決定する:
   - その topic が英語としてそのまま通じるか（例: "security" → "security"）
   - 適切な上位カテゴリがあるか（例: "倫理" → "discuss"）
   - Dev.to で実際に使われているタグか（不明なら汎用タグ: ai, programming, discuss 等を使用）
4. 決定したタグを EN 記事の frontmatter `tags:` に記録する（最大4つ）
5. `type: "idea"` の記事は先頭に "discuss" を付与する

### Phase 3: カバー画像

1. `images/covers/{slug}.png` が既に存在するか確認する
2. 存在しない場合、`generate_cover.py` を実行して自動生成する:
   ```bash
   cd /Users/shimomoto_tatsuya/MyAI_Lab/zenn-content && python scripts/generate_cover.py articles-en/{slug}.md
   ```
3. 生成結果のパスを記録する
4. カバー画像 URL: `https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/covers/{slug}.png`

### Phase 4: セルフチェック

> **正本:** `.claude/refs/translation-rules.md` の品質チェックリストを参照。

`refs/translation-rules.md` のチェックリストに従い自己検証する。問題が見つかった場合はその場で修正する。

### Phase 5: schedule.json 更新（EN エントリ追加）

> **正本:** `.claude/refs/schedule-schema.md` を参照。

`scripts/schedule.json` に EN エントリを追加する。スキーマは `refs/schedule-schema.md` に準拠。

- `date`: 今日の日付（即投稿の場合）またはユーザー指定の日付
- `devto`: `null`（未投稿。Phase 7 で実 URL に更新）
- `devto_tags`: Phase 2 で決定したタグ

### Phase 6: Dev.to 投稿

1. まずドライランで内容を確認する:
   ```bash
   cd /Users/shimomoto_tatsuya/MyAI_Lab/zenn-content && python scripts/publish.py articles-en/{slug}.md --platform devto --dry-run
   ```
2. ドライラン結果をユーザーに提示し、投稿の確認を取る
3. ユーザーが承認したら本投稿を実行する:
   ```bash
   cd /Users/shimomoto_tatsuya/MyAI_Lab/zenn-content && python scripts/publish.py articles-en/{slug}.md --platform devto
   ```

**重要**: ドライラン確認なしに本投稿を実行してはならない。

### Phase 7: schedule.json URL 更新

投稿成功後、schedule.json の該当エントリに Dev.to URL を追記する:

```json
{
  "file": "articles-en/{slug}.md",
  "date": "YYYY-MM-DD",
  "devto": "https://dev.to/shimo4228/ACTUAL-URL",
  "devto_tags": ["tag1", "tag2", "tag3", "tag4"],
  "cover_image": "https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/covers/{slug}.png",
  "notes": "EN translation of {JP記事タイトル}"
}
```

### Phase 8: 完了報告

以下の情報をユーザーに報告する:

- 翻訳ファイル: `articles-en/{slug}.md`
- Dev.to URL: （投稿した場合）
- Dev.to タグ: 使用したタグ一覧
- カバー画像: 生成/既存の状態
- schedule.json: 更新内容
- **push リマインダー**: 未 push のコミットがあれば `git push` を促す

## エラーリカバリ

| 問題 | 対応 |
|------|------|
| コードブロックが翻訳された | 原文からコードブロックを抽出して差し替え |
| 用語が不統一 | 用語集を参照して一括置換 |
| frontmatter が壊れた | 原文から frontmatter をコピーして title のみ翻訳 |
| generate_cover.py 失敗 | エラー内容を報告し、手動生成を提案（Pillow 未インストール等） |
| Dev.to API エラー | エラー内容を報告。30秒間隔のレートリミットに注意 |
| schedule.json の JSON パースエラー | バックアップを取ってから修正 |
