---
title: "Claude ModsとOutput Styleで、Claude Codeを執筆用のハーネスにする"
emoji: "✍️"
type: "tech"
topics: ["claudecode", "claude", "contextengineering", "プラグイン", "執筆"]
published: true
published_at: 2026-10-03 17:31
---

Claude Codeで記事を書くと、claude.aiのチャットとは違う良さがあります。スキルやルールといったハーネスを自分で組めますし、Claudeにどんなコンテキストを渡すかもかなり自由に決められます。私はこのリポジトリ（zenn-content）に、執筆用のスキルとレビュー用のエージェントを置いて記事を書いています。

ただ、執筆のリポジトリで開いても、Claudeに見えているのはコード用に育てたグローバルのハーネスでした。2026年10月3日に測ると、Claudeに渡るスキル一覧は98件、26,252字ありました。このリポジトリのスキルはそのうち7件で、残りは`~/.claude`の自作スキル、プラグイン、ビルトイン、claude.aiから同期されたスキルです。`tdd`や`implementation-chain`も並んでいました。

コード用のハーネスと執筆の規約がぶつかるので、これまで色々な手を打ってきましたが、どれも外科的処置に留まっていました。今回、Claude Mods（Claude Codeのmod。プラグインに入れるhooks module）とOutput Style（出力スタイル）を組み合わせると、かなりタスクに特化したハーネスが組めることが分かってきました。その最初の1つを、コードとは違う規約が要る執筆で作りました。

この記事では、Claudeに見せるものをModで選び、Claudeの話し方を出力スタイルで決める、という2つの組み方と、作る途中で測って分かったことを書きます。計測はClaude Code 2.1.287と2.1.288で、`claude -p`を使いました。

![Claudeに渡るスキル98件・エージェント37型・指示ファイル21件（リポジトリ分を含む総数）は、Modのprofile zenn-writingで49件・14型・19件になる。リポジトリのものはModでも外れない。出力スタイル zenn-writingは1ターン目に会話の規約の本文を差し込み、2ターン目からは名前の念押しだけを差し込む](/images/harness-scope-writing-harness-hero.png)

ModはClaudeに見えるものを選び、出力スタイルはClaudeの話し方を決めます。2つは別の経路でClaudeに届きます。

## 設定でいくつか外しても、一覧はほとんど縮みませんでした

Claude Codeには、リポジトリの`.claude/settings.json`で外す設定があります。2.1.287では、`skillOverrides`（スキル）、`enabledPlugins`（プラグイン）、`claudeMdExcludes`（指示ファイル）がリポジトリ単位で効きました。

ただ、自作スキルを3件外しても、スキル一覧はほとんど縮みませんでした。2.1.287では一覧が101件、26,551字あり、3件外すと26,534字でした。[公式ドキュメント](https://code.claude.com/docs/en/skills)によると、スキル一覧にはcontext windowの1%の文字数の予算があり、溢れると一部のスキルの説明が落とされます。3件ぶん空いた字数は、残りのスキルの説明に回ったと見ています。

プラグインは、もう1つ問題がありました。プラグインのスキルは`skillOverrides`で外しても一覧に残り、`enabledPlugins`でプラグインごと切ると、スキルとエージェントが一緒に消えます。私の執筆の手順では、Codexプラグインのエージェント（`codex:codex-rescue`）に初見の読み手を頼んでいます。Codexのスキルは要りませんが、プラグインごと切るとこのエージェントまで消えてしまいます。

## Modで、リポジトリごとに見せるものを選びます

Modを使うと、Claude Codeが、Claudeに渡すスキル一覧や指示ファイル（CLAUDE.mdやrules）を組み立てる途中に関数を差し込めます。2.1.287以降では既定で有効です（[Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)）。

これを使って、グローバルのハーネスは1つのまま、リポジトリごとにClaudeに見せるものを選ぶ[harness-scope](https://github.com/shimo4228/harness-scope)を作りました。インストールは1回だけです。

```bash
claude plugin marketplace add shimo4228/harness-scope
claude plugin install harness-scope@harness-scope
```

外すものは、`~/.claude/harness-scope/profiles/`に名前付きのprofileとして書きます。リポジトリの側は、どのprofileを使うかを1行で選ぶだけです。

```json
{ "profile": "zenn-writing" }
```

これを`.claude/harness-scope.json`に置きます。zenn-content用のprofile `zenn-writing`は、外すものを並べる形で書きました。後で出てくる出力スタイルにも同じ名前を付けたので、この記事では「profile zenn-writing」「出力スタイル zenn-writing」と呼び分けます。抜粋です。

```json
{
  "skills": {
    "deny": ["implementation-chain", "tdd", "verify-bootstrap", "codex:*", "hookify:*"]
  },
  "agents": {
    "deny": ["architect", "refactor-cleaner", "security-reviewer", "pr-review-toolkit:*"]
  },
  "instructions": {
    "deny": ["~/.claude/rules/common/testing.md", "~/.claude/rules/common/coding-style.md"]
  }
}
```

Codexは、スキルだけを`codex:*`で外し、エージェントは残しています。スキルとエージェントを別々に選べるので、設定では切れなかった組み合わせが書けます。

残る49件は、このリポジトリの7件のほか、翻訳や見出しづくりなどの自作スキル12件、ビルトイン、claude.aiから同期されたスキル、プラグインのスキル2件です。ビルトインは、`code-review`や`simplify`のようにコード用のものでも残しました。

> Claudeのビルトイン系は念のため残しといて。仕様が変わると追従コストが大変だし。

新しい会話で`/harness-scope`を打つと、何が外れているかが出ます（スキル名の一覧は省略しています）。

```text
harness-scope: profile "zenn-writing" from ~/.claude/harness-scope/profiles/zenn-writing.json, selected by …/zenn-content/.claude/harness-scope.json
skills (deny): 49 off — archify, authorship-strategy, config-gc, …
agents (deny): 23 off — architect, claude-security:claude-security, …
instructions (deny): 2 off — ~/.claude/rules/common/coding-style.md, ~/.claude/rules/common/testing.md
tools: not in the profile
```

冒頭の計測と同じ日、同じ版（2.1.288）で、Modを切った場合と比べました。

| | Modなし | profile zenn-writing |
|---|---|---|
| スキル一覧 | 98件、26,252字 | 49件、15,242字 |
| エージェント一覧 | 37型、17,921字 | 14型、5,519字 |
| 指示ファイル | 21件 | 19件 |

半分を外すと、スキル一覧の字数は4割ほど減りました。3件外したときと違うのは、残ったスキルが予算に収まるようになったためと見ています。外したスキルをSkillツールで呼ぼうとすると、理由付きで断られます。

harness-scopeには、残すものだけを並べる形の`writing`というprofileも同梱しています。2.1.287で当てると、スキル一覧は101件26,551字から、リポジトリ自身の7件、1,623字まで縮みました。ビルトインまで外すなら、この形になります。

## 外すつもりだったコーディング指示は、Claude 5系にはありませんでした

Modを作ろうと決めたとき、外したかったものはもう1つありました。Claude Codeのsystem promptにあるコーディング用の指示です。出力スタイルには`keep-coding-instructions`という項目があり、`false`にするとコーディング用の部分が外れます（[Output styles](https://code.claude.com/docs/en/output-styles)）。

まずOpus 5.5で、`keep-coding-instructions: false`の出力スタイルを選ぶ前と後のsystem promptを記録しました。外れた節はありませんでした。Claudeはこの1条件の結果から、外したかったものはそもそも無い、とまとめました。私はこの結論を止めました。

> どういうこと？おかしいでしょ。じゃあなんでそんな仕組みがあるの？セッション途中だからじゃないの？

モデルを変えて取り直すと、結果はモデルの世代で分かれました。

| モデル | system promptの節の合計 | `keep-coding-instructions: false`で外れた節 |
|---|---|---|
| Haiku 4.5 / Opus 4.6 / Sonnet 4.6 | 28,108字 | `doing_tasks` 3,319字（Haiku 4.5で確認） |
| Sonnet 5.5 / Opus 5.5 | 6,557字 | なし |
| Fable 5.1 | 12,621字 | （未計測。`doing_tasks`は最初から無い） |

`doing_tasks`は、依頼をソフトウェア開発として解釈する、既存のファイルの編集を優先する、といった指示の節です。Claude 5系のsystem promptには、この節が最初からありません。Sonnet 5.5とOpus 5.5では、出力スタイルを選んで変わるのは本体の1行目だけでした。

```text
You are an agent working with the user toward their goals, using your own judgment along the way.
```

これが「…according to your "Output Style"…」に替わります。Claude 5系では、system promptに外すものはありませんでした。外すものが残っていたのは、前の節で扱ったグローバルのハーネスの方でした。

![system promptの節の合計は、Claude 4系（Haiku 4.5 / Opus 4.6 / Sonnet 4.6）で28,108字、Sonnet 5.5 / Opus 5.5は6,557字、Fable 5.1は12,621字。doing_tasks 3,319字は4系にあり、5系には最初から無い。Sonnet 5.5 / Opus 5.5で変わるのは1行目だけ](/images/harness-scope-writing-harness-generations.png)

高さは節の合計字数に比例しています。`doing_tasks`があるのは、計測したClaude 4系の3モデルのsystem promptだけです（外れることはHaiku 4.5で確認しました）。

## 出力スタイルには、私との会話の規約を書きました

この結果を見て、出力スタイルで何をするかを決め直しました。

> なるほどね、じゃあシステムプロンプトは気にしなくていい。純粋に執筆用のリポジトリに適したOutput-styleを作ればいい

記事の文章の規約は、リポジトリのルールとスキルにすでにあります。足りなかったのは、執筆のセッションでClaudeが私とどう話すかの規約でした。過去のセッションで私がClaudeの応答に返した発言1,017件をClaudeに読み返させ、繰り返し出ていた反応を項目にしました。問いに改稿で返された、選ぶ材料が実物でなかった、Claudeの案の枠が命題に残った、といった反応です。

できたのが出力スタイル `zenn-writing`で、本文は7項目、526字です。

```markdown
このスタイルは著者との会話の規約。記事・brief・訳文の文章は `.claude/rules/writing-principles.md` と channel contract に従う。

- 問いにはそのターンで答える。稿や規約のファイルは、著者が変えてと言ってから触る（問いに改稿で返すと、著者が言い直すことになる）
- 選んでもらうときは、候補の実物（文・抜粋・差分）を番号付きで並べ、推奨を 1 つ理由付きで添える。1 つの問いに観点は 1 つ（著者は実物を見て一語で決める）
- 中心命題・評価・記事の向きが論点になったら、案より先に著者の考えを聞き、著者の語で言い返してから案を出す（先に出した案の枠が本文に残る）
- 著者の考えが動いたら、新しい向きを著者の語で確かめて付いていく。事実と食い違うときだけ、根拠を一度示す
- 報告では、確かめた事実と自分の推測を分ける。「できない」「無い」は、記録と設定を見てから言う
- 通読を頼むときは、説明より先に、稿そのものを開ける形（private な Artifact）で渡す
- 用語や外部の知見を聞かれたら、出典付きで平易に説明し、著者の題材への当てはめは「私の読み」として分けて添える
```

記事の本文も同じ会話の中でClaudeが書くので、冒頭の1文で、このスタイルは会話の規約で記事の文章には効かない、と範囲を切っています。

置き場所は`.claude/output-styles/zenn-writing.md`で、`.claude/settings.json`の`"outputStyle": "zenn-writing"`で選びます。リポジトリで選ぶので、このリポジトリを開けば毎回このスタイルになります。スクリプトの修正のようなコーディング作業では、`.claude/settings.local.json`に`"outputStyle": "default"`を置けば外れ、1行目も元に戻ります。

スタイルの本文は、system promptではなく、会話の中に差し込まれるリマインダーとして届きます。本文のリマインダーが差し込まれるのは最初のターンだけでした。2ターン目から新しく差し込まれるのは、スタイル名を念押しする95字の短い文だけです。

![1ターン目には出力スタイルの本文（会話の規約7項目）と名前の念押し95字が差し込まれ、2ターン目には名前の念押し95字だけが差し込まれる](/images/harness-scope-writing-harness-turns.png)

高さは字数に比例しています。会話の規約の本文が新しく差し込まれるのは、1ターン目だけです。

## 見せるものと話し方を、別々に決める

Modで、Claudeに見せるスキル・エージェント・指示ファイルを選び、出力スタイルで、Claudeが私とどう話すかを決めました。2つは別々の場所にありますが、執筆のリポジトリを開くと一緒に効きます。

確かめていないことも残っています。最初のターンに差し込まれたスタイルの本文が、長いセッションでどこまで効き続けるかは測っていません。harness-scopeは、2.1.287での確認の9回のうち1回、Modが読み込まれなかったと見られ、何も外さずに素通しになりました。原因はまだ分かっていません。

コード以外のタスクにも同じ組み方が使えるかは、まだ決めていません。まずは、コードとは違う規約が求められる執筆で作りました。

## 関連リンク

- [harness-scope（GitHub）](https://github.com/shimo4228/harness-scope) — この記事のMod
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/harness-scope-writing-harness.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
