---
title: "Cursorが重いからZedに乗り換えた日 — AIコーディングの最適解は「黒い画面」だった"
emoji: "⚡"
type: "tech"
topics: ["zed", "claude", "cursor", "ai", "エディタ"]
published: false
---

# CursorからZedへ。迷走と発見の1日

2026年2月11日、私はCursorを捨ててZedに乗り換えました。

正確に言うと、「乗り換えようとして迷走し、最終的に想定外の最適解にたどり着いた」1日でした。この記事はその悪戦苦闘の記録です。

## 前提: 私はコードを書かない

まず前提を共有します。私は個人開発者ですが、**コードを一切書きません。** Claude Code（Anthropicが提供するCLIツール）にすべて任せています。

私の開発フローはこうです。

1. エディタでコードを**読む**（レビュー）
2. ターミナルでClaude Codeに**指示を出す**
3. 生成されたコードを**確認する**

つまりエディタに求めるのは「高速に表示すること」だけ。コード補完もスニペットもいりません。

この前提が、今日の迷走を引き起こし、同時に最適解への鍵になりました。

## きっかけ: ECCの開発者がZedを使っていた

[Everything Claude Code (ECC)](https://github.com/anthropics/ecc) — 私が日常的に使っているClaude Codeの設定コレクションです。その開発者がZedを使っているのを見て、前から気になっていました。

Cursorは機能が豊富ですが、重い。起動に時間がかかるし、バックグラウンドでインデックスを作り続けてメモリを食います。私はCursorの独自AI機能（Tab補完やComposer）を使っておらず、Claude Codeの拡張機能だけを動かしている状態でした。

つまり**「重い器に、軽い中身」**。無駄の塊です。

この違和感を解消するため、Geminiに相談したところ、衝撃的な事実を教えられました。

## Geminiからの衝撃: 「その構成、勿体ないですよ」

> Cursorという重い器を使って、中身は VS Code用のClaude拡張 を動かしている状態ですよね。CursorのAI機能を使わないなら、ただ重いだけです。

痛いところを突かれました。さらに続きます。

> Zedは最初からエディタの機能として「Assistant Panel」が組み込まれています。APIキーを入れるだけで、拡張機能なしでClaudeが使えます。

なるほど。Zedは拡張機能をインストールする必要がなく、ネイティブでClaude対応しているのか。しかも動作が軽い。

「後で、Zedの開発環境をClaude Codeに作らせてみよう」

そう決めた瞬間から、悪戦苦闘が始まりました。

## 第1の壁: インストールしたけど、何をすればいいのかわからない

Zedをインストールし、Claude Codeに`settings.json`を書かせました。

```jsonc
{
    "vim_mode": false,
    "soft_wrap": "editor_width",
    "ui_font_size": 16,
    "buffer_font_size": 16,
    "autosave": "on_focus_change",
    "terminal": {
        "dock": "left",
        "font_size": 15,
        "line_height": "comfortable"
    }
}
```

設定は一瞬で終わりました。Claude Codeに頼めば、Zedのドキュメントを読む必要すらありません。

問題はその先です。**Zedを開いたけど、何をすればいいのかわからない。**

Cursorなら左サイドバーにChatパネルがあって、そこに話しかければよかった。Zedにはそれに相当するものが見当たりません。

「ZedでClaudeのパネルを開くにはどうしたらいいのか？」

Geminiに聞いて、`Cmd + ?`でAssistant Panelが開くことを知りました。開いてみると、右側にチャット画面が現れます。

ここで**Claude Codeのサインイン**が必要だと気づき、さらに手間取りました。CursorのようにGUIでポチポチ設定する世界とは勝手が違います。

## 第2の壁: Agent Panelのブラックボックス問題

Assistant PanelでClaude Code（Agent）を選択すると、Cursorと同じようにチャットベースでAIに指示を出せます。ファイル作成もコマンド実行も自律的にやってくれる。

**しかし、コンテキストの消費量が表示されない。**

Cursorなら「何%使用中」がバーで可視化されます。Zedにはそれがありません。

「見当たらないのだが」

Geminiに確認したところ、これはZedの仕様上の制限でした。

> Claude Code（ACP接続）のトークン消費量は、ZedのAgent Panelでは表示されません。外部エージェント連携では、この機能はサポートされていません。

これは痛い。コンテキストの残量がわからないまま作業するのは、ガソリンメーターのない車を運転するようなものです。

「Cursorなら見れるから、Cursorの方がいい気がしてきた。ただZedすごいさくさくなんだよなあ」

この葛藤が、今日のターニングポイントでした。

## 転機: 「標準モード」に逃げるな

「じゃあ標準モードを使えばいいのか？」

ZedにはAgent Panel以外に「標準モード」（APIを直接叩くモード）があり、こちらならトークン消費量が表示されます。一瞬、これに切り替えようとしました。

Geminiに止められました。

> 標準モードにすると、Claudeは「こう書けば直りますよ」とテキストを表示するだけになります。ファイル作成もコマンド実行も自動ではやりません。

| 機能 | Agent Panel（Claude Code） | 標準モード |
|:---|:---|:---|
| コード修正 | 自動でファイルを書き換え | コード提示のみ（手動コピペ） |
| コマンド実行 | 自動でテスト・インストール実行 | 不可（手動でターミナル操作） |
| ファイル作成 | 自動 | 不可 |
| トークン表示 | **非表示** | **表示あり** |

「コードを書かない」私にとって、標準モードは致命的です。AIが提示するだけで、自分でコピペしないといけない。それは一番やりたくないことです。

## 最適解の発見: CLIをZedに住まわせる

この膠着状態を打破したのは、Geminiの一言でした。

> ZedのAgent Panelを使わず、Zedのターミナルで`claude`を実行するという手があります。

目から鱗でした。

**Zedの中のターミナルでClaude Code CLIを起動する。** これなら：

- CLI版なのでコンテキスト消費量が**見える**
- Claude Codeの全機能（ファイル操作、コマンド実行）が**使える**
- Zedの爆速表示が**活きる**

Agent Panel（GUI）にこだわる必要は全くなかったのです。

## 「ハッカーのコックピット」完成

ターミナルを左側に配置し、エディタを右側に置く。このレイアウトが完成した瞬間、すべてが繋がりました。

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   Claude Code CLI   │    Zed Editor       │
│   (ターミナル)       │    (ファイル表示)     │
│                     │                     │
│   指示を出す         │    結果を確認する     │
│   ↓                 │    ↑               │
│   コンテキスト%表示   │    即時反映          │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

**左が「脳」、右が「体」。**

- 左のCLIで指示を出すと、Claude Codeがファイルを修正する
- 右のZedに即座に反映される
- コンテキスト消費量はCLIにそのまま表示される

Cursorでも同じことはできます。しかしCursorは「重い器」です。Zedはファイルの表示が一瞬で、余計なバックグラウンド処理がありません。

**エディタはただの「表示器」でいい。** コードを書かない私にとって、エディタに求めるのは軽さと速さだけ。Zedはその要件を完璧に満たします。

## settings.json: 最終形

試行錯誤を経て、`~/.config/zed/settings.json`はこうなりました。

```jsonc
{
    "edit_predictions": {
        "provider": "none",
    },
    "agent": {
        "enabled": false,
        "dock": "left",
    },
    "session": {
        "trust_all_worktrees": true,
    },
    "theme": "Ayu Dark",
    "vim_mode": false,
    "soft_wrap": "editor_width",
    "ui_font_size": 16,
    "buffer_font_size": 16,
    "buffer_font_family": "SF Mono",
    "autosave": "on_focus_change",
    "show_whitespaces": "none",
    "terminal": {
        "dock": "left",
        "font_family": "SF Mono",
        "font_size": 15,
        "line_height": "comfortable",
        "working_directory": "current_project_directory",
    },
    "tab_size": 4,
    "format_on_save": "on",
    "indent_guides": {
        "enabled": true,
        "coloring": "indent_aware",
    },
    "inlay_hints": {
        "enabled": true,
    },
    "scrollbar": {
        "show": "auto",
    },
    "git": {
        "inline_blame": {
            "enabled": true,
        },
    },
    "project_panel": {
        "auto_reveal_entries": true,
        "dock": "right",
    },
    "languages": {
        "Swift": {
            "tab_size": 4,
            "format_on_save": "on",
        },
        "JSON": {
            "tab_size": 2,
            "soft_wrap": "editor_width",
        },
        "Python": {
            "tab_size": 4,
            "format_on_save": "on",
        },
    },
}
```

ポイントをいくつか。

- **`"edit_predictions": { "provider": "none" }`** — コード補完は不要。書かないので。
- **`"agent": { "enabled": false }`** — Agent Panelは使わない。CLIで十分。
- **`"terminal": { "dock": "left" }`** — ターミナルは左。ここがメインの作業場。
- **`"project_panel": { "dock": "right" }`** — ファイル一覧は右。ターミナルの邪魔にならない。
- **`"working_directory": "current_project_directory"`** — ターミナルを開いた瞬間、プロジェクトルートにいる。`cd`不要。

テーマは「One Dark」から「Ayu Dark」に変更しました。これも今日の試行錯誤の産物です。

## 並行開発: ウィンドウを分ければ`cd`は不要

Zedでは`Cmd + Shift + N`で新しいウィンドウを開けます。プロジェクトごとにウィンドウを分ければ、ターミナルは自動的にそのプロジェクトのルートで起動します。

```
[Zed ウィンドウ1: g-kentei-ios]     [Zed ウィンドウ2: xmetrics-web]
┌─────────┬──────────┐          ┌─────────┬──────────┐
│ Claude  │ Swift    │          │ Claude  │ TypeScript│
│ Code    │ コード    │          │ Code    │ コード     │
└─────────┴──────────┘          └─────────┴──────────┘
```

2つのClaude Codeを同時に走らせ、片方でiOSアプリを修正させながら、もう片方でWebアプリを改修する。これがコードを書かない開発者の理想形です。

## 今日わかったこと

1日の迷走を経て、いくつかの教訓を得ました。

### エディタのAI機能は「CLI未満」になりつつある

ZedのAgent PanelもCursorのComposerも、確かに便利です。しかしClaude Code CLIの方が情報量が多く（コンテキスト消費量、思考プロセス、実行ログがすべて見える）、制御しやすい。

**GUIは「わかりやすさ」を提供しますが、CLIは「透明性」を提供します。** AIに仕事を任せるなら、何が起きているか見えることの方が重要です。

### 「重いエディタ」は過去の遺物

CursorやVS Codeは、人間がコードを書くことを前提に設計されています。コード補完、リファクタリング支援、デバッガ統合 — これらはすべて「人間が書く」前提の機能です。

コードをAIが書く時代に、エディタに求められるのは**「速く表示すること」**だけ。Zedの「余計なことをしない軽さ」は、この新しいパラダイムに最適です。

### Geminiの「教師役」としての価値

今日の迷走で一番助けられたのは、実はGeminiでした。Zedの仕様、レイアウトの提案、「標準モードに逃げるな」という判断 — これらはすべてGeminiとの対話から生まれました。

Claude Codeは「実行者」として最強ですが、「どの道具をどう使うか」という戦略的判断には、別の視点が必要です。AIツールの使い分けも、個人開発の重要なスキルだと実感しました。

## まとめ: 「コードを書かない開発者」のエディタ論

| 項目 | Cursor (Before) | Zed + CLI (After) |
|:---|:---|:---|
| 起動速度 | 遅い | 爆速 |
| メモリ消費 | 重い（独自AI機能が常駐） | 軽い |
| Claude Code連携 | 拡張機能経由 | CLI直接実行 |
| コンテキスト表示 | 拡張機能では非表示 | CLIで表示 |
| 並行開発 | 可能だが重い | ウィンドウ分割で軽量に |
| AI機能 | 使っていない（無駄） | 使わない設計（無駄なし） |

**結論: エディタはただの「表示器」でいい。本体はCLIにある。**

CursorからZedへの移行は、単なるエディタの乗り換えではありませんでした。「GUIのAIチャット」から「CLIの自律エージェント」へ、開発スタイルそのものの転換です。

重い器に軽い中身を入れていた過去の自分に言いたい — **お前が必要なのは黒い画面だけだ。**

---

:::message
**タイムライン（2026-02-11）**
- 午前 — Geminiとの対話でZed移行を決意
- 午後 — Zedインストール、初期設定をClaude Codeに構築させる
- 午後 — Agent Panel（GUI）でトークン表示されない問題に直面
- 午後 — CLI版をZedターミナルで起動する最適解を発見
- 夕方 — テーマ・フォント・レイアウトの調整を完了
- 夜 — 「ハッカーのコックピット」レイアウト確立
:::

:::details Zed settings.json のポイント解説
- `edit_predictions.provider: "none"` — AI補完OFF。Claude Code CLIに任せる
- `agent.enabled: false` — Agent Panel（GUI）は使わない
- `terminal.dock: "left"` — ターミナルをメインの作業場に
- `terminal.working_directory: "current_project_directory"` — cd不要
- `project_panel.dock: "right"` — ファイル一覧は邪魔にならない位置に
- `autosave: "on_focus_change"` — 保存操作を意識しない
:::
