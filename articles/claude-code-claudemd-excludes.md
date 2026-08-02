---
title: "Claude Codeに2つ目のハーネスを持たせる"
emoji: "⚙️"
type: "tech"
topics: ["claudecode", "anthropic", "contextengineering", "cli", "claude"]
published: true
published_at: 2026-08-03 09:00
---

育ててきた CLAUDE.md・rules・skills 一式は、普段の開発では効きます。ただ、実験や自律ループを回すときには重すぎることがあります。用途によって持ち替えたくなります。

ところが Claude Code に、**個人ハーネスだけを入れ替え、repo の設定は残す単一のプロファイル切り替えはありません**。一番近いのは設定ディレクトリを差し替える `CLAUDE_CONFIG_DIR` ですが、これは半分しか切り替えません。skills と agents は入れ替わるのに、CLAUDE.md と rules は元のまま付いてきます。手元では 16 ファイル・3,404 語が毎回入っていました。

公式に用意されていないのはここだけです。そこで、設定ディレクトリの切り替えとパス単位の除外を組み合わせます。

前半では、この組み合わせが必要な理由と、何が残るかを説明します。後半には、そのまま手元のコーディングエージェントへ渡せる計画プロンプトを置きます。読者の環境を読み取ったうえで、実行前のプランまで作らせます。

## 前提

- Claude Code v2.1.220 / macOS で実測しました
- 「ハーネス」はこの記事では、`CLAUDE.md`・`rules/`・`skills/`・`agents/` をまとめた設定一式を指します
- 以降、`CLAUDE_CONFIG_DIR` で指定した新しいディレクトリを「分けた側」と呼びます

## 設定ディレクトリはハーネスを半分しか切り替えない

`CLAUDE_CONFIG_DIR` は、Claude Code が使う設定ディレクトリを別の場所に向ける環境変数です。これを使ったとき、何が切り替わり、何が残るかを確かめると次のようになります。

| 対象 | ハーネスの部品か | 分けた側に切り替わるか |
|---|---|---|
| `skills/` と `agents/` | ✅ | 切り替わる |
| **`CLAUDE.md` と `rules/`** | ✅ | **切り替わらない（元のものが入ってくる）** |
| `settings.json`（hooks の定義を含む） | — | 切り替わる |
| セッション履歴・プラグイン | — | 切り替わる |

ハーネスの 4 部品のうち、入れ替わるのは上半分だけです。

下 2 行は公式ドキュメントの説明どおりです。

> Override the configuration directory (default: `~/.claude`). All settings, session history, and plugins are stored under this path
> （[Environment variables](https://code.claude.com/docs/en/env-vars)）

skills と agents はこの文に出てきませんが、実際には切り替わりました。分けた側で起動して一覧を尋ねると、自作スキルは出てこず、分けた側に置いたものだけが並びます。

認証情報の保存先は OS で違います。Linux と Windows では設定ディレクトリ配下、macOS ではシステムのキーチェーンです。この記事で実測した macOS では、設定ディレクトリと一緒に認証ファイルが移るわけではありません。

残るのが `CLAUDE.md` と `rules/` です。これらは設定ディレクトリの管轄ではなく、別の仕組みで探されます。

> Claude Code reads CLAUDE.md files by walking up the directory tree from your current working directory
> （[How Claude remembers your project](https://code.claude.com/docs/en/memory)）

たどる途中で見つかった `.claude/` は、どの階層のものでもプロジェクトの設定として読まれます。ホームの下で作業していれば必ず `~/` を通るので、`~/.claude/` が毎回その対象になります。設定ディレクトリをどこに向けても関係ありません。

:::details 「祖先をたどる」を確かめた記録
中身が空の設定ディレクトリを指定して起動しました。設定ディレクトリからは何も読めないはずですが、`~/.claude` の 16 ファイルが読み込まれます。しかも Claude Code はこれを個人設定ではなくプロジェクトのファイルとして記録します。

| 起動条件 | 読み込まれた `~/.claude` のファイル | 記録された種別 |
|---|---|---|
| 既定（設定ディレクトリ = `~/.claude`） | 16 | 個人設定（`User`） |
| 空の設定ディレクトリを指定 | 16 | プロジェクト（`Project`） |

ラベルが変わるだけで、読み込まれる事実は変わりません。作業ディレクトリをホームの外に置けばこの経路は消えます。シンボリックリンクで別の場所に見せかける方法も試しましたが、実体のパスが解決されるため効きませんでした。
:::

Claude Code には、カスタマイズを広く止める公式手段はあります。ただし、どれも今回の境界とは違います。

| 公式手段 | 止まるもの | 今回使わない理由 |
|---|---|---|
| `--safe-mode` | CLAUDE.md・skills・hooks・plugins などのカスタマイズ全般 | repo 側のカスタマイズも止まる |
| `--bare` | CLAUDE.md・hooks・plugins・MCP・自動メモリーなどの自動読み込み | スクリプト向けの最小起動で、repo 側も止まる。skill は明示的に呼び出せる |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` | user・project・自動メモリーの指示ファイル | repo の CLAUDE.md まで止まる |

欲しいのは、個人ハーネスだけを入れ替え、repo の取扱説明書と機械ゲートは残す動きです。この選択的な切り替えには、単一の公式スイッチがありません。「グローバルの CLAUDE.md をセッション単位で無効化したい」という [issue #30380](https://github.com/anthropics/claude-code/issues/30380) も、not planned として閉じられています。

## 人間が決めるのは、どの境界で分けるか

今回作る境界は次のとおりです。

| 対象 | 扱い |
|---|---|
| 普段の `~/.claude` | 変更しない |
| 個人の CLAUDE.md・rules・skills・agents | 2 つ目へ入れ替える |
| repo の CLAUDE.md・rules・settings・hooks | そのまま残す |
| プロジェクトメモリー | 既定では分ける。必要なら共有する |

これなら、普段の開発環境に影響を与えず、実験用・自律ループ用・別アカウント用などのハーネスを持てます。

仕組みは 2 段です。

1. `CLAUDE_CONFIG_DIR` で settings・skills・agents・履歴などの置き場を変える
2. 分けた側の `claudeMdExcludes` で、元の `~/.claude/CLAUDE.md` と `rules/` を読み込み対象から外す

`claudeMdExcludes` は絶対パスの glob を受け取ります。ターミナルでは `~`（チルダ）がホームディレクトリの省略記号として使われますが、ここでは展開されません。`~/.claude/**` と書くと、エラーが出ないまま除外に失敗します。

会社や学校の管理端末では、IT 管理者が端末全体へ CLAUDE.md を配布している場合があります。この組織管理の指示だけは、個人の設定では除外できません。個人端末で使っていなければ、この例外は無視して構いません。

ここまで理解できれば、残りは読者ごとに異なるファイル操作と検証です。手で記事のコマンドをなぞるのではなく、エージェントに自分の環境を調べさせ、実装プランに変換します。

## この記事をエージェントに渡してプランする

この記事の URL と、次のプロンプトを手元のコーディングエージェントへ渡してください。この段階では、エージェントにファイルを変更させません。

````text
この記事を読み、Claude Code の用途別ハーネスをこのマシンに作るための実装プランを作ってください。

重要:
- この依頼では読み取り専用で調査する
- ファイルの作成・編集・移動・削除、設定変更、symlink 作成、git 操作はしない
- 実行コマンドはプランに書くだけで、まだ実行しない

希望:
- TARGET_CONFIG_DIR 候補: ~/.claude-alt
- 2 つ目のハーネスの中身: 未定。既存候補がマシン内にあるか探す
- プロジェクトメモリーの共有: しない

目的:
- 普段の ~/.claude は一切変更しない
- TARGET_CONFIG_DIR に、別の CLAUDE.md・rules・skills・agents を置けるようにする
- TARGET_CONFIG_DIR で起動したとき、元の ~/.claude/CLAUDE.md と ~/.claude/rules/** は読み込ませない
- 作業中の repo にある CLAUDE.md・.claude/rules・settings・hooks は残す

この記事を取得できない場合も、以下の調査・計画条件を正本として作業する。

読み取り調査:
1. claude --version、OS、HOME の実パスを確認する。
2. ~/.claude、設定ディレクトリ候補、repo 内の .claude の構成を調べる。内容を公開レポートに転記する必要はない。
3. 2 つ目のハーネス候補を探し、CLAUDE.md・rules・skills・agents ごとに何を移すか候補を出す。候補がなければ empty 構成とする。
4. 既存の settings.json、symlink、projects/、managed policy の有無を確認する。

プランに必ず含める要件:
- 普段の ~/.claude と repo 内のファイルは変更しない
- 設定ディレクトリ候補を絶対パスへ解決し、`/`・HOME・~/.claude・~/.claude 配下・既存 symlink は対象から外す
- 既存ファイルは上書きしない。同名資産は差分を出し、同一ならスキップ、異なるなら人間の承認点にする
- symlink は実体をコピーせず、リンク先とリスクを示す
- settings.json の既存キーを保ったまま、`claudeMdExcludes` に HOME を解決した絶対パスの `<HOME>/.claude/**` をマージする。`~/.claude/**` は使わない
- CLAUDE.md・rules・skills・agents の配置先をファイルごとに示す
- 除外設定の追加前に baseline を取り、追加後と比較する検証手順を書く
- 検証は一時ディレクトリと `--settings` を使い、既存 settings.json や hooks を検証用に書き換えない
- InstructionsLoaded hook は `matcher: "session_start"` に限定する。プロセス終了後に上限時間つきでログの安定を待ち、`file_path` のユニーク件数と内訳を比較する
- 成功条件は、元の ~/.claude 由来 0 件、2 つ目の CLAUDE.md / rules は読み込み、repo 由来は維持とする
- LLM の返答内容ではなく、/context または InstructionsLoaded の記録を証拠にする
- 検証後に一時ファイルを削除し、最終 settings.json の差分と JSON 構文を再確認する
- プロジェクトメモリーを共有する案は本プランから外す。代替案として、会話履歴の混在と `claude project purge` の削除リスクつきで別記する

出力:
1. 現在状態の要約
2. 採用する構成と理由
3. 実装手順。各ステップに対象パス、実行コマンド、変更内容、復元方法を付ける
4. 検証手順と成功条件
5. 人間の承認が必要な箇所
6. 未検証事項とリスク

プランを提示したら停止し、私が明示的に承認するまで実行しないでください。
````

出てきたプランで、対象パス・上書きしないこと・復元方法・成功条件を確認します。問題がなければ、同じエージェントに「このプランを実装し、記載した成功条件まで検証して」と明示的に承認して進めます。

プランで目指す配置は次の形です。

```text
~/.claude-alt/
├── CLAUDE.md        # 2 つ目のハーネス案にある場合
├── settings.json
├── rules/
├── skills/
└── agents/
```

`settings.json` に入る要点はこの 1 キーです。プランでは、既存のキーを残したままマージする手順を出させます。

```json
{
  "claudeMdExcludes": [
    "/Users/you/.claude/**"
  ]
}
```

`/Users/you/` は説明用です。実ファイルには、エージェントが取得した HOME の絶対パスが入ります。

## 成功はロード元で判定する

手軽な確認は、分けた側で起動して `/context` を実行し、**Memory files** を見ることです。

自動確認には `InstructionsLoaded` hook を使います。この hook は CLAUDE.md や rules が読み込まれるたびに、絶対パスの `file_path`、`memory_type`、`load_reason` を出します。プロンプトでは、この記録を使った対照実験まで必須にしています。

Claude Code v2.1.220 の手元の環境では、同じ repo で除外設定だけを変えると次の結果になりました。

| ロード元 | 除外なし | 除外あり |
|---|---:|---:|
| `~/.claude` 由来 | 16 | **0** |
| repo 由来 | 1 | 1 |
| 合計 | 17 | **1** |

`~/.claude/**` と書いた場合は 17 件のままでした。絶対パスに直すと 1 件になりました。これは v2.1.220 での実測です。エラーの有無ではなく、`file_path` の内訳で成功を判定してください。

:::message
LLM に「この指示を知っていますか」と聞いても、ロード元の証明にはなりません。同じ情報を repo のメモリーや学習済み知識から答えられるためです。Claude Code 自身が出す `/context` と `InstructionsLoaded` の記録を使います。
:::

:::details 応用：ハーネスは分けても、プロジェクトの記憶は共有する
プロジェクトメモリーも設定ディレクトリ配下なので、分けた側からは見えなくなります。いつもの記憶を引き継ぎたい場合も、すぐにリンクを作らせず、計画プロンプトの「プロジェクトメモリーの共有」を「検討する」に変えて再計画させます。

`projects/` を丸ごとつなぐと、以後の新規プロジェクトも張り直し不要で共有されます。

ただし共有されるのはメモリーだけではありません。同じディレクトリには会話の記録も入っているので、`/resume` の一覧に分けた側のセッションが混ざります。

**共有している間は `claude project purge` を実行しないでください。** v2.1.220 の手元の `--dry-run` では、1 プロジェクトに対して 72 項目が削除対象に挙がりました。`projects/` を丸ごとつないだ状態で purge が `projects/<slug>/` を削除すると、リンク先にある通常環境の会話記録と自動メモリーも消えます。file-history・tasks・設定エントリ・入力履歴など、ほかの削除対象は分けた側にあるものです。
:::

## まとめ

やることは 2 つだけです。

1. `CLAUDE_CONFIG_DIR` で設定ディレクトリを分ける（skills・agents・hooks・履歴がここで切り替わる）
2. 分けた側の `settings.json` に `claudeMdExcludes` を書く（CLAUDE.md と rules もここで切り替わる）

これで「起動時に環境変数を指定するとハーネスごと入れ替わる」状態になります。切り替えスイッチを探すと見つかりませんが、**切り替わらずに残る部分を名指しで外す**と、同じ結果に届きます。

最後にもう一度だけ。**除外を書いたら必ず読み込み結果を確認してください。** 効いていない状態がエラーではなく沈黙として現れるのが、この設定のいちばん厄介なところです。

## 参考リンク

- [How Claude remembers your project](https://code.claude.com/docs/en/memory) — CLAUDE.md の読み込み順序と `claudeMdExcludes`
- [Hooks reference](https://code.claude.com/docs/en/hooks) — `InstructionsLoaded` hook
- [Environment variables](https://code.claude.com/docs/en/env-vars) — `CLAUDE_CONFIG_DIR` を含む環境変数一覧
- [CLI reference](https://code.claude.com/docs/en/cli-usage) — `--safe-mode` と `--bare`
- [issue #30380](https://github.com/anthropics/claude-code/issues/30380) — グローバル CLAUDE.md の無効化要望（not planned）

## 関連リンク

- [claude-harness](https://github.com/shimo4228/claude-harness) — 筆者が実際に育てている Claude Code ハーネス
- [github.com/shimo4228](https://github.com/shimo4228) — 筆者のほかのリポジトリ一覧
