---
title: "Claude Code で Zenn → Qiita → Dev.to クロスポストを1コマンドで"
emoji: "🔄"
type: "tech"
topics: ["claudecode", "zenn", "qiita", "python"]
published: false
---

Zenn で書いた記事を Qiita にコピペしたら、`:::message` ブロックがそのまま表示されていることに翌日気づきました。読者から「表示が崩れています」とコメントが来てから慌てて修正。`:::details` や `/images/` パスも全部壊れていました。

手動でプラットフォームごとの記法変換を続けるのは現実的でありません。Claude Code に「Zenn 記法を確実に変換してクロスポストする仕組みを作って」と依頼し、`scripts/publish.py` を生成しました。

## 使い方

```bash
# Qiita に新規投稿
python scripts/publish.py articles/my-article.md --platform qiita

# Qiita の既存記事を更新（タイトルで自動検索）
python scripts/publish.py articles/my-article.md --platform qiita --update auto

# Dev.to に投稿（canonical URL 付き — SEO でオリジナル記事を明示）
python scripts/publish.py articles/my-article.md --platform devto \
  --canonical-url https://zenn.dev/shimo4228/articles/my-article

# dry-run で変換結果を確認
python scripts/publish.py articles/my-article.md --platform qiita --dry-run
```

## Zenn 記法の変換

スクリプトは3種類の Zenn 固有記法を標準 Markdown に変換します。

**:::message → blockquote**

```markdown
<!-- 変換前（Zenn） -->
:::message
注意事項です
:::

<!-- 変換後 -->
> 注意事項です
```

**:::details → HTML の details タグ**

```markdown
<!-- 変換前（Zenn） -->
:::details クリックで展開
詳細な内容
:::

<!-- 変換後 -->
<details><summary>クリックで展開</summary>

詳細な内容

</details>
```

**/images/ → GitHub raw URL**

```markdown
<!-- 変換前 -->
![図](/images/diagram.png)

<!-- 変換後 -->
![図](https://raw.githubusercontent.com/user/zenn-content/main/images/diagram.png)
```

Zenn の `/images/` パスは Zenn 内でしか解決されません。他プラットフォームでは GitHub リポジトリの raw URL に置き換えます。

## --update auto の仕組み

`--update auto` を指定すると、記事のタイトルで既存記事を検索します。

```python
def find_qiita_item_by_title(title: str, token: str) -> str | None:
    """タイトル完全一致で Qiita 記事を検索（簡略版）"""
    page = 1
    while page <= 5:
        resp = httpx.get(
            f"{QIITA_API_BASE}/authenticated_user/items",
            headers={"Authorization": f"Bearer {token}"},
            params={"page": page, "per_page": 20},
            timeout=30,
        )
        # エラーハンドリング省略（実装では status_code チェックあり）
        for item in resp.json():
            if item.get("title") == title:
                return item["id"]
        page += 1
    return None
```

タイトルの完全一致で検索するため、Zenn 側でタイトルを変更した場合は `--update <記事ID>` で直接指定してください。

## 英語記事ガード

Dev.to や Hashnode は英語圏のプラットフォームです。`articles/` ディレクトリ（日本語記事）から直接投稿しようとすると、エラーで停止します。

```bash
$ python scripts/publish.py articles/my-article.md --platform devto
Warning: No English translation found at articles-en/my-article.md
Run /translate-article first, or pass --force to publish in Japanese.
```

英訳済みの記事は `articles-en/` に配置し、そちらから投稿します。日本語のまま投稿する場合は `--force` フラグでガードをスキップできます。

## セットアップ

### 依存パッケージ

```bash
pip install httpx python-frontmatter
```

### API トークン

`scripts/.env` に各プラットフォームのトークンを設定します。

```text
QIITA_ACCESS_TOKEN=xxxxx
DEVTO_API_KEY=xxxxx
HASHNODE_API_TOKEN=xxxxx
HASHNODE_PUBLICATION_ID=xxxxx
```

`.env` は `.gitignore` に追加してください。スクリプトは起動時に `scripts/.env` を自動で読み込みます（`python-dotenv` ではなく自前の軽量ローダーを使用。依存を最小限にするためです）。

**画像パスの設定**: スクリプト内の `GITHUB_RAW_BASE` に GitHub ユーザー名とリポジトリ名がハードコードされています。自分の環境に合わせて変更してください。

```python
# scripts/publish.py 内の定数を自分のリポジトリに変更
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/<your-user>/zenn-content/main/images"
```

## 設計判断

**Why: なぜ自作したか**

既存のクロスポストツール（zenn-to-qiita、cross-post-cli 等）は Zenn 固有記法の変換が不十分でした。`:::message` や `:::details` をそのまま残すものが多く、結局手動で修正が必要になります。Claude Code に「Zenn 記法を確実に変換して」と指示することで、自分のユースケースに合ったスクリプトを生成できました。

**Why: なぜ `--update auto` をつけたか**

記事を更新するたびに Qiita の管理画面で記事 ID を探すのが面倒です。タイトル検索で自動マッチングすることで、Zenn 側を更新 → `--update auto` で Qiita も追従、というワークフローが1コマンドで完結します。

## まとめ

- Zenn 固有記法（`:::message`、`:::details`、`/images/`）を自動変換してクロスポストできる
- `--update auto` でタイトル検索による既存記事の自動更新が可能
- 英語圏プラットフォームへの誤投稿を防ぐガード付き
- Claude Code に依頼して約30分で動くスクリプトが完成した

Hashnode は `--update auto` に未対応のため、更新時は `--update <記事ID>` を直接指定してください。
