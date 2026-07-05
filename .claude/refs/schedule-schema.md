# schedule.json Schema（正本）

> このファイルは `scripts/schedule.json` のスキーマの **唯一の正本**。
> `schedule-publish`, `publish-article`, `devto-translator` はここを参照する。
> 根拠: [ADR-0002](../docs/adr/0002-writing-team-orchestration.md)

---

## エントリ構造

### JP 記事エントリ

```json
{
  "file": "articles/example-article.md",
  "date": "2026-04-15",
  "notes": "ガバナンスシリーズ第3回"
}
```

### EN 記事エントリ

```json
{
  "file": "articles-en/example-article.md",
  "date": "2026-04-16",
  "devto": null,
  "devto_tags": ["ai", "programming", "discuss"],
  "cover_image": "https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/covers/example-article.png",
  "notes": "EN translation of 記事タイトル"
}
```

## フィールド定義

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `file` | string | Yes | 記事ファイルパス（`articles/` or `articles-en/`） |
| `date` | string | Yes | 公開日 `YYYY-MM-DD` |
| `devto` | string \| null | EN のみ | Dev.to URL。未投稿は `null`、投稿済みは実 URL |
| `devto_tags` | string[] | EN のみ | Dev.to タグ（最大4つ） |
| `cover_image` | string | No | カバー画像 URL（GitHub raw URL） |
| `notes` | string | No | メモ |
| `score` | object | No | `schedule-publish` skill が記録する4軸スコア（`discover`/`anchor`/`ready`/`fresh`/`total`）。トレーサビリティ用、公開処理では未使用 |

## `devto` フィールドの状態遷移

```
null  →  "https://dev.to/shimo4228/actual-url"
(未投稿)        (投稿済み)
```

- schedule.json 登録時: `null`
- Dev.to 投稿成功後: 実 URL に更新

## canonical_url について

- **JP 記事**: canonical_url は不要（Zenn が git push で自動公開するため）
- **EN 記事**: canonical_url を設定しない（言語が異なるため Zenn canonical は無意味）

## 投稿ペースガイドライン

投稿頻度・曜日・時間帯の正本は `.claude/rules/zenn-writing.md`「投稿ペース方針」。値の二重管理を避けるためここでは再掲しない。
