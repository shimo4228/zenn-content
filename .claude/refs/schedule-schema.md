# schedule.json Schema（正本）

> このファイルは `scripts/schedule.json` の**スキーマ**の正本。
> `publish-article`, `devto-translator` はここを参照する。
>
> **membership・日付・title の正本は `articles/*.md` frontmatter**。
> schedule.json は Dev.to URL のエンリッチ専用で、記事一覧の正本ではない。
このファイル自体が現在の運用schemaであり、執筆・公開時に履歴文書を参照しない。

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
  "devto": null,
  "devto_tags": ["ai", "programming", "discuss"],
  "cover_image": "https://raw.githubusercontent.com/shimo4228/zenn-content/main/images/covers/example-article.png",
  "notes": "EN translation of 記事タイトル"
}
```

> **投稿日時はここに書かない。** Dev.to の投稿タイミングは `devto_crosspost.py schedule <slug> --at "<日時>"` の引数で渡す（launchd ジョブに変換）。schedule.json は投稿済み URL の台帳。

## フィールド定義

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `file` | string | Yes | 記事ファイルパス（`articles/` or `articles-en/`） |
| `date` | string | Optional | **歴史的記録**。日付の正本は `articles/*.md` frontmatter の `published_at`。新規エントリでは付けなくてよい |
| `devto` | string \| null | EN のみ | Dev.to URL。未投稿は `null`、投稿済みは実 URL（`post` が自動書き戻し） |
| `devto_tags` | string[] | EN のみ | Dev.to タグ（最大4つ） |
| `cover_image` | string | No | カバー画像 URL（GitHub raw URL） |
| `notes` | string | No | メモ |

## `devto` フィールドの状態遷移

```
null  →  "https://dev.to/shimo4228/actual-url"
(未投稿)        (投稿済み)
```

- schedule.json 登録時: `null`
- Dev.to 投稿成功後: 実 URL に更新

## canonical_url について

- **legacy フィールド**（表に定義が無いまま実データに 27 件、最終 2026-04-18）。**新規エントリでは付けない**
- **JP 記事**: canonical_url は不要（Zenn が git push で自動公開するため）
- **EN 記事**: canonical_url を設定しない（言語が異なるため Zenn canonical は無意味）

## 投稿ペースガイドライン

投稿頻度・曜日・時間帯の正本は `.claude/rules/publishing-channels.md`「Cadence and scheduling」。
