---
title: "Claude Code で Obsidian Vault 3,674ファイルを一括整理した"
emoji: "🗄️"
type: "tech"
topics: ["obsidian", "claudecode", "claude", "python"]
published: true
---

## はじめに

Evernote・Apple Notes・Apple Journal から書き出した 3,674 個の Markdown ファイルが、Obsidian Vault の中で眠っていました。frontmatter なし、タグなし、分類なし。Web クリップと自分の文章が混在し、重複ファイルが大量に存在する状態です。

これを Claude Code（Opus 4.6）を使って 1 日で整理しました。

| 指標 | Before | After |
|------|--------|-------|
| 総ファイル数 | 3,674 | 約 1,000 |
| frontmatter あり | 0 | 全件 |
| 重複ファイル | 2,751 | 0 |
| MOC (Map of Content) | 0 | 5 |
| プラグイン（設定済み） | 0 | 10 |
| テンプレート | 0 | 6 |

---

## なぜ Claude Code か

Obsidian にはコミュニティプラグインが豊富にあります。しかし 3,674 ファイルへの frontmatter 一括挿入やタグ付け、重複検出、プラグイン設定の JSON 調整となると、GUI 操作では現実的ではありません。

Claude Code なら、以下のような作業をシェルから一気に進められます。

- **Python スクリプトの生成と実行**: 分類ロジックを Python で書いて即実行
- **ファイル内容の個別判断**: 混在フォルダ内の 100 件超のファイルを 1 件ずつ読んで分類
- **プラグイン設定の JSON 編集**: 10 個分のプラグイン設定を一括で書き換え
- **試行錯誤のサイクル**: スクリプトが失敗したら修正して再実行、を高速に回す

要するに、**「大量のファイルに対して、ルールベース＋判断ベースの処理を混ぜて適用する」** という作業は Claude Code の得意領域です。

---

## Phase 1: frontmatter 一括挿入

### アプローチ

3,491 件の Markdown ファイルに、以下の構造の frontmatter を挿入する Python スクリプトを Claude Code に生成・実行してもらいました。

```yaml
---
category: tech        # tech / personal / creative / reference
type: fleeting        # fleeting / literature / permanent / moc
status: draft         # draft / review / done
tags:
  - 日記
  - 内省
source: evernote      # evernote / apple-notes / apple-journal
date: "2020-01-15"
---
```

フォルダ名からタグへのマッピングを 26 フォルダ分定義し、`bulk_frontmatter.py` で一括処理しました。3,491 件、エラー 0 です。

### ハマりポイント: macOS の NFD/NFC 問題

Apple Notes から書き出したファイルで、ファイル名のマッチングが謎の失敗を起こしました。原因は macOS ファイルシステムの **NFD（Normalization Form D）** です。

```python
# macOS のファイルシステムは NFD で格納する
# Python の文字列リテラルは NFC
# → マッチしない

import unicodedata

# 解決策: 比較前に NFC に正規化する
normalized = unicodedata.normalize("NFC", filename)
```

macOS 上で日本語ファイル名を扱う Python スクリプトを書くなら、`unicodedata.normalize("NFC")` は必須です。Obsidian に限らず、あらゆるファイル操作で発生しえます。

---

## Phase 2: 不要ファイルの削除

### 重複ファイル: 2,751 件削除

Evernote のエクスポートでは `filename 2.md` というパターンの重複ファイルが大量に生成されます。正規表現で検出し、オリジナルとの差分を確認したうえで削除しました。

### 薄いファイル: 1,196 件削除

文字数が極端に少ないファイル（50 文字以下、統計テーブルのみなど）を検出して削除しました。ただし一律削除ではなく、フォルダごとに閾値を変えています。たとえば日記系フォルダは短くても意味があるため除外しました。

### Web クリップの分離: 1,612 件をアーカイブ

ここが最も試行錯誤した部分です。

**失敗したアプローチ: ひらがな比率ヒューリスティック**

「自分の文章はひらがな比率が高い」という仮説でフィルタリングを試みました。結果は失敗です。日本語の Web 記事もひらがな比率は十分に高く、誤分類が大量に発生しました。

```python
# これは機能しなかった
def is_personal(text: str) -> bool:
    hiragana = sum(1 for c in text if '\u3040' <= c <= '\u309f')
    total = len(text)
    return hiragana / total > 0.3  # 閾値をどう設定しても精度が出ない
```

**成功したアプローチ: フォルダ単位の分類**

結局、Evernote 時代のフォルダ構造が最も信頼できる分類基準でした。「日記」「内省」など明らかに自分の文章が入るフォルダはそのまま残し、「Study」「Lifehack」など Web クリップ中心のフォルダは丸ごとアーカイブに移動しました。

混在するフォルダ（Inbox 等）だけ、Claude Code にファイルを 1 件ずつ読ませて判断しました。124 件中 47 件が自分の文章、77 件が Web クリップと判定され、精度は高かったです。

**教訓: 自然言語の統計的特徴でコンテンツの「出自」を判別するのは困難です。メタデータ（フォルダ構造・ファイル名パターン）のほうがはるかに信頼できます。**

---

## Phase 3: プラグイン設定の一括最適化

### 導入した 10 個のプラグイン

Obsidian の設定が落ち着いた後、以下のプラグインを導入・設定しました。

| プラグイン | 用途 | 設定のポイント |
|-----------|------|---------------|
| **Dataview** | メタデータベースのクエリ・ダッシュボード | JS クエリ・インライン有効化 |
| **Linter** | frontmatter の自動整形 | YAML キー順序の固定、重複タグ除去 |
| **Templater** | テンプレートエンジン | フォルダテンプレート連携 |
| **Tag Wrangler** | タグの一括リネーム・統合 | 77 個のタグを整理 |
| **Calendar** | カレンダービュー | ロケール ja、週開始を月曜に |
| **Auto Note Mover** | 新規ノートの自動振り分け | Inbox に集約、既存フォルダは除外 |
| **QuickAdd** | クイックキャプチャ | 用途別に 3 コマンド登録 |
| **Graph** | ナレッジグラフの可視化 | フォルダ別の色分け |
| **Smart Connections** | セマンティック検索・関連ノート | 日本語対応モデルに変更（後述） |
| **Periodic Notes** | Daily/Weekly/Monthly ノート | テンプレート連携 |

### Claude Code でプラグイン設定を編集する際の注意

Obsidian のプラグイン設定は `.obsidian/plugins/{plugin-name}/data.json` に保存されます。Claude Code でこの JSON を直接編集すれば、GUI でポチポチ設定する手間が省けます。ただし注意点があります。

**Obsidian が起動中は設定ファイルを編集しないでください。** Obsidian がメモリ上に設定を保持しているため、CLI で書き換えても次回保存時に上書きされます。編集は Obsidian を終了してから行いましょう。

### Vault ルート問題の発見

セッション中、プラグインの設定変更が一切反映されない問題に遭遇しました。原因を調査したところ、**Obsidian の Vault が 1 階層上のディレクトリに設定されていた**ことがわかりました。

```text
Documents/                  ← Obsidian が認識していた Vault ルート
├── .obsidian/              ← こちらの設定が有効だった
└── Obsidian Vault/
    ├── .obsidian/          ← こちらは無視されていた
    └── (実際のノート群)
```

`.obsidian` ディレクトリが 2 つ存在し、別の設定が使われていました。正しい方にマージして解決しています。

**教訓: プラグイン設定が反映されないときは、まず `find . -name ".obsidian" -type d` で `.obsidian` の場所を確認しましょう。**

### Smart Connections の日本語対応

Smart Connections はセマンティック検索で関連ノートを表示するプラグインです。デフォルトの埋め込みモデル `TaylorAI/bge-micro-v2` は英語特化であり、日本語 Vault では精度が出ません。

さらに厄介なことに、**このプラグインの設定は `data.json` ではなく `.smart-env/smart_env.json` に保存されます**。ドキュメントにほぼ記載がなく、`main.js` を読んで判明しました。

```json
// .smart-env/smart_env.json
{
  "smart_sources": {
    "embed_model": {
      "model_key": "Xenova/multilingual-e5-small"
    }
  }
}
```

モデルを `Xenova/multilingual-e5-small`（多言語対応）に変更し、埋め込みデータをクリアして再インデックスしました。日本語ノート間の関連性が正しく表示されるようになっています。

**教訓: Obsidian プラグインの設定ファイルは `data.json` とは限りません。設定が反映されないときは `.obsidian/plugins/{plugin}/` 以外の場所も疑いましょう。**

---

## MOC とダッシュボード

整理したノートを活用するために、5 つの MOC（Map of Content）と Dataview ダッシュボードを作成しました。

MOC は特定テーマのノートを手動リンクと Dataview クエリの組み合わせで一覧するファイルです。たとえば以下のような Dataview クエリで、特定タグのノートを自動一覧できます。

```dataview
TABLE date, status
FROM #瞑想
SORT date DESC
```

ダッシュボードには、ステータス別のノート数や最近更新したノート、未分類ノートの一覧などを表示しました。Dataview の JS クエリを有効化しておくと、より柔軟な集計が可能です。

---

## Claude Code で Obsidian を扱う際の Tips

### 1. iCloud 上のファイル操作は問題ない

iCloud Drive 上の Obsidian Vault で、Claude Code から `.md` ファイルの読み書きや Python スクリプトを実行しましたが、同期の問題は発生しませんでした。ただしプラグイン設定ファイル（`.obsidian/` 以下）は Obsidian を終了してから編集してください。

### 2. Python スクリプトは「生成して実行」が最速

Claude Code に直接 3,674 ファイルを読ませるのはトークン的に非現実的です。代わりに「Python スクリプトを生成→実行→結果を確認→修正→再実行」のサイクルを回すのが効率的でした。実際に使ったスクリプトは 5 本です。

| スクリプト | 用途 | 処理件数 |
|-----------|------|---------|
| `bulk_frontmatter.py` | frontmatter 一括挿入 | 3,491 |
| `apple_notes_folders.py` | サブフォルダベースの分類 | 66 |
| `apple_notes_root.py` | 内容分析ベースの分類 | 86 |
| `vault_audit.py` | タグ分布・欠損検出 | 全件 |
| `tag_cleanup.py` | タグ統合・リネーム | 全件 |

### 3. 日本語ファイル名は NFC 正規化を忘れずに

前述の通り、macOS + 日本語ファイル名 + Python の組み合わせでは `unicodedata.normalize("NFC")` が必須です。ファイル検索、パターンマッチ、辞書のキー比較――あらゆる場面で NFD/NFC の不一致が起こりえます。

### 4. 失敗を前提にバックアップを取る

最初に `tar.gz` でバックアップを取ってから作業を始めました。実際、ひらがな比率による分類の失敗後、バックアップからの復元が必要になりました。大量ファイル操作では「とりあえず試す→ダメなら戻す」を高速に回せるバックアップ体制が重要です。

---

## まとめ

Claude Code で Obsidian Vault 3,674 ファイルの整理を 1 日で完了しました。技術的な要点をまとめます。

1. **大量ファイル処理は Python スクリプト生成→実行が最速**。Claude Code に全ファイルを読ませるのではなく、処理ロジックをコードに落とす
2. **統計的ヒューリスティックより、メタデータ（フォルダ構造）のほうが信頼できる**。ひらがな比率でのコンテンツ分類は失敗した
3. **プラグイン設定の JSON 直接編集は強力だが、Obsidian 終了後に行うこと**。Vault ルート問題や `data.json` 以外の設定ファイルにも注意
4. **Smart Connections の日本語対応は `multilingual-e5-small` モデルに変更**。設定は `.smart-env/smart_env.json`
5. **macOS + 日本語ファイル名は NFD/NFC 正規化が必須**

Claude Code はコードを書くだけのツールではありません。ファイルシステム上のあらゆる「整理」作業に使えます。特に、ルールベースの一括処理と内容ベースの個別判断を組み合わせられるのが強みです。
