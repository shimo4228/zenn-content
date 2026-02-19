---
title: "Claude Code で日本語テキスト分析 MCP サーバーを使う — kuromoji.js"
emoji: "🇯🇵"
type: "tech"
topics: ["claudecode", "mcp", "自然言語処理", "日本語"]
published: false
---

## やりたいこと

「この記事は何文字？」と Claude Code に聞いたら「約2,800文字です」と返ってきました。実際に数えたら3,200文字。LLM は日本語のトークン境界を正確に扱えないため、推測ベースの回答になります。

Claude Code で Zenn の記事を書いているとき、文字数や読みやすさを正確に知りたい場面は頻繁にあります。英語なら単語数を数えるだけですが、日本語はスペースで区切られないため、形態素解析が必要です。

MCP（Model Context Protocol）サーバーとして日本語テキスト分析ツールを接続することで、Claude Code の会話内から直接テキスト分析ができるようになります。

## MCP サーバーの設定

`~/.claude.json` の `mcpServers` にキーを追加します。

:::message
`~/.claude.json` は Claude Code が自動管理するファイルです。**ファイル全体を上書きしないでください**。既存の内容を保持したまま `mcpServers` オブジェクトにキーを追加する形で編集してください。
<!-- textlint-disable ja-technical-writing/ja-no-mixed-period -->
:::
<!-- textlint-enable ja-technical-writing/ja-no-mixed-period -->

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

初回起動時に npm パッケージが自動ダウンロードされます。kuromoji.js（形態素解析エンジン）を内蔵しているため、追加の辞書インストールは不要です。

:::message
GitHub リポジトリから直接インストールするため、`npm audit` によるセキュリティチェックが効きません。本番環境で使う場合はコミットハッシュを固定することを推奨します。
<!-- textlint-disable ja-technical-writing/ja-no-mixed-period -->
:::
<!-- textlint-enable ja-technical-writing/ja-no-mixed-period -->

## できること

ツールは大きく2種類あります。**ファイルパス系**（`count_chars`, `count_words`, `analyze_file`）はファイルを指定して分析します。**インラインテキスト系**（`count_clipboard_chars`, `count_clipboard_words`, `analyze_text`）はテキストを直接渡します。

> 以下の出力例はイメージです。実際の値は記事の内容によって変わります。

### 文字数カウント

ファイルまたはテキストの文字数を計測します。スペースと改行を除いた実質的な文字数です。

```text
me: この記事の文字数を教えて
Claude Code: [JapaneseTextAnalyzer.count_chars を実行]
→ 2,556文字（改行・スペース除外）
```

### 単語数カウント

kuromoji.js による形態素解析で日本語の単語数を計測します。

```text
me: この記事の単語数は？
Claude Code: [JapaneseTextAnalyzer.count_words を実行]
→ 850単語
```

### テキスト分析

品詞の割合、語彙の多様性、文の複雑さなどを定量評価します。

```text
me: この段落の読みやすさを分析して
Claude Code: [JapaneseTextAnalyzer.analyze_text を実行]
→ 名詞: 35%, 動詞: 18%, 助詞: 25%
→ 平均文長: 45文字
→ 語彙多様性: 0.72
```

## 実際の使い方

### 執筆中の文字数確認

Zenn 記事は2,000〜4,000字が読みやすい範囲です。執筆の途中で文字数を確認し、分量を調整します。

```text
me: articles/claude-code-auto-memory.md の文字数を確認して
Claude Code: 2,556文字です。ちょうどよい分量です。
```

### 公開前の品質チェック

`analyze_text` で文の複雑さや品詞バランスを確認できます。名詞が多すぎる場合は説明が足りていない可能性があり、動詞を増やして具体的な手順を補足します。

### クリップボードのテキスト分析

ファイルに保存していないテキストも分析できます。`count_clipboard_chars` や `analyze_text` にテキストを直接渡します。

## なぜ MCP サーバーか

Claude Code 自体も文字数を数えられますが、日本語の形態素解析は LLM の得意分野ではありません。kuromoji.js の辞書ベースの解析のほうが正確です。

MCP サーバーとして接続するメリットは以下の通りです。

- Claude Code の会話フローを中断せずに分析できる
- ファイルパスを渡すだけで自動的に読み込んで分析する
- 形態素解析の結果を Claude Code が解釈して改善提案を出せる

## セットアップのポイント

**グローバル設定に置く**: `~/.claude.json` へ追加すると全プロジェクトで使えます。日本語分析はプロジェクトを問わず使う機能なので、プロジェクト固有の設定にする必要はありません。

**初回は時間がかかる**: `npx -y` で初回起動時にパッケージのダウンロードと kuromoji.js の辞書読み込みが走ります。環境によっては10〜15秒かかることがあります。2回目以降はキャッシュが効いて数秒で応答します。

## まとめ

- MCP サーバーで kuromoji.js の日本語テキスト解析を Claude Code に接続できる
- 文字数・単語数カウント、品詞分析、読みやすさ評価が会話の中で完結する
- `~/.claude.json` に設定を追加するだけで全プロジェクトから利用可能
- LLM の推測に頼らず、辞書ベースの正確な解析結果が得られる

次のステップとして、分析結果から記事の改善提案を Claude Code へ出させるワークフローを試してみてください。
