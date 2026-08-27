---
title: "iPhone公式アプリでClaude Codeを運用する — 新セッション・再認証・git push、3つの穴の塞ぎ方"
emoji: "📱"
type: "tech"
topics: ["claudecode", "tmux", "remotecontrol", "iphone", "github"]
published: true
published_at: 2026-07-09 09:00
---

> **この記事でわかること**: iPhoneの公式Claudeアプリ（Remote Control）をメインにClaude Codeを外から動かすとき、ぶつかりやすい3つの穴の塞ぎ方です。

以前、[iPhoneからClaude Codeを操作する環境をTermius + Tailscale + tmuxで作った話](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)を書きました。あれはSSHで黒い画面に直接繋ぐやり方です。

その後、Claudeの公式モバイルアプリに**Remote Control**（Mac上のClaude Codeをそのまま遠隔操作する機能）が数ヶ月前に追加されました（Claude Code v2.1.51 以降で使えます）。UIがよくできていて、いまはこちらがメインです。SSHの黒い画面より、承認プロンプトも進捗も圧倒的に見やすいです。

ただ、公式アプリをメインにすると3つの穴にぶつかります。しかもどれも、外出先のiPhoneだけでは塞げません。

| 穴 | 症状 | 塞ぎ方 |
|---|---|---|
| **その1** 新しいセッションを立てられない | アプリは既存セッションに接続するだけ | tmuxワンライナーでspawn |
| **その2** Claudeの認証切れ | ログイン用ブラウザがMac側で開く | VNCで認証の瞬間だけ画面に入る |
| **その3** git pushが通らない | `Device not configured` で落ちる | GitHubのデバイスフロー + `--insecure-storage` |

## 前提

この記事は、以下がすでに整っている前提で進めます。環境構築そのものは前回のTermius記事に譲ります。

- **公式Claudeアプリの Remote Control が有効**で、Mac上のClaude Codeをすでに遠隔操作できている。Remote ControlはClaudeのサービス経由でつながるので、iPhoneとMacが同じネットワークにいる必要はありません
- **自宅のMacが常時起動**している（電源接続・蓋を開けたまま・スリープ無効）
- Macに `tmux` が入っている（なければ `brew install tmux`）
- GitHubへのpushは **HTTPS + `gh auth login`** で認証している（SSH鍵でpushしている場合、穴その3は該当しません）
- 後半のVNC再認証では、**iPhoneからMacの画面共有（Screen Sharing）に届く経路**が別途必要です。これはRemote Controlとは別の通信で、自宅LAN内かTailscale等のVPN経由で用意します（設定は[前回記事](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)参照）

## 穴その1：モバイルから新しいセッションを起動できない

公式のRemote Controlには、はっきりした制約があります。**モバイルアプリ自身は、新しいセッションを起動できません。** できるのは、Mac上ですでに動いているセッションを一覧して接続することだけです。一覧に出すセッションは、どこかであらかじめ起動しておく必要があります。

これが地味に効きます。iPhoneでプロジェクトAを操作している最中に「別プロジェクトBのセッションも並行で立てたい」と思っても、その起動をモバイルから引き起こせません。Macの前まで戻って `claude` を叩くしかなく、外出先では詰みます。

:::message
Mac1台で複数セッションを持つこと自体はできます。`claude --remote-control` を名前付きで何本も起動すれば、一覧に並びます。問題はその"起動"をiPhoneから引き起こせない点です。
:::

:::details 純正の別解（server mode / Dispatch）ではダメなのか
Anthropic純正の別解も2つあります（[公式ドキュメント](https://code.claude.com/docs/en/remote-control)）。

**server mode（`claude remote-control`）** は「受付係」のプロセスを1つ常駐させておくと、モバイル側の要求に応じて新しいセッションをその場で生成してくれます（上限は `--capacity N`）。ただし生成されるセッションは**受付係を起動したディレクトリ（または同一リポジトリのworktree）に縛られる**ため、複数の別リポジトリを跨いで立てたい用途には合いません。

**Dispatch**（Desktop連携）は、手元で試した範囲（2026年7月時点）ではまだ試験段階の感触でした。

- 実行環境が Claude Code 本体ではなく別基盤（Cowork——Claude のエージェント向け作業環境）に準じるようで、Claude Code 用に作った自作スキルが使えません
- セッション起動時に「git status・最近のコミット・構成を確認して報告して」といった定型指示が自動で注入され、頼んでいない長い状態レポートから会話が始まります

当面は、この記事の spawn 方式をメインにしています。
:::

### 生きているセッションに、別のセッションを起動させる

回避策の発想はシンプルです。**いま生きているセッション（iPhoneから操作できているもの）にBashを実行させ、そのセッションにMac上で別のClaude Codeを起動させます。**

Claude Codeは `--remote-control` 付きで起動すると、自分自身をRemote ControlのセッションとしてClaudeのサービス側に登録します。登録された生きたセッションは、モバイルアプリの一覧に並びます。だから、tmuxの中で新しい `claude --remote-control` をdetached（バックグラウンド）で起動すれば、それが一覧に一つ増える、という理屈です。

流れを図にするとこうです。

```text
iPhone（公式アプリ / Remote Control）
   │  「新しいセッション立てて」と指示
   ▼
いま生きているセッション（Mac上・RC接続中）
   │  Bash で下のコマンドを実行
   ▼
tmux（detached・ptyを保持 → 切断後も生存）
   │  claude --remote-control "AKC"
   ▼
新しいClaudeプロセス → 自分をRCとして登録 → アプリ一覧に「AKC」が出る
```

iPhoneのRemote Controlから、いま操作しているClaudeにこう頼みます。「`~/MyAI_Lab/agent-knowledge-cycle` で新しいRemote Controlセッションを立てて」。するとClaudeがMac上でこのコマンドを実行します。

```bash
# 新しい Remote Control セッションを tmux で detached 起動する
tmux new-session -d -s cc-AKC \
  "exec $SHELL -lc 'cd ~/MyAI_Lab/agent-knowledge-cycle && exec claude --remote-control \"AKC\"'"
```

ポイントは3つです。

- **`-d`（detached）** — バックグラウンドで起動します。呼び出し元のセッションを乗っ取りません
- **ログインシェル `-lc`** — `node` / `claude` のPATHを読み込ませてから起動します。これがないと「claudeが見つからない」で即死します
- **tmuxがpty（仮想端末）を保持する** — だからSSHやネットワークが切れても、呼び出し元セッションを閉じても、起動したClaudeは生き残り続けます

数秒後、iPhoneのアプリを開くと、セッション一覧に「AKC」が増えています。**Macには一切触れていません。**

実際のセッション一覧がこれです。この記事を書いている `zenn-content` も、その下の `AKC` も、spawnで立ち上げたセッションです[^1]。

[^1]: 前回のTermius記事にも「新セッション」の話が出てきますが、あれは単一のtmuxセッション `cc` の中で `/exit` → `claude` と打ち直して中身を**入れ替える**方法でした。同時に持てるのは1つだけで、別プロジェクトの並行はできません。今回のspawnは名前付きのセッションを複数並べる方法です。

![公式アプリのセッション一覧。spawnで立ち上げた zenn-content と AKC が並んでいる](/images/iphone-claude-code-remote-control-session-list.png)
*スマホからspawnしたセッションが一覧に並ぶ。入力待ち・レビュー待ちのフィルタも使える*

### 毎回手打ちするのは面倒なので、起動スクリプトにまとめた

このワンライナーを毎回手で打つ（しかもiPhoneのフリック入力で）のは現実的ではありません。そこで、プロジェクト名を渡すだけで起動できるように `spawn.sh` という起動スクリプトにまとめ、Claude Codeの**スキル**（特定のタスクをスクリプト化して `/コマンド` で呼び出せる、Claude Code の Agent Skills 機能）から呼べるようにしました。

iPhoneからは「AKCのセッション立てて」と言うだけです。スキル側が "AKC" → `agent-knowledge-cycle` のようにプロジェクトを解決し、下のスクリプトに渡します。このスキルは [spawn-session](https://github.com/shimo4228/claude-harness/blob/main/skills/spawn-session/SKILL.md) として公開しています（スキル定義の書き方ごと参考にできます）。

:::details spawn.sh の全体（コピペで使えます）

```bash
#!/usr/bin/env bash
# spawn.sh — 新しい Claude Code (Remote Control) セッションを tmux で detached 起動する。
# Usage: spawn.sh <project-dir> [display-name]
# 動作条件: tmux 3.2+（new-session の -e オプションを使うため）
set -euo pipefail

PROJECT="${1:?usage: spawn.sh <project-dir> [display-name]}"
PROJECT="${PROJECT/#\~/$HOME}"                       # 先頭 ~ を展開
[[ -d "$PROJECT" ]] || { printf 'spawn.sh: no such directory: %s\n' "$PROJECT" >&2; exit 1; }

NAME="${2:-$(basename "$PROJECT")}"                  # 省略時はディレクトリ名
SESSION="cc-${NAME// /-}-$(date +%H%M%S)"            # tmux セッション名（空白は -）

# tmux を探す。PATH に無くても Homebrew の既定パス（Apple Silicon / Intel 両方）を拾う
TMUX_BIN=""
for candidate in "$(command -v tmux 2>/dev/null || true)" /opt/homebrew/bin/tmux /usr/local/bin/tmux; do
  [[ -n "$candidate" && -x "$candidate" ]] && { TMUX_BIN="$candidate"; break; }
done
[[ -n "$TMUX_BIN" ]] || { printf 'spawn.sh: tmux not found (install: brew install tmux)\n' >&2; exit 1; }

LOGIN_SHELL="${SHELL:-/bin/zsh}"

# tmux -e で値を環境変数として渡す（クォート地獄を回避）。
"$TMUX_BIN" new-session -d -s "$SESSION" -e "CCDIR=$PROJECT" -e "CCNAME=$NAME" \
  "exec $LOGIN_SHELL -lc 'cd \"\$CCDIR\" && exec claude --remote-control \"\$CCNAME\"'"

printf '✅ Remote Control session started: "%s"\n' "$NAME"
printf '   tmux: %s\n' "$SESSION"
printf '   dir:  %s\n' "$PROJECT"

# 起動直後に落ちていないかの簡易チェック（あくまで早期検知。成功保証ではない）
sleep 1
if "$TMUX_BIN" has-session -t "$SESSION" 2>/dev/null; then
  printf '   (tmux session live ✓ — アプリ一覧に出たか最終確認してください)\n'
else
  printf '   ⚠️  起動直後に tmux セッションが消えました（auth 切れ / claude が PATH に無い等）\n' >&2
  exit 1
fi
```

エイリアス表（"AKC" → 実ディレクトリ）はスクリプトに埋めず、呼び出し側のスキルに持たせています。スクリプトは「解決済みのディレクトリと名前を受け取るだけ」の起動役に徹する、という分担です。
:::

実行するとこう返ります。

```text
✅ Remote Control session started: "AKC"
   tmux: cc-AKC-143512
   dir:  /Users/you/MyAI_Lab/agent-knowledge-cycle
   (tmux session live ✓ — アプリ一覧に出たか最終確認してください)
```

この `✓` は「tmuxのペインが1秒後もまだ生きている」だけを表す早期チェックです。**成功の確定はアプリ一覧を見て判断してください。**

:::details ✓ と実際の成否がズレるケース（うまくいかないとき）
- **`✓` が出たのに一覧に出ない** — `claude` が認証待ちや信頼確認のプロンプトで止まっていると、ペインは生きたまま（`✓`）でもセッションは登録されません
- **`✓` が出ずに落ちた** — 認証切れが最有力ですが、PATHやフラグの間違いでも同じ落ち方をします

どちらの場合も、まずはtmuxのペイン（`tmux attach -t cc-AKC-143512`）を覗いて原因を確かめると確実です。
:::

:::message
この回避策は「最低1つのセッションが生きている」ことに依存します。Mac再起動直後で何も動いていないときだけは、Macの前で最初の1つを手動で起動してください。とはいえMacがオフならiPhoneから何もできないので、実運用では問題になりません。
:::

## 穴その2：Claudeの認証が切れると、手元で再ログインできない

モバイルで数日運用していると、ときどきClaude CodeのOAuth認証が切れます。切れた状態でspawnすると、起動直後にこう落ちます。

```text
   ⚠️  起動直後に tmux セッションが消えました（auth 切れ / claude が PATH に無い等）
```

認証切れだった場合、ここからが本番です。認証を通すには、Claude Codeが表示するログインURLをブラウザで開く必要があります。**そのブラウザが開くのは、リモート操作されている自宅のMac側です。** 外出先のiPhoneには何も表示されません。`/login` はMac上のCLIで完結する操作で、Remote Controlはそのブラウザログインを手元に代理してくれるわけではないからです。

### VNCで、認証のためだけにMacの画面に入る

そこで、**認証のときだけ**Macの画面そのものを覗きに行きます。使っているのは無料で使えるVNCビューア（RealVNC Viewer）です。

手順はこれだけです。

1. iPhoneのRealVNC Viewerで自宅Macに接続する
2. Mac側で開いているClaude Codeのブラウザ認証を、iPhoneの指で完了させる
3. 認証が通ったらVNCを閉じ、公式アプリのRemote Controlに戻る

VNCは画面まるごとの映像転送なので、iPhoneの小さい画面での常用はつらいです。でも**「ログインボタンをタップして認証を通す」という一瞬の操作のためだけ**に使うなら、これで十分です。認証さえ通れば、あとは操作性のいい公式アプリに戻れます。

:::details 「無料で使える」の条件（RealVNCのライセンス）
「無料で使える」かはMac側のVNCサーバー次第です。Mac側にRealVNC ServerのLiteプラン（無料・非商用）を入れて繋ぐなら無料で完結します。一方、macOS標準の画面共有（Screen Sharing）に繋ぐ場合、RealVNCの現行ライセンスでは「サードパーティVNCサーバー」扱いとなり、Viewer側に有料プランが必要になります。無料で済ませたいならサーバー側もRealVNCで揃えるのが確実です。
:::

:::message alert
**VNCはセキュリティに注意してください。** Mac画面への遠隔アクセスをカフェのWi-Fiなど共有回線に直接晒すのは危険です。**Mac側の画面共有（VNC）サービスは、自宅LAN内か、Tailscale等のVPN経由でだけ到達できるように限定してください。** 公式アプリのRemote ControlはClaudeのサービス経由でつながる別経路なので、VNCの経路とは切り離して考えます（Remote Controlが動いているからVNCも安全、ではありません）。加えて、VNCには強固なパスワードと暗号化を必ず有効にします。
:::

### 認証をなるべく切らさない

VNCは「切れたときの復旧手段」です。そもそも切らさないに越したことはありません。効くのは1つです。

**Macの前にいるうちに一度ログインし、tmuxでセッションを生かしておきます。** 前回記事のtmux方式と同じ発想です。ローカルでログイン済みの状態からセッションを起動すれば、認証フローに触れる回数そのものが減ります。spawnもこの「生きているセッション」を土台にしているので、大元のセッションを長く生かすほど、再認証の出番は減ります。

## 穴その3：git push が通らない

外で数日運用していると、今度は `git push` が通らなくなりました。作業は終わっているのに、最後のpushでこう落ちます。

```text
fatal: could not read Username for 'https://github.com': Device not configured
```

`gh auth status` を見ると「The token in default is invalid」。トークンが失効した、ように見えます。ここに罠があります。**トークンは生きていて、読めないだけ**のことが多いのです。

### 原因は「SSH/tmuxセッションはKeychainを読めない」

gh（GitHub CLI）は、トークンをmacOSのKeychainに保存します。login Keychainがアンロックされるのは**GUIログインのとき**です。SSH経由のセッションやspawnで起動したtmuxセッションは、ロックされたKeychainを解除することも、アクセス許可の確認ダイアログを表示することもできません。読み取りは「対話禁止」エラー（exit 36）で失敗し、ghはトークンを読めず「invalid」と誤報告し、git pushは認証情報を取れずに落ちます。

[前回記事](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)でClaude CodeのOAuthがSSH経由で毎回切れたのも、根本原因はこれと同じでした。リモート運用では、**Keychainに依存するツールすべてがこの壁に当たります**。

原因の切り分けはコピペで確認できます。

```bash
# Keychain の gh トークンが読めるか（ロック中は exit 36 で失敗する）
security find-generic-password -s "gh:github.com" -w >/dev/null; echo "exit=$?"

# SSH 経由のセッションかどうか
echo "SSH_TTY=${SSH_TTY:-unset}"
```

`exit=36` かつ `SSH_TTY` が設定されていれば、Keychainアクセスの問題です。逆に `exit=0`（トークンは読めている）なのに invalid と言われる場合は、本当に失効しています——その場合も、塞ぎ方は次の節と同じです。

### 塞ぎ方：デバイスフローをClaude自身に走らせる

Claude CodeのOAuth（穴その2）と違い、GitHubには**デバイスフロー**——ワンタイムコードを別デバイスのブラウザで入力して認証を通す方式——があります。これなら**VNCは不要**です。

セッション内のClaudeにこう頼みます。「ghの再認証をデバイスフローで開始して、ワンタイムコードを教えて」。Claudeが実行するのは実質これだけです。

```bash
# バックグラウンドで認証フローを起動し、ワンタイムコードをログから読む
printf '\n' | gh auth login -h github.com --git-protocol https --web --insecure-storage \
  > /tmp/gh-login.log 2>&1 &
sleep 3 && cat /tmp/gh-login.log
```

```text
! First copy your one-time code: XXXX-XXXX
Open this URL to continue in your web browser: https://github.com/login/device
```

あとは**手元のiPhoneのブラウザ**で `github.com/login/device` を開き、表示されたコードを入力して承認するだけです。承認が通るとMac側の認証プロセスが完了し、そのまま `git push` が通ります。

Macの画面には一度も入っていません。穴その2のClaude OAuthは「ブラウザが開く場所」がMac側に固定されるためVNCが要りましたが、デバイスフローは**コードさえ合っていればブラウザはどの端末で開いてもいい**。この違いが効きます。

### `--insecure-storage` は付けて大丈夫なのか

上のコマンドの `--insecure-storage` は、新しいトークンをKeychainではなく `~/.config/gh/hosts.yml`（パーミッション0600の平文ファイル）に保存するフラグです。これが恒久対応になります。**Keychainを経由しなくなるので、以後はSSHでもtmuxでも `git push` が通ります。**

「insecure」の意味は正確に押さえておきます。弱くなるのは1点だけ——「あなたのユーザー権限で動くプロセスなら読める」ことです。

| 脅威 | Keychain保存 | hosts.yml平文保存 |
|---|---|---|
| 盗難・他ユーザーによるディスク読み取り | 保護される | 0600 + FileVault（電源オフ時）で実質保護される |
| 自分の権限で動く悪意あるプロセス | アプリ単位のACLで一定の防壁 | **読める（ここがinsecure）** |
| バックアップ・dotfiles同期への混入 | Keychainファイル自体が暗号化されている | **`~/.config` ごと平文で載りうる** |
| SSH/tmuxセッションからの利用 | 不可（今回の問題） | 可 |

つまり守りが下がるのは、「マシン内で任意コード実行を許した後」のシナリオと、`~/.config` をバックアップやdotfiles同期に含めている場合です。それでも `~/.aws/credentials` や `.env` の平文APIキーと同じ水準で、CLIツールとしては標準的な保存方式でもあります。漏洩を疑ったらGitHubの [Applications設定](https://github.com/settings/applications) から即失効できます。

保存場所の堅牢さより、**トークンの権限範囲を絞る方が漏洩時の実害には効きます**。絞り方は畳んでおきます。

:::details さらに影響範囲を絞りたい場合（fine-grained PAT）
fine-grained PAT（対象リポジトリと有効期限を限定できるアクセストークン）に切り替える手があります。ただしghは、fine-grained PATを `--with-token` で登録すると一部コマンドの挙動が混乱しうるとして、環境変数 `GH_TOKEN` で渡す方式を推奨しています。pushだけできればよい場合向けの絞り方です。
:::

## 完成した運用

いまのモバイル運用はこの形に落ち着いています。

| 端末・ツール | 役割 | 経路 |
|---|---|---|
| 公式Claudeアプリ（Remote Control） | メインの操作UI。進捗確認・承認・指示出し | Claudeのサービス経由 |
| spawn（tmuxワンライナー / スキル） | Macに触れず新しいセッションを起動する | 上記セッション内のBash |
| RealVNC Viewer | Claudeの認証が切れたときだけMacのブラウザログインをiPhoneから通す | LAN / Tailscale（VNCのみ） |
| デバイスフロー（`gh auth login --web`） | git pushの認証切れをiPhoneのブラウザだけで復旧する | GitHubのサービス経由 |

日常の流れはこうです。

1. iPhoneの公式アプリでいつも通り操作する
2. 別プロジェクトが必要になったら「◯◯のセッション立てて」でspawn。アプリ一覧に出たか確認する
3. `⚠️ セッションが消えた`＝認証切れが最有力なら、VNCで認証だけ通して公式アプリに戻る
4. `git push` が `Device not configured` で落ちたら、Claudeにデバイスフローを走らせてiPhoneのブラウザで承認する（`--insecure-storage` で恒久化すれば以後は発生しません）

正直に書くと、iPhoneは前回同様やはり「リモコン」です。本格的なレビューはMacに戻ってやります。ただ、**Macに一切触れずにセッションを起動できて、認証が切れても外から復旧できて、pushまで完結する**——この3点が塞がったことで、外出先で詰む場面はほぼなくなりました。

## まとめ

- 公式アプリのRemote ControlはUIがよく、モバイル操作のメインに向く。ただし「モバイルからは新セッションを起動できない」「Claudeの認証切れを手元で直せない」「git pushの認証が通らない」の3つの穴がある
- **新セッション問題**は、生きているセッションに `tmux new-session -d ... claude --remote-control` を起動させて回避する。新プロセスが自分でRemote Controlのセッションを登録し、アプリ一覧に並ぶ（`✓` は早期チェック。確定はアプリ一覧で）
- **Claudeの認証切れ**は、VNCで認証のときだけMac画面に入り、ブラウザログインをiPhoneから通して塞ぐ。VNC（画面共有）の経路はLAN/VPNに限定し、Remote Controlとは別扱いにする
- **git pushの認証**は、原因がKeychain（SSH/tmuxからは読めない）。ghのデバイスフローをClaudeに走らせてiPhoneのブラウザで承認し、`--insecure-storage` でKeychain非依存にして恒久化する
- 環境構築（Tailscale等）は前回のTermius記事に譲り、この記事は公式アプリ主軸の実運用に絞った

エディタを捨て、SSHの黒い画面すら経て、いまはポケットの公式アプリからMacに触れずにセッションを起動し、pushまで済ませています。残った穴は、tmuxのワンライナー・VNC・デバイスフローで一つずつ塞げました。

## 関連記事

道具の話はここまで。一段奥の、エージェント設計そのものの話:

- [ReAct エージェントが本当に必要な業務はどれか](https://zenn.dev/shimo4228/articles/react-agent-business-quadrant)
- [Claude Codeから簡単にCodexレビューさせるスキルを作った](https://zenn.dev/shimo4228/articles/codex-review-cross-model-decorrelation)

前回のモバイル環境構築編:

- [Claude Code をiPhoneから操作する方法 — Termius + Tailscale + tmux 環境構築ガイド](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)

記事で使ったスキル:

- [spawn-session skill（claude-harness）](https://github.com/shimo4228/claude-harness/blob/main/skills/spawn-session/SKILL.md) — 本記事の spawn 方式をスキル化したもの

研究としての成果物（DOI 付き）は [github.com/shimo4228](https://github.com/shimo4228) に。

## 関連リンク

- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/iphone-claude-code-remote-control.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
