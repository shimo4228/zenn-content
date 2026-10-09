---
title: "うわっ…私のスキルのdescription長すぎ…！？"
emoji: "📏"
type: "tech"
topics: ["claudecode", "claude", "agentskills", "llm"]
published: false
---

自分のスキルのdescriptionを眺めていて、「長すぎない？」と思いました。書き直す前、`~/.claude/skills/` には54本のスキルを置いていて、descriptionは合計28,131字、中央値435.5字、800字を超えるものが10本ありました。

長いと何が起きるのかを、Claude Codeの `/skill-doctor`（読み込んだスキルごとに、毎ターンどれだけの文脈を使っているかを出す診断コマンド）で見ました。出力の一部です。

```text
  skill                                              source                    context  7d tokens   uses  last used
  jev-judgment-design                                userSettings                 < 20          -     0×  never
  loop-design-check                                  userSettings                 < 20          -     0×  never
  mono-color                                         userSettings                 < 20          -     0×  never
  repair-discipline                                  userSettings                 < 20          -     0×  never
  …
  context = this skill's one-line listing in the system prompt, included every turn
```

`context` は、そのスキルが毎ターンのスキル一覧に載る1行の大きさです。この4本のdescriptionは459〜1,048字あります。それが20トークン未満で載っているので、一覧には名前しか載っていません。4本とも、一度も使っていないスキルでした。使っていないスキルのうち、descriptionを長く書いたものほど、モデルからはdescriptionが見えなくなっていました。

この記事は、なぜそうなるのかをClaude Codeの実装で確かめ、私がdescriptionをどう書き直したかを示します。ただし、それが正しい書き方かどうかは、まだ分かっていません。

## スキル一覧には予算があり、超えると名前だけになります

Claude Codeは、モデルが自分で呼べるスキルの一覧を、毎ターンsystem promptに入れます。1行は `- 名前: description` の形です。一覧には、自作のスキルだけでなく、pluginのスキルとclaude.aiから同期されたスキルも載ります。私の環境では94本が読み込まれていて、一覧の予算はその全部で取り合います。

予算は、文字の数ではなく表示の幅で数えます。幅は `Bun.stringWidth` で測るので、半角1字が1、全角1字が2です。Claude Code 2.1.295の本体のコードでは、予算は次の式でした。

- context windowのトークン数 × 1トークンあたりの字数 × 0.01（設定 `skillListingBudgetFraction` の既定値）
- 1トークンあたりの字数は、Claude 3〜4.6の一部のモデルで4、Opus 5.5を含むそれ以外で3
- Opus 5.5の1M windowなら、予算は幅30,000。アカウントで1Mのcontextが使えない状態なら200,000トークンで計算し、幅6,000

一覧が予算を超えると、Claude Codeは「Skill listing over budget」という警告をdebug logに出し、どのスキルにdescriptionを付けるかを選びます。

1. Claude Codeに同梱のスキルは、常にdescription付きで残る
2. 残りのスキルを、使用スコア（使った回数と、最後に使った日から決まる値）の高い順に並べる
3. 上から順に、descriptionを丸ごと足しても予算に収まるものだけに付ける。収まらないものは飛ばして、次のスキルへ進む
4. 最後まで付かなかったスキルは、名前だけになる

予算が足りないときに、descriptionが途中で切られることはありません（1本あたりの上限1,536字を超えた分だけは切られます）。付くか、名前だけになるかのどちらかです。

使用スコアの式は、本体のコードではこうなっています（minifyされたままの逐語です）。

```js
function xwt(e){let n=Oa(ce().skillUsage??{},e);if(!n)return 0;let r=(Date.now()-n.lastUsedAt)/86400000,s=Math.pow(0.5,r/7);return n.usageCount*Math.max(s,0.1)}
```

使った回数に、最後に使ってからの日数で7日ごとに半分になる係数（下限0.1）を掛けたものです。一度も使っていないスキルは0です。

冒頭の4本は、使用回数が0なのでスコアが0で、最後に回っていました。長いdescriptionは残りの予算に入らず、名前だけになりました。名前だけのスキルは、モデルから見ると何をするものか分かりません。呼ばれなければスコアは0のままで、予算が足りないままなら、次のセッションでも名前だけです。これはコードから読める循環で、呼ばれにくくなったことを発火の回数で測ったわけではありません。

![予算を超えると、丸ごと収まるdescriptionだけが付く。予算は幅30,000（Opus 5.5の1M window）。同梱のスキル、使用スコアが高いスキルにはdescriptionが付き、使用スコア0で長いスキル（loop-design-check）は残りの予算に収まらず名前だけ、使用スコア0で短いスキルは次へ進んで収まればdescriptionが付く](/images/skill-description-pointer-budget.png)

同じ使用スコア0でも、名前だけになるかどうかは、そのときの残りの予算とdescriptionの長さで決まります。

## 削っても、戻っていました

descriptionが長いことに気づいたのは、これが初めてではありません。8月末にも、descriptionから常駐の量を削ろうとしていました。そのときの8月30日の時点で、リポジトリの中のスキル（外のリポジトリからsymlinkで置いた2本を除く）は57本、descriptionの合計は26,738字でした。今回の書き直しの直前は、同じ数え方で52本、27,105字です。本数は5本減ったのに、字数は増えていました。

スキルを足すたび、直すたびに、descriptionには「こういうときにも使う」が書き足されます。本数を減らしても、残ったスキルの一文ずつが伸びていきます。

## 先に、モデルに呼ばせるスキルかどうかを決めました

書き直しの方針は、Matt Pocockのスキル集の設計指針から取りました。彼はスキルを、誰が呼ぶか（invocation）で2つに分けています（[invocation.md](https://github.com/mattpocock/skills/blob/b0618bc/.agents/invocation.md)）。

- 人が `/名前` で呼ぶスキルは `disable-model-invocation: true` にして、descriptionは人向けの1行の要約にする
- モデルに自分で呼ばせるスキルのdescriptionは、モデル向けに書く

モデル向けのdescriptionの書き方については、別のスキル（[writing-for-agents](https://github.com/mattpocock/skills/blob/b0618bc/skills/productivity/writing-for-agents/SKILL.md)）で、descriptionを本文を指す "context pointer" と呼び、1つの分岐に1つのトリガーを書くこと、否定より肯定で書くことを挙げています。それを短く書くと決めたのは、予算を見た私の判断です。

`disable-model-invocation: true` のスキルは、Claude Codeの実装でもスキル一覧の手前で外されます。一覧に載らないので、予算を使いません。私は2本をこちらへ移しました。たとえば、計画を1問ずつ問い詰めてもらう `grill-me` は、私が頼んだときにしか使わないスキルでした。

```text
Before: A relentless one-question-at-a-time interview that stress-tests a plan or design before you build. Use when the user wants to pressure-test a plan, says "grill me" / "grill this" / "stress-test this" / "poke holes in this" / "interview me about this design", or before committing to expensive or hard-to-reverse implementation work while the goal is still vague.
After:  A relentless one-question-at-a-time interview that stress-tests a plan or design.   (+ disable-model-invocation: true)
```

モデルに呼ばせるスキルは、毎ターン一覧に載ります。だから、そのdescriptionは毎ターン常駐するポインタとして書きます。手順や出力の形は本文に任せ、いつ使うかだけを書きます。いちばん縮んだ例が、測定の結果で判断するときのスキル `measurement-discipline` です。

Beforeは、同じ分岐を日本語と英語の言い回しで10組並べ、使わない場面を3つ挙げていました（1,046字）。

```text
Discipline for designing or evaluating measurement-based claims, thresholds, guards, experiment results and observation periods. Use when the user says 「この実験結果で判断していい？」 / "can I decide on this experiment result?", 「閾値を決めたい」 / "I want to set a threshold", 「ガード/検査を足したい」 / "I want to add a guard or check", 「1 回通ったから大丈夫」 / "it passed once, so it's fine", 「観察期間はどれくらい」 / "how long should the observation period be?", 「いつゲートを開く」 / "when do we open the gate?", 「shadow のまま何週待つ」 / "how many weeks do we wait in shadow?", 「この RFC 塩漬けでは」 / "isn't this RFC just sitting idle?", 「本番より良い」 / "it's better than production", 「本番と比べて」 / "compare it against production", when a design places a numeric threshold, a suspicion flag, or a wait-for-N-observations condition, when a candidate is compared against production, or when a claim rests on measured data. NOT for — designing the instruments themselves (read-only distributions and readings) — out of scope here; designing an LLM judge (llm-as-judge); whether a loop's structure is sound (out of scope here).
```

Afterは、分岐ごとに1つのトリガーにし、日本語でしか打たない語だけを括弧で1回入れました（291字）。

```text
Measurement discipline for claims that rest on data. Use when deciding on an experiment result, setting a threshold (閾値) or guard, choosing an observation period (観察期間) or when to open a gate, comparing a candidate with production (本番比較), or when an automated gate rejects outputs you trust.
```

日本語は1字で幅2を使うので、日英を両方書くと予算を二重に払うことになります。使わない場面は、この例では全部外しました。残すのは隣のスキルと取り合う組だけにして、「Xのときはyを使う」の肯定形で書くことにしました。

![先に、誰が呼ぶかで分ける。人が /名前 で呼ぶスキルは disable-model-invocation: true で一覧の手前で外され、予算を使わず、descriptionは人向けの1行（例: grill-me）。モデルに呼ばせるスキルは毎ターンのスキル一覧に載り、descriptionは毎ターン常駐するポインタとして、いつ使うかだけを書き、手順や出力の形は本文に任せる（例: measurement-discipline 1,046字 → 291字）。短く書くのは筆者の判断](/images/skill-description-pointer-invocation.png)

一覧の予算を使うのは右側のスキルだけです。descriptionを予算のために短く書く理由は、右側にしかありません。

## 幅は、lintで数えることにしました

削っても戻る以上、書くときの注意だけでは足りません。私のハーネスのcommit前の検査に、一覧の幅を数えるlintを足しました。

```python
LISTING_WIDTH_MAX = 12_000
DESCRIPTION_WIDTH_MAX = 400

def listing_width(text: str) -> int:
    """Claude Code が listing 行を測る Bun.stringWidth の近似 — 全角 (W/F) を 2 と数える。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
```

モデルに呼ばせるスキルの一覧の1行を全角2で数え、1本が400、合計が12,000を超えるとcommitを止めます。12,000は、1M windowのときの予算30,000の40%です。この400と12,000は私が決めた値で、何かに合わせて較正したものではありません。

書き直した結果です。

| | 前 | 後 |
|---|---|---|
| descriptionの合計（54本、字数） | 28,131字 | 10,378字 |
| 中央値 | 435.5字 | 189.5字 |
| 800字を超える本数 | 10本 | 0本 |
| モデルに呼ばせるスキルの一覧の幅 | 24,203 | 9,780 |
| `/skill-doctor` で20トークン未満の、`~/.claude/skills/` のスキル | 4本 | 0本 |

書き直した後の `/skill-doctor` では、jev-judgment-design・loop-design-check・mono-color・repair-discipline の4本の `context` は `< 20` から `~80`〜`~250` になり、descriptionが付いて一覧に載りました。使用回数は4本とも0のままです。

## 決めなかったこと

書き直しで、モデルがスキルを自分で呼ぶ回数が変わったかは、測っていません。

逆向きの経験はあります。半年前に、`search-first` というスキルのdescriptionの文言を直したことがあります。そのときは、モデルが自分で呼んだ割合が27%から8%に下がり、元に戻しました（分母は記録に残っていません）。descriptionを磨けば呼ばれるようになる、とは言えないことだけが分かっています。

呼ばせるかを先に決め、呼ばせるものは短く書き、幅はlintで数える。ここまでが決めたことです。これで、自分のスキルが名前だけで一覧に載ることはなくなりました。ただ、descriptionが見えるようになったことと、必要なときに呼ばれることは別のことです。スキルのdescriptionはどうあるべきか。私はまだ、その答えを持っていません。

## 関連リンク

- [mattpocock/skills（GitHub）](https://github.com/mattpocock/skills/tree/b0618bc) — invocationでスキルを分ける設計指針の出典
- [Claude Code のスキルのドキュメント](https://code.claude.com/docs/en/skills) — `disable-model-invocation` などの公式の説明
- [決定の記録（ADR-0092）](https://github.com/shimo4228/claude-harness/blob/main/docs/adr/0092-skill-description-as-resident-pointer.md) — この書き直しの判断と、測っていないこと
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/skill-description-pointer.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧

---

**この記事の書き方**: 本文は Claude（Claude Code）が書きました。素材は、私のセッション記録とdescriptionの前後の計測と、私との対話です。invocationを先に決めて書き直すこと、答えを出さずに問いのまま渡すことは、私が決めました。公開前に私が全文を読み、内容の責任は私が負います。
