---
title: "Claude Code と Zenn 執筆環境を一から育てた記録"
emoji: "🛠️"
type: "tech"
topics: ["claudecode", "zenn", "textlint", "python"]
published: false
---

Claude Code で Zenn に記事を書き始めるとき、最初にやったのはトーンの定義だった。「技術的だけどくだけすぎない」「AI スロップ禁止」「失敗談も正直に」――こういった語調の指示を細かく出して、Claude Code の `zenn-writer` スキルとして保存した。スキルにしておけば、次の記事からは毎回指示しなくても同じトーンで書ける。

記事を3本書いたあと、まとめて lint を回したら28件のエラーが出た。全角スペース混入、見出しレベルの飛び、表記ゆれ。自分で手を動かして修正するわけではなく、記事全文を読んで問題を見つけたら Claude Code に指摘して直させる、というスタイルだ。ファクトチェックも同じ要領で、記事の記述が実際の経緯と合っているかを毎回つぶさに確認する。ただ、28件を1つずつ指摘するのはさすがに非効率で、ここから環境構築が始まった。

さらに何本か投稿してプロジェクトの傾向が見えてきた頃、Claude Code に「このプロジェクトに必要なスキルをリサーチしてインストールして」と指示を出した。Claude Code はセッションの履歴を分析して、lint 設定のハマりどころやクロスポストのワークフローなど、繰り返し発生するパターンを `learned/` スキルとして自動抽出してくれた。

結果、約2週間で zenn-writer（トーン定義）、6本の learned スキル（経験知の自動抽出）、コミュニティスキル1本という構成ができあがった。この記事では、その過程で潰した4つの具体的な問題を振り返る。

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
記事を書く（zenn-writer スキルがトーンを維持）
  → git commit → pre-commit hook が textlint + markdownlint を自動実行
  → 「何文字？」→ MCP サーバーが正確にカウント
  → publish.py → Zenn 記法を変換して Qiita/Dev.to に1コマンドで投稿
```

そしてこの過程で得た知見は、Claude Code の `learned/` スキルとして自動で蓄積されていく。markdownlint の globs 問題、prh のハイフン回避、textlint の `:::` 誤検知回避――一度踏んだ地雷は二度と踏まない仕組みが、環境の一部として残る。

振り返ると、環境構築には3つのフェーズがあった。

1. **定義**: トーンや語調を決めてスキル化する（zenn-writer）
2. **問題解決**: 遭遇した問題をその場で Claude Code と一緒に潰す
3. **蓄積**: 解決パターンが learned スキルとして自動抽出される

どの仕組みも、最初から計画して作ったわけではない。記事を書く中で問題にぶつかり、解決し、その知見が自動で蓄積される。環境構築が「事前の設計作業」から「使いながら育てるもの」に変わった。
