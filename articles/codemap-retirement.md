---
title: "3か月で159回commitしたLLM向けアーキテクチャ文書を消した。構造はLSP、理由はADR、図は人間に"
emoji: "🧩"
type: "tech"
topics: ["claudecode", "aiエージェント", "lsp", "ドキュメント", "adr"]
published: true
published_at: 2026-09-05 19:58
---

きっかけは 1 枚の図でした。

![Archify で生成した Contemplative Agent のアーキテクチャ図。cli → adapters → core の一方向 import、外部 API、production 外の evals / testing が 9 ノードで描かれている](/images/codemap-retirement-archify.png)

2026 年 9 月 5 日の朝、話題になっていた [Archify](https://github.com/tt-a1i/archify)（JSON の仕様からアーキテクチャ図の HTML を生成し、幾何を検証する skill）を試して、自分のリポジトリの図を 1 枚作りました。9 ノード、カード 3 枚。検証は 9 項目すべて通過。見た目はきれいでした。

そこで私はこう打ち込みました。「すごいな、これ。Codemap を置き換えてもいいんじゃないの？」

Codemap というのは、私が 2026 年 3 月からリポジトリに置いてきた `docs/CODEMAPS/` のことです。次のセッションの LLM が読むための、手書きのアーキテクチャ文書です。

答えは「置き換えられない」でした。図は輪郭で、codemap には閾値と理由が入っている。ここまでは予想どおりです。

予想と違ったのはその 2 時間後です。私は codemap を graph 化するのではなく、**6 ファイル 205,239 バイトを全部消し**、それを生成していた仕組みも消しました。この記事は、なぜ「改善」ではなく「削除」になったのかと、読者が自分の文書で同じ判定をするときの問いを書きます。

## 「graph 化すべきか」を「そもそも要るか」に置き直した

図を作った直後の会話で、私は「codemap を graph で記述すれば人間層と LLM 層の両方の可読性を上げられないか」と考えていました。方向としては自然です。Archify とは別に、コードから知識 graph を作って LLM に渡す系統のツールは 2026 年 9 月時点でも増え続けていて、たとえば [Graphify](https://github.com/safishamsi/graphify/releases) は 8 月 19 日から 9 月 5 日の間に 8 回リリースされています。

ただ、その場で決めるのはやめました。同じセッションは Archify を褒めたばかりで、判断が「作る」側に傾いています。

そこで事実だけを渡し、結論を渡さないプロンプトを書いて、新しいセッションでゼロから問い直しました。冒頭にこう書きました。

> 「作らない」が正解でも構わない。結論を先に置かず、まず前提を自分で確認してから判断すること。

前提の確認から始めた理由は単純で、依頼文の数字が古い可能性があったからです。

## 前提が 2 点ずれていた

依頼文には「Markdown 5 枚、architecture.md は約 15,600 token」と書きました。新しいセッションが最初にやったのは、これを実測することです。

```bash
$ wc -c docs/CODEMAPS/*.md
  118891 docs/CODEMAPS/architecture.md
  ...
  205239 total
$ ls docs/CODEMAPS | wc -l
6
```

6 枚でした。`adapters-moltbook.md` が抜けていました。

architecture.md は 118,891 バイトで、約 30k token です。「15,600」はファイル冒頭の header に書いてある推定値で、2026 年 8 月 1 日の値のまま更新されていませんでした。

つまり、鮮度を守るための header 自体が古かった。この時点で私は少し冷静になりました。

更新の頻度も測りました。

```bash
$ git log --since=2026-06-01 --format=%h -- src | wc -l
197
$ git log --since=2026-06-01 --format=%h -- docs/CODEMAPS | wc -l
159
```

3 か月で、ソースの commit 197 件に対して codemap の commit 159 件。ソースを 1 回触るたびに、ほぼ 1 回 codemap を直していたことになります。

この同期は hook が促していたので、私は苦痛を感じていませんでした。苦痛がないから、コストも見えていませんでした。

## 詰まっている作業が無かった

ゼロベースで問い直すとき、最初の問いは「今、誰のどの作業が詰まっているか」です。

答えは「無い」でした。codemap の本文にある path 参照 68 件のうち、実在しないのは 2 件で、どちらも本文が「退役した」と説明している tombstone です。

壊れてはいない。LLM セッションが codemap を読んで困った記録もない。

実害の候補は肥大だけでした。architecture.md の Data Flow 節を読み直すと、日付つきの括弧が本文に inline された変更履歴になっていて、INDEX.md の再走査段落は 9,000 字ありました。git log を散文で写していたわけです。

ここで graph 化に戻ると、graph は肥大を解きません。ノードと辺が持てるのは関係で、肥大していたのは理由の散文の方だからです。「graph 化すべきか」という問いは、解くべき問題が無いところに手段を置いていました。

## 「LLM の理解」を構造と理由に分解した

では codemap は何のためにあったのか。「次のセッションの LLM がリポジトリを理解するため」です。この「理解」を 2 つに分けました。

**構造**。どのファイルがどれを呼ぶか、どの層がどの層を import してよいか。
**理由**。なぜその guard があるか、なぜ import の制約をその形で書いたのか。

構造については、Claude Code の LSP tool を実際に走らせました。language server は `pyproject.toml` の dev group に既にある pyright で、追加の設定は要りません。

```text
LSP incomingCalls  src/contemplative_agent/core/distill.py:104:5

Found 17 incoming calls:

src/contemplative_agent/cli/memory_cmds.py:
  _handle_distill (Function) - Line 39 [calls at: 64:18]

tests/benchmark_distill.py:
  run_benchmark (Function) - Line 166 [calls at: 203:9]

tests/test_distill.py:
  test_basic_distillation (Function) - Line 71 [calls at: 125:18]
  ...（14 件略）
```

`distill()` を呼ぶ 17 箇所が、行番号つきで返ってきます。codemap の `core-modules.md` にあった `distill.py` の行と、architecture.md の「誰が distill を呼ぶか」の散文は、まさにこの答えを手で写したものでした。

159 commit かけて更新してきたものが、1 回の query で、常に最新の状態で出てきます。import の方向は import-linter が既に契約として強制しています。

構造は保存する必要がなかった。問いごとに導出すればよい。

理由については、削除の前に監査しました。architecture.md の Data Flow 節と Untrusted Boundary 節から「なぜこの guard があるか」の記述を全部抜き出し、ADR（Architecture Decision Record。設計判断を 1 件 1 ファイルで記録する文書）、docstring、テストを grep しました。

結果は 25 項目中 23 件が既に別の場所にありました。多くは所有する ADR に verbatim か、それ以上の粒度で書いてあります。ソースの 70 ファイルが ADR 番号を直接引用しているので、コードから理由への導線もあります。

残り 2 件（計器の不連続の記録と、出力の欠落を監視する watchdog script の閾値 512 バイトの根拠）だけを ADR と script header に移しました。

codemap は鏡でした。構造はコードの写し、理由は ADR の写し。写しは正本が動くたびに更新が要り、それが 159 commit の正体です。

## 縮小案は「同じ罠の縮小版」だった

ここまで来ても、私は全削除を選んでいませんでした。最初に選んだのは縮小案で、Data Flow 節だけを残して他を消す。

理由の散文は価値があるように見えたからです。

この案を、会話の文脈を持たない別の agent（build-or-not を独立に判定する役）に渡しました。返ってきた判定は却下でした。

> the Data Flow *is* the accretion (its dated brackets are the changelog inlined). Shrinking the file leaves the growth vector intact, and the hook will re-grow it within the month

肥大源は header でも INDEX でもなく、Data Flow 節そのものだという指摘です。日付つき括弧は変更履歴の inline 化で、それを書かせる hook が残る限り、縮めても 1 か月で元に戻る。

これは自分では気づけませんでした。私は「どの節に価値があるか」を見ていて、「どの節が増えるか」を見ていなかった。縮小案は価値のある節を残す案でしたが、同時に増える節を残す案でもありました。

削除に倒しました。

## 消したら何が壊れたか

削除 commit は 40 ファイル、+98 / −3,623 行です。機械的に壊れたのは 3 点だけでした。

- codemap の存在を assert していたテスト 2 本
- ADR と CHANGELOG からの相対リンク

リンクを直した後のテストスイートは 3,763 passed / 81 skipped で、機能の退行はありませんでした。

危なかったのは、壊れなかった側です。ドキュメント整合性を読む scan は、codemap の鮮度を 2 つの読み値で持っていました。

対象ディレクトリが消えると、この読み値は**エラーを出さずに空になる**。「異常なし」と区別がつきません。

code review がこれを拾い、唯一残った鮮度対象が欠けたら `FILE_MISSING` を出すように直しました。

消す作業で本当に見るべきは、落ちるテストではなく、黙って空になる計器です。

生成側も消しました。codemap を書く skill、鮮度を検査する script、stale を検知して再生成へ回す hook。これらは 1 つのリポジトリではなく、私の全リポジトリに共通する Claude Code の設定（`~/.claude/` 配下。以下 harness）に置いてありました。

4 日前に採択したばかりの「鮮度 gate を script 化する」ADR も、この日に新しい ADR で上書きされ、効力を失いました。

独立判定の agent は「まず 1 リポジトリで様子を見て、全体からの撤去は 2 つ目の同結論で」と勧めました。私は harness から機構ごと撤去しました。生成する側が残っている限り、他のリポジトリでは再生成が要求され続け、新しいリポジトリではまた生えるからです。

## 人間向けの図は残す。ただし出所を刻む

ここで冒頭の Archify に戻ります。codemap を消したなら、図も要らないのでしょうか。

要ります。読者が違うからです。

codemap の読者は次のセッションの LLM でした。LLM は symbol index を自分で引けるようになったので、保存した構造文書は要らなくなった。

一方、README を開いた人間は LSP を叩きません。人間には輪郭の図が要ります。私は「人間が読みやすいように書く」手間を README と出力の文面にだけかける方針なので、Archify の図はそこに置きます。

ただし 1 つ条件があります。**図は正本から導出した説明で、しかもファイルとして残る。** 会話の中で消える説明（eli5 のような）は drift しようがありませんが、716KB の HTML はリポジトリに居座り、半年後にモジュールが消えていても堂々と古い図を見せます。

Archify の architecture schema には、この対策の欄が用意されていました。

```json
{
  "meta": {
    "repository": { "url": "…", "revision": "<40 桁の commit SHA>" }
  },
  "components": [
    { "id": "core", "sources": [ { "path": "src/contemplative_agent/core/", "label": "…" } ] }
  ]
}
```

`meta.repository.revision` に描いた時点の commit を、各ノードの `sources` に対応する path を刻む。これで「この図はどの commit の何を見て描いたか」が成果物側に残り、HEAD から何 commit 離れたかを機械が読めます。保存する graph を推す側でも「stale な graph は無いより悪い、commit hash と provenance を付けよ」と言われていて、条件は同じです。

冒頭に貼った図は、この欄を埋めていません。README 用に作り直すとき、まずここを埋めます。

## 公式ガイダンスと同じ方向だった

書き終えてから調べたのですが、Claude Code の[公式ドキュメント](https://code.claude.com/docs/en/memory)は 2026 年 7 月 9 日のバージョン（v2.1.206）以降、`/doctor` コマンドが checked-in の CLAUDE.md から「Claude がコードから導出できる内容（directory layout、依存一覧、architecture overview）」を削り、pitfall と理由と規約だけを残すと書いています。auto memory も architecture や file path を保存しません。

私の codemap の中身は、この trim 対象そのものでした。逆張りをしたつもりが、公式と同じ判断を自分のリポジトリで実測して確かめただけだった、というのが正確な位置づけです。

一方で、導出の手段はエージェント間で揃っていません。2026 年 9 月 4 日時点で Codex CLI に built-in の LSP はなく、Claude Code でも [cloud session では language server が起動しません](https://code.claude.com/docs/en/discover-plugins)。[clangd](https://github.com/anthropics/claude-code/issues/90114) と [gopls](https://github.com/anthropics/claude-code/issues/91916) の plugin が LSP tool を登録しない issue も open です。

「導出できるものは削れ」は、導出できる環境でしか成り立ちません。

## 自分の文書で判定するなら

`docs/CODEMAPS/` という専用ディレクトリを持つ人は少数でしょう。ARCHITECTURE.md 1 本、あるいは CLAUDE.md の中の「Project structure」節が相手だと思います。判定の問いは同じです。

1. **その文書の読者は人間か、LLM か。** 人間向けなら残す。LLM 向けなら次へ
2. **今、誰のどの作業が詰まっているか。** 無ければ「改善案」は解くべき問題を持っていない
3. **構造の部分は、tool が問いごとに答えられるか。** LSP の `incomingCalls` と `workspaceSymbol`、import-linter や grimp を実際に走らせて確かめる。使えない環境なら、文書の復活でなく language server の導入で解く
4. **理由の部分は、別の所有者（ADR、docstring、テスト）に何割あるか。** grep で数える。私の場合は 23/25 だった
5. **縮小して残す案は、増える節を残していないか。** 日付つき括弧、「〜以降」「〜を追加」の語が並ぶ節は変更履歴の inline 化で、それを書かせる hook が残る限り再肥大する
6. **残す図・説明には、描いた時点の commit を刻めるか。** 刻めない形式なら、残す説明の寿命は会話内に留める

## この判断が効かない場合

- **LSP が使えない環境。** Codex CLI、cloud session、language server plugin が未整備の言語。構造の導出層が無いので、文書を消す根拠が消えます。解は文書の復活でなく導出層の整備です
- **理由が ADR にも docstring にもテストにも無いリポジトリ。** 監査で「他に無い」が大半なら、その文書は鏡ではなく正本です。消す前に移す先を作る必要があります
- **1 リポジトリの読みで global を変えた点。** 独立判定の agent が指摘したとおり、これは 1 回の測定です。私は残り 9 リポジトリの codemap を消すとき、codemap 無しで構造の問いが解けたかを commit message に 1 行ずつ残すことにしました。解けなかったリポジトリが出たら、文書を戻すのではなく、そのリポジトリに language server を入れます

## 出典・参考文献

- [How Claude remembers your project — Claude Code docs](https://code.claude.com/docs/en/memory) — `/doctor` が checked-in CLAUDE.md から導出可能な内容を削る仕様（v2.1.206 以降。取得: 2026-09-05）
- [Discover plugins — Claude Code docs](https://code.claude.com/docs/en/discover-plugins) — 公式 language server plugin の一覧と、cloud session では起動しない制約（取得: 2026-09-05）
- [Archify](https://github.com/tt-a1i/archify) — 本稿の図を生成した作図 skill。`meta.repository` と `sources` は architecture schema の field
- [Graphify releases](https://github.com/safishamsi/graphify/releases) — 2026-08-19〜09-05 に v0.9.47〜v0.9.54 の 8 リリース（取得: 2026-09-05）
- [openai/codex rust-v0.153.4](https://github.com/openai/codex/releases/tag/rust-v0.153.4) — 2026-09-04 時点の最新版。LSP 関連の記載なし。built-in LSP の要望は [#8745](https://github.com/openai/codex/issues/8745) が open（取得: 2026-09-05）
- [Coding Agents Need Codebase Maps, Not Bigger Prompts — Developers Digest](https://www.developersdigest.tech/blog/codebase-knowledge-graphs-ai-coding-agents) — 保存する graph を推す側の記事。「A stale graph is worse than no graph」と、いつ・どの commit から作ったかを graph 自身に持たせよという条件（2026-05-26。取得: 2026-09-05）
- [clangd-lsp plugin never registers an LSP tool — anthropics/claude-code #90114](https://github.com/anthropics/claude-code/issues/90114)、[gopls-lsp plugin … LSP tool never available for Go — #91916](https://github.com/anthropics/claude-code/issues/91916) — 本文で触れた open issue（取得: 2026-09-05）
- [ADR-0102: Retire docs/CODEMAPS — Contemplative Agent](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0102-retire-codemaps.md) — 本稿の判断記録。実測値と LSP probe の出力は `docs/evidence/adr-0102/` に凍結
- [ADR-0062: codemap 機構の退役 — claude-harness](https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0062-retire-codemap-machinery.md) — harness 側の撤去と、独立判定の勧告との差分

## 関連リンク

- [未使用コード検出が拾わなかった2,063行を消した——参照でなく消費を、新設時に書かせる](https://zenn.dev/shimo4228/articles/instrument-consumption-plan) — 前編。消費者ゼロの計器を消した話。本稿は同じ問いを文書に向けています
- [AIレビューを減らした先に、複雑度の上限をRuffで置いた](https://zenn.dev/shimo4228/articles/lint-as-subtraction) — 前々編。機械へ渡せるものを渡す分類表
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/codemap-retirement.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) — 本稿の測定対象。設計判断は `docs/adr/` にあります
