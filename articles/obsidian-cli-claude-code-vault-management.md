---
title: "Obsidian公式CLIが来た——もうVaultを裏口から触らなくていい"
emoji: "⌨️"
type: "tech"
topics: ["obsidian", "cli", "claudecode", "claude", "自動化"]
published: true
---

`mv` した瞬間、ウィキリンクが 47 本切れた。

3,674 ファイルの Obsidian Vault を Claude Code で整理していたとき、ファイル移動のたびにリンク切れを手動で直していた。プラグイン設定の JSON を書き換えたら Obsidian が上書きして消えた。frontmatter の一括挿入は Python スクリプトを 5 本書いて乗り切ったが、Obsidian のインデックスは知らん顔だった。

**Obsidian の外からファイルを触るのは、裏口から忍び込む行為だった。**

2026年2月27日、Obsidian 1.12.4 で公式 CLI がリリースされた。正面玄関が開いた。

<!-- textlint-disable -->
:::message
本記事の前提となる Vault 整理の詳細は、前回の記事「[3,674ファイルのObsidian地獄をClaude Codeに1日で片付けさせた](https://zenn.dev/shimo4228/articles/claude-code-obsidian-vault-organization)」を参照してほしい。
:::
<!-- textlint-enable -->

---

## 「リモコン」であって「ヘッドレスツール」ではない

Obsidian CLI は、Obsidian 1.12.0（2026年2月10日）で Catalyst メンバー向けに早期アクセスが開始された。v1.12.4（2026年2月27日）で全ユーザーに一般公開された**公式コマンドラインインターフェース**だ。別途インストールは不要で、一般公開版は Catalyst ライセンスも不要。

重要な設計原則がある。**CLI は起動中の Obsidian アプリの「リモコン」として動作する**。スタンドアロンのヘッドレスツールではない。Obsidian が起動していない状態で CLI コマンドを実行すると、自動的に Obsidian が起動する。

これが何を意味するかというと、CLI 経由の操作はすべて **Obsidian の内部 API を通る**。ファイルの移動ではウィキリンクを自動更新し、プロパティの変更はインデックスへ即座に反映される。直接ファイル操作で発生していたリスクが、設計レベルで解消されている。

---

## セットアップ

### 1. Obsidian を 1.12.4 以降に更新

[obsidian.md](https://obsidian.md) から最新版をインストールする。

### 2. CLI を有効化

Obsidian を開き、**設定 → 一般 → Command line interface** をオンにして、「Register CLI」をクリックする。

### 3. PATH を通す

macOS の場合、`~/.zshrc` に以下を追加する。

```bash
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
```

Windows・Linux もそれぞれバイナリのパスを環境変数に追加する。

### 4. 動作確認

```bash
obsidian version
```

バージョン番号が表示されれば準備完了だ。

---

## 100 超のコマンドを 8 カテゴリで把握する

Obsidian CLI のコマンドは大きく **8 つのカテゴリ**に分類できる。

| カテゴリ | 主なコマンド | 用途 |
|----------|-------------|------|
| **ファイル操作** | `files`, `read`, `create`, `append`, `move`, `delete` | ノートの CRUD |
| **プロパティ** | `properties`, `property:set`, `property:remove` | frontmatter 操作 |
| **検索** | `search`, `search:context` | 全文検索 |
| **タグ** | `tags`, `tag`, `tags:rename` | タグ管理・一括リネーム |
| **リンク** | `links`, `backlinks`, `unresolved`, `orphans` | リンク構造の分析 |
| **Daily Notes** | `daily`, `daily:append`, `daily:read` | デイリーノート操作 |
| **プラグイン** | `plugins`, `plugin:enable`, `plugin:disable` | プラグイン管理 |
| **開発者ツール** | `eval`, `dev:screenshot`, `devtools` | JS 実行・デバッグ |

### コマンド構文

```bash
obsidian <command> [param=value] [flag]
```

パラメータは `key=value` 形式、フラグはベアワード（`--` なし）で指定する。唯一の例外は `--copy`（クリップボードにコピー）で、これだけ `--` 付きだ。

複数 Vault がある場合は `vault="Vault名"` を付ける。

```bash
obsidian vault="仕事" search query="TODO"
```

---

## `mv` でリンクを壊す日々は終わった

前回の Vault 整理では、ファイルを `mv` するたびにウィキリンクが切れないか怯えていた。CLI なら、その恐怖から解放される。

### 一覧・読み取り

```bash
# Vault 内の全ノートを一覧
obsidian files

# フォルダ構造をツリー表示
obsidian folders

# ノートの内容を読み取り
obsidian read file="日記/2024-01-15"

# ノートのメタデータを表示
obsidian file file="プロジェクトA"
```

### 作成・追記

```bash
# 新規ノート作成
obsidian create name="議事録/2026-03-04" content="# 定例会議"

# テンプレートから作成
obsidian create name="読書メモ/影響力の武器" template="BookNote"

# 末尾に追記
obsidian append file="プロジェクトA" content="\n\n## 進捗メモ\n- タスクB完了"

# frontmatter の後に挿入（prepend）
obsidian prepend file="日記/2026-03-04" content="天気: 晴れ"
```

### 移動・削除

```bash
# 移動（ウィキリンクを自動更新）
obsidian move file="Inbox/メモ" to="Archive/"

# ゴミ箱へ移動
obsidian delete file="不要なノート"

# 完全削除（ゴミ箱を経由しない）
obsidian delete file="不要なノート" permanent
```

`move` コマンドは**ウィキリンクを自動で書き換える**。これは直接 `mv` コマンドでファイルを移動していた時代との最大の違いだ。前回の Vault 整理では、ファイル移動後にリンク切れが発生しないか手動で確認していた。CLI なら不要になる。

---

## 3,491 件の frontmatter を 1 件ずつ手で直す？

前回の Vault 整理で最も工数がかかったのは、3,491 件への frontmatter 一括挿入だった。Python スクリプト `bulk_frontmatter.py` を書いて処理した。

CLI なら `property:set` で 1 ファイルずつ操作できる。

```bash
# frontmatter のプロパティを確認
obsidian properties file="メモ"

# プロパティを設定
obsidian property:set file="メモ" name="category" value="tech"
obsidian property:set file="メモ" name="status" value="draft"

# プロパティを削除
obsidian property:remove file="メモ" name="status"
```

ただし、3,491 件に対して 1 件ずつ `property:set` を実行するのは現実的でない。**大量の一括処理なら、依然として Python スクリプトのほうが効率的だ**。CLI の `property:set` が威力を発揮する場面は、個別ノートの修正やスクリプトの後処理だ。

```bash
# シェルスクリプトで一括処理する例
obsidian files | while read -r f; do
  obsidian property:set file="$f" name="status" value="review"
done
```

---

## `grep -r` で Vault を探っていた時代の終わり

```bash
# 全文検索
obsidian search query="TODO"

# コンテキスト付き検索（grep ライク）
obsidian search:context query="ボトルネック" limit=10

# GUI の検索パネルを開く
obsidian search:open
```

`search:context` は検索結果の前後の行も表示する。ターミナルで `grep -C` のように使える。

---

## 77 個のタグを GUI でリネームした日を思い出す

前回、77 個のタグを整理するのに Tag Wrangler プラグインを使った。CLI なら `tags:rename` で一括リネームできる。

```bash
# 全タグを一覧
obsidian tags

# 特定タグを持つファイルを一覧
obsidian tag tag="#プロジェクト"

# タグの一括リネーム（Vault 全体に適用）
obsidian tags:rename old=meeting new=meetings
obsidian tags:rename old=日記 new=journal
```

`tags:rename` は Vault 内の全ファイルを横断してタグを書き換える。Tag Wrangler を GUI で操作するより遥かに速い。

---

## リンクが切れていることに気づかない問題

Obsidian の本質はリンクによるナレッジグラフだ。しかし、リンクが切れていても Obsidian は教えてくれない。CLI でリンク構造を分析できる。

```bash
# 発リンク（このノートからリンクしている先）
obsidian links file="MOC-読書"

# 被リンク（このノートにリンクしているノート）
obsidian backlinks file="Zettelkasten"

# 未解決リンク（リンク先ファイルが存在しない）
obsidian unresolved

# 孤立ノート（どこからもリンクされていない）
obsidian orphans
```

`orphans` と `unresolved` は Vault のヘルスチェックに使える。週次で cron 実行してレポートを生成する、といった運用が可能になる。

---

## 朝のルーティンをターミナルから回す

```bash
# 今日の Daily Note を開く（なければ作成）
obsidian daily

# 今日の Daily Note に追記
obsidian daily:append content="- [ ] 記事のレビュー"

# 今日の内容を表示
obsidian daily:read

# Daily Note のファイルパスを表示
obsidian daily:path
```

`daily:append` は朝のルーティンに組み込める。cron や Alfred/Raycast のワークフローから呼び出せば、ターミナルからタスクを追加できる。

---

## data.json を直接編集して設定が消えた教訓

前回の記事で `.obsidian/plugins/{name}/data.json` を直接編集して痛い目にあった。CLI ならプラグインの有効化・無効化を安全に行える。

```bash
# インストール済みプラグインの一覧
obsidian plugins

# プラグインの有効化・無効化
obsidian plugin:enable id=dataview
obsidian plugin:disable id=calendar

# プラグインのホットリロード（開発者向け）
obsidian plugin:reload id=my-plugin
```

テーマや CSS スニペットの管理もできる。

```bash
# テーマ一覧・切り替え
obsidian themes
obsidian theme:set name="Minimal"

# CSS スニペットの管理
obsidian snippets
```

---

## `eval` で Obsidian の内部に手を突っ込む

CLI で最も自由度の高いコマンドが `eval` だ。Obsidian の内部 API（`app` オブジェクト）に直接アクセスできる。

```bash
# Vault 内のファイル数を取得
obsidian eval code="app.vault.getFiles().length"

# アクティブなファイルの情報を取得
obsidian eval code="app.workspace.getActiveFile()?.path"

# DevTools を開く
obsidian devtools

# スクリーンショットを撮る（base64 PNG）
obsidian dev:screenshot

# コンソールメッセージを表示
obsidian dev:console

# JS エラーを表示
obsidian dev:errors
```

`eval` は Obsidian のプラグイン API にフルアクセスできるため、CLI の標準コマンドでカバーされない操作も実行可能だ。ただし、**内部 API を直接叩くため、バージョンアップで動作の変わるリスクがある**。安定した処理には標準コマンドを使い、`eval` はデバッグや一時的な調査に留めるのが安全だ。

---

## jq に渡せる、スプレッドシートに流せる

`search` など一部のコマンドは `format=` パラメータで出力形式を切り替えられる。スクリプティングに欠かせない機能だ。対応コマンドは `obsidian help <command>` で確認してほしい。

| フォーマット | 用途 |
|-------------|------|
| `json` | jq でパイプ処理 |
| `csv` / `tsv` | スプレッドシートへのエクスポート |
| `md` | Markdown 形式 |
| `paths` | ファイルパスのみ（パイプ用） |
| `text` | 人間向け（デフォルト） |
| `tree` | フォルダ階層表示 |
| `yaml` | YAML 形式（プロパティ表示のデフォルト） |

```bash
# search は format=json に対応
obsidian search query="TODO" format=json | jq '.[].file'

# ファイル一覧を xargs に渡す
obsidian tag tag="#archive" | xargs -I{} obsidian move file="{}" to="Archive/"

# クリップボードにコピー
obsidian read file="共有メモ" --copy
```

---

## GUI を開かずにファイルを選ぶ——TUI モード

引数なしで `obsidian` を実行すると、**フルスクリーンの TUI（Terminal User Interface）**が起動する。

| キー | 操作 |
|------|------|
| 矢印キー | ファイルを選択 |
| `/` | ファイル名でフィルタ |
| `Enter` | Obsidian で開く |
| `n` | 新規ノート作成 |
| `d` | ファイル削除 |
| `r` | リネーム |
| `Ctrl+R` | コマンド履歴検索 |
| `q` | 終了 |

タブ補完とコマンド履歴にも対応している。ターミナルから離れずに Vault を操作したいときに便利だ。

---

## あの 3,674 ファイル整理、CLI があったらどうなっていたか

ここからが本題だ。前回の記事では「Claude Code + Python スクリプト + 直接ファイル操作」で Vault を整理した。Obsidian CLI の登場で、このワークフローがどう変わるか。

### Before: Python で直接ファイル操作

```python
# 前回のアプローチ: Python でファイルを直接読み書き
import os
import yaml

for root, dirs, files in os.walk(vault_path):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'r') as fh:
                content = fh.read()
            # 既存の frontmatter チェックなし — バグの温床
            new_content = f"---\ncategory: tech\n---\n{content}"
            with open(path, 'w') as fh:
                fh.write(new_content)
```

**問題点:**

- Obsidian のインデックスが更新されない
- ファイル移動でウィキリンクが切れる
- Obsidian 起動中に編集すると競合する
- NFD/NFC 問題を自前で処理する必要がある

### After: CLI 経由で操作

```bash
# CLI 経由なら Obsidian の内部 API を通る
obsidian property:set file="メモ" name="category" value="tech"

# ファイル移動もリンクが自動更新される
obsidian move file="Inbox/メモ" to="Tech/"
```

**解決される問題:**

- インデックスは自動更新
- ウィキリンクは自動で書き換え
- Obsidian 起動中でも安全に操作可能
- ファイルパスの正規化は Obsidian が処理

### 実践: Claude Code から CLI を呼ぶ

Claude Code に Obsidian CLI を使わせることで、Vault 操作の安全性が格段に上がる。

```bash
# Claude Code に指示する例:
# 「Inbox フォルダのノートを内容に応じて分類して」

# Claude Code が生成するスクリプト:
obsidian tag tag="#inbox" | while read -r note; do
  content=$(obsidian read file="$note")
  # Claude Code が内容を判断して適切なフォルダに移動
  obsidian move file="$note" to="Tech/"
  obsidian property:set file="$note" name="category" value="tech"
done
```

### 使い分けの判断基準

CLI があればすべて解決するわけではない。用途に応じた使い分けが重要だ。

| 操作 | 推奨アプローチ | 理由 |
|------|---------------|------|
| 個別ノートの作成・移動 | **CLI** | リンク保持、インデックス更新 |
| frontmatter の個別修正 | **CLI** (`property:set`) | 安全、手軽 |
| 3,000 件への一括処理 | **Python スクリプト** | CLI の逐次実行は遅い |
| タグの一括リネーム | **CLI** (`tags:rename`) | 1 コマンドで完了 |
| 孤立ノートの検出 | **CLI** (`orphans`) | 専用コマンドが存在 |
| 内容ベースの分類判断 | **Claude Code + CLI** | AI 判断 + 安全な操作 |
| プラグイン設定の変更 | **CLI** (`plugin:enable/disable`) | 安全 |
| 複雑なプラグイン設定 | **JSON 直接編集**（Obsidian 終了後） | CLI 未対応の設定がある |

---

## 整理した Vault は放っておくと再び散らかる

CLI の真価は自動化にある。一度整理しても、ノートを追加し続ければ孤立ファイルや未解決リンクは自然に増える。cron やスクリプトで定期的に Vault の状態を監視できる。

```bash
#!/bin/bash
# vault-health.sh — 週次 Vault ヘルスチェック

echo "=== Obsidian Vault Health Report ==="
echo "Date: $(date)"
echo ""

echo "## ファイル統計"
obsidian files total

echo "## 孤立ノート"
obsidian orphans

echo "## 未解決リンク"
obsidian unresolved

echo "## タグ分布（上位 10 件）"
obsidian tags
```

これを cron で週次実行し、結果を Daily Note に追記する。

```bash
# crontab -e
0 9 * * 1 obsidian daily:append content="$(/path/to/vault-health.sh)"
```

---

## 制限事項

Obsidian CLI は Vault 操作の大半をカバーするが、知っておくべき制限がある。

1. **Obsidian が起動していないと動かない**: CLI はリモコンであり、ヘッドレスツールではない。初回コマンド実行時に自動起動するが、起動完了まで待つ必要がある
2. **デスクトップ限定**: モバイル版（iOS / Android）には CLI がない
3. **複数 Vault**: デフォルトではアクティブな Vault に接続する。複数 Vault を使う場合は毎回 `vault="名前"` を指定する必要がある
4. **大量の逐次実行は遅い**: 各コマンドが Obsidian アプリとの通信を伴うため、数千件の一括処理に向かない。Python スクリプトで直接操作するほうが高速な場合もある
5. **Windows の Unicode 問題**: v1.12.4 で修正済みだが、以前のバージョンでは日本語パスで問題が発生していた

---

## Vault は「整理するもの」から「運用するもの」になった

Obsidian に CLI が入ったことの本質は、コマンドが増えたことではない。**Vault がコードで制御可能なシステムになった**ことだ。

前回の記事で裏口から忍び込んでいた操作が、すべて正面玄関から行える。リンクは自動で更新され、インデックスは壊れず、設定は競合しない。

ただし、3,000 件超の一括処理は依然として Python スクリプトが速い。CLI は万能ではない。「安全な操作は CLI で、力仕事はスクリプトで」——これが現実的な使い分けだ。

`obsidian orphans` を 1 回叩いてみてほしい。自分の Vault がどれだけ散らかっているか、数字で突きつけられる。

## 関連記事

道具の話はここまで。一段奥の、エージェント設計そのものの話:

- [コーディングエージェントの知識をどこに置き、どう守らせるか](https://zenn.dev/shimo4228/articles/coding-agent-memory-architecture)
- [推論でもツールでもない — AIエージェントの本質は「記憶」ではないか](https://zenn.dev/shimo4228/articles/agent-essence-is-memory)

研究としての成果物（DOI 付き）は [github.com/shimo4228](https://github.com/shimo4228) に。
