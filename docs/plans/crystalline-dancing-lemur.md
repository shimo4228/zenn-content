# 執筆プラン — Jev を既存ハーネスに後付けして見えたこと: 効果は部分的、土台から組めば別物、だから作らずに追う

## Context

入力は証拠台帳 `drafts/article-context_jev-skill-router_2026-09-21.md`（gitignore 下、~/.claude セッション dec93d9c の /collect-context 出力）と、このプラン中の著者発言 3 本（2026-09-21）。
問いは 3 度動いた: 「効く条件は移ったか」→「引き返した地点」→「Jev の実装を通して見えたパラダイムシフト」。
3 つを節として並べると中心命題が 3 つになるので、**1 本の因果線に畳んだ**: 後付けは上乗せにしかならなかった（条件の話）→ 既定を崩す道の手前で引き返した（Mods の話）→ 限界は Jev でなく土台の前提にあると考えた（見立て）→ 作らずに追うことにした（daily-research line）。
引き返した理由が「沼るから」だけでなく「土台ごと変わる可能性があるから、作るより追う」になり、前の brief より因果が 1 段深くなる。
今朝公開の `articles/jev-vs-opus-skill-selection.md`（0.32 秒・費用 約 560 分の 1・確率 0.5 以上の 45 件は Opus と食い違い 0）が、見立ての節の実測の足場になる。
承認後に進めるのは brief 確定 → 執筆 → review panel → 内容 GO → タイトル → quality-gate まで。**公開・投稿・予約・commit はしない。**

## Channel / path

- Zenn（`articles/*.md`）。path: `articles/jev-retrofit-limits.md`（slug 仮）。`published: false` のまま
- register: 日本語ですます、直接指示・具体観察・判断則。channel editor = `editor`
- 読者との約束は「判断できる」の側: Jev を自分のハーネスに足すか、待って追うか
- EN（Dev.to）展開はこのプランの外

## Editorial brief（草案 — 承認後に Step 1 で確定）

- **Reader（仮説）**: Claude Code などのエージェントハーネスを毎日使い、hook・skill・plugin で不便を自分で埋めてきた engineer。Jev（文章を書かず確率だけ返すモデル）を知って「自分のハーネスのどこかに入れられないか」と考えている。ReAct は知っている（仮説）
- **Central thesis**: Jev を ReAct 前提の既存ハーネスに後付けしても、効果は部分的にとどまる。効き方が変わるのは、ツール選択やモデルルーティングを Jev で組み、最後の推論だけをフロンティアモデルに渡す、Jev を土台にしたハーネスが出たときだ — と実装を通して考えるようになり、私は既定の挙動を崩す手前で引き返して、その動きを追う側に回った
- **Entry bridge**: 普段、ギガテックのハーネス周りの改良には手を出さない。不便を実装で埋めても、2 週間ほどで公式が対応して要らなくなることを、この半年繰り返してきたから。それでも今回は好奇心が優って、Jev の cookbook を Claude Code の hook に移植した
- **Causal spine**:
  1. 観察（作った）— cookbook の 2 request レシピを UserPromptSubmit hook にした。足すのは 1 行。用意した依頼文では 6/6 で妥当な skill を 1 秒前後で名指しした
  2. 緊張（後付けは上乗せにしかならない）— 著者の問い「結局 Claude Code のスキル選択も同時に走ってるの？」。hook は 1 行足せるだけで、Claude Code は全 skill の description をモデルに見せ続け、選ぶのはモデル。cookbook が効いた条件（Haiku 4.5 が 60 字に切られた索引で選ぶ。60 字は Hermes の既定幅）は Claude Code に無い。名簿 59 本で 60 字に収まる description は 2 本。Jev の判定は、強いモデルの選択の横を並走するだけになる
  3. 分岐点（既定を崩す道）— 効かせるには一覧そのものを変えるしかない。Claude Mods の型定義は skill 一覧を書き換え可能な添付（`skill_listing`）として公開している。設計のプランを走らせた。頑張ればやれないことはないかもしれないが、Claude Code の既定の挙動を崩してまで実装すると沼ると判断し、すぐにやめた
  4. 機序と見立て — 後付けが部分的なのは Jev の力不足ではなく、土台の前提のせい。ReAct 前提のハーネスは、強いモデルが全部を見て、選択も判定も自分の推論の中でやる。そこへ速い判定器を足しても、置き換わる仕事が無い。逆に、ツール選択・ルーティング・判定を最初から Jev で組み、最後の推論だけフロンティアモデルを呼ぶハーネスなら、速度・費用・精度が別物になる可能性がある。**ここは著者の見立てと明示する**。足場に置ける実測は今朝の記事の値（0.32 秒、費用 約 560 分の 1、確率 0.5 以上の 45 件で Opus と食い違い 0）まで
  5. 読者の判断と著者の行動 — 後付けで埋めるか、土台が変わるのを追うか。私は後者を選び、その動きを追う daily-research の line を新設した。後付けの側に残したのは、「router としては効きそうにない」と冒頭に書いた README と shadow の計器。足すだけの拡張は外せば元に戻るので、試す人はそこから始められる
- **変わりうる読者の見方（仮説）**: 新しい種類のモデルを「いまのハーネスのどこに挿すか」で評価する前に、「このモデルを前提に組んだら土台はどうなるか」を考える

### 事実と見立ての仕分け（本文で混ぜない）

| 層 | 中身 | 書き方 |
|---|---|---|
| 実測・一次ソース | spine 1〜3 の全部、今朝の記事の数値 | 断定 |
| 著者の経験 | 「この半年」「2 週間くらいで公式が対応」 | 一人称の経験として。一般則・予測にしない。件数は足さない |
| 著者の見立て | 後付けの効果は今後も部分的／Jev 基盤ハーネスの可能性 | 「〜と考えています」「可能性があります」。精度については今朝の記事が「Opus 同士の一致の約半分」と書いた事実を隠さない |
| 書かない | 「router として効いた／効かなかった」の率、Mods で「できる／できない」の断定、Jev 基盤ハーネスの性能の数値予測 | — |

### Selected evidence（役割つき）

| 証拠 | 役割 | 扱い |
|---|---|---|
| 著者の発言 3 本（本セッション）+ 台帳の判断記録「Mods まで作って作り込むのは沼にハマるからやめておこう…」 | Entry bridge・spine 3・4・5 の核 | 一人称。著者の言葉の語彙を優先 |
| 注入される 1 行の JSON / README のログ 1 行 | spine 1 の実物（説明より先） | 公開 repo の golden・README と照合 |
| D6（0.2.0 live 6 本: 6/6、0.7〜1.6 秒） | spine 1 | 「用意した単一意図の依頼文」「1 回の読み値」と明示 |
| D11 + 著者の問いの逐語 | spine 2 の転回点 | hooks docs の `additionalContext` を原文確認 |
| D4・D12・C2（60 字は Hermes の既定幅、Haiku 4.5、16.8% → 7.3%）・D5（59 本中 2 本） | spine 2 の機序。短く | cookbook は本プラン作成時に原文で再確認済み（15–17 行・40 行・99 行）。1,536 字は skills docs を執筆前に確認。D5 は公開 repo `scripts/roster.py` で再集計 |
| D13 の型定義 `skill_listing`・設計スレッド #91870 | spine 3 | 執筆前に原文確認、as-of 日付つき。「試していない」と明示。**⚠ 「mods の索引 72 本に無い」は伝聞なので使わない** |
| 今朝の記事の実測（0.32 秒・約 560 分の 1・45 件）と TypeSafe 発表記事の位置づけ（"a frontier-intelligence function call"、System 1 / System 2 の区別） | spine 4 の足場 | 自記事は関連リンク + 本文 1 回。vendor の主張は vendor の主張として引用し、日付つき |
| daily-research line の新設 | spine 5 の行動 | **一次ソース未取得**（下記） |
| D1（公開 repo、shadow 既定、README 冒頭の警告）・D14（`skillOverrides`） | spine 5 | 本文 self-link は repo へ 1 回 |

D7・D8（実セッション 16 行）は落とす前提。spine 2 が構造の議論で立つので、⚠ つきの逸話を足す理由が無い。

### Out of scope（本文に戻さない）

既製調査の取りこぼし（C4・D2）／security の 5 件（C12・D16・S2-4）／review hook の誤 block（C13〜C15・S2）／worktree・verify 赤（C17〜C19）／token 消費 150 万／vendor 案から自作への plan 転換／awesome list PR（D15）／D18 の誤り一覧／D9・D10／料金（C22）／RFC-0024 の枠オフロード動機／既存実装の比較（skillranker 等は「初の実装ではない」の 1 文と関連リンクだけ。C5 の 2 件は ⚠ 要約経由なので名前を出さない）

## 足りない証拠

**load-bearing（無いと書けない・弱くなる）:**

1. **daily-research line の一次ソース** — 著者によれば別セッションで並行実装中（2026-09-21）。手元に見つからなかったのはそのため。実装が終わったら、line の名前、何を追うか（追う対象の定義）、設定ファイルの path か commit を受け取る。執筆は待たずに進め、spine 5 の該当段落だけ仮置きにする。「新設した」と過去形で書くのは実在を確認してから（内容 GO の前に照合。未完なら「新設しているところです」と実態どおりに書く）
2. **「Jev を土台にしたハーネスはまだ無い」の as-of 確認** — 見立ては「今後出れば」の形なので、すでに在るなら節 4 の書き方が変わる。台帳の 357 repo の中に `BillionsBobby/JevRouter`・`kerpopule/hermes-jev-skills` など名前だけ挙がった候補がある。TypeSafe docs の cookbook 一覧も未読。→ 下の `theme-reviewer` に持たせる
3. **「実装した → 約 2 週間で公式が対応して不要になった」の具体例 1〜2 件** — 台帳にも記憶にも特定の事例は無く、推測で埋めない。brief 確定時に著者へ 1 問で聞く。公開索引の候補（該当するかは著者判断）: `obsidian-cli-claude-code-vault-management`／`claude5-rules-official-shift-audit`／`codemap-retirement`／`iphone-claude-code-remote-control`

**あれば足すもの:** Mods の設計プランをどこでやめたか（中止セッション 4698f10b。無ければ著者の言葉「プランを走らせてすぐにやめた」のまま）／cookbook が一覧を動かさない理由に prefix cache を挙げる行（README は書いているが台帳の Claims に無い。私が原文で特定し、無ければ書かない）

**著者にしか出せないもの:** 公開 README 冒頭節の通読（spine 5 の「正直な README」の一次ソース）。

## writing-ecosystem の chain — 回す段

| 段 | 回す／飛ばす | 内容 |
|---|---|---|
| 1 Route and discover | route + **`theme-reviewer` を 1 回** | Zenn に解決済み。`session-theme-mining` 不要。稿が「既存ハーネスへの後付けは部分的／Jev 基盤ハーネスという方向」という外部言説に対する見立てを持つようになったので、`theme-reviewer` の起動条件に当たる（このプランの承認を著者の指示として扱う）。問い一文・台帳 path・TypeSafe 発表記事と docs を渡し、findings と深化の問いだけ受け取る。足りない証拠 2 の as-of 確認もここで |
| 2 Collect, then select | 回す | theme-reviewer の findings を反映した brief を確定形で提示し、足りない証拠 3 の具体例を 1 問で聞く → **著者確認で停止**。足りない証拠 1（並行実装中の line）は待たない |
| 3 Outline and draft | 回す | orchestrator が執筆。節ごとに spine の役割 1 つ、具体物を先。錨は「2026 年 9 月 21 日」1 本、台帳の UTC 時刻は写さない。harness 内部語彙（判断役・shadow-first・RFC 番号）は入れない。事実と見立ては節を分ける。`zenn-format`、末尾に関連リンク 2 行 + Jev×Opus 記事 + 公開 repo |
| 4 Freeze, review, content GO | 回す | 構造凍結後に並列で各 1 回: `editor` ／ `prose-clarity-reviewer`（原稿 path と channel contract だけ渡す）／ `fact-checker`（台帳 path・cookbook URL・公開 repo・skills / hooks docs・型定義・TypeSafe 発表記事を名指し）。`codex-review` は contract の要求どおり凍結時 1 回（採用はカテゴリのすり替え・事実誤り・帰属誤りのみ。見立てへのヘッジ追加要求は採らない）。反映 → Final structural pass → **著者通読・内容 GO で停止** |
| 5 Title | 回す | `headline-craft` → `title-reviewer` → **著者が選択**。50 字以内（必要なら 60）、em dash 連結なし。見立てを事実のように約束するタイトルにしない |
| 6 Acceptance | 回す | `npm run validate`、`npm run evidence -- articles/<slug>.md`（deviations 0）、public-safety scan、`/quality-gate`。PASS を報告して停止 |
| Publish | **回さない** | `publish-article`・`published_at`・commit / push・Dev.to はこのプランの外 |

執筆中にまた中心命題が動いたら、継ぎ足さず停止して brief からやり直すかを著者に 1 問で聞く。

## Verification

- fact-checker: INACCURATE 0・未解決 PARTIALLY 0（対象: C2・D4・D5・D6・D11・D12・D13 の型定義・D14・今朝の記事から引く数値・vendor 引用）
- 見立ての節に、実測と読める断定の数値が入っていない（editor と著者通読で確認）
- `npm run validate` 通過、`npm run evidence` deviations 0
- 本文に個人 path・session id・UTC 時刻・harness 内部語彙が残っていない（grep）
- 本文の self-link は公開 repo へ 1 回、関連リンク 2 行あり
- `git status` で変更が `articles/<slug>.md` 1 ファイルだけ（未 commit）
