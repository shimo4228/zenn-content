---
title: "Zed を Claude Code の「観測窓」として構築する — IBM Plex で統一する日本語タイポグラフィ"
emoji: "🪟"
type: "tech"
topics: ["zed", "claudecode", "font", "ibmplex", "typography"]
published: true
published_at: 2026-04-16 07:00
---

# Zed を観測窓にする。フォントと認知資源の設計記録

[前回の記事](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration)で、Cursor から Zed へ乗り換えた経緯を書いた。「重い器に、軽い中身」の違和感を解消するため Zed を選び、Claude Code CLI を主軸とした開発フローに着地した、という話だった。

あれから2ヶ月。Zed で何も困っていない。

困っていないが、3つだけ「微妙に気になること」が残っていた。

1. **ファイルを開くと、なぜかフォーマットが変わる**
2. **左 dock に使わないパネルが並んでいる**
3. **日本語フォントに、言語化できない違和感がある**

この記事は、その3つを1日かけて解消した記録だ。ただし、単なる設定変更の話ではない。各設定項目の「なぜこの値なのか」を突き詰めていった結果、**3つの設計原則**と、**予想外の再発見**にたどり着いた。

![Before: Zed 初期状態 — SF Mono + 整理前の dock](/images/zed-observation-window-01-initial.png)
*Before: セッション開始時の Zed。SF Mono、整理前の dock、標準 UI*

## 観測窓という役割定義

まず前提を再確認する。私は Claude Code CLI で開発している。コードを書くのも、テストを走らせるのも、git 操作も、すべてターミナルの Claude Code が担う。

では Zed は何をしているのか。

**Zed は「観測窓」だ。** CLI が push してくる情報（ファイル変更、テスト結果、コミットログ）を、人間が pull で確認するための窓。書くためのツールではなく、見るためのツール。

この役割を意識すると、エディタに求める要件が変わる。

| 機能 | 書く道具として | 観測窓として |
|------|-------------|-----------|
| コード補完 | 必須 | 不要 |
| フォーマッタ | 必須 | 邪魔（CLI 側が担う） |
| デバッガ | 必須 | 不要 |
| ファイルツリー | 必須 | 必須（変更箇所の特定） |
| git 差分表示 | あると便利 | 必須（何が変わったか） |
| フォント品質 | あると嬉しい | **必須**（長時間読むから） |

「書く」と「見る」では、優先順位がまるで違う。この前提で、3つの気になりポイントを順に解消していった。

## 二重管理を断つ — format_on_save: off

### 症状

「ファイルを開いたら、なんかフォーマットが変わってる」

最初は気のせいかと思った。だが開くたびにインデントが微妙に変わる。差分が出る。Claude Code で書いたコードなのに、開いただけで diff が発生する。

### 診断

原因は**二重フォーマット**だった。

1. Claude Code の PostToolUse hook が `black` / `ruff` でフォーマット
2. Zed の `autosave: on_focus_change` + `format_on_save: on` が Zed 側の LSP フォーマッタで再フォーマット
3. 両者のルール設定が微妙に異なり、差分が発生

つまり **2つのフォーマッタが、同じファイルを異なるルールで交互に書き換えていた**。

### 処方

```jsonc
// Claude hooks が format を担うので off
"format_on_save": "off",
```

1行で解決した。実は[前回の記事](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration)では `format_on_save: on` にしていた。移行直後は Claude Code の hook 体制が整っておらず、Zed 側でフォーマットする方が合理的だった。だが PostToolUse hook で `black` / `ruff` を本格運用し始めた結果、二重フォーマットが発生するようになった。環境が変われば設定も変わる。

この1行には、観測窓にとって重要な原則が含まれている。

:::message
**原則①: プライマリチャネル優先、セカンダリで複製しない**

Claude Code CLI がプライマリチャネルとして情報を運ぶなら、Zed（セカンダリ）は同じ機能を複製しない。フォーマットの責任は CLI に一本化する。情報の重複は観測性の向上ではなく、認知資源の浪費だ。
<!-- textlint-disable -->
:::

![設定編集中 — format_on_save と dock の調整過程](/images/zed-observation-window-02.png)
*設定変更の過程。settings.json を編集しながら対話している*

## 視覚ノイズを削る — button: false の設計

### 左 dock の問題

整理前の左 dock には、Terminal、Agent Panel、Debugger、Outline、Git と、使わないパネルが並んでいた。観測窓として使うのは Terminal だけなのに、他のパネルのアイコンが常に視界に入る。

使わないものが視界にあるのは、ノイズだ。

### button: false という解法

Zed には `button: false` という設定がある。パネルの**機能は生かしたまま、ボタン（アイコン）だけ非表示にする**。

```jsonc
// 使わない panel は機能を殺さず button だけ隠す
"debugger": { "dock": "left", "button": false },
"agent": { "enabled": true, "dock": "left", "button": false },
"outline_panel": { "button": false },
"collaboration_panel": { "button": false },
"diagnostics": { "button": false },
"notification_panel": { "button": false },
"search": { "button": false },
```

`enabled: false` で機能ごと殺すこともできるが、あえてそうしない。Agent Panel は ACP（Agent Control Protocol）連携で必要になる可能性がある。**機能に触るな、視覚に触れ。**

### deprecated key の罠

この作業中、Zed が「Your settings file uses deprecated settings」と警告を出した。

原因は2つ。

- `collab_panel` → 正しくは `collaboration_panel`（リネーム済み）
- `chat_panel` → 独立 panel として存在しない（collaboration に統合済み）

古い設定キーを使い続けても動くが、警告が出続ける。正規のキー名に修正した。

### Notifications Connect の誤解

右 dock の Notifications パネルに "Connect" ボタンがあった。これを押せば GitHub の PR レビュー、CI の lint エラー、deploy 失敗などの通知が Zed 内で見られると期待した。

![右側 Notifications panel の Connect ボタン](/images/zed-observation-window-05.png)
*"Connect to view notifications." — GitHub 連携だと思った*

**実態は違った。** Zed 公式ドキュメントで確認したところ、この "Connect" は **Zed 独自のコラボレーション機能**（Zed Channels）への接続だった。GitHub OAuth を使うが scope は `read:user` のみで、リポジトリへのアクセス権限は一切取得しない。

GitHub リポジトリ通知を Zed に統合する公式機能は、存在しない。

Connect しなかった。期待する機能が得られず、得られる機能（コラボ）を使わない。両側で価値ゼロ。

**教訓: UI のラベル（"Connect"）だけで機能を推測しない。** 認証を伴う接続は特に、実際に何に繋がるか確認してから押す。

### 「推測した値が通らない」事件

status_bar を空にしたくて、`active_encoding_button` を `"never"` と書いた。CSS の `display: none` のノリで。

> **Invalid user settings file:** unknown variant 'never', expected one of 'enabled', 'disabled', 'non_utf8'

Zed の設定ファイルは**型安全な JSONC + schema validation** だ。誤った値は silent failure にならず、即座にエラーを返す。しかもエラーメッセージに valid values が列挙されている。

今日のセッションで同種の失敗が3回あった。

1. `collab_panel`（deprecated、正解は `collaboration_panel`）
2. `font-moralerspace-nf`（discontinued、正解は `font-moralerspace`）
3. `"never"`（存在しない、正解は `"disabled"`）

共通構造は **「それっぽい名前で推測する」パターン**。推測する前に確認する。設定ファイルの値は直感ではなく公式ソースから取る。

### LSP を残す判断

観測窓用途なら、Language Server（Pyright、tsserver 等）の主要機能 — autocomplete、hover、diagnostics — を全く使わない。切ってもいいのでは？

![LSP 診断 panel が空の状態](/images/zed-observation-window-04.png)
*"No problems in workspace" — LSP は動いているが何も言っていない*

結論: **残す**。理由は3つ。

1. Apple Silicon + 潤沢メモリでは LSP の体感負荷がほぼゼロ
2. JSON schema hints（settings.json 編集時の補完）が意外と役に立つ — 今日の長いセッションで実証された
3. 切り替えコスト（設定追加 + 失う機能）> 節約できる認知資源（ほぼゼロ）

**「消しても良さそう」と「消すべき」は別の判断だ。** 認知資源への実害がないなら、あえて触らないのも最適化。

:::message
**原則②: 機能に触るな、視覚に触れ（hide, don't delete）**

使わない機能は `button: false` で視覚的にだけ消す。機能を殺すと副作用のリスクがある。

**原則③: 見える視覚ノイズは削る、見えない背景は許容する**

dock のアイコンや status_bar の表示項目は認知資源を消費するから削る。LSP のようなバックグラウンドプロセスは、視界に入らないから許容する。
<!-- textlint-disable -->
:::

## フォントの長い旅 — SF Mono から PlemolJP Console NF へ

ここからが本題だ。3つの気になりポイントの中で、最も時間をかけたのがフォントだった。

### SF Mono には日本語グリフがない

Zed のデフォルト（正確には macOS のデフォルト）として SF Mono を使っていた。日本語も「ふつうに」表示されていた。だが **SF Mono にはラテン文字しか入っていない**。

では日本語はどこから来ていたのか。

答えは **CJK フォールバック** だった。macOS のフォントレンダリングが SF Mono に日本語グリフがないことを検出し、Hiragino Sans や PingFang SC などの system fallback フォントで描画していた。

問題はメトリクスだ。フォールバック先のベースライン、字幅、行間が SF Mono と微妙にズレていて、**「なんとなくガタつく」違和感**を生んでいた。言語化しにくいが、確実にある違和感。

解決策は明確だった。**CJK 統合フォント** — ラテン文字と日本語グリフが同一フォントファイルに含まれ、メトリクスが最初から統一されているフォントを使う。

### Moralerspace Argon: 太い

最初に試したのは [Moralerspace](https://github.com/yuru7/moralerspace)。UDEV Gothic と同じ作者（yuru7）による CJK 統合フォントで、Monaspace + IBM Plex Sans JP を合成したものだ。Argon バリアントを選んだ。

```bash
brew install --cask font-moralerspace
```

:::message alert
`font-moralerspace-nf`（Nerd Font 専用 cask）は 2025-07-29 に discontinued。Nerd Font は "patched font file" から "symbols overlay" 方式にシフトしつつあり、基底 `font-moralerspace` が後継。
<!-- textlint-disable -->
:::

結果: **ボールドに感じた。** Regular weight でもストロークに存在感がありすぎる。Modern で洗練されたデザインだが、長時間コードを読む観測窓用途では、もう少し控えめなフォントが欲しかった。

### PlemolJP Console NF: Light は薄すぎ、Regular で着地

次に試したのが [PlemolJP](https://github.com/yuru7/PlemolJP)。IBM Plex Mono + IBM Plex Sans JP を合成した CJK 統合フォントだ。Console NF バリアント（等幅 + Nerd Font 記号）を選んだ。

```bash
brew install --cask font-plemol-jp-nf
```

まず Light（weight 300）を試した。**薄すぎた。** 文字が背景に溶けるような感覚で、読むのに微妙に力が要る。

Regular（weight 400）に上げた。**着地した。** Plex Mono 譲りのクラシックなストロークで、Moralerspace ほど主張せず、Light ほど消えない。Sweet spot。

#### フォント family 名の正確な取得

brew install 直後、Zed の settings.json にフォント名を書こうとして困った。**正確な family 名がわからない**。

macOS の Spotlight インデックスが未更新だと `mdls` が空を返す。確実な方法は `system_profiler`:

```bash
system_profiler SPFontsDataType 2>/dev/null | \
  grep -B 1 -A 4 "PlemolJPConsoleNF-Regular:" | head -20

# 結果:
#   Full Name: PlemolJP Console NF Regular
#   Family: PlemolJP Console NF
#   Style: レギュラー
```

`Family: PlemolJP Console NF` — これが settings.json に書く値だ。

### 全レイヤー統一の失敗: monospace で散文を読む苦痛

PlemolJP Console NF で Buffer と Terminal が快適になった。勢いで **UI にも同じフォントを当てた**。全レイヤー統一、美しい。

![UI に PlemolJP を当てた時の散文 monospace 問題](/images/zed-observation-window-03.png)
*UI monospace 化の失敗。日本語の散文が grid に並ぶ違和感*

**違和感があった。** パネルのラベル、Insight ブロックの日本語テキスト、ファイルパスの日本語部分 — これらが「四角い箱の連続」に見える。

原因を考えて気づいた。**monospace フォントは等幅 grid を前提としている。** ASCII 文字は grid に揃って自然だが、日本語の散文は本来 proportional（文字ごとに異なる幅）で読む方が自然だ。

これは活字の歴史と関係がある。

- **monospace**: タイプライター由来。物理的に各活字が同じ幅でなければキャリッジが動かなかった。コードは grid で読む文化が定着している
- **proportional**: 活版印刷以来、散文は proportional が標準。文字ごとの幅が自然に変わることで、視線の流れがスムーズになる

UI は散文的なラベルが中心だ。散文に monospace を当てるのは、タイプライターで小説を組むようなものだった。

### IBM Plex Sans JP: UI だけ proportional に戻す

UI を proportional に戻す。だが system default に戻すのではなく、**PlemolJP と同じ IBM Plex ファミリー**の中から選ぶ。

```bash
brew install --cask font-ibm-plex-sans-jp
```

IBM Plex Sans JP は IBM Plex Sans の日本語拡張版で、PlemolJP の「proportional な兄弟」にあたる。デザイン言語が統一されているので、Buffer（monospace）と UI（proportional）の間に違和感が生まれない。

```jsonc
{
  // UI: proportional（散文向き）
  "ui_font_family": "IBM Plex Sans JP",
  "ui_font_size": 16.0,
  "ui_font_weight": 400,

  // Buffer: monospace（コード向き）
  "buffer_font_family": "PlemolJP Console NF",
  "buffer_font_size": 15.0,
  "buffer_font_weight": 400,

  // Terminal: monospace（CLI 出力向き）
  "terminal": {
    "font_family": "PlemolJP Console NF",
    "font_weight": 400,
    "font_size": 14,
    "line_height": "comfortable"
  }
}
```

3層それぞれに適切なフォントタイプを割り当てた。

| レイヤー | 用途 | フォントタイプ | フォント | サイズ |
|---------|------|-------------|---------|-------|
| UI | パネルラベル、メニュー | proportional | IBM Plex Sans JP | 16pt |
| Buffer | コード表示 | monospace | PlemolJP Console NF | 15pt |
| Terminal | CLI 出力 | monospace | PlemolJP Console NF | 14pt |

Buffer は「読書」、Terminal は「流し読み」。情報密度に応じてサイズを1ptずつ下げている。

## 再発見 — Zed のデフォルトは IBM Plex だった

ここまでの作業に満足していたとき、ふと Zed のデフォルトフォントを調べた。

Zed は `.ZedSans` と `.ZedMono` というエイリアスを使っている。その実体はこうだ。

- **`.ZedSans`** = **IBM Plex Sans**
- **`.ZedMono`** = **Lilex**（IBM Plex Mono + ligatures のフォーク）

Zed のデフォルトフォントは、**IBM Plex ファミリーだった**。

つまり、今回の構成は次のようなものだった。

> **SF Mono → Moralerspace（合わない）→ PlemolJP（IBM Plex Mono 系）に着地 → UI も IBM Plex Sans JP にした → 結果的に Zed default の日本語最適化版を構築していた**

独自に IBM Plex ファミリーに到達したのは偶然ではなかった。Zed の開発チームも IBM Plex を選んでいる。Zed のデザイン哲学の延長線上で自然に到達した、というのが正確だ。

<!-- textlint-disable -->
![Zed 最終 UI — IBM Plex Sans JP + PlemolJP Console NF](/images/zed-observation-window-final-ui.png)
<!-- textlint-enable -->
*After: 左 dock は Terminal のみ、Buffer に PlemolJP Console NF、UI に IBM Plex Sans JP。右 dock にファイルツリー。*

## おわりに — settings.json は設計判断の記録である

今日の作業で 140行の settings.json を書き上げた。各項目が3つの原則のどれかに対応している。

| 原則 | 該当する設定 |
|------|------------|
| **プライマリチャネル優先** | `format_on_save: "off"`、`edit_predictions.provider: "none"` |
| **機能に触るな、視覚に触れ** | 各種 `button: false`、`agent.enabled: true`（残しつつ非表示） |
| **見えるノイズは削る、見えない背景は許容** | `status_bar` 全項目 off、`show_whitespaces: "none"`、LSP 残留 |

この settings.json は設定の羅列ではない。**認知資源を守るための設計判断の記録**だ。

「変える」と「最適化する」は違う。Zed のデフォルト設計を理解した上で、自分の使い方（観測窓）と環境（日本語混在）に適応させた。壊したのではなく、localize した。

前作では「Cursor から Zed に乗り換えた」と書いた。今ならもう少し正確に言える。

**Zed を、Claude Code の観測窓として構築した。**

<!-- textlint-disable -->
:::details 完全版 settings.json

```jsonc
{
    "diagnostics": { "button": false },
    "calls": { "share_on_join": true, "mute_on_join": true },
    "notification_panel": { "button": false },
    "pane_split_direction_vertical": "right",
    "active_pane_modifiers": { "inactive_opacity": 1.0 },
    "use_system_window_tabs": false,
    "bottom_dock_layout": "contained",
    "tabs": { "file_icons": false, "git_status": false },
    "tab_bar": {
        "show_pinned_tabs_in_separate_row": false,
        "show_nav_history_buttons": true,
        "show": true
    },
    "title_bar": {
        "show_user_picture": false,
        "show_sign_in": true,
        "show_project_items": true,
        "show_branch_name": true
    },
    "status_bar": {
        "active_encoding_button": "disabled",
        "show_active_file": false,
        "active_language_button": false,
        "cursor_position_button": false
    },
    "search": { "button": false },
    "agent_servers": { "claude-acp": { "type": "registry" } },
    "debugger": { "dock": "left", "button": false },
    "icon_theme": "Zed (Default)",
    "edit_predictions": { "provider": "none" },
    "agent": { "enabled": true, "dock": "left" },
    "session": { "trust_all_worktrees": true },
    "theme": {
        "mode": "system",
        "light": "Tokyo Night Light",
        "dark": "Tokyo Night"
    },
    "vim_mode": false,
    "soft_wrap": "editor_width",
    "ui_font_family": "IBM Plex Sans JP",
    "ui_font_size": 16.0,
    "ui_font_weight": 400,
    "buffer_font_family": "PlemolJP Console NF",
    "buffer_font_size": 15.0,
    "buffer_font_weight": 400,
    "autosave": "on_focus_change",
    "show_whitespaces": "none",
    "terminal": {
        "flexible": true,
        "show_count_badge": false,
        "dock": "left",
        "font_family": "PlemolJP Console NF",
        "font_weight": 400,
        "font_size": 14,
        "line_height": "comfortable",
        "working_directory": "current_project_directory"
    },
    "tab_size": 4,
    "format_on_save": "off",
    "indent_guides": { "enabled": true, "coloring": "indent_aware" },
    "inlay_hints": { "enabled": true },
    "scrollbar": { "show": "auto" },
    "git": {
        "disable_git": false,
        "inline_blame": { "enabled": true }
    },
    "project_panel": {
        "file_icons": true,
        "hide_gitignore": false,
        "hide_root": false,
        "git_status_indicator": true,
        "bold_folder_labels": false,
        "entry_spacing": "comfortable",
        "button": true,
        "auto_reveal_entries": true,
        "dock": "right"
    },
    "git_panel": {
        "show_count_badge": false,
        "tree_view": true,
        "file_icons": true,
        "dock": "right"
    },
    "outline_panel": { "button": false },
    "collaboration_panel": { "button": false },
    "languages": {
        "Swift": { "tab_size": 4 },
        "JSON": { "tab_size": 2, "soft_wrap": "editor_width" },
        "Python": { "tab_size": 4 }
    }
}
```

:::

<!-- textlint-enable -->

<!-- textlint-disable -->
:::details フォントインストールコマンド

```bash
# Buffer / Terminal 用（IBM Plex Mono + IBM Plex Sans JP の合成）
brew install --cask font-plemol-jp-nf

# UI 用（proportional、日本語対応）
brew install --cask font-ibm-plex-sans-jp

# フォント family 名の確実な取得方法
system_profiler SPFontsDataType 2>/dev/null | \
  grep -B 1 -A 4 "PlemolJPConsoleNF-Regular:"
```

:::
<!-- textlint-enable -->
