---
title: "prh と Node.js 20 で正規表現エラーが出たときの対処法"
emoji: "⚠️"
type: "tech"
topics: ["nodejs", "textlint", "正規表現", "トラブルシューティング"]
published: true
---

## 症状

Node.js を 18 から 20 にアップグレードした翌日、CI の textlint が突然クラッシュしました。コードは一切変えていないのに。

textlint + prh で表記ゆれチェックを設定し、`prh.yml` にハイフンを含むパターンを書くと、以下のエラーが出ます。

```text
SyntaxError: Invalid regular expression: /Claude\-Native/v: Invalid escape
```

Node.js 18 以前では動いていたのに、Node.js 20 以降で突然クラッシュする場合はこのパターンです。

## 原因

Node.js 20 は V8 エンジン v11.3 以降を搭載しており、正規表現の **Unicode Sets mode (`v` flag)** をサポートしています。prh は内部で正規表現を `v` フラグ付きでコンパイルするため、`\-`（バックスラッシュ + ハイフン）がリテラルハイフンのエスケープとして認識されず、構文エラーになります。

従来の `u` フラグでは `\-` が許容されていましたが、`v` フラグではより厳格な構文チェックが行われます。

## 再現する prh.yml

```yaml
# NG: Node.js 20+ でクラッシュ
- expected: Claude-Native
  pattern: /Claude\-Native/
```

## 対処法

### 方法1: patterns を使う（正規表現を避ける）

```yaml
# OK: 文字列マッチを使う
- expected: Claude-Native
  patterns:
    - Claude based
    - claude native
```

`patterns` はリテラル文字列として指定します（内部で正規表現に変換されるため、`\-` のような手動エスケープは不要です）。`Claude-Native` のようにハイフンを含む文字列もそのまま書けます。

### 方法2: 文字クラスでハイフンを安全に扱う

```yaml
# OK: 文字クラスの先頭にハイフンを置く（v フラグでも有効）
- expected: Claude-Native
  pattern: /Claude[-]Native/
```

文字クラス `[...]` 内でハイフンを使う場合は、先頭か末尾に置きます。

```yaml
# NG
pattern: /[a\-z]/

# OK: ハイフンを先頭に
pattern: /[-az]/

# OK: ハイフンを末尾に
pattern: /[az-]/
```

### 方法3: ハイフン含むパターン自体を prh に書かない

私が採用した方法です。`prh.yml` にはハイフンを含まないパターンだけを書き、ハイフン入りの用語統一は別の手段（レビュー時のチェックリスト等）で対応します。

```yaml
# prh.yml — ハイフンを含むパターンは書かない方針
- expected: GitHub
  patterns:
    - Github

- expected: TypeScript
  patterns:
    - Typescript
```

## 確認方法

```bash
node -v   # v20 以上か確認
npx textlint articles/test.md   # クラッシュしないことを確認
```

## 移行チェックリスト

Node.js 20 にアップグレードするとき、prh.yml を以下の手順で確認してください。

1. `prh.yml` で `\-` を含む `pattern` を検索する
2. 該当するルールを `patterns`（リテラル文字列）に書き換える、または文字クラス `[-]` で回避する
3. `npx textlint articles/任意の記事.md` でクラッシュしないことを確認する
4. `node -v` が v20 以上であることを確認する

**要点**: `pattern`（正規表現）でハイフンを使うとクラッシュする。`patterns`（リテラル文字列）なら安全。
