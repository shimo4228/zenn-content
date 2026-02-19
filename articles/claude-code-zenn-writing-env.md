---
title: "Claude Code と Zenn 執筆環境を一から育てた記録"
emoji: "🛠️"
type: "tech"
topics: ["claudecode", "zenn", "textlint", "python"]
published: false
---

Claude Code で Zenn の記事を3本書いたあと、まとめて lint を回したら28件のエラーが出た。全角スペース混入、見出しレベルの飛び、表記ゆれ。1つずつ手で直しながら「これ、次もやるのか？」と思ったのが始まりだった。

ここから約2週間、Claude Code と一緒に執筆環境を育てていった。自分が問題に気づくこともあれば、Claude Code が先に検知してくれることもあった。振り返ると、4つの問題を1つずつ潰していった結果、lint → 文字数確認 → クロスポストが一気通貫でできる環境になっていた。

## 第1章: 28件のエラーから始まった pre-commit hook

最初の3本を書き終えて `npx textlint articles/*.md` を実行したら、28件。Claude Code に「コミット前に自動で止める仕組みがほしい」と伝えたら、husky + lint-staged で pre-commit hook を組んでくれた。

構成はこうなった。

```text
package.json             ← lint-staged の設定
.husky/pre-commit        ← husky の hook（npx lint-staged を実行）
.textlintrc.json         ← textlint ルール
.markdownlint-cli2.jsonc ← markdownlint ルール
prh.yml                  ← 表記ゆれ辞書
```

textlint は `preset-ja-technical-writing` をベースに、`no-dead-link`（リンク切れ検出）と `prh`（表記ゆれ）を追加。markdownlint は Zenn 固有のルールを無効化した。

```jsonc
// .markdownlint-cli2.jsonc — Zenn 向けの無効化
{
  "config": {
    "MD013": false,  // 日本語は1行が長くなる
    "MD025": false,  // Zenn はフロントマターが H1 相当
    "MD041": false,  // 先頭行はフロントマター
    "MD060": false   // :::message を誤検知する
  }
}
```

### ハマりポイント: markdownlint の globs 設定

最初 Claude Code が `.markdownlint-cli2.jsonc` に `"globs": ["articles/**/*.md"]` を入れた。一見よさそうだが、lint-staged 経由で実行すると、ステージされたファイルだけでなく**全ファイルが lint される**。config 側の globs が lint-staged のファイル指定を上書きしてしまうためだ。

Claude Code にこの挙動を伝えたら、globs を削除して lint-staged 側でファイルパターンを制御する形に修正してくれた。

```json
// package.json — lint-staged でファイルを絞る
{
  "lint-staged": {
    "articles/**/*.md": ["textlint", "markdownlint-cli2"],
    "books/**/*.md": ["textlint", "markdownlint-cli2"]
  }
}
```

導入前は記事を5〜6本書き溜めてから28件のエラーと格闘していた。pre-commit hook にしてからは、コミットのたびに1〜2件ずつ修正するだけで済む。

## 第2章: Node.js 20 で突然クラッシュした朝

コードを一切変えていないのに、翌日 textlint がクラッシュした。

```text
SyntaxError: Invalid regular expression: /Claude\-Native/v: Invalid escape
```

原因は Node.js のアップデートだった。Node.js 20 は V8 の Unicode Sets mode（`v` flag）をサポートしており、`\-`（エスケープされたハイフン）を構文エラーとして扱う。prh が内部で正規表現を `v` フラグ付きでコンパイルするため、`prh.yml` にハイフン入りのパターンがあると即クラッシュする。

Claude Code にエラーログを見せたら、すぐに原因を特定してくれた。

```yaml
# NG: Node.js 20+ でクラッシュ
- expected: Claude-Native
  pattern: /Claude\-Native/

# OK: patterns（リテラル文字列）なら安全
- expected: Claude-Native
  patterns:
    - claude native
    - Claude based
```

`pattern`（正規表現）ではなく `patterns`（リテラル文字列マッチ）を使えば、内部でハイフンが安全に処理される。Claude Code が prh.yml 全体をスキャンして、ハイフン含みの pattern をすべて patterns に書き換えてくれた。

**学び**: ランタイムのメジャーアップデートは、ソースコードだけでなく設定ファイルの正規表現も壊すことがある。CI が落ちたとき「コード変えてないのに」と思ったら、ランタイムのバージョンを疑う。

## 第3章: 「約2,800字です」は嘘だった

Zenn 記事は2,000〜4,000字が読みやすい。執筆中に Claude Code へ「この記事は何文字？」と聞いたら「約2,800文字です」と返ってきた。実際に数えたら3,200文字。400字もずれている。

LLM は日本語のトークン境界を正確に扱えない。英語なら空白で区切れるが、日本語はスペースで区切られないため、推測ベースの回答になる。

Claude Code に「正確に数える方法がほしい」と言ったら、MCP サーバーとして kuromoji.js ベースの日本語テキスト分析ツールを提案してきた。`~/.claude.json` に設定を追加するだけで接続できる。

```json
{
  "mcpServers": {
    "JapaneseTextAnalyzer": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "github:Mistizz/mcp-JapaneseTextAnalyzer"]
    }
  }
}
```

これで Claude Code の会話内から文字数カウントと品詞分析ができるようになった。

```text
me: この記事の文字数を確認して
Claude Code: [JapaneseTextAnalyzer.count_chars を実行]
→ 3,201文字（改行・スペース除外）
```

推測ではなく kuromoji.js の辞書ベースで数えるので正確だ。`~/.claude.json`（グローバル設定）に置くことで、全プロジェクトから使える。

## 第4章: 「Qiita にも出したい」と言ったら記法の違いを先に指摘された

記事が何本か溜まってきた頃、「Qiita にもクロスポストしたい」と Claude Code に伝えた。すると「Zenn の `:::message` や `:::details` は Qiita では表示されません。記法変換が必要です」と先に指摘してきた。言われてみれば当然だが、自分では気づいていなかった。

そのまま Claude Code に変換スクリプトを作ってもらい、`scripts/publish.py` ができあがった。

変換ルールは3つ。

- `:::message` → blockquote（`>` 記法）
- `:::details タイトル` → HTML の `<details>` タグ
- `/images/` → GitHub raw URL

```bash
# Qiita に新規投稿
python scripts/publish.py articles/my-article.md --platform qiita

# 既存記事を更新（タイトルで自動検索）
python scripts/publish.py articles/my-article.md --platform qiita --update auto

# dry-run で変換結果だけ確認
python scripts/publish.py articles/my-article.md --platform qiita --dry-run
```

`--update auto` はタイトルの完全一致で既存記事を検索して更新する。Zenn 側を直したら `--update auto` で Qiita も追従、というワークフローが1コマンドで完結する。

英語圏プラットフォーム（Dev.to、Hashnode）への誤投稿も防いでくれる。`articles/`（日本語記事）から直接 Dev.to に投稿しようとすると、英訳ファイルの有無をチェックしてエラーで止まる。

## 環境が「育った」結果

2週間で4つの問題を潰した結果、こうなった。

```text
記事を書く
  → git commit → pre-commit hook が textlint + markdownlint を自動実行
  → 「何文字？」→ MCP サーバーが正確にカウント
  → publish.py → Zenn 記法を変換して Qiita/Dev.to に1コマンドで投稿
```

どの仕組みも、最初から計画して作ったわけではない。記事を書いている過程で問題にぶつかり、そのたびに Claude Code と一緒に解決していった結果、統合された環境ができあがった。

Claude Code との協業で感じたのは、「問題が起きるたびに、その場でツールを作れる」という点だ。lint の設定からクロスポストスクリプトまで、「これ直して」「こういう仕組みがほしい」と伝えれば動くものが出てくる。環境構築が「事前の設計作業」から「日常的な改善の積み重ね」に変わった。
