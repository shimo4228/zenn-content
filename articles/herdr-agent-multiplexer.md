---
title: "AI エージェント版 tmux「Herdr」— Zed に足りない並列エージェント管理を埋める"
emoji: "🐑"
type: "tech"
topics: ["herdr", "claudecode", "zed", "terminal", "ai"]
published: true
published_at: 2026-07-21 09:00
---

> **この記事でわかること**: 複数の Claude Code を状態つきで一覧監視し、離席後や SSH 越しでも同じセッションに戻れて、さらに**エージェント自身に画面レイアウトを再編成させられる**ターミナル環境の作り方。エディタ（Zed）との住み分けまで含めて、導入から検証までの実録です。

## はじめに — 並列エージェントの「置き場所」問題

Claude Code や Codex を複数並列で回し始めると、こんな壁に当たります。

- ターミナルタブが散らかり、「どのタブでどの作業をしていたか」を思い出すのに毎回時間がかかる
- エディタやターミナルアプリを終了すると、走っていたエージェントのセッションごと消える
- 離席先の iPhone や別マシンから、いま走っているエージェントの様子を確認できない
- エージェントは自分の実行環境（ペイン配置・ワークスペース）に一切触れない。並べ直すのは常に人間の手作業

この記事では、これらを **Herdr**（agent multiplexer = エージェント用の端末多重化ツール）で解決します。筆者は Zed ユーザーで、導入直後は「Zed の機能と冗長では？」と評価していたのですが、**エージェント自身にレイアウトを操作させた瞬間に評価が反転**しました。その過程も含めて書きます。

## 前提

- macOS + Homebrew（Herdr は Linux でも動きます）
- Claude Code 等の CLI エージェントを利用中
- 本記事は **Herdr v0.7.4 時点**（2026-07-18 検証）の情報です。公開約 3 ヶ月半の新しいツールなので、コマンド体系は変わる可能性があります
- 記事中のペイン ID（`w5:p8` など）は筆者環境の実値です。環境により異なります

## Herdr とは — tmux との差分は 2 つだけ

Herdr は「ターミナルに常駐する agent multiplexer」です。Rust 製の単一バイナリで、tmux と同じくセッションをサーバとして永続化します（prefix キーも tmux 互換の `ctrl+b`）。

tmux との本質的な差分は 2 つだけです。

1. **エージェント状態の意味的追跡** — ペイン内のエージェントを自動検出し、`working` / `blocked` / `done` / `idle` / `unknown` の状態をサイドバーに一覧表示する。「どの子が手待ちか」を目視巡回せずに把握できます
2. **socket API** — ペイン分割・コマンド実行・出力読み取り・レイアウト変更のすべてを、外部プロセスから操作できる（`herdr pane run` などの CLI コマンドは、Unix ソケット経由の API を包んだラッパーです）。つまり**エージェント自身が自分の実行環境を操作できる**

画面は **workspace（作業部屋）→ tab → pane** の 3 階層です。CLI からは `w1`（workspace 1）、`w1:t1`（その中のタブ 1）、`w1:p1`（ペイン 1）という ID で指定します。以降のコマンド例はこの記法で読んでください。

基本情報（2026-07-18 時点で筆者確認）:

- GitHub: [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr) — 個人開発、リポジトリ作成から 113 日で 17,700 stars
- 2026-06-29 に [Hacker News](https://news.ycombinator.com/item?id=48714802) に載り 166 ポイント・110 コメント
- ライセンスは AGPL-3.0-or-later + 商用ライセンスのデュアル（LICENSE ファイルに明記）

## 導入する — インストールは brew 1 コマンド

homebrew-core に bottled 収載済みなので brew で入れます。公式サイトの `curl | sh` はスクリプトの中身を監査しにくいため選びませんでした。設定ファイルの生成まで含めて 4 行です。

```bash
brew install herdr                                    # v0.7.4
mkdir -p ~/.config/herdr
herdr --default-config > ~/.config/herdr/config.toml  # 305 行のベースライン設定
herdr config check                                    # → config: ok
```

`herdr` を実行すると TUI が起動し、サーバ（`herdr server`）も自動で立ち上がります。ログイン時常駐（`brew services`）は不要でした。

動作確認として、socket API のスモークテストを流します。これは後述の「エージェントに環境を操作させる」の最小例でもあります。

```bash
# ワークスペースを作り、ペインでコマンドを実行し、出力を待って読む
herdr workspace create --cwd ~ --label smoke-test --no-focus
# → JSON で workspace_id と pane_id が返ります。以下は "w1:p1" が返った例なので、
#   手元で返った ID に読み替えてください（既存 workspace があると w2 以降になります）
herdr pane run "w1:p1" "echo herdr-smoke-ok"
herdr wait output "w1:p1" --match "herdr-smoke-ok" --timeout 5000
herdr pane read "w1:p1" --lines 10
# → 出力に herdr-smoke-ok が返れば疎通 OK
```

4 つとも通れば、レイアウト・実行・読み取りが外部プロセスから制御できる状態です。

## Zed で足りる範囲、足りない範囲

ここで正直に書くと、導入直後の筆者の評価は「**Zed とほぼ変わらない**」でした。

Zed は 2026-04-22 に [Parallel Agents](https://zed.dev/blog/parallel-agents) を発表しています。Threads サイドバーで複数エージェントを並列に走らせ、スレッドごとに git worktree を分離できます。ターミナルもタブ（`cmd+N`）と分割（`cmd+D`）に対応済みです。デスクに座って GUI でレビューしながらエージェントを回すなら、Zed のほうが体験は上です。Herdr の workspace 切り替えは、Zed のウィンドウ切り替えとほぼ同じに見えました。

実際、筆者は一度「デスク = Zed、離席 = Herdr」と役割を分けて塩漬けにしかけました。

評価が変わったのは、Zed に**構造的に存在しないレイヤー**を使ったときです。

| レイヤー | Zed | Herdr |
|---|---|---|
| GUI でのレビュー体験 | ◎ Parallel Agents + エディタ統合 | —（ターミナルのみ） |
| 実行の永続化 | アプリ終了で実行も止まる（スレッド履歴は残る） | サーバ常駐。アプリを全部閉じても実行が続く |
| 走行中セッションへの外部からの再接続 | 不可（SSH リモート開発機能はあるが別物） | iPhone 等から `ssh → herdr` で同一画面に復帰 |
| エージェント自身による環境操作 | 不可 | socket API で全操作可能 |

上 1 行が Zed の勝ち、下 3 行が Herdr にしかない領域です。つまり競合ではなく、**Zed が弱い「多数エージェントの管理」を Herdr が埋める**という補完関係でした。

もう 1 つ、実務で効くトラップがあります。**Zed のエージェントパネルから立ち上げたセッションは、Claude Code 公式アプリ（Remote Control）や Termius など外部から掴めません**（筆者確認）。エディタプロセスの中に閉じているためです。ターミナルから CLI として起動した Claude Code なら、公式アプリの一覧にも出ますし、SSH → Herdr 経由でも触れます。外から見る可能性が少しでもあるセッションは、CLI 起動にしておくのが安全です。

次の節が、補完関係の決定打です。

## エージェント自身にレイアウトを操作させる

導入後、複数のタブに散らばっていたエージェントたちを 1 画面で見たくなり、ふと Claude Code 本人にこう頼みました。「タブを 1 枚に統合して」。

Claude Code が実行したのは次の 3 コマンドです。

```bash
# 別タブのペインを、タブ t2 に分割配置で移動する（実行者は Claude Code 自身）
herdr pane move w5:p5 --tab w5:t2 --split right --no-focus
herdr pane move w5:p7 --tab w5:t2 --split down --target-pane w5:p4 --no-focus
herdr pane move w5:p6 --tab w5:t2 --split down --target-pane w5:p5 --no-focus
# → タブに散っていたペインが 1 タブの 2×2 グリッドに。空になったタブは自動クローズ
```

このとき 2 つのエージェントは `working` 状態で走っていましたが、**1 つも止まらずに**配置だけが変わりました。頼んだ側がやったことは日本語の一言だけです。ペインを開き直してプロセスを中断させる心配も、move コマンドの並びを自分で組み立てる手間もありません。

実際の様子がこちらです。エージェントごとにタブが分かれた状態（Before）から、

![Before: エージェントごとにタブが分かれた状態。タブバーに 4 枚並び、一度に 1 セッションしか見えない](/images/herdr-tab-to-pane-before.png)
*Before: タブバーに 4 枚。一度に見えるのは 1 セッションだけ*

別ペインの Claude Code に「まとめて」と一言頼むと、

![Claude Code にタブ統合を指示している画面。タブ一覧の把握と実行ログが写っている](/images/herdr-tab-to-pane-instruction.png)
*指示は日本語の一言。Claude Code が現在のタブ構成を socket API で把握し、pane move を組み立てて実行する*

1 タブの 2×2 グリッドに統合されます。

![After: 1 タブの 2×2 グリッドに統合され、4 ペインが同時に見える状態](/images/herdr-tab-to-pane-after.png)
*After: 全エージェントが 1 画面に。走行中のプロセスは止まらない*

エージェントは環境変数で自分の位置を知っています。

```bash
$ env | grep -i herdr    # 出力のホームディレクトリは ~ に置換しています
HERDR_ENV=1
HERDR_PANE_ID=w5:p8
HERDR_SOCKET_PATH=~/.config/herdr/herdr.sock
HERDR_TAB_ID=w5:t2
HERDR_WORKSPACE_ID=w5
```

つまり「自分がどのペインにいるか」を知った上で、隣にペインを割り、コマンドを走らせ、結果を読めます。**実行環境の形そのものがエージェントの道具になる**わけです。ちなみにこの記事の執筆セッション自体も Herdr ペイン内の Claude Code で、`herdr agent list` には執筆中の自分が `working` として写っています。

git worktree との連携も 1 コマンドでした（筆者検証済み）。

```bash
# worktree 作成 + ブランチ作成 + 新ワークスペース開設が一発
herdr worktree create --workspace w6 --branch feature-x
# → ~/.herdr/worktrees/<repo名>/feature-x/ に worktree を作り、
#    それを cwd にした workspace が「feature-x」ラベルで開く
```

「ブランチごとに部屋を分けて並列作業」という Zed Parallel Agents と同じ構図を、エージェント自身が CLI から組み立てられます。

:::details ハマりポイント: ズーム中のタブはレイアウト変更を拒否する
`pane move` が `changed: false`（reason: `"zoomed_tab"`）を返して何も起きないことがあります。対象タブがズーム表示中だと、レイアウト変更が拒否される仕様です。`herdr pane zoom <ペインID> --off` でズームを解除してから実行してください。
:::

:::details ハマりポイント: `--current` は「呼び出し元」ではなくフォーカス中のペイン
Claude Code に `herdr pane split` を実行させたとき、意図したワークスペースではなく、**人間がそのとき見ていた別のワークスペース**にペインが割れました。CLI の `--current` は「コマンドの呼び出し元ペイン」ではなく「TUI でフォーカス中のペイン」に解決される仕様です。

エージェントに操作させるときは、`--current` に頼らず `HERDR_PANE_ID` で自分の位置を明示指定させてください。
:::

:::details ハマりポイント: サーバの寿命と起動ディレクトリ
- **サーバは起動した親プロセスの所有物**です。Claude Code のシェルから `herdr server` を起動すると、セッション終了と運命を共にしえます。筆者は検証後に一度サーバを止め、ユーザー自身の `herdr` 起動にサーバ所有権を持たせました
- **起動時の cwd が効くのは新規セッション作成の 1 回だけ**。リポジトリに `cd` してから `herdr` を実行しても、2 回目以降は既存セッションに復帰するだけです。リポジトリの追加は Herdr 内から `herdr workspace create --cwd <repo> --label <name>` で行います。「cd で移動」から「workspace 切り替えで移動」へのメンタルモデルの引っ越しが必要でした
:::

## サイドバーは「状態」を映すか「履歴」を映すか

Zed のターミナル内で Herdr を動かすと、次のような入れ子になります。

![Zed ターミナル内の Herdr。左に spaces/agents サイドバー、右に 2 分割ペインで 2 つの Claude Code が並走](/images/herdr-zed-spaces-agents.png)
*左サイドバーの spaces / agents 一覧。エージェントの状態とコンテキスト残量が 1 行ずつ並ぶ*

使ってみて気づいたのは、Herdr のサイドバーには**生きたプロセスと 1:1 対応する行しか出ない**ことです。エージェントが終われば行も消えます。構造的に散らかりようがありません。

一方、Zed の Threads サイドバーは**履歴の一覧**です。数日〜数ヶ月前に終わったセッションと現役のセッションが同列に並び、プロジェクトも入り乱れます。終わった作業が「注意の在庫」として画面に混ざり続けるわけです。

![Zed の Threads サイドバー。終了済みの履歴セッションと現役セッション、複数プロジェクトが同じ一覧に並ぶ](/images/zed-threads-sidebar-history.png)
*Zed の Threads サイドバー。4 日前・2 週間前・2 ヶ月前の履歴セッションと現役セッションが同じ一覧に混ざる*

一覧が**現在の状態**を映すのか、**過去の履歴**を映すのか。並列エージェント時代の UI を見分けるリトマス試験紙だと感じました。

この気づきは画面全体の使い方も変えました。以前はエディタと CLI で画面を常時 2 分割していたのですが、エディタは「コードを読むとき」しか見ておらず、残りの時間はデッドスペースでした。

![Before: 常時 2 分割。左に claude CLI、右にエディタとファイルツリー](/images/herdr-zed-split-editor-cli.png)
*Before: 常時 2 分割。エディタ側は見ていない時間のほうが長い*

![After: エディタ専用のフルスクリーン表示。コードを読むときだけこの画面に切り替える](/images/herdr-zed-editor-fullscreen.png)
*After: 普段は Herdr（CLI 側）を主画面にし、コードを読むときだけ `cmd+shift+バッククォート` でエディタを全画面表示*

エージェント主導の開発では、主役画面がエディタからエージェント CLI に反転し、**エディタのほうがオンデマンド側に回ります**。サイドバーの話と同根で、「視界に入るものは、いま使っているものだけ」に揃えると認知資源の浪費が減ります。この運用に変えてからの体感では、Zed は「コードを読むときだけ開くファイルエクスプローラー付きエディタ」に近づいています。

## 住み分けの結論 — デスクは Zed、それ以外は Herdr

筆者の運用は次の形に落ち着きました。

| 場面 | 使うもの | 理由 |
|---|---|---|
| デスクで GUI レビューしながら回す | Zed（Parallel Agents） | レビュー体験が上。worktree 分離も GUI で完結 |
| 離席・アプリ終了後もエージェントを走らせ続ける | Herdr | サーバ常駐。アプリの生死とセッションが独立 |
| iPhone・SSH からの監視と復帰 | Herdr | `ssh → herdr` で同一画面にそのまま復帰（筆者実機確認済み） |
| レイアウト・並列実行をエージェントに任せる | Herdr | socket API は Zed に無いレイヤー |

iPhone からの接続経路（Tailscale + Termius）の構築は [tmux 時代に書いた記事](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)と同一で、tmux が Herdr に置き換わっただけです。会話 UX が主目的なら [Claude Code 公式アプリの運用記事](https://zenn.dev/shimo4228/articles/iphone-claude-code-remote-control)のほうが合います。役割分担は「会話 = 公式アプリ / 艦隊監視 = Termius + Herdr」です。

複数クライアントで同時に attach したときの挙動も実測しました。Mac のターミナルと iPhone の Termius から同じセッションに attach すると、両者は**同一画面のミラー**になります。片方での workspace 切り替えやフォーカス移動は、もう片方にもほぼ遅延なく反映されます。

![iPhone の Termius から Mac と同じ Herdr セッションをミラー表示している画面](/images/herdr-termius-iphone-sync.png)
*iPhone 側の表示。Mac の画面とほぼ遅延なく同期する。写っているのは本記事の執筆セッション自身*

このとき表示サイズは**小さい側のクライアントに合わせて同期**します。iPhone から触っている間は、Mac 側のターミナルも iPhone の画面幅に折り返された表示になります。

![iPhone 操作中の Mac 側の画面。ペイン内容が iPhone の画面幅に合わせて表示されている](/images/herdr-termius-mac-sync.png)
*同時刻の Mac 側。iPhone から操作している間は、Mac の表示も iPhone サイズに同期する*

注意点として、サーバは Mac 上のユーザープロセス（launchd 管理外）として動くので、**Mac がスリープしている間はエージェントも進みません**（macOS のスリープはユーザープロセスを一時停止するため）。スリープでサーバが死ぬことはなく、復帰すればセッションはそのまま生きています（筆者実測: スリープ→復帰でセッション継続を確認）。離席中も走らせ続けたい場合は、スリープさせない設定が必要です。

## おわりに — 実行環境の形がエージェントの道具になる

Herdr は「tmux の後継」として見ると Zed と冗長に見えます。評価が反転したのは、socket API でエージェント自身に環境を操作させたときでした。

少なくともこの 3 つを見る限り、エディタ（Zed Parallel Agents）・ターミナル（Herdr）・ハーネス（Claude Code 本体のサブエージェント機構）という各レイヤーが、同時に「エージェントの編成機能」を吸収し始めています。そのなかで Herdr が持つ固有の答えは、**実行環境のレイアウトそのものをエージェントの操作対象にした**ことです。ペインを割り、部屋を作り、worktree を切る——人間がやっていた「作業環境の整備」ごと任せられるようになります。

まずは brew 1 コマンドで入るので、Claude Code を 2 本以上並列で回している方は、`herdr agent list` に自分のエージェントたちが写るところから試してみてください。

## 関連リンク

- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr) — Herdr 本体（GitHub）
- [herdr.dev](https://herdr.dev/) — 公式サイト・ドキュメント
- [Zed: Parallel Agents](https://zed.dev/blog/parallel-agents) — Zed 側の並列エージェント機能
- [iPhoneからClaude Codeを操作する — Termius + Tailscale + tmux](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code) — モバイル接続経路の構築（tmux を Herdr に読み替え可）
- [iPhone公式アプリでClaude Codeを運用する](https://zenn.dev/shimo4228/articles/iphone-claude-code-remote-control) — 会話 UX 側の運用
- [Cursor から Zed への移行記](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration) — 本記事の Zed 環境の前提
- [github.com/shimo4228](https://github.com/shimo4228) — 筆者の GitHub（エージェント関連のスキル・ツール置き場）
