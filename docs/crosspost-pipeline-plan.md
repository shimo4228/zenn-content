# Dev.to + Hashnode クロスポスト自動化プラン

## 概要

既存の `scripts/publish.py` (Zenn→Qiita) を拡張し、Dev.to / Hashnode への英語記事投稿を自動化する。

## 前提条件（実行前にやること）

- [ ] Dev.to アカウント作成 → https://dev.to/settings/extensions で API Key 取得
- [ ] Hashnode アカウント作成 → https://hashnode.com/settings/developer で PAT 取得
- [ ] Hashnode publication ID 取得（ダッシュボードURL or GraphQL query）
- [ ] `scripts/.env` に以下を追記:
  ```
  DEVTO_API_KEY=xxx
  HASHNODE_API_TOKEN=xxx
  HASHNODE_PUBLICATION_ID=xxx
  ```

## 使い方

```bash
# 1. Claude Code で翻訳
# "この記事を英語に翻訳して articles/ecc-cheatsheet.en.md に保存して"

# 2. Dev.to に投稿（dry-run で確認）
python scripts/publish.py articles/ecc-cheatsheet.en.md \
  --platform devto \
  --canonical-url "https://zenn.dev/shimomoto/articles/ecc-cheatsheet" \
  --dry-run

# 3. Dev.to に投稿（本番）
python scripts/publish.py articles/ecc-cheatsheet.en.md \
  --platform devto \
  --canonical-url "https://zenn.dev/shimomoto/articles/ecc-cheatsheet"

# 4. Hashnode に投稿
python scripts/publish.py articles/ecc-cheatsheet.en.md \
  --platform hashnode \
  --canonical-url "https://zenn.dev/shimomoto/articles/ecc-cheatsheet"

# 5. 既存記事の更新
python scripts/publish.py articles/ecc-cheatsheet.en.md \
  --platform devto --update auto
```

## API 仕様メモ

### Dev.to
- REST API: `POST https://dev.to/api/articles`
- Auth: `api-key` ヘッダー
- Tags: 最大4つ、小文字
- Markdown ネイティブ対応

### Hashnode
- GraphQL API: `POST https://gql.hashnode.com`
- Auth: `Authorization` ヘッダー (PAT)
- publication ID 必須
- Markdown ネイティブ対応
