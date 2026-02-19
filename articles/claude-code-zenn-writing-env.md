---
title: "Claude Code と Zenn 執筆環境を一から育てた記録"
emoji: "🛠️"
type: "tech"
topics: ["claudecode", "zenn", "textlint", "python"]
published: false
---

Claude Code で Zenn の記事を書いている。自分の役割は方向性を決めて、書き上がった記事を全文読んでファクトチェックや指摘を入れること。修正作業そのものは Claude Code がやる。

この体制で約2週間やってみて気づいたのは、問題が起きるたびに「二度と繰り返さないよう仕組み化する」サイクルが自然と回ることだ。口頭の指示はスキルへ、手動の作業はスクリプトへ、踏んだ地雷は learned スキルへ。すべてが再利用可能な形で環境に残る。

この記事では、実際に遭遇した4つの問題と、それぞれが何に仕組み化されたかを記録する。

## まずトーンをスキル化した

記事を書き始める前に、最初にやったのはトーンの定義だった。「技術的だけどくだけすぎない」「AI スロップ禁止」「失敗談も正直に書く」――こういった語調の指示を細かく出し、Claude Code の `zenn-writer` スキルとして保存した。

スキルにしておけば、次の記事から毎回指示しなくても同じトーンで書ける。口頭の指示は忘れるが、スキルファイルは消えない。これが仕組み化の起点になった。

## 28件の lint エラー → pre-commit hook

記事を3本書いたあと、まとめて lint を回したら28件のエラーが出た。全角スペース混入、見出しレベルの飛び、表記ゆれ。1つずつ指摘するのは非効率なので、Claude Code に「コミット前に自動で止める仕組みがほしい」と伝えた。

husky + lint-staged で pre-commit hook を組んでくれた。

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

ここでハマりポイントがあった。最初 Claude Code が `.markdownlint-cli2.jsonc` に `"globs": ["articles/**/*.md"]` を入れた。しかし lint-staged 経由だと config 側の globs がファイル指定を上書きし、**全ファイルが lint される**。この挙動を伝えたら、globs を削除して lint-staged 側で制御する形に直してくれた。

```json
// package.json — lint-staged でファイルを絞る
{
  "lint-staged": {
    "articles/**/*.md": ["textlint", "markdownlint-cli2"],
    "books/**/*.md": ["textlint", "markdownlint-cli2"]
  }
}
```

**仕組み化の結果**: 28件のエラーは pre-commit hook になった。そしてこの globs の落とし穴は `learned/zenn-markdownlint-config` スキルとして自動抽出され、Claude Code が同じミスを繰り返さなくなった。

## Node.js 20 のクラッシュ → learned スキル

コードを一切変えていないのに、textlint がクラッシュした。

```text
SyntaxError: Invalid regular expression: /Claude\-Native/v: Invalid escape
```

原因は Node.js 20 の V8 Unicode Sets mode（`v` flag）だった。`\-` が構文エラーとして扱われる。prh が内部で `v` フラグ付きコンパイルを行うため、`prh.yml` にハイフン入りパターンがあると即クラッシュする。

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

Claude Code が prh.yml 全体をスキャンして、ハイフン含みの pattern をすべて patterns に書き換えてくれた。

**仕組み化の結果**: この回避策は `learned/prh-hyphen-regex-escape` スキルとして自動抽出された。以降、Claude Code が prh.yml を編集するときは、ハイフンを含む pattern を自動で避ける。ランタイムのバージョン起因のクラッシュという、再現条件が分かりにくい問題ほど、スキルとして残す価値がある。

## 嘘の文字数 → MCP サーバー

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

```text
me: この記事の文字数を確認して
Claude Code: [JapaneseTextAnalyzer.count_chars を実行]
→ 3,201文字（改行・スペース除外）
```

**仕組み化の結果**: `~/.claude.json`（グローバル設定）に置いたので、全プロジェクトで使える。LLM の推測に頼らず、辞書ベースの正確な値が返る。「LLM が苦手なことは外部ツールに任せる」という判断自体が、MCP サーバーという仕組みになった。

## クロスポスト → Python スクリプト

記事が何本か溜まってきた頃、「Qiita にもクロスポストしたい」と Claude Code に伝えた。すると「Zenn の `:::message` や `:::details` は Qiita では表示されません。記法変換が必要です」と先に指摘してきた。

そのまま変換スクリプトを作ってもらい、`scripts/publish.py` ができあがった。

変換ルールは3つ。

- `:::message` → blockquote（`>` 記法）
- `:::details タイトル` → HTML の `<details>` タグ
- `/images/` → GitHub raw URL

```bash
# Qiita に新規投稿
python scripts/publish.py articles/my-article.md --platform qiita

# 既存記事を更新（タイトルで自動検索）
python scripts/publish.py articles/my-article.md --platform qiita --update auto
```

`--update auto` はタイトルの完全一致で既存記事を検索して更新する。Zenn 側を直したら `--update auto` で Qiita も追従、というワークフローが1コマンドで完結する。英語圏プラットフォーム（Dev.to、Hashnode）への誤投稿を防ぐガードも付いている。

**仕組み化の結果**: 手動コピペの記法崩れリスクが `publish.py` というスクリプトに置き換わった。さらにクロスポストの手順全体が `learned/zenn-qiita-crosspost-workflow` として自動抽出され、Claude Code がクロスポストを提案する際の手順書になっている。

## 仕組み化のサイクル

2週間で環境がこうなった。

```text
記事を書く（zenn-writer スキルがトーンを維持）
  → git commit → pre-commit hook が lint を自動実行
  → 「何文字？」→ MCP サーバーが正確にカウント
  → publish.py → 記法変換して Qiita/Dev.to に投稿
```

各問題とその仕組み化先を整理する。

| 問題 | 仕組み化先 | 種類 |
|------|-----------|------|
| トーンが毎回ぶれる | `zenn-writer` | スキル |
| lint エラー28件 | pre-commit hook | 設定 |
| markdownlint globs の罠 | `learned/zenn-markdownlint-config` | learned スキル |
| prh × Node.js 20 クラッシュ | `learned/prh-hyphen-regex-escape` | learned スキル |
| LLM の嘘文字数 | JapaneseTextAnalyzer MCP | 外部ツール接続 |
| クロスポストの記法崩れ | `scripts/publish.py` | スクリプト |
| クロスポスト手順 | `learned/zenn-qiita-crosspost-workflow` | learned スキル |

どれも最初から計画して作ったわけではない。記事を書く中で問題にぶつかり、Claude Code と一緒に解決し、その知見がスキルやスクリプトとして環境に残る。問題が起きるたびに環境が少し賢くなる。これが Claude Code で執筆環境を「育てる」ということだった。
