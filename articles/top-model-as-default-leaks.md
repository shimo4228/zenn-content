---
title: "最上位モデルをセッション既定にしたら、重い実装とレビューでFableの使用限度が尽きた"
emoji: "🧭"
type: "tech"
topics: ["claudecode", "aiエージェント", "サブエージェント", "anthropic", "llm"]
published: true
published_at: 2026-09-17 08:30
---

2026年8月22日、Fableのセッションで重めの実装を始め、そのままレビューを走らせたら、一瞬でFableの使用限度に到達しました。レビューを担うbuilt-inのskillが、セッションのモデルをそのまま継いで走ったからです。

その3日後の朝、別の問題を追いかけていて気づきました。自分のリポジトリで起きる過剰設計は、Fableの使用限度が切れたあと、代わりに設計を引き受けたOpusのセッションで起きていました。

この2つは同じ出来事の前半と後半です。最上位モデルをセッションの既定にすると、まず壊れるのは成果物ではなく使用限度で、限度が尽きたあとに判断そのものが下位モデルへ落ちます。この記事は、既定がどの経路へ漏れたか、規約と警告ではなぜ止まらなかったか、何で止まったか、そして限度が尽きたあとに何が落ちたかの記録です。

## 前提: 3層に3つのモデル

私はClaude Codeを購読プラン（Max）で使い、3つのモデルを役割で分けています。最上位のFableが判断（前提の検証、計画、検収）、その下のOpusが実装で、新しいセッションに渡します。機械的な照合はSonnetです。私のプランではFableの使用限度はOpusと別枠で、Fableが尽きてもOpusは使えます。以下、判断を担う側を判断層、実装を担う側を実装層と呼びます（私の設定ファイルでは英語でjudge-tier / build-tierと書いています）。`settings.json`の既定モデルは`fable`で、実装を渡す先の役割分担は[以前の記事](https://zenn.dev/shimo4228/articles/ai-task-loop-judge-bottleneck)に書きました。

自作のサブエージェントには、8月に入ってから全部`model:`を書いています。定義ファイルにモデルを書いて固定することを、以下ではpinと呼びます。`~/.claude/agents/*.md`の11本は、この記事を書き始めた9月16日の時点でfable 1 / opus 4 / sonnet 5 / haiku 1です。書き忘れはlintが落とします。

ここまでやれば階層化できている、と思っていました。

## 既定はpinできない経路へ漏れる

限度が尽きた日に漏れたのは、`/code-review`と`/simplify`です。この2つはClaude Codeに同梱のskillで、モデル引数を持たず、セッションのモデルで走ります。Fableのセッションから呼べばFableで走り、一瞬で限度に届きました。

漏れる経路は他にもあります。frontmatterを持たないbuilt-inのサブエージェントです。自分のログ（`~/.claude/metrics/agent-usage.jsonl`）を数えると、後述するレビューのhookを入れてからこの記事を書くまでの3週間で、agent起動576件のうちgeneral-purpose 231、Explore 121、Plan 10、claude-code-guide 11の計373件、65%がbuilt-inでした。自作agentに`model:`を書いても、起動の3分の2には届いていません（claude-code-guideはHaiku固定なので、セッションのモデルを継ぎうるのは362件、63%です）。このログはモデルを記録していないので、そのうち何件がFableで走ったかは分かりません。数えて初めて気づいた穴で、この記事を書きながらほぼ埋めました。何で埋めたかは最後に書きます。

公式ドキュメント（2026年9月16日時点）によれば、サブエージェントのモデルは、呼び出し時の指定、定義の`model:`、環境変数`CLAUDE_CODE_SUBAGENT_MODEL`、セッションのモデル、の順で決まります。Exploreはセッションのモデルを継ぎつつOpusで頭打ち、general-purposeとPlanは頭打ちなしで継ぎます。つまり呼び出し側がモデルを指定せず、環境変数も置いていなければ、Fableのセッションが起動するgeneral-purposeは全部Fableです。環境変数を置いても変わるのはgeneral-purposeだけで、ExploreとPlanは変わりません。

同じ機構に、私は2月にも落ちています。当時は`--model opus`がメインにしか効かず、サブエージェントが意図しないHaikuで走りました（[当時の記事](https://zenn.dev/shimo4228/articles/daily-research-agent-team)。仕様はその後変わっています）。2月は意図より下のモデルへ、今回は上のモデルへ。継承の既定は両方向に漏れます。

同じ報告は公開のissueにもあります。7月10日の#76514は「per-agentの`model`を省くとFableが全サブエージェントへ伝播する」と書いて、対応予定なしで閉じられました。9月12日の#93894は「Fable 5.1で`/code-review high`を1回走らせるとセッション予算を使い切り、レビューは完走しない」と書いて、まだ開いています。

## 規約では止まらず、警告でも止まらなかった

限度が尽きた当日の対処は規約でした。実装計画の最後に「このセッションが実装するか」を1行で決める手順を足し、重い実装はOpusの新セッションへ渡すことにしました。hookで強制する案は、方針をhookの中に埋めることになるので却下しています。

2日後の夜、私はこう書いています。

> ……Fableは設計を担当して実装はopusみたいな規約を入れてるんだけどあんまり守られてないんだよな。実装はまだいいけど、そのままレビュー、とくにsimplifyとcode-reviewが走ると、かなりトークンを無駄にしちゃう。……

そこでhookを入れました。最初の版は、Fableのセッションでレビューが起動されたら警告を出すadvisoryでした。翌朝に分かったのは、advisoryは「レビューが走ったあとに読まれる」ことです。警告を見てから中断し、Opusで再レビューすると、Fable 1回分とOpus 1回分の二重払いになります。

その朝のうちに、`review-model-notice.sh`を書き直しました。最初に却下したのは、方針をhookに埋めることでした。今回hookに置いたのは、skill名とセッションモデルの組み合わせという機械的な判定だけで、どのモデルが何をするかという方針はrulesの側に残しています。経路で応答を分けます。コメント中のjudge-tierは判断層（Fable）のことです。

```bash
# ~/.claude/hooks/review-model-notice.sh（抜粋、一部省略）
# 経路で応答を分ける:
#   Skill 直呼び (code-review / simplify) → **block**。判定が完全に機械的（skill 名 ×
#     セッションモデル）で誤検知の余地が無く、advisory だと skill が同 turn で走って
#     judge-tier トークンを消費してから助言が読まれる（実測 — 中断 + Opus
#     再レビューで二重払いになった）。効くのは実行前の block だけ。
#   Agent/Task 起動で model pin 欠落 → advisory に留める。prompt 部分一致の
#     ヒューリスティックで誤検知しうるので、deny の権限を持たせない。
```

セッションのモデルはhookのpayloadに入っていません。transcriptの末尾から直近の`"model"`を読み、読めなければ黙ります。

```bash
model=$(tail -c 2000000 "$T" 2>/dev/null | grep -o '"model" *: *"[^"]*"' | tail -n 1) || true
case "$model" in
  *fable*) ;;
  *) exit 0 ;;
esac
# ...（block / advisory の文面を組む）
if [[ "$mode" == "block" ]]; then
  jq -cn --arg reason "$msg" '{decision:"block", reason:$reason}'
  exit 0
fi
```

blockの理由文を読んだモデルは、自分で`Agent(subagent_type: "general-purpose", model: "opus")`に切り替えます。人間が止めてコマンドを打ち直す必要はなくなりました。

## 壊れたのは予算、そのあと判断

同じ朝、別の会話で過剰設計の話をしていました。その直前に、週次レポートの機構を大幅に簡素化して、数千行単位でコードを減らしたばかりでした。私はこう書いています。

> 割とオーバーエンジニアリングは、fableの使用制限が過ぎたopusの時に起きてる

> この問題はFableを実装やレビューに無駄遣いして使用制限が過ぎてOpusをオーケストレーターにせざるを得ずに起きるということが真の問題だ。

上位モデルを既定にして壊れるのは、最初は予算です。ただ予算は、判断層のモデルを買うためのものでした。予算が尽きると判断層がOpusに落ち、落ちた判断層が過剰設計を通します。つまり最上位モデルを「既定」に置くことは、最上位モデルを「判断層」から外す方向に働きます。ここまでは数件からの印象で、Opusの判断が過剰設計を通した回数は数えていません。

だから塞ぐ向きを逆にしました。セッション既定は最上位のままにして、既定から判断層へ届く経路は残し、既定からそれ以外へ漏れる経路を切ります。判断層はpinします。作るか作らないかを判定する`architect` agentは、この日から9月16日の時点まで、私の環境で唯一の`model: fable`でした。

## それでも週末のたびに尽きた

3日後の金曜日、私はこう書いています。

> Fableの使用制限がいつも1番使う土日のわたしと休日になくなってしまう。なくなった後は、Opusが設計をするのだが、やはりFableの不在を感じる。Fableの強みである設計とプランに集中して、他は他のモデルに委譲できるようにしたい。現状も可能ならOpusに委譲するようになっているが、そのままFableが実装してしまうことが多い。

レビューの経路は塞いだのに、実装そのものがFableで走っていました。最初の規約は「条件を満たさなければこのセッションで実装してよい」という逃げ道を持ち、その判定はモデル自身がしていました。

同じ日に3つ変えました。

1. **既定の反転**。「このセッションが実装するか」の既定を「Opusへ渡す」にしました。自分で実装してよいのは、設計文書（ADRなどの判断記録）の散文編集、渡せない具体的な理由、ユーザーの明示指示のいずれかを計画に1行書いたときだけです。説明責任が、渡す側から渡さない側へ移りました
2. **計画承認直後のhook**。`ExitPlanMode`のPostToolUseで、Fableのセッションにだけ「実行者の決定」を思い出させます。実装のEditを打つ前で、いちばん遅い安全な位置がここでした
3. **常駐ルールに1行**。plan modeを通らない実装にも届くように、rulesに「judge-tierセッションでの実装はbuild-tierへのdispatchが既定」と書きました。判断層のセッションでは実装せず、実装層のセッションへ渡すのが既定、という1行です

2のhookには、鳴らさない条件があります。計画本文に定型句「実行者の決定」が既にあれば黙ります。最初は`dispatch`や`spawn-session`のような一般語も抑制語に入れていました。過去のExitPlanMode 271件で試すと31件が抑制され、うち30件は誤抑制でした。実装を渡すこと自体を話題にしただけの計画、つまり最も鳴ってほしい、タスクの振り分けだけをするセッションで鳴らなくなります。抑制語は定型句1つに絞り、「dispatchを話題にしただけの計画では鳴る」を回帰テストに置きました。機械的に判定できる条件だけを機構に置く、という点でレビューのhookと同じ判断です。

それから3週間、使用限度が尽きたという報告は、私のセッションログにありません。これは報告が「無い」ことで、残量を測った記録ではありません。使用限度の残量を機械的に記録する仕組みは、私の環境にはまだありません。Fableで走ったレビューがOpusより何かを拾っていたかも、見ていません。言えるのは、同じ報告を書かずに済んだことまでです。

## 読者への判断則

同じ構成で使っている人が持ち帰れるのは、この4つです。

**階層を「既定」に任せず、判断層をpinして漏れる経路を塞ぐ。** 私はセッション既定を`fable`のままにしています。変えたのは既定ではなく、既定が流れ込む経路です。漏れる先はbuilt-inのskill、built-inのサブエージェント、セッション自身の実装で、自作agentの`model:`はこの3つに届きません。

**built-inサブエージェントの既定は、環境変数と同名の定義で埋める。** `CLAUDE_CODE_SUBAGENT_MODEL=opus`を置けば、general-purposeの既定が変わります。ExploreとPlanはこの変数だけでは変わらず、`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`で全部を1つに固定するか、同名のagent定義を置いて`model:`を持たせます。私はこの記事を書きながら、環境変数を`opus`に、Exploreを同名の定義で`sonnet`に置きました。上の362件のうち残っているのはPlanの10件です。

**判定が機械的ならblock、ヒューリスティックならadvisory。** skill名とセッションモデルの組み合わせは誤検知しないので、実行前に止めます。promptの部分一致でしか判定できないものは警告に留めます。実行後の助言は予算を守りません。

**規約の既定を反転する。** 「守られていない規約」の多くは、守らない側に説明責任がありません。既定を渡す側に置くと、渡さない理由を書かなければならなくなります。

この配線には失効条件を書いてあります。モデルのティア区別と使用限度が消えるか、Claude Codeがセッション単位のモデル切替を自分で行うようになったら外します。`opusplan`（planはopus、実行はsonnet）は既にあるので、fableからopusへ落ちる版が来れば、hookは要らなくなります。

## 出典

- [Create custom subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents) — モデルの解決順、Exploreの頭打ち、`CLAUDE_CODE_SUBAGENT_MODEL_FORCE`（2026-09-16取得）
- [Model configuration - Claude Code Docs](https://code.claude.com/docs/en/model-config) — `opusplan`、`CLAUDE_CODE_SUBAGENT_MODEL`（2026-09-16取得）
- [anthropics/claude-code #76514](https://github.com/anthropics/claude-code/issues/76514) — Fableセッションのサブエージェントが全部Fableを継ぐ（2026-07-10、closed as not planned）
- [anthropics/claude-code #93894](https://github.com/anthropics/claude-code/issues/93894) — Fable 5.1の`/code-review high`1回でセッション予算が尽きる（2026-09-12、open）

## 関連リンク

- [タスク41件をAIループに任せたら、詰まっていたのは実装より判断だった](https://zenn.dev/shimo4228/articles/ai-task-loop-judge-bottleneck) — 判断はFable、実装はOpusという役割分担の経緯
- [最強モデルで司令塔を組んだら9倍遅くなった](https://zenn.dev/shimo4228/articles/daily-research-agent-team) — 同じ継承の既定に、下向きに落ちた2月の記録
- [AIレビューを6系統から1系統へ——「指摘ゼロ」で終われないループの切り方](https://zenn.dev/shimo4228/articles/review-chain-damping) — advisory版hookの二重払いに気づいた同じ朝に、レビューの系統数を切った記録
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/top-model-as-default-leaks.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
- [claude-harness](https://github.com/shimo4228/claude-harness) — 本稿のhook `hooks/review-model-notice.sh` とテストの公開ミラー
