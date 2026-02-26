---
title: "毎回コンテキストを失う Claude Code に記憶を埋め込んだ"
emoji: "🧠"
type: "idea"
topics: ["claudecode", "ai", "mcp", "生産性"]
published: false
---

Claude Code は強力だが、セッションをまたぐと記憶を失う。CLAUDE.md の auto memory で確定した知見は残せるが、手動で書かなければ記録されない。「前回どこまで調べた」「どのファイルを編集した」といったセッションの行動コンテキストは毎回消える。これが痛い。

この問題に対して Mem0 と claude-mem という2つのアプローチを試した。本記事では、その過程で得た知見と、それぞれの特性を整理する。

<!-- textlint-disable no-dead-link -->
<!-- textlint-disable ja-technical-writing/ja-no-successive-word -->

なお、5層のコンテキストスタックという設計思想は以前の記事「[Claude Code の真価はコード生成ではない](https://zenn.dev/shimo4228/articles/claude-code-context-orchestration)」で書いた。本記事はその第5層──セッション間の「記憶」を実際にどう構築したかの実践記録となる。

<!-- textlint-enable ja-technical-writing/ja-no-successive-word -->
<!-- textlint-enable no-dead-link -->

## アプローチ1：Mem0（MCP サーバー）

### Mem0 とは

[Mem0](https://github.com/mem0ai/mem0) は AI アプリケーション向けのメモリレイヤーだ。MCP サーバーとして Claude Code に接続でき、会話の記憶を永続化できる。

### 実際に試したこと

別プロジェクト（daily-research）で Mem0 Cloud の MCP サーバーを試験導入した。このプロジェクトは `claude -p`（非対話モード）で毎朝 AI リサーチレポートを自動生成するパイプラインだ。

設定自体はシンプルだった。プロジェクトルートに `.mcp.json` を置くだけで動く。

```json
{
  "mcpServers": {
    "mem0": {
      "command": "npx",
      "args": ["-y", "@mem0/mcp-server@0.0.1"],
      "env": {
        "MEM0_API_KEY": "<YOUR_MEM0_API_KEY>"
      }
    }
  }
}
```

過去レポートの内容を Mem0 に投入する `seed-memory.sh` も作った。各レポートを Claude に読ませ、`mcp__mem0__add-memory` で要約とメタデータを登録するスクリプトだ。対話セッションでは問題なく動作し、「先週調査したテーマ」を検索して重複を避ける運用ができた。

### 問題と解決

問題は `claude -p`（非対話モード）との組み合わせで発生した。MCP サーバーの初期化時に `npx` がハングし、プロセスがタイムアウトする。対話セッションでは起きないが、`claude -p` 経由だと再現する。

launchd 環境では PATH に `npx` がないためスキップされて逆に問題が出ないという皮肉な状況だった。手動実行（ターミナル）のときだけハングする。

この問題は Claude Code の MCP 初期化の改善と設定調整により解決し、現在は daily-research プロジェクトで本番運用している。以下の内容は問題発生時の記録として残している。

### Mem0 の評価

- **記憶の質**: カテゴリ付きメタデータで構造化できる点は良い。`topic_history`、`research_method`、`source_quality` など自由にカテゴリを設計できた
- **手動操作が必要**: 何を記憶させるか、いつ検索するかを明示的に指示しなければならない
- **Claude Code との統合が薄い**: ファイル編集やコマンド実行といった行動レベルの自動記録は想定外
- **セッション開始時の自動注入がない**: 毎回「Mem0 を検索して」と指示する必要がある

「使えるが、求めていたものとは違う」という感触だった。Mem0 は「何を覚えるか」を人間が設計する仕組みであり、「セッションの行動を自動で残す」仕組みではない。後者を求めた場合、別のアプローチが必要だ。

## アプローチ2：claude-mem（Claude Code プラグイン）

### claude-mem とは

[claude-mem](https://github.com/thedotmack/claude-mem) は Claude Code 専用の永続メモリプラグインだ。セッション中の全ツール操作を自動キャプチャし、Claude API で圧縮してから SQLite + Chroma（ベクトル検索）に保存する。次回セッション開始時に関連コンテキストを自動注入する。

### Mem0 との違い

| 観点 | Mem0 | claude-mem |
|------|------|------------|
| 統合方式 | MCP サーバー | Claude Code プラグイン（hooks） |
| 記録対象 | 明示的に保存したもの | 全ツール操作を自動キャプチャ |
| 検索 | 手動で検索指示 | セッション開始時に自動注入 + MCP 検索 |
| 圧縮エンジン | なし（そのまま保存） | Claude API で構造化 |
| Claude Code 特化 | 汎用 | 専用設計（ライフサイクルフック） |
| コスト | Mem0 Cloud API（無料枠あり） | Claude API 従量課金（Observation ごと） |

### インストールで躓いたこと

Claude Code のセッション内で以下を実行する（ターミナルのコマンドではない）。

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

しかし `marketplace add` で SSH 認証エラーが発生した。GitHub に SSH 鍵を設定していない環境だったからだ。

**解決策**: HTTPS で手動クローンし、`known_marketplaces.json` にエントリを追加した。

```bash
# HTTPS でクローン
git clone https://github.com/thedotmack/claude-mem.git \
  ~/.claude/plugins/marketplaces/thedotmack-claude-mem
```

`known_marketplaces.json`（`~/.claude/plugins/` 配下）に以下の形式で追加する。

```json
{
  "thedotmack-claude-mem": {
    "source": "git",
    "url": "https://github.com/thedotmack/claude-mem.git"
  }
}
```

その後 Claude Code セッション内で `/plugin install claude-mem` → **Install for you (user scope)** で完了した。

### claude-mem の仕組み

ドキュメントでは5段階のフックシステム（SessionEnd 含む）と記載されている。ただし実際にインストールされる `hooks.json` には SessionEnd が含まれておらず、4つのフックで動作する。

1. **SessionStart** — 過去の関連コンテキストを検索し、セッション冒頭に自動注入する
2. **UserPromptSubmit** — ユーザーの入力をキャプチャし、行動の意図を記録する
3. **PostToolUse** — ファイル編集・コマンド実行などツール操作の結果を記録する
4. **Stop** — セッション終了時に2段階処理を実行する。まず `summarize` で操作ログを AI 圧縮し、次に `session-complete` で永続化する

裏では worker-service が常駐し、Observation の圧縮処理を非同期で捌く。デフォルトポートは 37777 で、`CLAUDE_MEM_WORKER_PORT` 環境変数または `~/.claude-mem/settings.json` で変更できる。

重要なのは**各フックが fire-and-forget（送信後即座に制御を返す）方式で HTTP リクエストを送る**点だ。タイムアウトは2秒。メインのセッションをブロックせず、AI 処理はワーカー側で非同期に行われる。

### 実際の動作：Observation と6つのタイプ

claude-mem が記録する単位は **Observation**（観測）と呼ばれる。各 Observation には Claude API によってタイプが自動付与される。以下は claude-mem の UI やコンテキストインデックスで使われるタイプラベルだ。

| タイプ | 意味 | 例 |
|--------|------|-----|
| bugfix | バグ修正 | 認証エラーの原因特定と修正 |
| feature | 新機能追加 | 記事の新セクション執筆 |
| refactor | リファクタリング | 関数の分割・命名変更 |
| change | 設定変更・更新 | schedule.json の更新 |
| discovery | 発見・調査結果 | ライブラリの挙動調査 |
| decision | 意思決定 | アーキテクチャの方針決定 |

セッション終了時、Stop フックがこれらの Observation を圧縮し、SQLite（構造化データ・全文検索）と Chroma（ベクトル検索、MCP 経由で接続）の両方に保存する。SQLite の FTS5 で「いつ・何を」を正確に引き、Chroma で「意味的に近い過去の操作」を横断検索する二重構造だ。

**API コストについて**: 各 Observation の圧縮に Claude API が呼ばれる。1セッションで数十件のツール操作があれば、それだけ API コールが発生する。デフォルトモデルは `sonnet` だが、`~/.claude-mem/settings.json` で `haiku` に変更すればコストを抑えられる。

### MCP 経由の3層検索

claude-mem は MCP サーバーとしても動作する。セッション中に過去の記録を検索するとき、3段階のワークフローでトークン消費を最小化する。

```text
Step 1: search(query)         → ID付きインデックスを取得（〜50トークン/件）
Step 2: timeline(anchor=ID)   → 前後のコンテキストを確認
Step 3: get_observations(IDs) → 必要な記録だけ全文取得
```

ポイントは **Step 1 で全文を取得しない** ことだ。まずタイトルとメタデータだけのインデックスを取り、関連がありそうな ID だけを Step 3 で展開する。claude-mem のドキュメントでは「10x token savings」と謳われている。実際、50件の Observation を全文取得すると数万トークンだが、インデックスだけなら数千トークンで済む。

セッション開始時に SessionStart フックが走ると、以下のようなコンテキストインデックスが自動注入される。

```text
# [zenn-content] recent context, 2026-02-25 9:57pm GMT+9

**#S42** Extract and document learned patterns (Feb 25 at 8:06 PM)
**#S43** Article correction: Fix factual inaccuracies (Feb 25 at 8:41 PM)

| ID  | Time    | T | Title                                    |
|-----|---------|---|------------------------------------------|
| #185| 8:42 PM | discovery | AI peer review article completed |
| #186| "       | change | Article scheduled for publication    |
```

「前回どこまでやったか」がセッションの冒頭で自動的に見える。これが Mem0 や CLAUDE.md の auto memory との決定的な違いだ。

## 期待できること・できないこと

### 期待できること

- **セッション継続性**: 前回どこまでやったかが自動で残る。セッション冒頭にコンテキストインデックスが注入されるので「前回の続きから」と言えばすぐ始まる
- **コンテキスト再収集の削減**: 同じファイルを何度も読み直す必要が減る
- **暗黙知の蓄積**: 明示的に書き残さなくても行動レベルの記録が残る。ベクトル検索で「以前にも似た操作をしたはず」と掘れる

### 期待しすぎないこと

- **構造化されたナレッジの代替にはならない**: 記事のアウトラインや要点整理は依然として意図的に作る必要がある
- **CLAUDE.md auto memory の置き換えではない**: auto memory は「確定した知見」を簡潔に残す場所。claude-mem は「セッションの行動ログ」の圧縮。用途が違う
- **「コンテキストを集めて」の指示自体は必要**: 自動注入される過去の行動記録と、新たなコンテキスト収集の判断は別物だ。後者は引き続き人間が行う
- **まだ成熟途上のプロジェクト**: GitHub Issues を見ると、Observation が保存されないケースや環境依存のエラーが報告されている。安定性に過度な期待は禁物だ

## まとめ

| | CLAUDE.md auto memory | Mem0 | claude-mem |
|---|---|---|---|
| 記録方式 | 手動 | 半手動（MCP 経由で明示的保存） | 自動（hooks） |
| 内容 | 確定した知見 | カテゴリ付きメモリ | ツール操作ログの圧縮 |
| 注入タイミング | セッション開始時に全量 | 手動で検索指示 | セッション開始時に自動で関連分 |
| 粒度 | 粗い（人間が要約） | 中程度（人間が設計） | 細かい（全操作を AI 圧縮） |
| Claude Code 特化度 | ◎ | △ | ◎ |
| 追加コスト | なし | Mem0 Cloud API | Claude API（Observation ごと） |

結論として、CLAUDE.md auto memory と claude-mem の併用が現時点でのベストプラクティスだと考えている。

- **CLAUDE.md auto memory**: 確定した知見・ルール・パターンを簡潔に残す（人間が管理）
- **claude-mem**: セッションの行動コンテキストを自動で残す（プラグインが管理）

「何を知っているか」と「何をしたか」を分けて管理する。この使い分けがうまく回れば、毎セッションのコンテキスト収集コストはかなり下がるはずだ。

なお、Mem0 は現在 daily-research プロジェクトで本番運用しているが、用途は異なる。Mem0 は「調査テーマの履歴管理」という明示的なナレッジベースとして使い、claude-mem は「作業ログの自動記録」として使う。両者は補完し合う関係だ。
