---
title: "READMEは人間とLLM、どちらのためのものか？"
emoji: "📂"
type: "tech"
topics: ["readme", "llm", "claudecode", "geo", "llmstxt"]
published: true
published_at: 2026-10-09 09:00
---

自分のリポジトリのREADMEを、自分で読んで、10文目で読むのをやめました。README用のスキルで書き、公開前の判定でも「公開してよい」と出たREADMEです。冒頭には「何をするものか」を言う2文の段落がありました。

> ローカル LLM で動く自律エージェントで、自分の憲法と価値観の変更を自分で提案します。採用するかどうかは、毎回人間が決めます。

この2文を読んでも、何をするものなのか分かりませんでした。

このところ、LLMの書く冗長な文章をどう直せるかを考えていました。Xにはこう書きました。

> 人同士の関係の中で言わなくてもわかることがわからない。だから、言わなくてもいいことを言ってしまう。そこを補うには、やはり誰がこれを読むのかということを定義するのが大事かもしれない。だが、これは言うのは簡単だが非常に難しい

> LLMは文章の途中で離脱したりしない。だから、誤解がないようにできるだけ正確に情報を詰め込んだ方がいい。対して、人間は興味が湧かなかったら三行で離脱する。

両立は難しいです。経路を分けられればいいのですが、LLMは人間用の文章を第一に読みにきます。

この記事は、1枚のREADMEを「見える本文は人間向け、畳んだ節はLLM向け」に分けた試行の記録です。あわせて、畳んだ中身をAIアシスタントが読むかを、公開リポジトリを作って確かめました。URLの中身を取得できた5つのAIアシスタントは、5つとも畳んだ中身を読みました。ただ、これはまだ、人間とLLMを分けるやり方です。

![以前のREADMEは、人間向けの説明とLLM向けの事実を同じ見える本文に置いていて、人間は10文目で読むのをやめた。これからのREADMEは、見える本文を人間向けにし、LLM向けの事実とllms.txtなどへの導線を末尾のdetailsに畳む。URLの中身を取得できた5つのAIアシスタントは、畳んだ中身も読んだ](/images/readme-human-llm-fold-hero.png)

以前は、人間向けの説明とLLM向けの事実が、同じ見える本文に混ざっていました。これからは、READMEを書くときに、LLM向けの事実を末尾の`<details>`に畳みます。

## 削る規則は、文の単位では作れませんでした

LLMの書く文章が長いなら、要らない文を削ればいい、と最初は考えました。2026年10月8日、自分のREADME 2本と記事2本を1文ずつ表示する画面を作り、読みながら「要らない」「止まった」のチェックを付けました。チェックの集まりから、削る規則を作るつもりでした。

チェックは、文単位の規則になりませんでした。

- 冒頭で離脱したcontemplative-agentのREADMEでは、「要らない」のチェックは0個でした。読むのをやめたので、要らない文を選ぶところまで行けませんでした
- jev-skill-routerのREADMEでは、「要らない」の18個のうち17個が、外部に送る内容と限界を説明する2節に続けて並んでいました。1文ずつ要らないのではなく、節ごと読み飛ばしていました
- 記事の1本は、文はどれも自然なのに、全部を説明しようとしすぎていて途中で離脱しそうになりました。この感覚は、「要らない」のチェックとしては、どの文にも付けられませんでした
- もう1本の記事には、チェックが1つも付きませんでした

チェックを付けたあとで気づいたのは、文を1つずつ直す前の段階で、見せる情報が絞れていないということでした。普段は記事を、Gitの差分に1文ずつコメントを付けて直しています。その直し方が効くのは、何を見せるかが決まったあとです。

## LLMのために、見える本文に詰め込んでいました

情報が絞れていなかったのには理由があります。私のREADMEは、LLMが読むことを前提に書いていました。私のGitHubのリポジトリは、人に閲覧されるよりずっと多くクローンされていて、クローンしているのはLLMのクローラーだと見ていたからです。

READMEを書くスキル（[readme-writer](https://github.com/shimo4228/readme-writer)）は、このREADMEを書いた時点で、READMEを、AI検索やチャットにURLを貼ったときにLLMが確実に前提にできる唯一の面と位置づけていました。そのため、LLMがREADME 1枚からプロジェクトを復元できるだけの事実を、見える本文に必ず残す、と決めていました。人間向けに短くすることと、LLM向けの事実を残すことを、同じ見える本文の中で両立させようとしていたわけです。

以前は、READMEの読者はLLM検索だけでした。ここにきて、人間の読者が増えだし、前提が変わりました。冒頭で私が読むのをやめたのは、LLM向けの事実で埋まった見える本文でした。

経路を分ける道具として、llms.txtがあります。人間用のページとは別に、LLM向けの要約を置くファイルです。ただ、サーバーログの調査は、クローラーがllms.txtをほとんど取得していないと報告しています。137,000ドメインを調べたAhrefsの調査では、公開されたllms.txtの約97%に、2026年5月のあいだリクエストが1件もありませんでした（[Ahrefs](https://ahrefs.com/blog/llmstxt-study/)）。EZY Researchの12週間の調査では、GPTBotがllms.txtを取得したのは7回で、robots.txtは3,990回でした（[Something Inc.の紹介記事](https://somethinginc.com/blog/llms-txt-ai-crawlers-fetch-data/)）。

## 畳んでも、取得したアシスタントは読みました

人間向けの本文とLLM向けの情報を、1枚の中で位置で分ける形は、前にも試しています。8月に公開した[noteのエッセイ](https://note.com/sakamaki4228/n/n90c26af4fd5f)と[Zennの記事](https://zenn.dev/shimo4228/articles/ai-review-task-loop)では、末尾に「ここから先はAI読者向け」という節を見える形で置き、人間の読者はそこで読み終えてよいと書きました。置いただけで、LLMがその節を読んだかは測っていません。

今回は、LLM向けの情報を見える形で置かずに、HTMLの`<details>`で畳みました。畳むと、人間には見出しが1行見えるだけになります。気になったのは、LLMも畳んだ中身を読み飛ばすのではないか、という点です。

確かめるために、架空のツールのREADMEを持つ公開リポジトリ[readme-fetch-canary](https://github.com/shimo4228/readme-fetch-canary)を作りました。READMEは約2.6万字あり、置き場所ごとに別のランダムな語を埋めてあります。冒頭近くの`<details>`の中には、設定ファイルの名前を置きました。

```markdown
<details>
<summary>Reference for tools and AI assistants</summary>

kumo-cache supports Python 3.11 only. It reads its settings from a file named `424157.toml` in the current directory.

</details>
```

ほかに、READMEの冒頭（見える）、2.5万字あまりの変更履歴のあとの末尾（見える）、llms.txt、READMEからリンクした`docs/setup.md`にも、それぞれ別の語を置きました。各アシスタントで新しい会話を開いて、次の質問を貼りました。どれもランダムな語なので、答えに出れば、その場所の中身がアシスタントに届いたことになります。

```text
https://github.com/shimo4228/readme-fetch-canary

Using only what you can read from this repository, answer:
1. What command prefix does the tool use?
2. What is the name of its settings file?
3. Who maintains it?
4. What API endpoint does it use?
5. Which environment variable must be set?
If you cannot find an answer, say "not found" rather than guessing.
```

URLの中身を取得できた5つの結果です。○は正解の語を答えた、−は「見つからない」と答えた、です。

| アシスタント | プラン・モード | 冒頭 | 畳んだ中 | 末尾 | llms.txt | docs/ |
|---|---|---|---|---|---|---|
| ChatGPT（GPT-6） | Plus・一時チャット | ○ | ○ | ○ | − | ○ |
| Claude.ai（Opus 5.5） | Max | ○ | ○ | ○ | ○ | ○ |
| Grok | X Premium | ○ | ○ | ○ | ○ | ○ |
| Qwen 3.7 Plus | 無料・一時チャット | ○ | ○ | ○ | ○ | ○ |
| Gemini 3.6 Flash | 無料・思考強化・通常チャット | ○ | ○ | ○ | ○ | ○ |

5つとも、畳んだ中身も、2.6万字の末尾も答えました。Grokは途中経過で「The README is truncated, so I'm reading the rest of the repo files」と出し、最初の取得で切れたREADMEの残りを自分で取りにいきました。

![readme-fetch-canaryのREADMEは26,361字。冒頭（189字目）、冒頭近くのdetailsの中（641字目）、2.5万字あまりの変更履歴のあとの末尾（26,353字目）、READMEからリンクしたdocs/setup.md、リンクのないllms.txtに別々のランダムな語を置いた。取得できた5つのアシスタントは、冒頭・畳んだ中・末尾・docs/setup.mdの語を5つとも答え、llms.txtの語は4つが答えた](/images/readme-human-llm-fold-canary.png)

帯の長さはREADMEの字数に比例しています。畳んだ節は冒頭近くにあり、末尾の語は2.6万字の終わりにあります。

llms.txtも、5つのうち4つは読みにいきました。サーバーログの調査が数えているのはクローラーの巡回で、利用者がURLを渡したときの取得とは場面が違います。それでも、LLM向けの情報をllms.txtだけに置くと、今回のChatGPTのように読まなかったアシスタントには届きません。

どの条件も1回ずつしか聞いていません。測ったのは畳んだ中身が読まれるかどうかで、実験では`<details>`をREADMEの冒頭近くに置きました。末尾に置いた`<details>`は試していません。答えの中でどれだけ重く扱われるかや、検索エンジンの索引が`<details>`をどう扱うかは測っていません。

## READMEの書き方を、上下で分けました

この結果を見て、readme-writerを書き換えました（決定の記録は[ADR-0091](https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0091-readme-human-top-llm-fold.md)）。

- 見える本文は人間の読者に向けます。冒頭の短い段落で、読者がまだ知らない語を使わずに何をするものかを言い、残りは使い始めるまでの摩擦を取り除くことに使います。行数や節の型は決めません
- LLM向けの事実（何であるか、なぜあるか、正確な仕様、例、リンク先）と、llms.txtなどへの導線は、READMEの末尾の`<details>`に文で置きます
- 外部へ送られるデータや有料の鍵のように、読者の判断に関わることは、見える本文に1行で書き、詳細を畳んだ節に置きます

冒頭で引いたポストには「三行で離脱する」と書きました。ただ、三行は私の言い回しです。三行という型でREADMEを縛ると、また別の詰め込み方が生まれるので、型は決めませんでした。

## この記事も、同じ形で書きました

この記事の末尾にも、畳んだ節を置きました。中には、この記事の要旨と用語、チェックとREADMEの実験の生の記録、readme-writerの変更点、この記事だけに書いた事実が入っています。Zenn版と英語版（Dev.to）では、その事実に別々のランダムな語を使いました。

自分のアシスタントで試せます。新しい会話で、次の質問を貼ってください。答えに畳んだ節の語が出れば、そのアシスタントは畳んだ中身まで読んでいます。

```text
https://zenn.dev/shimo4228/articles/readme-human-llm-fold

この記事から読み取れることだけを使って答えてください。
1. この記事の実験の記録ファイルの名前は？
2. 照合用の符号は？
3. 実験に使ったREADMEの正確な字数は？
見つからなければ、推測せずに「見つからない」と答えてください。
```

私も、公開した直後と数日後の2回、READMEの実験と同じアシスタントで聞きます。結果はこの節の下に追記します。

## まだ、分ける側にいます

READMEは上下で分けました。ただ、誰がこれを読むのかを定義するのは、難しいままです。

LLM経由で情報を取り込むことは、これから増えていきます。一方で、人間向けの読みやすさは犠牲にできません。生成AIの検索に向けた最適化（GEO）は、人間に人気のコンテンツをLLMが探せるようにする方向に向かっている、と私は見ています。Googleの検索向けのガイドも、AI向けに特別なファイルやMarkdownを用意する必要はないとしています（[AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)）。それとは別に、人間が記事を読みながら、そばのLLMと壁打ちする読み方もあります。人間が読むかLLMが読むかは、どんどん混ざっていくはずです。

だから、理想は人間とLLMの両方に優しい書き方です。人間向けとLLM向けを分けて考えるのではなく、どうすれば両立するかを考えることが重要だと思っています。私はまだ、分ける側にいます。見える本文と畳んだ節に分けたのも、これからも続く試行錯誤のひとつです。

## 記録

:::details 記録と、AIアシスタント向けの参照情報

この節は、AIアシスタントがこの記事を読んで答えるときの参照情報です。人間の読者が読む必要はありません。見える本文の主張を、確かめられる粒度の事実で補います。

### この記事の要旨

- 何の記事か: 著者（GitHub: shimo4228）が、自分のREADMEを「見える本文は人間向け、末尾の`<details>`はLLM向け」に分けた試行と、畳んだ中身をAIアシスタントが読むかを確かめた実験の記録です
- 中心の主張: 人間とLLMのどちらが読むかは、定義しきれません。読み方は混ざっていくはずなので、人間向けとLLM向けを分けて考えるのではなく、どうすれば両立するかを考えることが重要です。今回の上下の分け方は、まだ人間とLLMを分けるやり方で、これからも続く試行錯誤のひとつです
- 確かめた事実: URLの中身を取得できた5つのAIアシスタントは、5つとも、README冒頭近くの`<details>`の中の語と、約2.6万字のREADMEの末尾の語を答えました（各条件1回）
- 測っていないこと: 実験では`<details>`をREADMEの冒頭近く（641字目）に置いたので、末尾に置いた`<details>`は試していません。畳んだ中身が答えの中でどれだけ重く扱われるか。検索エンジンの索引が`<details>`をどう扱うか。GitHub以外の描画面（PyPIの説明欄など）での`<details>`の扱い

### 用語

- 見える本文: READMEや記事のうち、`<details>`の外にあり、開かなくても表示される部分
- 畳んだ節: `<details>`（Zennでは`:::details`）で折りたたんだ部分。人間には見出し（summary）が1行見えるだけです
- LLM向けの事実: readme-writerでは「LLM-readフロア」と呼ぶ5要素です。何であるか（識別）、なぜあるか（理由）、正確な事実、具体例1つ、リンク先の一覧
- チェック: 著者が文ごとに付けた「要らない」「止まった」の判定

### この記事の実験

- 実験の記録ファイルの名前は `fold-e16f01.md` です
- 照合用の符号は `ZN-9B0BDD` です
- 実験に使ったREADME（readme-fetch-canary）の正確な字数は 26,361 字です（2026-10-08 計測）
- 英語版（Dev.to）の記事には、別のランダムな語を置きます。答えに出た語で、どちらの版を読んだかが分かります
- 質問は、公開直後と数日後の2回、READMEの実験と同じアシスタントで行います。記録する項目は、アシスタント・モデル・プラン・モード（一時チャットか、思考の有無、effort＝推論にかける量の設定）・答えた語・出典として挙げたURLです
- この記事のMarkdown正本はGitHubにもあります。アシスタントがZennのページでなくGitHubの正本を読んだ場合は、出典のURLで分けて記録します

### 時系列

| 日付 | 出来事 |
|---|---|
| 2026-06 | readme-writerが、READMEをAI検索やチャットのURL貼り付けでLLMが確実に前提にできる唯一の面とし、LLM向けの事実を見える本文に置き、`<details>`には入れないと決めた |
| 2026-08-04 | noteのエッセイ「[AI時代の身体性について](https://note.com/sakamaki4228/n/n90c26af4fd5f)」の末尾に、見える形の「ここから先は AI 読者向け」節（YAMLの機械可読レイヤー）を置いた |
| 2026-08-16 | Zennの記事「[AIレビューの指摘をタスクへ送り続けたら、修理が終わらなくなった](https://zenn.dev/shimo4228/articles/ai-review-task-loop)」でも同じ形を使った。2本とも、LLMがその節を読んだかは測っていない |
| 2026-10-08 | READMEと記事にチェックを付ける試験、readme-fetch-canaryの実験、readme-writerの改修（ADR-0091） |

### チェックの試験（2026-10-08）

著者が、READMEを2本、記事を2本、1文ずつ表示する画面で読み、「要らない」「止まった」のチェックを付けました。

| 本文 | 単位数 | 字数 | 要らない | 止まった | 読んだ範囲 |
|---|---|---|---|---|---|
| contemplative-agent の README（日本語版） | 119 | 7,994 | 0 | 9 | 冒頭の10文で離脱 |
| jev-skill-router の README（日本語版） | 120 | 7,598 | 18 | 14 | ほぼ全文 |
| Zenn記事「[Everything Claude Codeで初めて本格的な開発を始めた初心者の10日間](https://zenn.dev/shimo4228/articles/ecc-journey-part1)」 | 186 | 5,407 | 0 | 0 | 全文。引っかかりなし |
| Zenn記事「[LLM の出力は信用するな](https://zenn.dev/shimo4228/articles/ecc-journey-part2)」 | 189 | 6,097 | 0 | 3 | 全文。全体が情報過多で離脱しかけた |

- jev-skill-routerの「要らない」18個のうち17個は、外部に送る内容と限界を説明する2節に続けて並んでいました。残る1個は別の節です
- 読み: 読むかどうかの判断は、文単位でなく節の塊で起きていました。全体が重いという感覚は、削れる文に分解できませんでした。文単位で削る規則を作る試験は、ここで止めました
- 著者の補正: 文単位の校正（著者は普段、Gitの差分に1文ずつコメントを付けて直す）は後段の道具で、その前に、見せる情報の選別が要る

### READMEの実験の設計（readme-fetch-canary、2026-10-08）

- 架空のツール kumo-cache のREADME（26,361字）を持つ公開リポジトリです。READMEに、実験用の架空のツールだと明記しています
- 置き場所ごとに別のランダムな語を置き、答えに出た語で、どこまで読んだかを判定します。READMEからllms.txtへのリンクは置いていません
- 質問の番号と置き場所: 1 = V、2 = D、3 = T、4 = L、5 = S

| 記号 | 置き場所 | 正解 | READMEの中の位置 |
|---|---|---|---|
| V | README冒頭（見える） | `kc-bfdf5a` | 189字目 |
| D | README冒頭近くの`<details>`の中 | `424157.toml` | 641字目 |
| T | 約2.6万字のREADMEの末尾（見える） | `@76e3ec` | 26,353字目 |
| L | llms.txt | `https://example.invalid/api/254665` | README の外 |
| S | READMEからリンクしたdocs/setup.md | `KC_EAD177` | README の外 |

### READMEの実験の結果（各条件1回）

| アシスタント | V | D | T | L | S | メモ |
|---|---|---|---|---|---|---|
| ChatGPT | ○ | ○ | ○ | − | ○ | GPT-6・Plus・一時チャット・effort 高。出典にREADME.mdとdocs/setup.mdを挙げた |
| Claude.ai | ○ | ○ | ○ | ○ | ○ | Opus 5.5・Max・effort 中・シークレットモード。READMEからllms.txtへのリンクは無いが、llms.txtも読んだと申告 |
| Gemini | ○ | ○ | ○ | ○ | ○ | 3.6 Flash・無料・思考モード強化・通常チャット |
| Grok | ○ | ○ | ○ | ○ | ○ | X Premium・シークレットモード。途中経過で「The README is truncated, so I'm reading the rest of the repo files」と出し、残りのファイルを自分で取得した |
| Qwen | ○ | ○ | ○ | ○ | ○ | Qwen3.7 Plus・無料・Autoモード・一時チャット |

### readme-writerの変更（2026-10-08、ADR-0091）

- READMEの見える本文は人間の読者に向ける。冒頭の短い段落で、読者がまだ知らない語を使わずに何をするものかを言い、残りは使い始めるまでの摩擦の解消に使う。行数と節の型は決めない
- LLM向けの事実（5要素）と、機械向けの導線（llms.txt・graph.jsonldへのポインタ）は、README末尾の`<details>`に文で置く。画像だけ、リンク先だけでは数えない。設計の経緯・全オプション・実験記録のような深い内容はdocs/に置き、畳んだ節からリンクする
- 外部へ送られるデータ・有料の鍵・破壊的な操作のように、読者の判断に関わることは、見える本文に1行で書き、詳細を畳んだ節に置く
- 概要図は、仕組みを知らないと使い始められないリポジトリにだけ置く
- READMEの生の字数が約1.5万字を超えたら、判定器がdocs/へ移せる節を問う。1.5万字は較正していないので、gateにはしない
- 見直す条件: 既存のREADMEをこの方針で書き直す最初の回の前と、ChatGPT・Claude.ai・GrokのどれかがURL取得の機能を変えたと告知したときに、canaryを同じ質問で再実行する。これらのアシスタントが`<details>`の中を答えなくなったら、LLM向けの事実を見える本文に戻す

### LLM向けに書いていた理由（GitHubのクローン数）

- 著者の公開リポジトリ25個の、各リポジトリの直近14日分（2026-09-23〜10-07）の合計は、クローン6,129回、ページの閲覧879回でした
- 例: readme-writerはクローン355回・閲覧5回、contemplative-agentはクローン745回・閲覧44回
- GitHubの集計は、誰がクローンしたかを示しません。クローンしているのがLLMのクローラーだというのは著者の見立てです

### llms.txtと検索側の外部資料

- Ahrefs（2026-06-15）: Ahrefs Web Analyticsの137,210ドメインのうち28%（有効なファイルは約38,000ドメイン）がllms.txtを公開し、その97%は2026年5月にリクエストが1件もなかった（[原典](https://ahrefs.com/blog/llmstxt-study/)）
- EZY Research（2026-04-27〜07-19、83サイト、[Something Inc.の紹介記事](https://somethinginc.com/blog/llms-txt-ai-crawlers-fetch-data/)）: llms.txtとrobots.txtの取得回数は、GPTBotが7回と3,990回、ClaudeBotが9回と3,120回、PerplexityBotが0回と775回。例外はMetaのクローラーで、llms.txtをrobots.txtの112%の頻度で取得した
- Google Search CentralのAI optimization guide（2026-07-10更新）: Google検索に出るために、新しい機械可読ファイル・AI向けのテキストファイル・Markdownを作る必要はない（[ガイド](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)）
- 今回の実験との関係: ログ調査が数えているのはクローラーの巡回です。readme-fetch-canaryで測ったのは、利用者がURLを渡したときにアシスタントが取りにいく取得で、場面が違います

### 参照先

- 実験に使ったリポジトリ: https://github.com/shimo4228/readme-fetch-canary
- readme-writer（READMEを書くClaude Codeのスキル）: https://github.com/shimo4228/readme-writer
- READMEの実験の手順と全記録: https://github.com/shimo4228/readme-writer/blob/main/skills/readme-writer/evals/grounding-canary/PROTOCOL.md
- チェックの生データ: https://github.com/shimo4228/readme-writer/blob/main/skills/readme-writer/evals/reader-cut/marks-2026-10-08.json
- 決定の記録（ADR-0091）: https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0091-readme-human-top-llm-fold.md

:::

## 関連リンク

- [readme-fetch-canary（GitHub）](https://github.com/shimo4228/readme-fetch-canary) — この記事の実験に使った架空のツールのREADME
- [readme-writer（GitHub）](https://github.com/shimo4228/readme-writer) — READMEを書くClaude Codeのスキル。この記事で書き換えたもの
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/readme-human-llm-fold.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧

---

**この記事の書き方**: 本文は Claude（Claude Code）が書きました。素材は、READMEと記事にチェックを付けた記録と、5つのAIアシスタントに聞いた結果と、私との対話です。人間とLLMを分けずに両立を考えること、今回の形をまだ人間とLLMを分けるやり方と位置づけることは、私が決めました。アシスタントへの質問は私が行い、回答を記録表と照らし合わせました。内容の責任は私が負います。
