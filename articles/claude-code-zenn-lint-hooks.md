---
title: "Claude Code × Zenn 執筆に textlint + markdownlint の hooks を設定する"
emoji: "🔧"
type: "tech"
topics: ["claudecode", "zenn", "textlint", "markdownlint"]
published: false
---

Claude Code で Zenn 記事を3本書いたあと、まとめて lint を回したら28件のエラーが出ました。全角スペース混入、見出しレベルの飛び、表記ゆれ――手動チェックでは漏れるものばかりです。

「コミット前に自動で止めてくれれば、こんな手戻りは起きない」

pre-commit hook で textlint と markdownlint を強制実行する仕組みを作りました。

## 構成の全体像

```text
package.json          ← lint-staged の設定
.husky/pre-commit     ← husky の hook
.textlintrc.json      ← textlint の設定
.markdownlint-cli2.jsonc ← markdownlint の設定
prh.yml               ← 表記ゆれ辞書
```

## セットアップ

### 1. パッケージのインストール

```bash
npm install -D textlint textlint-rule-preset-ja-technical-writing \
  textlint-rule-prh textlint-rule-no-dead-link \
  textlint-filter-rule-comments \
  markdownlint-cli2 husky lint-staged
```

### 2. husky の初期化

```bash
npx husky init
```

`.husky/pre-commit` に以下を書きます。

```bash
npx lint-staged
```

### 3. lint-staged の設定

`package.json` に追加します。

```json
{
  "lint-staged": {
    "articles/**/*.md": [
      "textlint",
      "markdownlint-cli2"
    ],
    "books/**/*.md": [
      "textlint",
      "markdownlint-cli2"
    ]
  }
}
```

ステージされた `.md` ファイルだけが lint 対象になります。

### 4. textlint の設定

`.textlintrc.json` を作成します。

```json
{
  "filters": {
    "comments": true
  },
  "rules": {
    "preset-ja-technical-writing": {
      "no-exclamation-question-mark": false,
      "ja-no-mixed-period": {
        "periodMark": "。",
        "allowPeriodMarks": ["："]
      }
    },
    "no-dead-link": {
      "checkRelative": true,
      "ignore": ["https://localhost*"],
      "retry": 3
    },
    "prh": {
      "rulePaths": ["prh.yml"]
    }
  }
}
```

`filters.comments` を有効にすると、`<!-- textlint-disable -->` で部分的にルールを無効化できます。Zenn 記事では意図的にくだけた表現を使う箇所で便利です。

### 5. markdownlint の設定

`.markdownlint-cli2.jsonc` を作成します。

```jsonc
{
  "config": {
    "MD013": false,
    "MD025": false,
    "MD041": false,
    "MD060": false,
    "MD034": false,
    "MD036": false,
    "MD033": {
      "allowed_elements": ["details", "summary", "br"]
    }
  },
  "ignores": ["node_modules", "drafts", ".zenn"]
}
```

Zenn 固有の無効化ルールを解説します。

- **MD013** (行の長さ制限): 日本語は1行が長くなるため無効化
- **MD025** (H1 は1つだけ): Zenn はフロントマターの title が H1 相当。本文の `#` は H1 ではない
- **MD041** (先頭行は見出し): フロントマターが先頭なので不要
- **MD034** (裸の URL): Zenn は行単独の URL をリッチ埋め込みに変換する仕様
- **MD036** (強調テキストを見出し代わりにしない): Zenn 記事では太字をサブ見出しとして使う慣習がある
- **MD060** (コードスパン内のスペース): Zenn の `:::message` など独自記法をインラインコードで書く際に誤検知する

### 6. prh（表記ゆれ辞書）

`prh.yml` で用語を統一します。

```yaml
version: 1
rules:
  - expected: GitHub
    patterns:
      - Github

  - expected: サーバー
    pattern: /サーバ(?!ー)/
```

## ハマりポイント2つ

### markdownlint の config に glob を書かない

`.markdownlint-cli2.jsonc` の `globs` フィールドにパターンを書くと、lint-staged 経由でもそのパターンが優先されます。結果、ステージされたファイルだけでなく**全ファイルが lint される**ことになります。

```jsonc
// NG: lint-staged と競合する
{
  "globs": ["articles/**/*.md"]
}
```

glob は config に書かず、lint-staged 側で制御してください。

### prh にハイフン含むパターンを書かない

Node.js 20 以降、正規表現の Unicode モードがデフォルトで有効です。`\-`（エスケープされたハイフン）がリテラルハイフンとして認識されず、textlint がクラッシュします。

```yaml
# NG: Node.js 20+ でクラッシュ
- expected: Claude-Native
  pattern: /Claude\-Native/

# OK: patterns を使う（リテラル文字列マッチ）
- expected: Claude-Native
  patterns:
    - claude-native
    - Claude native
```

`patterns`（文字列マッチ）で代替するか、ハイフンを含まない正規表現パターンに書き換えてください。

## 動作確認

```bash
# 手動で全ファイルを lint
npm run lint:all

# Git commit で自動 lint（ステージされたファイルのみ）
git add articles/my-article.md
git commit -m "feat: 新しい記事を追加"
# → textlint と markdownlint が自動実行される
```

エラーがあればコミットがブロックされます。修正してから再度コミットしてください。

## この設定で変わったこと

導入前は記事を5〜6本書き溜めてからまとめて lint を回し、大量のエラーと格闘していました。pre-commit hook にしてからは、コミットのたびに1〜2件ずつ修正するだけで済みます。

残課題として、`no-dead-link` ルールはネットワークアクセスが必要なため、オフライン環境では pre-commit hook がタイムアウトすることがあります。CI 側で dead link チェックを行い、ローカルでは `--no-verify` で一時的にスキップする運用も選択肢です。
