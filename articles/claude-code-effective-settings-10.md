---
title: "デフォルトのまま使うな ── Claude Code で本当に効いた設定10選"
emoji: "⚙️"
type: "tech"
topics: ["claudecode", "ai", "cli", "devtools"]
published: true
---

承認ダイアログを 1 日 200 回叩いた。作業が乗ってきた瞬間にコンテキストが飛んで「さっきの話、覚えてないんですけど」と言われた。Claude が勝手に `git add .` して `.env` をステージングした。

270 セッションでこういう事故を全部潰した。残ったのが 10 個の設定だ。

:::message
<!-- textlint-disable -->
本記事は 2026 年 3 月時点の Claude Code（CLI 版）の設定に基づいている。バージョンアップで仕様が変わる可能性がある。
<!-- textlint-enable -->
:::

## 前提

- **用途**: Python 自動化スクリプト、Zenn 記事執筆、iOS アプリ開発
- **ポリシー**: コードは Claude が書く。人間は設計と判断に集中する

設定ファイルの全体構造は [設定ファイルを全棚卸しして分かった5つのこと](https://zenn.dev/shimo4228/articles/claude-code-context-audit) で書いた。本記事はさらに踏み込んだ「実運用で事故を防いだ具体的な設定」だ。

---

## 1. コンテキストが飛ぶ前に気づく

Claude Code の最大の罠は、コンテキストウィンドウが静かに埋まっていくことだ。気づいたときには 90% を超えていて、自動圧縮（auto-compact）でそれまでの作業文脈がごっそり消える。

`~/.claude/settings.json` にステータスラインを設定すると、ターミナルの下部に常時表示される。

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  }
}
```

表示スクリプト（`~/.claude/statusline-command.sh`）:

```bash
#!/bin/bash
input=$(cat)
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
model_name=$(echo "$input" | jq -r '.model.display_name // "Claude"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')

status_parts=()
status_parts+=("$model_name")
[ -n "$cwd" ] && status_parts+=("$(basename "$cwd")")

if [ -n "$used_pct" ]; then
  used_int=$(printf "%.0f" "$used_pct")
  bar_width=20
  filled=$(( used_int * bar_width / 100 ))
  empty=$(( bar_width - filled ))
  bar=""
  for ((i=0; i<filled; i++)); do bar+="█"; done
  for ((i=0; i<empty; i++)); do bar+="░"; done
  status_parts+=("[${bar}] ${used_int}%")
fi

printf "%s" "${status_parts[0]}"
for ((i=1; i<${#status_parts[@]}; i++)); do
  printf " | %s" "${status_parts[$i]}"
done
printf "\n"
```

実行結果はこうなる。

```text
Claude Opus 4.6 | zenn-content | [████████░░░░░░░░░░░░] 40%
```

**80% を超えたら作業を区切る** というルールを自分に課している。これだけで「突然の文脈消失」がなくなった。

---

## 2. 「許可しますか？」を 1 日 200 回叩く地獄から抜ける

デフォルトの Claude Code は、Bash コマンドを実行するたびに「許可しますか？」と聞いてくる。`git status` で許可、`ls` で許可、`python` で許可。1 セッションで何度も発生する。

`settings.json` の `permissions.allow` に安全なコマンドを列挙する。

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(python:*)",
      "Bash(npm:*)",
      "Bash(ls:*)",
      "Bash(grep:*)",
      "Bash(jq:*)",
      "Bash(curl:*)",
      "Bash(ruff:*)",
      "Bash(black:*)",
      "Bash(pytest:*)",
      "Read",
      "WebFetch",
      "WebSearch"
    ]
  }
}
```

書式は `"Bash(コマンド名:*)"` で、`*` はすべての引数を許可する。自分の環境では **88 個の Bash コマンド** と **MCP ツール 30 個以上** を事前許可している。

ポイントは **`rm` を入れない** ことだ。ファイル削除だけは毎回確認したい。同様に `sudo`、`dd`、`mkfs` など破壊的なコマンドは意図的にリストから外している。

---

## 3. 全自動にしつつ `rm -rf /` だけは止める

設定 2 のさらに先。`defaultMode` を `bypassPermissions` にすると、許可リストに **ない** コマンドも含めてすべてが自動実行される。

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
```

「それは危険だろう」と感じるだろう。その通りだ。だからこそ **PreToolUse フック** を安全弁として組み合わせる。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/validate-bash.sh"
          }
        ]
      }
    ]
  }
}
```

`validate-bash.sh` の中身はこうだ。

```bash
#!/usr/bin/env bash
set -euo pipefail
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[[ -z "$COMMAND" ]] && exit 0

block() {
  echo "{\"decision\": \"block\", \"reason\": \"$1\"}"
  exit 0
}

# rm -rf /
echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\s+/(\s|$|\*)' \
  && block "rm -rf / is blocked for safety"

# git push --force
echo "$COMMAND" | grep -qE 'git\s+push\s+.*(-f|--force)' \
  && block "git push --force is blocked. Use --force-with-lease"

# git add -A / git add .
echo "$COMMAND" | grep -qE 'git\s+add\s+(-A|--all|\.)(\s|$)' \
  && block "git add -A is blocked. Stage specific files instead"

# sudo
echo "$COMMAND" | grep -qE '(^|[;&|]\s*)sudo\s' \
  && block "sudo is blocked in automated mode"

exit 0
```

仕組みはシンプルだ。Bash ツール実行の **直前** にスクリプトが走り、コマンド文字列を正規表現でチェックする。危険なパターンに該当すれば `{"decision": "block"}` を返して実行を阻止する。該当しなければ何も出力せず通過する。

**ブロック対象は最小限に絞る** のがコツだ。あれこれブロックすると、結局フックが承認ダイアログの代わりになってしまう。自分がブロックしているのは 6 パターンだけだ。

1. `rm -rf /`（システム破壊）
2. `git push --force`（履歴破壊）
3. `git add -A` / `git add .`（意図しないファイルのステージング）
4. `sudo`（権限昇格）
5. `dd` / `mkfs`（ディスク操作）
6. `/dev/` への書き込み（デバイスファイル保護。`/dev/null` 等は許可）

実際にブロックが発動したのは `git add .` が数回。Claude は便利なコマンドを選びがちなので、これが一番役に立っている。

---

## 4. Claude に TDD を強制する

Claude がファイルを編集した **直後** に自動でテストを走らせる。壊れたら Claude 自身に直させる。PostToolUse フックでそれができる。

自分が設定しているのは `.sh` ファイル専用の自動テストだ。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/bats-autorun.sh"
          }
        ]
      }
    ]
  }
}
```

`bats-autorun.sh` は、編集されたファイルが `.sh` で、かつ隣接ディレクトリに `tests/` があるときだけ bats テストを実行する。テストが失敗すると `{"decision": "block"}` を返し、Claude に「テストが壊れたから直せ」と伝える。以下は要点を抜粋した簡略版だ（実際のスクリプトには JSON エスケープ処理などが加わる）。

```bash
#!/usr/bin/env bash
set -euo pipefail
INPUT=$(cat)
filepath=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')

# .sh ファイル以外は無視
[[ "$filepath" == *.sh ]] || exit 0

# tests/ ディレクトリがなければ無視
dir=$(dirname "$filepath")
[[ -d "$dir/../tests" ]] || exit 0

cd "$dir/.."
result=$(bats tests/ 2>&1) || true

if echo "$result" | grep -q "^not ok"; then
  printf '{"decision":"block","reason":"bats tests failed after editing %s"}' \
    "$(basename "$filepath")"
else
  printf '{"systemMessage":"[bats] all tests passed for %s"}' \
    "$(basename "$filepath")"
fi
```

これにより **「編集 → テスト失敗 → Claude が自動修正 → テスト再実行」** のループが人間の介入なしに回る。TDD を Claude に強制する仕組みとも言える。

Python の場合は [Zenn 執筆環境の記事](https://zenn.dev/shimo4228/articles/claude-code-zenn-writing-env) で書いた textlint / markdownlint の自動実行が同じ役割を果たしている。

---

## 5. セッション終了時に散らかしを片付けさせる

PreToolUse（実行前）、PostToolUse（実行後）に加えて、**Stop**（セッション終了時）がフックの第 3 層だ。Claude が散らかしたまま帰ろうとするのを止める。

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/driftcheck.sh"
          }
        ]
      }
    ]
  }
}
```

自分の `driftcheck.sh` は `docs/` ディレクトリの構造を検証する。具体的にはこうだ。

- `docs/README.md` が存在するか
- ルート直下に許可されていないファイルがないか
- `records/` のファイルが `YYYY-MM-DD_` プレフィックスを持つか
- `.DS_Store` が紛れ込んでいないか

**「セッション中に散らかしたものを、終了前に片付けさせる」** という発想だ。CI/CD のプリコミットフックに近い。

3 層フックの全体像を表にまとめた。

| フック | タイミング | 役割 | 例 |
|--------|-----------|------|-----|
| **PreToolUse** | 実行直前 | 破壊的操作をブロック | `rm -rf /`、`git push --force` |
| **PostToolUse** | 実行直後 | 品質チェック・自動テスト | bats テスト、lint |
| **Stop** | セッション終了時 | 整合性の最終検証 | ドキュメント構造チェック |

---

## 6. 「不変性を優先しろ」を 1 回だけ書く

Python でも TypeScript でも「イミュータビリティ優先」と言いたい。だが言語ごとにルールファイルを作ると、同じ原則が 2 箇所に書かれ、片方だけ更新される。Claude Code のルールファイル（`~/.claude/rules/`）は、ディレクトリ構造でこの問題を解決できる。

```text
~/.claude/rules/
├── common/           # 言語に依存しない原則
│   ├── coding-style.md
│   ├── testing.md
│   ├── security.md
│   └── git-workflow.md
├── python/           # Python 固有のルール
│   ├── coding-style.md   ← common/coding-style.md を拡張
│   └── testing.md        ← common/testing.md を拡張
└── typescript/       # TypeScript 固有のルール
    ├── coding-style.md
    └── testing.md
```

`common/coding-style.md` に「イミュータビリティを優先する」と書く。

`python/coding-style.md` の冒頭で `common/coding-style.md` を参照し、`@dataclass(frozen=True)` を使えと具体化する。

`typescript/coding-style.md` では同じ原則を `{...obj, field: value}` のスプレッド構文で具体化する。

**「不変性を優先しろ」を 1 回書くだけで、Python でも TypeScript でも一貫した振る舞い** になる。ルールが 13 ファイル・約 1,000 行に育った今、この構造がなかったら確実に矛盾が発生していた。

---

## 7. iOS 開発中に textlint を引用された日

スキルが 20 個を超えたあたりで異変が起きた。iOS アプリのビルド中に、Claude が Zenn の textlint ルールを引用してきたのだ。スキル（`.claude/skills/`）を 2 つのスコープに分けるべきタイミングだった。

| スコープ | パス | いつ読み込まれるか |
|---------|------|-----------------|
| **グローバル** | `~/.claude/skills/` | 常に |
| **プロジェクト** | `{repo}/.claude/skills/` | そのプロジェクト内でのみ |

自分の場合はこうだ。

- **グローバル**（22 個）: `python-patterns`, `security-review`, `backend-patterns` など汎用スキル
- **プロジェクト**（7 個）: `zenn-writer`, `publish-article`, `seo-optimizer` など Zenn 専用

`zenn-writer` を iOS 開発中に読み込む必要はないし、`security-review` は全プロジェクトで使いたい。この切り分けを意識するだけで、Claude に渡すコンテキストの無駄が減る。

`zenn-writer` を iOS 開発中に読み込む必要はないし、`security-review` は全プロジェクトで使いたい。この切り分けを意識するだけで、Claude に渡すコンテキストの無駄が減る。

---

## 8. 「レビューして」と毎回頼むのをやめた

Claude は頼まれれば何でもやるが、**頼まなければ何もしない**。コードを書いた後に「レビューして」と毎回言うのは、自分の仕事だと思っていた。違った。「頼まなくてもやれ」と事前に書いておけばいい。

自分のルールファイル（`~/.claude/rules/common/agents.md`）にはこう書いてある。

```markdown
## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests → Use **planner** agent
2. Code just written/modified → Use **code-reviewer** agent
3. Bug fix or new feature → Use **tdd-guide** agent
4. Architectural decision → Use **architect** agent
```

つまり「コードを書いたら code-reviewer を呼べ」「バグ修正なら tdd-guide を使え」と **ルールでトリガー条件を定義** している。

これにより、以下が実現する。

- 複雑な機能実装 → 自動で planner が起動し、計画を立ててから実装に入る
- コード変更後 → 自動で code-reviewer がレビューする
- テストが必要な場面 → tdd-guide が RED → GREEN → REFACTOR のサイクルを強制

「レビューして」と毎回頼む必要がなくなった。

---

## 9. 200 行を超えたら MEMORY.md は壊れる

MEMORY.md（`~/.claude/projects/{project}/memory/MEMORY.md`）は、セッション開始時に自動で読み込まれる永続メモリだ。コンテキスト圧縮が起きても消えない。仕組みの詳細は[記憶を埋め込んだ記事](https://zenn.dev/shimo4228/articles/claude-code-persistent-memory)で書いた。

便利だが、**200 行を超えると truncate される**。何を書いて何を書かないかの取捨選択が運用の核心だ。

**書くべきもの**（= 何度も参照する情報）。

- プロジェクトのツールチェーン（linter の設定、テストの実行方法）
- 過去にハマった罠と解決策（Key Gotchas）
- 文体規約やブランディング方針
- 外部サービスの制約（API レートリミット、文字数制限）
- 進行中タスクの状態

**書くべきでないもの**（= すぐ古くなる情報）。

- 特定セッションの作業ログ
- 一度しか使わない調査結果
- CLAUDE.md と重複する内容
- 検証していない仮説

自分の MEMORY.md は現在約 180 行で、トピック別にセマンティックな構造で整理している。長くなりそうなトピックは別ファイルへ切り出し、MEMORY.md からリンクする運用だ。

---

## 10. プラグインは全部入れるな

Claude Code にはプラグインシステム（`enabledPlugins`）がある。全部有効にしたくなるが、やめた方がいい。プラグインが増えると起動が遅くなるだけでなく、Claude に渡されるコンテキストが膨れてトークンを圧迫する。

```json
{
  "enabledPlugins": {
    "pyright-lsp@claude-plugins-official": true,
    "github@claude-plugins-official": false,
    "swift-lsp@claude-plugins-official": true,
    "hookify@claude-plugins-official": true,
    "claude-mem@thedotmack-claude-mem": true,
    "everything-claude-code@everything-claude-code": true
  }
}
```

自分の場合、`github` プラグインは `gh` CLI で十分なので無効にしている。逆に `pyright-lsp`（Python 型チェック）と `swift-lsp`（Swift の LSP）は常時有効だ。

プラグインのポイントをまとめる。

- **LSP プラグイン**（pyright, swift-lsp）: Claude がコードの型情報をリアルタイムで参照できる。型エラーの早期検出に直結する。
- **hookify**: フックの管理 UI を提供する。フックが増えてきたら必須だ。
- **claude-mem**: セッション間の永続メモリ。MEMORY.md を補完する検索可能なデータベースとして機能する。
- **everything-claude-code**: エージェント・スキル・コマンドのパッケージ。自分の環境の土台になっている。

使うものだけ有効にする。それだけで起動が速くなり、トークンの無駄遣いが減る。

---

## settings.json の全体像

ここまでの設定をまとめると、`~/.claude/settings.json` の骨格はこうなる（本記事で紹介した設定の抜粋）。

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(python:*)",
      "Bash(npm:*)",
      "Bash(ls:*)",
      "Bash(grep:*)",
      "Read",
      "WebFetch",
      "WebSearch"
    ],
    "defaultMode": "bypassPermissions"
  },
  "model": "opus",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/validate-bash.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/bats-autorun.sh"
        }]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/driftcheck.sh"
        }]
      }
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  },
  "enabledPlugins": {
    "pyright-lsp@claude-plugins-official": true,
    "swift-lsp@claude-plugins-official": true,
    "hookify@claude-plugins-official": true,
    "claude-mem@thedotmack-claude-mem": true,
    "everything-claude-code@everything-claude-code": true
  }
}
```

---

## まとめ: 事故が起きてからでは遅い

10 個の設定に共通するのは、**「問題が起きない仕組みを先に作る」** ことだ。

- コンテキストが飛ぶ → ステータスラインで残量を見る
- 承認ダイアログ地獄 → 許可リストで消す
- `rm -rf /` → フックで止める
- レビュー忘れ → エージェントに自動起動させる
- スキルのノイズ → スコープを分ける

デフォルトのまま Claude Code を使うのは、シートベルトなしで高速道路を走るようなものだ。270 セッションの事故記録が、この 10 個に結晶した。

設定ファイルの全体構造は [設定ファイルを全棚卸しして分かった5つのこと](https://zenn.dev/shimo4228/articles/claude-code-context-audit) も参考にしてほしい。
