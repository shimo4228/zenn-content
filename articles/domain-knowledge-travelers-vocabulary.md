---
title: "業務の中にいる人は、それを「ドメイン」とは呼ばない"
emoji: "🗺️"
type: "idea"
topics: ["aiエージェント", "ddd", "設計", "ai"]
published: true
published_at: 2026-09-16 09:00
---

「エンジニアに残るのはドメイン知識だ」という言葉を、この夏、何度も目にしました。

2026 年 6 月、Anthropic は Claude Code の約 40 万セッションを分析し、「成功へ導く力は、コードを書く力よりドメインを掌握しているかから来る」と報告しました[^1]。その少し前には「ドメインの専門性こそが本当の堀だった」というエッセイが広く読まれ[^2]、エージェントの実装能力が上がるほど、この言説は強くなっています。

私はこの言説にうなずきながら、別のところで引っかかっていました。引っかかるのは結論ではなく、「ドメイン知識」という言葉そのものです。この言葉は、業務を外から眺める人がいることを前提にして成り立っています。その前提が、エージェントが実装を担う時代にはもう崩れている、というのがこの記事の主張です。

順番にこう進めます。まず、この言葉が今どう使われているかを確認します。次に DDD での出自を一次資料で押さえ、この言葉が「翻訳」のために作られたものだと確かめます。そのうえで、翻訳する人（翻訳者）と、翻訳される側（業務の中にいる人）の視点を対比しながら、言葉を使い続けることが何を意味するのかを書きます。

## 「ドメイン知識」は今、何のための言葉か

今年の言説を並べると、「ドメイン知識」という同じ言葉が、二つの違う用法で使われていることが見えてきます。一つは道具の話、もう一つはキャリアの話です。

**道具の話。** 2026 年 2 月、Matt Pocock の skills リポジトリが、DDD の語彙をエージェントの context management に持ち込みました。26 万 star を集めたこのリポジトリの README は、Evans を引用してこう書いています。

> プロジェクトの初期、開発者と、その相手である業務側（ドメインエキスパート）は、たいてい別の言語を話している。私は自分のエージェントにも同じ緊張を感じた[^3]

解決策は CONTEXT.md という共有言語の文書で、エージェントが業務の jargon を解読するための用語集です。ここでの「ドメイン知識」は、エージェントに業務を伝えるための道具です。エージェントが開発者の椅子に座ったので、DDD の翻訳装置をエージェント向けに組み直した、ということです。

**キャリアの話。** 同じ 2 月、Claude Code の作者 Boris Cherny が「コーディングは実質的に解決した。ソフトウェアエンジニアという肩書は消えていく」と語り[^4]、エンジニア不要論が前提として置かれました。これに応える形で、5 月末の「ドメインの専門性こそが本当の堀だった」というエッセイは Hacker News で 500 件を超えるコメントを集め[^2]、「業界を一つ選び、かつてプログラミング言語を学んだように学べ」とエンジニアに勧めました。

6 月の Anthropic の分析は、この用法に数字を与えました。「上位 10 職種すべてが、ソフトウェアエンジニアと 7 ポイント以内の成功率」で、非ソフトウェア職の中で伸びているのは管理職、営業、法務でした[^1]。分析自体は職種の代替可能性を主張していませんが、不要論の側に引用されるデータになりました。

9 月には「最高のエンジニアはもうコードを書かなくなる。ドメインエキスパートになり、アーキテクチャを定義し、エージェントを指揮して結果を判定する」[^5]、日本でも「エンジニアには事業理解を」[^6] という形で、キャリア助言の語彙として定着しています。

二つを並べると、こう見えます。エージェントに業務を伝えるための道具だった言葉が、エンジニアの居場所を確保するための言葉として使われ始めています。そして「学べ」という処方箋は、読者がエンジニアで、業務はこれから学びに行く対象だ、という前提を持っています。

ここで問いが立ちます。「ドメイン知識」という言葉は、そもそも誰の側から見た言葉なのか。それを確かめるために、出自に戻ります。

## 「ドメイン知識」という言葉はどこから来たか

「ドメイン」は日常語ではなく、ソフトウェア工学の語彙です。語自体は 1980 年代の domain analysis 以来使われ、Michael Jackson の Problem Frames（2001 年）にも受け継がれていますが[^7]、「ドメイン」「モデル」「ユビキタス言語」を一つの語彙体系として広く定着させたのは、Eric Evans の『Domain-Driven Design』（2003 年、以下 DDD）です。

DDD の中核概念は、すべて翻訳の道具です。それを確かめるために、本論に必要な 6 つだけ押さえます。

**ドメイン（domain）。** Evans の定義では「知識、影響、または活動の領域。ユーザーがプログラムを適用する対象領域が、そのソフトウェアのドメインである」[^8]。航空券予約システムなら予約業務が、会計ソフトなら会計がドメインです。

**ドメインエキスパート（domain expert）。** その領域を熟知している人です。開発者が兼ねることもありますが、DDD は典型的には別の人が担う前提で道具を組んでいます。この人たちの頭の中にある知識を、ソフトウェアに使える形へ取り出すことが出発点になります。

**ドメインモデル（domain model）。** 業務を全部写し取るものではなく、「選択的に単純化し、意識的に構造化した知識の形」[^9] です。Evans は映画作りに例えています。記録映画でさえ、編集なしの現実は映しません。

**ナレッジクランチング（knowledge crunching）。** 開発者とドメインエキスパートが対話を重ね、大量の情報から関係する細い流れを探り当ててモデルを練る過程です。Evans はこう書いています。「ナレッジクランチングは一人でやる活動ではない。開発者とドメインエキスパートのチームが協働する。通常は開発者が主導して」[^10]。

**ユビキタス言語（ubiquitous language）。** ドメインモデルを背骨にして組み立てた言葉を、会話でもコードでも図でも、チーム全員が使い続けることです。Evans は翻訳の害を明確に書いています。「共通言語のないプロジェクトでは、開発者はドメインエキスパートのために翻訳しなければならない。……翻訳は常に不正確であり、理解の食い違いを隠す」[^11]。

**境界づけられたコンテキスト（bounded context）。** 同じ「顧客」という語が営業と経理で違う意味を持つことを DDD は認めていて、モデルの通用範囲に線を引く装置をこう呼びます。定義は「特定のモデルが定義され、適用される境界の記述」[^12] です。これは記事の後半で効いてきます。

6 つを並べると、DDD が何のための道具かがはっきりします。開発者は業務を知らず、業務の人はソフトウェアを知らない。この断絶の上に橋を架けるための語彙が、ドメイン、モデル、ユビキタス言語です。

つまり DDD の語彙体系は、最初から翻訳の問題を扱うために組まれています。翻訳が必要なのは、両岸に別々の人が立っているからです。片方にしか人がいなければ、橋は要りません。

以下では、この「橋」の上に立つ人を翻訳者と呼びます。開発者として業務を外から仕入れ、コードの言葉に置き換える人のことです。

## 「ドメイン」は業務の外側から見た言葉

「ドメイン知識を学ぶ」「ドメイン知識をキャッチアップする」という言い方が成り立つ視点は、業務の外側にあります。中にいる人にとって、それは「仕事」であって、外から仕入れる知識ではありません。

旅行者だけが「現地」と言います。住んでいる人は自分の町を現地とは呼びません。「キャッチアップする」という言い方には、自分はよそから来ていて、いつか帰る場所が別にある、という前提が最初から埋め込まれています。だから「興味を持てるかどうか」が問題になります。住んでいる町に興味があるかどうかを問う人はいません。

「業界を選んで学べ」という処方箋の善意も、この構図の中に収まっています。学びに行く人を褒める言い方は、学びに行かなくても許される立場をそのまま残します。本来、業務の中身を知らずに仕様を書いていることのほうが異常なはずです。それが常態だから、知っている人が例外として称賛されます。

## 問いは業務の中からしか生まれない

外から学ぶことと中にいることの違いは、エージェントを使うときに、はっきり差になって現れます。例で示します。

営業担当が見積を出す前に、必ず倉庫に電話して在庫を確かめています。在庫管理システムには数字が出ているのに、です。入庫処理が翌日にずれることがあって月初の数日は数字が信用できない、と手が覚えているからで、手順書のどこにも書いていません。架空の人ですが、似た手癖はどの職場にもあるはずです。

この人がエージェントに投げる問いは「月初に在庫数がずれる原因はどこか」です。在庫システムから出力した入出庫の記録と処理の時刻を突き合わせれば、一晩で当たりが付きます。原因が分かれば、同じエージェントに「入庫待ちの品目を毎朝一覧にして」と頼みます。翌朝から一覧が届き、倉庫への電話が一覧の確認に変わります。情シスに要件を説明し、在庫の言葉を開発の言葉に訳してもらい、リリースを待つ工程は、どこにもありません。

一方、在庫管理を外から学んだ人には、最初の問いがありません。学んで分かるのは「在庫システムに数字がある」ことまでで、電話をかける理由は誰も言葉にしていないからです。外の人が手順書を比べたり現場を観察したりして問いを拾うこともできますが、拾えるのは中の人がすでに言葉にした分だけです。言葉になる前の摩擦は、業務を回している人のところにしかありません。

エージェントが縮めたのは、問いを投げてから仕組みが動くまでの時間です。問いがなければ、縮めるものがありません。

ここが「興味を持てる業界を選べ」という処方箋の届かない場所です。興味があっても、業務を自分で回していない人には、投げるべき違和感がほとんど発生しません。興味以前に、位置の問題です。

もう一つ言えることがあります。「学べ」が勧めているのは知識を仕入れることですが、知識の仕入れはエージェントで誰でも速くなりました。誰でも速くなった分は、差になりません。差になるのは何を投げるかで、それは業務を回している人の違和感から出ます。「学べ」は、もう差にならなくなったほうを勧めています。

## 翻訳者の席がなくなる

経理の人が、自分の言葉のまま「この照合作業を楽にしてほしい」とエージェントに頼みます。それで済んでしまいます。その横で、仕様を聞き取ってコードの言葉に翻訳する役割の人が、何をしていいか分からず立っています。

DDD がドメインエキスパートと呼んだ人が、開発者を通さずに直接頼む側になる場面です。同じ光景を業務側から書いた記事があります。15 年の経験を持つ医療運営の責任者がエージェントで自分の業務ツールを作る話で、筆者はこう書いています。

> 彼女はエンジニアを置き換えているのではない。自分がボトルネックであることをやめているのだ[^13]

事例はすでにあります。関税分類の誤りが直接の損失になる貿易コンプライアンスで、専門家の 5 段階の判断手順をそのまま再現したエージェントを 2 人のチームが作り、世界ベンチマークの 1 位を取った報告[^14]や、Anthropic のハッカソンを弁護士が制した話[^15]です。業務の摩擦に日々触れている人が自分の言葉のまま頼むほうが、間に一人挟むよりずっと早く、ずれも少ないのです。

ここで「翻訳が消えたのではなく、エージェントへ移っただけだ」という反論が立ちます。そのとおりで、曖昧さをほどく仕事も、例外を明示する仕事も消えません。営業の「顧客」と経理の「顧客」が違うことは、誰かが言葉にしなければならないままです。

変わるのは、その仕事をする人の立ち位置です。ほどくのは業務の中にいる人で、ほどいた結果は業務の言葉のまま残ります。外から来た人が自分のモデルの語彙に置き換える工程が、丸ごと要らなくなります。

「ドメイン知識が大事」という主張を裏返すと、こうなります。業務の中にいて、かつエージェントを使える人だけが残る。翻訳者の席がなくなる。

### 翻訳者は両側から挟まれる

翻訳者の席が消える順番は、現場の形によって二通りあります。

DDD が成り立つ現場、つまり業務側が開発者と毎日同じ部屋にいる内製の組織では、業務側はすでにシステムの隣に座っています。エージェントを自分で使う距離にいるので、翻訳者を通す必要が最初になくなります。翻訳がいちばんうまくいっていた現場から、翻訳者が要らなくなるということです。

DDD が成り立たない受託や SIer では、翻訳は最初から開発者の一方通行で、ユビキタス言語は語彙だけが残っていました。そこにエージェントが入ると、業務側は開発者を通す理由を失います。

どちらの現場でも、消えるのは翻訳者の席からです。

## 命名権も一緒に戻る

翻訳者が消えるとき、一緒に業務側へ戻るものがもう一つあります。言葉の意味を決める権利です。この節では、その権利が今どちらにあるのかを確かめます。

**業務側にはすでに言葉がある。** 歴史の長い業務なら、業務側はすでに用語集を持っています。経理には勘定科目の定義があり、固定資産には償却区分の一覧があります。開発者が「共通の言葉を作りましょう」と言うとき、業務側から見れば言葉はもうあって、ないのは開発者の側だけです。

**DDD はその言葉を一つの意味に固定する。** DDD は業務側の用語集を捨てはしませんが、そのままも使いません。Evans は業務で使われている文書をナレッジクランチングの素材に挙げる一方で、「ドメインモデルに基づくユビキタス言語は、働いているモデルが一つだけであることを前提にする」と書いています[^16]。ドメインモデルは「選択的な単純化」なので、開発者は用語集の中からモデルに要る語を選び、一つの意味に固定します。

このとき落ちるのが、用語集に書いていない層です。営業と経理は「顧客」を別の意味で使い、担当者は「この取引先だけ請求先が別」という例外を語の一部として覚えています。業務側の言葉は、この運用と一緒に生きています。モデルに固定された語はこの層を持てません。持てないから、開発者は業務側に「以後はモデルの語彙で話してください」と求めます。共通と言いながら、語の意味を決めたのは開発者です。

**対等という建前と、その崩れ方。** Evans の建前では、両者は対等です。「ドメインエキスパートは、業務理解を伝えるのに不自然または不十分な用語や構造に異議を唱え、開発者は設計を狂わせる曖昧さや不整合に目を光らせる」と書いていて[^17]、業務側に拒否権がある前提です。

ただ、対等という建前そのものが、システムの側から見た発想です。業務が先にあってシステムが後から付くのだから、本来、語の意味を決める席は業務側にしかありません。それを交渉の場に載せた時点で、主従が消えています。

運用ではさらに崩れます。異議を唱えるには、業務側が開発者と毎日モデルを練り直す場が要ります。受託や短い要件定義の現場では、業務側が開発者と会うのは最初の数回で、あとは開発者が持ち帰って語を固定します。業務側が「その語は違う」と言える機会は、できあがったものを見る受入テストまで来ません。そこで言えたとしても、要件定義のあとの変更は仕様変更として費用と工期に跳ね返るので、業務側のほうが折れます。

旅行者が現地に来て「お互いのために共通語を決めましょう」と提案し、決まるのは旅行者の言葉、という構図です。

**DDD 自身はこの問題を知っていた。** 境界づけられたコンテキストは、営業の「顧客」と経理の「顧客」を別のモデルに分けて、どちらも生かす装置です。それでも運用で語の意味が一つに寄るのは、境界を引くのも開発者だからです。Evans が書いたのは「通常は開発者が主導して」までで、主導と命名権は別物ですが、運用ではこの二つが一致しやすい、というのが私の見立てです。

**開発者からは見えにくい。** 開発者の側からこれが見えにくいのは、開発者にとってこれが敬意に見えるからです。「業務の言葉をちゃんと学びます」「専門家の話を聞きます」という善意でやっています。だから業務側に「舐めている」と言われても心当たりがなく、指摘が届きません。

**エージェントで命名権が戻る。** 業務側がエージェントに自分の言葉のまま頼めるということは、語の意味を決める権利が業務側に戻るということです。エージェント向けの用語集が要らなくなるのではありません。書く人が業務側に変わり、例外が用語集の外に落ちなくなります。

## 何が残るか

ここまで「業務の中にいる人だけが残る」と書いてきました。エンジニアの側にも、残る仕事はあります。

エージェントが動く環境そのものを作る人がいます。権限やログや失敗時の扱いを決め、大規模なデータの整合性や複数の業務をまたぐ処理を設計する人も、まだ要ります。誰が何を承認し、どの状態を正しいとするかには業務判断が混じりますが、その判断を下すのは業務側で、翻訳者ではありません。

複数の業務をまたぐ調整は、翻訳に近い仕事として残ります。ただし、それは業務と業務の間の翻訳です。この記事が消えると言っているのは、業務とコードの間の翻訳だけです。

残る仕事を一言で言えば、業務とコードの間の翻訳ではなく、水道を引くことです。蛇口をひねる側が業務で、配管を通す側が残るエンジニアです。

以前、[AI ハーネスの価値構造を砂時計型と書きました](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall)。上（何を作るかの判断）と下（データ、インフラ、物理的制約）は価値を保ち、中間の実装層はゼロに向かう、という見立てです。あのとき私は「ドメイン知識」を上の層に置きました。この記事はそれを分解しています。上に残るのは業務そのものであって、エンジニアが外から仕入れる知識としての「ドメイン知識」は、真ん中の層と一緒に抜けます。

そして残る側のうち、数が圧倒的に多く価値も大きいのは業務の側です。現場で実務をしながらエージェントを使える人は、自分の摩擦を自分で解消できるようになった人で、誰かに何かを教える必要がそもそもありません。

この主張が厳しいのは、仕事が減るからではありません。エンジニアが要ると思っていた根拠そのものが、業務側の手に渡ってしまうからです。

どこまでが「水道」で、どこからが「翻訳」なのか、その線はまだ引けていません。業務の複雑さによって線の位置が変わることは分かっていますが、それ以上のことは、私にはまだ分かりません。

## これは責める話ではない

ここまでの主張は個人への評価に見えるかもしれませんが、これは分業の形が生んだ結果であって、個々のエンジニアの落ち度ではありません。

「ドメイン知識」という言葉を必要としたのは、実装が稀少だった時代の分業の形です。その分業の中では翻訳者は必要でしたし、その語彙は合理的でした。DDD が 2003 年に書かれたのは、その断絶が本物だったからです。変わったのは人ではなく地形のほうで、この指摘は「あなたが悪い」ではなく「あなたの育った地形が動いた」に近いものです。

処方箋を一つだけ足すなら、「学べ」ではなく「中に入れ」です。現場の困りごとが目の前で起きる位置にいれば、問いは勝手に発生します。「業界を選んで学べ」より「業務を一つ自分で回せ」のほうが、エージェントに投げる問いを持つ経路としては短いです。

ただし、その経路を進みきった先にいるのは「業務の中にいる人」であって、「ドメインに詳しいエンジニア」ではありません。

## おわりに

「ドメイン知識が大事」という言葉を聞くたびに、少し引っかかるものがありました。その正体を言葉にすると、大事なのは業務のほうで、知識としての取り込み方はもう主題ではない、ということになります。

「ドメイン知識を学ぶ」という語彙で世界を切っている限り、自分を稀少性の側に置き続けることになります。その語彙を使い続けることは、消える側に立っているのに気づきにくい、ということです。

あなたが次に「ドメイン知識を学ぶ」と口にするとき、その言葉がどちらの岸から見た景色か、一度確かめてみてください。橋の上に立っているなら、どちらの岸に降りるかを早めに決めてください。最初に消えるのは、橋の上の席です。

[^1]: Anthropic, "Agentic coding and persistent returns to expertise" (2026-06-16). 2025 年 10 月〜2026 年 4 月の約 40 万セッション・約 23.5 万人を分析。"the ability to steer Claude toward success comes more from command of a domain than from the ability to write code." / "every one of the ten largest occupations in our dataset lands within seven points of software engineers in terms of their success." / "The fastest-growing non-software occupation groups in our sample are management, sales, and legal occupations." https://www.anthropic.com/research/claude-code-expertise
[^2]: Aaron Brethorst, "Domain Expertise Has Always Been the Real Moat" (2026-05-30). "The binding constraint has moved from *can you build it* to *can you tell whether it's right*." / "Pick an industry, an instrument, a regulatory regime, a physical process, and learn it the way you once learned a programming language or framework." https://www.brethorsting.com/blog/2026/05/domain-expertise-has-always-been-the-real-moat/ 。Hacker News のスレッド（884 points / 549 comments）: https://news.ycombinator.com/item?id=48340411
[^3]: mattpocock/skills README（リポジトリ作成 2026-02-03、2026-09-12 時点で 260k stars）、"#2: The Agent Is Way Too Verbose" の節。"At the start of a project, devs and the people they're building the software for (the domain experts) are usually speaking different languages. I felt the same tension with my agents. Agents are usually dropped into a project and asked to figure out the jargon as they go. ... The Fix for this is a shared language. It's a document that helps agents decode the jargon used in the project." https://github.com/mattpocock/skills
[^4]: Boris Cherny（Claude Code 作者）、Y Combinator の podcast での発言。The San Francisco Standard, "AI writes code now. What's left for software engineers?" (2026-02-19) より。"Today coding is practically solved." / "We're going to start to see the title of software engineer go away. It's just going to be 'builder' or 'product manager.'" https://sfstandard.com/2026/02/19/ai-writes-code-now-s-left-software-engineers/
[^5]: Milan Milanović, "What is the future of software engineering?" (Tech World With Milan, 2026-09-03). "What we will see in the next few years is that the best engineers will not be the best coders anymore, and even they will not write any code. They will be domain experts, define architecture and direct agents and judge their outcomes." https://newsletter.techworld-with-milan.com/p/what-is-the-future-of-software-engineering-d52
[^6]: 地家伶人（パーソルキャリア）「専門性と越境」Enterprise IT Conference 2026 講演資料（2026-09-10）、スライド 9。「PdMには技術の勘所を、ITコンサルタントには開発知見を、エンジニアには事業理解を。同じ組織の中で、一緒に打ち手を考える関係へ。」 https://speakerdeck.com/techtekt/specialization-and-boundary-spanning
[^7]: Michael Jackson, *Problem Frames: Analysing and Structuring Software Development Problems* (Addison-Wesley, 2001)。domain analysis の系譜は Neighbors (1984)、Prieto-Díaz (1987) に遡る。
[^8]: Eric Evans, *Domain-Driven Design Reference: Definitions and Pattern Summaries* (Domain Language, 2015), Definitions. "A sphere of knowledge, influence, or activity. The subject area to which the user applies a program is the domain of the software." CC BY 4.0 で公開: https://www.domainlanguage.com/ddd/reference/
[^9]: Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software* (Addison-Wesley, 2003), Part I 冒頭（Chapter 1 の前の導入部）. "A model is a selectively simplified and consciously structured form of knowledge."
[^10]: 同書、Chapter 1 "Crunching Knowledge". "Knowledge crunching is not a solitary activity. A team of developers and domain experts collaborate, typically led by developers."
[^11]: 同書、Chapter 2 "Communication and the Use of Language". "On a project without a common language, developers have to translate for domain experts. ... Translation is always inaccurate and hides disconnects in understanding."
[^12]: Evans (2015), Definitions. "A description of a boundary (typically a subsystem, or the work of a particular team) within which a particular model is defined and applicable."
[^13]: Marliis Schneider, "The Biggest Winners of the AI Revolution Aren't Engineers" (Built In, 2026-07-08). "She's not replacing the engineer. Instead, she's removing herself as a bottleneck." https://builtin.com/articles/ai-rewards-domain-knowledge
[^14]: Gahee Seo, "The 1% problem: How domain expertise + Claude let a 2-person team hit #1 on a global classification benchmark", Code w/ Claude: Extended | Tokyo（Anthropic 主催、2026-06-11）。Findy Tech Blog の参加レポート（2026-06-12）より: https://tech.findy.co.jp/entry/2026/06/12/180000
[^15]: Anthropic "Built with Opus 4.6" ハッカソン（2026 年 2 月）の優勝者がカリフォルニアの弁護士だった件。Anthropic の発表: https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon 。GIGAZINE (2026-04-25) が Dexter Hadley のコメントとともに紹介: https://gigazine.net/gsc_news/en/20260425-anthropic-hackathon/
[^16]: 同書、Chapter 2. "A UBIQUITOUS LANGUAGE based on the domain model assumes there is just one model in play." 業務文書を素材に挙げる箇所は Chapter 1: "It comes in the form of documents written for the project or used in the business, and lots and lots of talk."
[^17]: 同書、Chapter 2. "Domain experts object to terms or structures that are awkward or inadequate to convey domain understanding, while developers watch for ambiguity or inconsistency that will trip up design."

## 出典・参考

- Anthropic, "Agentic coding and persistent returns to expertise", 2026-06-16. https://www.anthropic.com/research/claude-code-expertise
- Aaron Brethorst, "Domain Expertise Has Always Been the Real Moat", 2026-05-30. https://www.brethorsting.com/blog/2026/05/domain-expertise-has-always-been-the-real-moat/
- The San Francisco Standard, "AI writes code now. What's left for software engineers?", 2026-02-19（Boris Cherny の発言）. https://sfstandard.com/2026/02/19/ai-writes-code-now-s-left-software-engineers/
- Matt Pocock, mattpocock/skills（README「The Agent Is Way Too Verbose」、`/domain-modeling`、`/grill-with-docs`）. https://github.com/mattpocock/skills
- Milan Milanović, "What is the future of software engineering?", 2026-09-03. https://newsletter.techworld-with-milan.com/p/what-is-the-future-of-software-engineering-d52
- 地家伶人「専門性と越境」Enterprise IT Conference 2026, 2026-09-10. https://speakerdeck.com/techtekt/specialization-and-boundary-spanning
- Marliis Schneider, "The Biggest Winners of the AI Revolution Aren't Engineers", Built In, 2026-07-08. https://builtin.com/articles/ai-rewards-domain-knowledge
- Findy Tech Blog「Code w/ Claude Extended | Tokyo 参加レポート」2026-06-12. https://tech.findy.co.jp/entry/2026/06/12/180000
- Anthropic, "Meet the winners of our Built with Opus 4.6 Claude Code hackathon". https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon
- GIGAZINE（英語版）, Anthropic "Built with Opus 4.6" ハッカソンの優勝者に関する記事, 2026-04-25. https://gigazine.net/gsc_news/en/20260425-anthropic-hackathon/
- Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software*, Addison-Wesley, 2003（邦訳『エリック・エヴァンスのドメイン駆動設計』今関剛 監訳、翔泳社、2011）
- Eric Evans, *Domain-Driven Design Reference: Definitions and Pattern Summaries*, Domain Language, 2015. CC BY 4.0. https://www.domainlanguage.com/ddd/reference/
- Vaughn Vernon, *Implementing Domain-Driven Design*, Addison-Wesley, 2013（邦訳『実践ドメイン駆動設計』髙木正弘 訳、翔泳社、2015）。戦略側の概念を実務の順で学び直すならこちら
- Michael Jackson, *Problem Frames: Analysing and Structuring Software Development Problems*, Addison-Wesley, 2001。DDD 以前の「ドメイン」用法の一例

## 関連リンク

- [登れる壁に看板を立てても意味がない](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall) — 本文で触れた砂時計モデルの初出
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/domain-knowledge-travelers-vocabulary.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
