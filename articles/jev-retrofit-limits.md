---
title: "JevのスキルルーターをClaude Codeに足して、スキル一覧を書き換える手前で引き返した"
emoji: "🧭"
type: "tech"
topics: ["jev", "claudecode", "aiエージェント", "llm"]
published: true
published_at: 2026-09-21 19:42
---

私は普段、Claude Codeのような大手のハーネスの不便を、自分の実装で埋めないようにしています。埋めても、しばらくすると公式の側が変わって要らなくなる、をこの半年繰り返してきたからです。

旧世代のモデルの弱点を補うために書き溜めたルールは、Opus 5世代で公式が「ルールは減らして判断に任せる」へ方針を変えたので、私は常駐分を[5,789 wordsから2,463 wordsまで削りました](https://zenn.dev/shimo4228/articles/claude5-rules-official-shift-audit)。複数のClaude Codeを並べて動かすために[herdrを入れて記事も書きました](https://zenn.dev/shimo4228/articles/herdr-agent-multiplexer)が、いまはClaude Code自身が[セッション同士でメッセージを送れます](https://code.claude.com/docs/en/cross-session-messaging)。1つの会話からClaudeが並行セッションを立てて管理する[Projects](https://code.claude.com/docs/en/claude-projects)も、公開ベータで順に展開されています。いまのProjectsが束ねるのはクラウドのセッションだけですが、手元のセッションまで扱うようになれば、herdrも要らなくなります。

それでも2026年9月21日は、好奇心が勝ちました。Jevは、文章を書かず、型の付いた問いに確率だけを返すモデルです。この日、Jevを作っているTypeSafeの[スキル提案のcookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion.md)をClaude Codeのhookに移植しました。

この記事は、作ったものがどこまで届き、どこで引き返し、引き返した先に何があったかを書きます。Jevを自分のハーネスに足そうか考えている人が、足す前に確かめることを3つ持ち帰れるようにします。

## 足したのは1行です

作ったのは、Claude Codeのプラグイン[jev-skill-router](https://github.com/shimo4228/jev-skill-router)です。プロンプトを送るたびに`UserPromptSubmit`のhookが動き、プロンプトと、手元に入っているスキルの名簿（名前とdescription）をJevに送ります。Jevへのリクエストは最大2回です。1回目は名簿全体を順位づけし、「そもそもスキルが要る依頼か」を3つのyes/noの問いで確かめます。2回目は上位3件だけを、SKILL.mdの全文つきで読み直します。1回目の3問の平均（ログの`gate`。3問目は向きを反転して平均します）か、2回目の候補ごとの値（`fits`）の最大が0.30に届かなければ、何も提案しません。

既定では何も足さず、判定をログに残すだけです。注入を有効にすると、0.30に届いたターンに次の1行だけが足されます。

```text
<skill_relevance>
Relevant to the current request: adr-writer. Ignore this if it does not fit what the user actually asked for.
</skill_relevance>
```

判定はログに1行ずつ残ります。設計判断をADRに記録したい、という日本語の依頼を送ったときの行です（抜粋）。

```json
{"mode": "inject", "model": "jev-1.13.0", "router_version": "0.2.0",
 "gate": 0.47,
 "shortlist": ["adr-writer", "adhd:adhd", "archify"],
 "fits": {"adr-writer": 0.93, "adhd:adhd": 0.14, "archify": 0.05},
 "suggestion": "adr-writer",
 "usage": {"input_tokens": 21597, "output_tokens": 702, "calls": 2},
 "elapsed_ms": 1567}
```

意図が1つだけの依頼文を6本用意して送ると、5本は私が見て妥当だと思うスキルを0.93〜0.98で名指しし、「ありがとう、今日はここまで」には何も提案しませんでした。所要は0.7〜1.6秒です。各1回の読み値で、割合として読める数ではありません。

ここまでは、cookbookのとおりに動きました。

## Claude Codeのスキル選択は、そのまま走っていました

動かしながら、私はこう聞きました。「これって、結局Claude Codeのスキル選択も同時に走ってるの？」

走っています。hookの`additionalContext`にできるのは、[文字列を1つ、モデルの文脈に足すこと](https://code.claude.com/docs/en/hooks)だけです。Claude Codeは、入っている全スキルの名前とdescriptionを並べたスキル一覧を、モデルに見せ続けます。そこから選ぶのはモデルです。スキル一覧に使われるトークンは1つも減りません。Jevの判定は、その選択の横を並走しているだけでした。

しかも、cookbookで効いた条件がClaude Codeにはありません。cookbookの実験は488リクエストで、そのうちスキルが当てはまる315件では、間違ったスキルの読み込みが16.8%から7.3%に減っています。このときスキルを選んでいたのは`claude-haiku-4-5`で、見ていたのは1スキルあたり60字に切られた索引でした。cookbookは冒頭でこう書いています。

> Hermes, the agent harness used here, cuts it to 60 characters by default.

60字はcookbookの推奨値ではなく、実験に使ったハーネスの既定の表示幅です。60字では`.pptx`を編集するスキルと作成するスキルの見分けがつかない、という例もcookbook自身が挙げています。cookbookは解こうとした問題を、エージェントが「ほとんど情報の無い状態で選んでいる」ことだと説明しています。小さいモデルが切り詰められた索引で選んでいるところへ、全文を読んだ判定を1行添える。効いたのはその条件の下でした。

Claude Codeは逆です。descriptionは（`when_to_use`と合わせて）[1,536字まで切らずに](https://code.claude.com/docs/en/skills)モデルに見せます。この記事を書いているリポジトリで数えると、入っているスキルは59本で、descriptionが60字に収まるのは2本、中央値は412字でした。選んでいるのはClaude Fable 5.1で、Haikuより強いモデルです。Claude Codeでのルーターは、同じ説明文をすでに全文で読んでいる強いモデルに、同じ説明文を読んだ別のモデルが横から助言する形になります。足せる情報はSKILL.mdの本文だけです。

これは仕組みからの議論で、測った結果ではありません。注入して何かが良くなったという証拠を、私は持っていません。プラグインの既定を注入にしなかったのはそのためです。

## スキル一覧を書き換える道はありました

ルーターとして効かせるには、1行足すのではなく、モデルに見せるスキル一覧そのものを変えるしかありません。

道はありました。Claude Codeの早期アクセス機能であるfunction hooks（通称Mods、[設計スレッド](https://github.com/anthropics/claude-code/issues/91870)）の型定義は、モデルに渡る添付の種類として`skill_listing`を挙げ、その本文はModの側で書き換えられると書いています（`anthropics/claude-code`の`mods/types/claude-code.d.ts`、2026年9月21日確認）。

設計のプランを走らせて、すぐにやめました。頑張ればやれないことはないかもしれません。ただしそれは、Claude Codeの既定のスキル選択を自作で置き換えることです。早期アクセスの型に乗り、既定の挙動を崩した実装は、公式が変わるたびに追従が要ります。埋めても公式が変わって要らなくなる、を繰り返してきた半年からすると、これは沼です。

READMEの冒頭に「Claude Code の強いモデルに対する router としては、役に立つ見込みが小さい」と理由つきで書き、同じことを考える人が参照できる状態にして、手を止めました。

## その道は、前日に歩かれていました

この記事の準備で改めて探すと、引き返した先はもう実装されていました。

[davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)のMod `jev-skill-suggestion`です。最初のcommitは日本時間で2026年9月20日の朝、私が引き返す前日です。この時点で、私が手前で引き返した書き換えそのものができていました。Modsの`skill_listing`に空を返して、スキル一覧をモデルに読ませません。代わりに、Jevが選んだ1件だけを「このスキルを読み込んでください」とモデルに伝えます。モデルはスキル一覧から自分で選べなくなり、残るのはJevの提案に従うか無視するかだけです。私が引き返した当日の昼の2つ目のcommitで、選んだスキルのSKILL.mdをMod自身が添付する形に進みました。いまのREADMEの1行目は、こう書いています。

> Takes the skill listing out of the context window and lets Jev, TypeSafe's System One decision model, pick at most one skill per prompt from the skills' descriptions — and then loads that one skill itself, by attaching its `SKILL.md` to the prompt.

選び方は、私のプラグインと同じcookbookの2リクエストです。スキル一覧を隠すところは自作ではなく、公式の設定[`skillOverrides`](https://code.claude.com/docs/en/skills)でした。スキルごとにモデルへの見せ方を4段階（名前と説明・名前だけ・ユーザーが呼んだときだけ・見せない）で切り替える設定です。スキル一覧のトークンを減らしたいだけなら、JevもModsも要りません。同じリポジトリには、モデルと推論の深さをJevで振り分ける`jev-model-router`もあります。

私はどちらも試していません。効くかどうかは分かりません。分かったのは、公式への追従を背負ってでも作る人が、私が手を止める前からいたことです。試したくなったら、私が作らなくても実物があります。

## 選ぶ役を誰が持っているか

ここからは、作ってみた私の見立てです。

Claude Codeでは、スキルを選ぶ役はClaude Codeとそのモデルが持っています。担っているのはフロンティアモデルで、私に開いているのは文を1行足す口だけでした。

Jevがどこまで効くかは、選ぶ役を誰が持っているかで決まる、と考えています。持っているのが弱い選び手なら、横から1行添えるだけで効きます。cookbookがそうでした。強い選び手が全文を見ているなら助言では動かず、選ぶ役そのものに届くしかありません。Modsは、ハーネスの側がその役を外へ開けた例です。Piというコーディングエージェントの拡張[pi-jev](https://github.com/TheoOliveira/pi-jev)は、Jevの確率が閾値を超えたツールだけを有効にします。助言ではなく、モデルに見える道具そのものが変わります。

いまのハーネスの多くは、モデルが考えては道具を呼ぶ往復（ReAct）を前提に作られていて、強いモデルがすべてを見て、選ぶことも判定することも自分の推論の中でやります。選び手が強いかぎり、そこへ速い判定モデルを足しても、置き換わる仕事がありません。この先もJevを既存のハーネスに部分的に組み込む動きは続くでしょうが、効果はハーネスが開けた範囲にとどまるはずです。

逆に、ツールの選択も、モデルの振り分けも、途中の判定も最初からJevで組み、最後の推論だけをフロンティアモデルに渡すハーネスが出てきたら、速度も費用も精度も別物になる可能性があります。TypeSafe自身、[発表記事](https://typesafe.ai/blog/introducing-system-one-models-and-jev)でJevを「a frontier-intelligence function call」と呼び、部品として呼ぶ使い方を想定しています。私が自作の別のエージェントのスキル選択で[JevとOpusを比べたとき](https://zenn.dev/shimo4228/articles/jev-vs-opus-skill-selection)は、Jevは1件0.32秒、費用はOpusの約560分の1で、Jevが確率0.5以上で指した45件は、1件もOpusの選択と食い違いませんでした。一方で、150件全体の一致は、Opusに同じ選択を2回やらせたときの一致の約半分でした。どこまでをJevに持たせられるかを、私は測っていませんし、測った報告も見つけていません。

2026年9月21日の時点で、私が探した範囲に、そういう汎用のハーネスはありませんでした。見つかったものはどれも、既存のハーネスへの組み込みです。

## 足す前に確かめる3つ

あなたがJevのような判定モデルを自分のハーネスに足そうとしているなら、書き始める前に3つ確かめてください。

1. **足したものは、選ぶ役に届きますか。** 文を足すだけなら、元の選択はそのまま走ります。届く口があるか（自作のループ、Mods、ツールの有効化）を先に調べます。
2. **選び手は、判定モデルと同じ情報をもう見ていませんか。** ベンダーの実験の数字を読む前に、実験の条件を読みます。選び手のモデルは何か。選び手に何が見えていたか。
3. **公式の手段で足りませんか。** 欲しいのがスキル一覧のトークンを減らすことなら、Claude Codeでは`skillOverrides`で足ります。判定モデルが要るのは、その先です。

文を足すだけの拡張は、外せば元に戻ります。好奇心で作ってかまいません。既定の挙動を置き換える実装は、作れるとしても、私は作りません。

私は追う側に回りました。Jevを土台にしたハーネスが出てくるかを、毎日の調査の項目に加えました。手元のプラグインは、何も足さずログだけを残す設定のまま動かしています。見るのは、Jevが名指ししたスキルと、そのターンで実際に使われたスキルの突き合わせです。名指ししたのに使われなかった回が積み上がるなら、1行添える意味があるかもしれません。積み上がらなければ外します。

## 関連リンク

- [文章を書かないモデルJevのスキル選択は、0.3秒でOpusにどこまで近づくか](https://zenn.dev/shimo4228/articles/jev-vs-opus-skill-selection) — Claude Codeではなく、gemma4:e4bで動く自作のエージェント（Contemplative Agent）のスキル選択で、JevとOpusを比べた計測です
- [TypeSafe: Skill suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion.md)
- [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — `jev-skill-suggestion` と `jev-model-router` はこの中のModです
- [DECRUX9812/typesafe-skill-router](https://github.com/DECRUX9812/typesafe-skill-router) / [Dicklesworthstone/skillranker](https://github.com/Dicklesworthstone/skillranker) — 同じcookbookの別実装
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/jev-retrofit-limits.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
