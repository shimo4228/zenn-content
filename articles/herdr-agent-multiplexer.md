---
title: "AI エージェント版 tmux「herdr」— エディタが要らなくなるまで"
emoji: "🐑"
type: "tech"
topics: ["herdr", "claudecode", "zed", "terminal", "ghostty"]
published: true
published_at: 2026-07-21 09:00
---

> **この記事でわかること**: 複数の Claude Code を状態つきで一覧監視し、離席後や SSH 越しでも同じセッションに戻れて、**エージェント自身に画面レイアウトを再編成させられる**ターミナル環境の作り方。導入から、エディタ（Zed）の役割が「書く」→「検収する」→「消滅」と縮退していくまでの実録です。

## はじめに — 並列エージェントの「置き場所」問題

Claude Code や Codex を複数並列で回し始めると、こんな壁に当たります。

- ターミナルタブが散らかり、「どのタブでどの作業をしていたか」を思い出すのに毎回時間がかかる
- エディタやターミナルアプリを終了すると、走っていたエージェントのセッションごと消える
- 離席先の iPhone や別マシンから、いま走っているエージェントの様子を確認できない
- エージェントは自分の実行環境（ペイン配置・ワークスペース）に一切触れない。並べ直すのは常に人間の手作業

この記事では、これらを **herdr**（agent multiplexer = エージェント用の端末多重化ツール）で解決します。筆者は Zed ユーザーで、導入直後は「Zed の機能と冗長では？」と評価していたのですが、**エージェント自身にレイアウトを操作させた瞬間に評価が反転**しました。

そして反転はそこで止まりませんでした。herdr を主戦場にすると、エディタ（Zed）の役割は「書く道具」から「エージェントの出力を検収（レビューして承認）する道具」に縮退し、最終的にはその役割すら失って開かなくなりました。導入から、エディタが要らなくなるまでの一部始終を、実際に効いた設定とコマンドつきで書きます。

## 前提

- macOS + Homebrew（herdr は Linux でも動きます）
- Claude Code 等の CLI エージェントを利用中
- 本記事は **herdr v0.7.4 時点**（2026-07-18 検証）の情報です。公開約 3 ヶ月半の新しいツールなので、コマンド体系は変わる可能性があります
- エディタは Zed（`markdown_preview_*` 系の設定が入った新しめのバージョン）、ターミナルは最終的に [Ghostty](https://ghostty.org/) を選びます（経緯は後述）
- 記事中のペイン ID（`w5:p8` など）は筆者環境の実値です。環境により異なります

## herdr とは — tmux との差分は 2 つだけ

herdr は「ターミナルに常駐する agent multiplexer」です。Rust 製の単一バイナリで、tmux と同じくセッションをサーバとして永続化します（prefix キーも tmux 互換の `ctrl+b`）。GitHub は [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr)、ライセンスは AGPL-3.0-or-later + 商用のデュアルです（LICENSE ファイルに明記）。

tmux との本質的な差分は 2 つだけです。

1. **エージェント状態の意味的追跡** — ペイン内のエージェントを自動検出し、`working` / `blocked` / `done` / `idle` / `unknown` の状態をサイドバーに一覧表示する。「どの子が手待ちか」を目視巡回せずに把握できます
2. **socket API** — ペイン分割・コマンド実行・出力読み取り・レイアウト変更のすべてを、外部プロセスから操作できる（`herdr pane run` などの CLI コマンドは、Unix ソケット経由の API を包んだラッパーです）。つまり**エージェント自身が自分の実行環境を操作できる**

画面は **workspace（作業部屋）→ tab → pane** の 3 階層です。CLI からは `w1`（workspace 1）、`w1:t1`（その中のタブ 1）、`w1:p1`（ペイン 1）という ID で指定します。以降のコマンド例はこの記法で読んでください。

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

Zed は 2026-04-22 に [Parallel Agents](https://zed.dev/blog/parallel-agents) を発表しています。Threads サイドバーで複数エージェントを並列に走らせ、スレッドごとに git worktree を分離できます。ターミナルもタブ（`cmd+N`）と分割（`cmd+D`）に対応済みです。デスクに座って GUI でレビューしながらエージェントを回すなら、Zed のほうが体験は上です。herdr の workspace 切り替えは、Zed のウィンドウ切り替えとほぼ同じに見えました。

実際、筆者は一度「デスク = Zed、離席 = herdr」と役割を分けて塩漬けにしかけました。

評価が変わったのは、Zed に**構造的に存在しないレイヤー**を使ったときです。

| レイヤー | Zed | herdr |
|---|---|---|
| GUI でのレビュー体験 | ◎ Parallel Agents + エディタ統合 | —（ターミナルのみ） |
| 実行の永続化 | アプリ終了で実行も止まる（スレッド履歴は残る） | サーバ常駐。アプリを全部閉じても実行が続く |
| 走行中セッションへの外部からの再接続 | 不可（SSH リモート開発機能はあるが別物） | iPhone 等から `ssh → herdr` で同一画面に復帰 |
| エージェント自身による環境操作 | 不可 | socket API で全操作可能 |

上 1 行が Zed の勝ち、下 3 行が herdr にしかない領域です（※ 1 行目の評価は、後述のプラグイン導入で変わります）。つまり競合ではなく、**Zed が弱い「多数エージェントの管理」を herdr が埋める**という補完関係でした。

もう 1 つ、実務で効くトラップがあります。**Zed のエージェントパネルから立ち上げたセッションは、Claude Code 公式アプリ（Remote Control）や Termius など外部から掴めません**（筆者確認）。エディタプロセスの中に閉じているためです。ターミナルから CLI として起動した Claude Code なら、公式アプリの一覧にも出ますし、SSH → herdr 経由でも触れます。外から見る可能性が少しでもあるセッションは、CLI 起動にしておくのが安全です。

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

つまり「自分がどのペインにいるか」を知った上で、隣にペインを割り、コマンドを走らせ、結果を読めます。**実行環境の形そのものがエージェントの道具になる**わけです。ちなみにこの記事の執筆セッション自体も herdr ペイン内の Claude Code で、`herdr agent list` には執筆中の自分が `working` として写っています。

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
- **起動時の cwd が効くのは新規セッション作成の 1 回だけ**。リポジトリに `cd` してから `herdr` を実行しても、2 回目以降は既存セッションに復帰するだけです。リポジトリの追加は herdr 内から `herdr workspace create --cwd <repo> --label <name>` で行います。「cd で移動」から「workspace 切り替えで移動」へのメンタルモデルの引っ越しが必要でした
:::

## サイドバーは「状態」を映すか「履歴」を映すか

Zed のターミナル内で herdr を動かすと、次のような入れ子になります。

![Zed ターミナル内の herdr。左に spaces/agents サイドバー、右に 2 分割ペインで 2 つの Claude Code が並走](/images/herdr-zed-spaces-agents.png)
*左サイドバーの spaces / agents 一覧。エージェントの状態とコンテキスト残量が 1 行ずつ並ぶ*

使ってみて気づいたのは、herdr のサイドバーには**生きたプロセスと 1:1 対応する行しか出ない**ことです。エージェントが終われば行も消えます。構造的に散らかりようがありません。

一方、Zed の Threads サイドバーは**履歴の一覧**です。数日〜数ヶ月前に終わったセッションと現役のセッションが同列に並び、プロジェクトも入り乱れます。終わった作業が「注意の在庫」として画面に混ざり続けるわけです。

![Zed の Threads サイドバー。終了済みの履歴セッションと現役セッション、複数プロジェクトが同じ一覧に並ぶ](/images/zed-threads-sidebar-history.png)
*Zed の Threads サイドバー。4 日前・2 週間前・2 ヶ月前の履歴セッションと現役セッションが同じ一覧に混ざる*

一覧が**現在の状態**を映すのか、**過去の履歴**を映すのか。並列エージェント時代の UI を見分けるリトマス試験紙だと感じました。

この気づきは画面全体の使い方も変えました。以前はエディタと CLI で画面を常時 2 分割していたのですが、エディタは「コードを読むとき」しか見ておらず、残りの時間はデッドスペースでした。

![Before: 常時 2 分割。左に claude CLI、右にエディタとファイルツリー](/images/herdr-zed-split-editor-cli.png)
*Before: 常時 2 分割。エディタ側は見ていない時間のほうが長い*

![After: エディタ専用のフルスクリーン表示。コードを読むときだけこの画面に切り替える](/images/herdr-zed-editor-fullscreen.png)
*After: 普段は herdr（CLI 側）を主画面にし、コードを読むときだけ `cmd+shift+バッククォート` でエディタを全画面表示*

エージェント主導の開発では、主役画面がエディタからエージェント CLI に反転し、**エディタのほうがオンデマンド側に回ります**。サイドバーの話と同根で、「視界に入るものは、いま使っているものだけ」に揃えると認知資源の浪費が減ります。

## 一度は「デスクは Zed、それ以外は herdr」で落ち着いた

評価が反転しても、置き場所の答えはいったん最初の直感（前述の「塩漬け」案）に戻りました。ただし今度は消極的な塩漬けではなく、「デスクで GUI レビューするなら Zed、離席・永続化・エージェントへの委任は herdr」という積極的な住み分けです。iPhone からの監視・復帰も herdr 側で実測済みです。

:::details 離席運用の実測メモ（iPhone ミラー・スリープ挙動）
- iPhone からの接続経路（Tailscale + Termius）は [tmux 時代に書いた記事](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)と同一で、tmux が herdr に置き換わっただけです。会話 UX が主目的なら [Claude Code 公式アプリの運用記事](https://zenn.dev/shimo4228/articles/iphone-claude-code-remote-control)のほうが合います。役割分担は「会話 = 公式アプリ / 艦隊監視 = Termius + herdr」です
- Mac のターミナルと iPhone の Termius から同じセッションに attach すると、両者は**同一画面のミラー**になります。片方での workspace 切り替えやフォーカス移動は、もう片方にもほぼ遅延なく反映されます

![iPhone の Termius から Mac と同じ herdr セッションをミラー表示している画面](/images/herdr-termius-iphone-sync.png)
*iPhone 側の表示。Mac の画面とほぼ遅延なく同期する*

- 表示サイズは**小さい側のクライアントに合わせて同期**します。iPhone から触っている間は、Mac 側のターミナルも iPhone の画面幅に折り返された表示になります

![iPhone 操作中の Mac 側の画面。ペイン内容が iPhone の画面幅に合わせて表示されている](/images/herdr-termius-mac-sync.png)
*同時刻の Mac 側。iPhone から操作している間は、Mac の表示も iPhone サイズに同期する*

- **Mac がスリープしている間はエージェントも進みません**（スリープはプロセスの実行を一時停止します。launchd 管理かどうかに関係ありません）。スリープでサーバが死ぬことはなく、復帰すればセッションはそのまま生きています（筆者実測: スリープ→復帰でセッション継続を確認）。離席中も走らせ続けたい場合は、スリープさせない設定が必要です
:::

ところが、この住み分けは長持ちしませんでした。herdr を主戦場にして数日使うと、次の疑問にぶつかります。**コードを書くのは Claude Code なのに、エディタで自分は結局何をしているのか？** ここからが後半戦です。

## Zed に残った 3 つの仕事 — 「書く道具」から「検収する道具」へ

コードを書く仕事を CLI（Claude Code）に全部任せると、エディタの「書く」機能はとうに引退しています。それでも Zed を残していたのは、次の 3 つのためでした。

- **読む** — 複数ファイルを 1 画面に並べて追う（multibuffer）
- **diff レビュー** — 変更の差分を目で確認する
- **Markdown を確認する** — 記事や設計メモの見た目を整える

つまり残っていたのは全部「読む側」の仕事です。ならば Zed を「読む・検収するための道具」として最適化してみよう、と発想を切り替えました。

まず効いたのが、`zed` の CLI です。ファイルパスに続けて `:行` を書くと、その行にカーソルを置いた状態で開けます。

```bash
# 特定の行を開く（行:列 まで指定可能）
zed src/contemplative_agent/cli.py:715

# 複数ファイルの検収ポイントをまとめて開く
zed src/core/metrics.py:88 src/cli.py:715 tests/test_cli.py:350

# --wait: 人間がファイルを閉じるまで、次のコマンドに進まない
zed --wait changed_file.py
```

これで検収の動線が逆向きになります。

- **従来**: `path:line` を文字で伝える → 人間がエディタで探す
- **これから**: Claude Code が `grep` で該当行を特定し、`zed <対象ファイル>:<行>` を実行 → 開いた状態のエディタを人間に差し出します

人間は探さずに、指された行を読むだけになります。さらに `--wait` を挟むと、「人間がそのファイルを目視するまで次に進まない」という一時停止を、コマンド 1 本で構造にできます。注意点として、**閉じる操作は「見た」ことしか意味しません**。承認・却下の判断は区別できないので、コミットのような不可逆な操作は `--wait` に連結せず、確認後に人間側で明示的に実行します。

:::message
この時点で Zed をアンインストールはしませんでした。使っていない間の常駐コストはゼロで、「読む」代替をターミナル側に作り直すコストの方が実在するからです。使う実態に決めさせる、という判断です。
:::

## 日本語表示の壁とホスト交代 — Ghostty へ

「読む・検収する」に最適化し始めると、今度は表示品質の壁に当たります。日本語まわりで 2 つありました。

**1 つ目は Zed の Markdown プレビューの行間です。** 日本語の Markdown をプレビューすると行間が詰まって読みにくいのですが、調べるとプレビューの段落行間は **1.3 に固定**されていて、ユーザー設定がありません（[zed#56111](https://github.com/zed-industries/zed/discussions/56111) で日本語向けの設定要望が上がっています）。プレビュー専用フォントの設定（`markdown_preview_font_family` など）でサイズは上げられますが、比率 1.3 自体は変えられず、根本解決になりません。記事の最終確認は `npx zenn preview`（本番と同じレンダリング）に寄せて、Zed のプレビューは「書きながらのチラ見」用に格下げしました。**Zed では読む体験を仕上げきれない**、という最初のひびです。

**2 つ目がもっと厄介で、Claude Code が出す Markdown の表がターミナルでずれる、罫線が途切れる問題でした。**

![Claude Code 出力の表がターミナルで崩れている実例](/images/terminal-ascii-table-cjk-breakage.png)

疑ったのは、罫線などの「East Asian Width（Unicode が定める文字幅の分類）が曖昧」な文字です。この幅を、文字幅を計算する Claude Code・グリッドに配置する herdr・実際に描くターミナルが、それぞれ別に解釈することがあります。層の間で幅の合意がずれると、表が崩れます（フォントのフォールバックなど、他の描画要因でも似た症状は起きるので、あくまで有力候補です）。

機構までは特定できませんでしたが、**どの層に原因があるか**は、ホスト（表示を担うターミナル）だけを差し替える対照実験で切り分けられました。同じ Claude Code + herdr の出力を Terminal.app に映したら、表が綺麗に揃ったのです。ずれていた層は Zed のターミナル描画だと確定しました。多層構成の表示バグでは、この「1 層だけ差し替える」が最速の切り分けになります。

| ホスト | 表の正確さ | 色（True Color） |
|---|---|---|
| Zed のターミナル | 崩れる | 正確 |
| Terminal.app | 正確 | 非対応 |
| Ghostty | 正確 | 対応 |

最終的に [Ghostty](https://ghostty.org/) に落ち着きました。罫線やブロック文字をフォントに頼らず自前で描くので表が崩れず、色も正確に出ます。

![Ghostty 上の herdr で、Claude Code が出力した罫線付きの表が崩れず表示されている](/images/ghostty-ascii-table-fixed.png)
*「解決後」。同じ Claude Code + herdr の出力でも、Ghostty では罫線付きの表がずれずに揃います。*

ホストが決まったら、外観も入れ子で統一します。ホスト（Ghostty）と TUI（herdr）で配色がずれると、視線を移すたびに小さな引っかかりが出るからです。herdr はホストの明暗に自動追従できます。

```toml
# ~/.config/herdr/config.toml
[theme]
name = "tokyo-night"
auto_switch = true          # ホストの light/dark に追従
dark_name = "tokyo-night"
light_name = "tokyo-night-day"
```

`herdr server reload-config` で警告なく適用でき、macOS の外観 → Ghostty → herdr の 3 段が同時に切り替わります。

![Ghostty 上の herdr のライトモード。2 ペインで 2 つの Claude Code が並走している](/images/ghostty-herdr-theme-light.png)

![同じ画面のダークモード。同一レイアウトで配色だけが対になっている](/images/ghostty-herdr-theme-dark.png)
*同じ 2 ペイン画面のライト版とダーク版。ホスト（Ghostty）の外観に追従して、TUI ごと切り替わります。*

## herdr が日本語入力まで作り込めている理由 — 作者と bot による個人開発

使っていて驚いたのは、herdr が日本語入力（IME）まわりの実務問題まで作り込んでいたことです。設定ダイアログには、こんな項目が並んでいます。

![herdr の設定ダイアログの experiments タブ。日本語入力（IME）向けの項目が並んでいる](/images/herdr-experiments-cjk-settings.png)

たとえば、日本語 IME が有効なまま `ctrl+b v` のようなキー操作を押すと、`v` が IME に食われる事故があります。herdr はキー操作の受付中だけ入力ソースを英字に切り替え、抜けたら戻す、という対策を入れていました。他にも、ペインのスクロール履歴をサーバ再起動またぎで保存する機能などがあります。

なぜここまで作り込めるのでしょうか。リポジトリの実データを見ると理由が透けます。

```bash
gh api repos/ogulcancelik/herdr \
  --jq '{created: .created_at, stars: .stargazers_count, license: .license.spdx_id}'
# → {"created":"2026-03-27...","stars":17794,"license":"NOASSERTION"}
#   （license が NOASSERTION なのは AGPL + 商用のデュアルを GitHub が自動判定できないため）

gh api "repos/ogulcancelik/herdr/contributors?per_page=6" \
  --jq '.[] | "\(.login): \(.contributions)"'
# → ogulcancelik: 979 / kangal-bot: 54 / github-actions[bot]: 43
#   akbash-bot: 16 / 人間のコントリビュータは各 4 コミット以下
```

作成から 113 日（2026-07-18 時点）で star は 1.7 万を超え、2026-06-29 には [Hacker News](https://news.ycombinator.com/item?id=48714802) にも載りました（166 ポイント・110 コメント。数値はいずれも執筆時点のもの）。一方コミットの約 979 は作者本人で、実質は個人開発です。おもしろいのは、コントリビュータの 2 位と 4 位が bot（kangal-bot と akbash-bot）だったこと。作者が運用しているエージェントがコミットしているのだと思われます。

:::message
余談ですが、kangal も akbash もトルコの家畜守護犬の実在の犬種名です。herdr（羊飼い）という名前とそろえているのかもしれません——ここは命名意図の推測です。API から確実に言えるのは「コミットのほぼ全てが、作者本人と bot 名義のアカウントに帰属している」ことまでで、その bot をエージェントとして作者が運用しているというのも状況からの推測です。
:::

道具の欠陥が毎日、開発者自身の速度に跳ね返ります。だから要求の発見が速くなります。エージェント時代の道具は、エージェントと共に作られたものほど手に馴染む、という構図がコントリビュータの一覧に出ていました。

## 結末 — Zed は検収ビューアにすらならなかった

ここまでは「Zed を検収ビューアとして最適化する」話でした。ところが、その役割すら herdr 側に奪われて終わります。

きっかけは herdr のプラグイン 2 つです。

- **file-viewer** — git を認識する読み取り専用のファイル閲覧
- **reviewr** — 差分をサイドバーに出し、行コメントをエージェントへ返送する

file-viewer で「読む」を、reviewr で「diff レビューして指摘を返す」を、どちらも herdr の中でできるようになりました。

![herdr の中で file-viewer プラグインがファイルを開いている。左が Claude Code、右がファイル閲覧](/images/herdr-file-viewer-reading.png)
*左のエージェントと、右で開いたファイルが同じ画面に並びます。「読む」がターミナル側に移りました。*

![herdr の中で reviewr プラグインが未コミットの diff を表示している。左が Claude Code、右が差分と変更ファイル一覧](/images/herdr-reviewr-diff.png)
*reviewr の画面。右サイドバーに未コミットの diff と変更ファイル一覧が出ます。写っているのは、まさにこの記事の統合作業の差分です。*

ここで動線が一周します。前の節で架けた「エージェント → 人間」の橋（`zed file:line`）に対して、reviewr は「人間 → エージェント」の逆向きの橋（コメント返送）を架けます。検収のループが herdr の中で閉じました。

:::message
このプラグイン置き場（marketplace）は GitHub のトピックを自動で拾うだけで、審査がありません。導入はコードの実行許可と同じなので、入れる前に manifest とインストールスクリプトを読みました（file-viewer は SHA-256 検証つき・自動フックなし、を確認）。
:::

結果、`zed file:line` の橋は、架けた数時間後に渡る必要がなくなりました。3 つ目の仕事だった Markdown の確認も、書きながらのチラ見は file-viewer の rendered 表示（`v` キーで diff ⇄ rendered ⇄ syntax を切替）で足り、最終確認はすでに `npx zenn preview` に一本化していたので、Zed 側に残る理由がありません。**Zed は検収ビューアの座すら失って、一日で開かなくなりました。**

最終スタックは Ghostty + herdr + プラグイン + Claude Code。エディタはありません。

## おわりに — 実行環境の形がエージェントの道具になる

herdr は「tmux の後継」として見ると Zed と冗長に見えます。評価が反転したのは、socket API でエージェント自身に環境を操作させたときでした。ペインを割り、部屋を作り、worktree を切る——人間がやっていた「作業環境の整備」ごと任せられます。

そして評価の反転は、道具の交代まで進みました。「Zed 不要では」から「検収特化」へ、そして「消滅」へ。エディタ・ターミナル・ハーネス（Claude Code 本体のサブエージェント機構）の各レイヤーが同時に「エージェントの編成機能」を吸収し始めるなか、herdr の固有の答えは**実行環境のレイアウトそのものをエージェントの操作対象にした**ことです。各層が単機能に痩せていくこの縮退は、退化ではなく注意の設計だと感じています。画面に置くものを、いまの役割に対して余計な層が一枚もない状態へ寄せていく作業でした。

とはいえ「ベスト」は今の役割に対する最適であって、恒久ではありません。判断は使用実態で検証するのが誠実なので、数週間後に「Zed を何回開いたか」を振り返るつもりです。

まずは brew 1 コマンドで入るので、Claude Code を 2 本以上並列で回している方は、`herdr agent list` に自分のエージェントたちが写るところから試してみてください。

## 関連リンク

- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr) — herdr 本体（GitHub）
- [herdr.dev](https://herdr.dev/) — 公式サイト・ドキュメント
- [Ghostty](https://ghostty.org/) — 最終的に選んだターミナル
- [Zed: Parallel Agents](https://zed.dev/blog/parallel-agents) — Zed 側の並列エージェント機能
- [zed#56111](https://github.com/zed-industries/zed/discussions/56111) — Markdown プレビュー行間のハードコードに関する Discussion
- [iPhoneからClaude Codeを操作する — Termius + Tailscale + tmux](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code) — モバイル接続経路の構築（tmux を herdr に読み替え可）
- [iPhone公式アプリでClaude Codeを運用する](https://zenn.dev/shimo4228/articles/iphone-claude-code-remote-control) — 会話 UX 側の運用
- [Cursor から Zed への移行記](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration) — 本記事の Zed 環境の前提
- [github.com/shimo4228](https://github.com/shimo4228) — 筆者の GitHub（エージェント関連のスキル・ツール置き場）
