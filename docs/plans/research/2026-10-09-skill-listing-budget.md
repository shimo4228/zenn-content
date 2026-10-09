kind: internal
# Claude Code 2.1.295 の skill listing 予算と、超過時の description の落とし方

## Scope searched

- 入力は 3 つだけ。(a) 抜粋 `scratchpad/listing/listing-excerpts.txt`（2.1.295 バイナリの `strings -n 8` から切り出した minify JS。以下「抜粋」）、(b) 台帳 `drafts/article-context_skill-description-pointer_2026-10-09.md`、(c) `/skill-doctor` の前後の生出力（before 07:38 / after 08:33）。
- 抜粋に無い関数は読んでいない。未読: `lj`（env の parse）、`ft`（settings の accessor）、`c5`（caller の追加フィルタ）、`CC`（"name-only" の判定元）、`Oa`（skillUsage の lookup）、`iMt`、`Gf`、`rc`、`xUn`、`gvs`、`Ot` / `We` / `Dt`（model 名の正規化）、`z`（`Bun.stringWidth` の第 2 引数）、`/skill-doctor` 本体と J2t の caller。
- 変数名は minify で意味を持たない。関数の役割は、周囲のコードと文字列から推測した名前で、推測と書いた箇所以外は逐語から直接言えることだけを書く。

## Found

### 1. 予算の式

逐語:

```js
var _Fo=0.01,Q2t=4,kFo=200000;var SFo=1536;
function Awt(){return ft().skillListingMaxDescChars??SFo}
function bFo(){return ft().skillListingBudgetFraction??_Fo}
function ntt(e,n=Q2t){let r=lj(process.env.SLASH_COMMAND_TOOL_CHAR_BUDGET);if(r)return r;let s=bFo(),h=(e??kFo)*n*s;return Math.max(1,Math.floor(h))}
```

- 予算（文字数）= `floor(max(1, window × bytesPerToken × fraction))`。
- fraction の既定は 0.01。settings の `skillListingBudgetFraction` で上書きできる。
- window は引数 `e`。undefined のときだけ 200,000（`kFo`）。
- bytesPerToken は引数 `n`。省略時は 4（`Q2t`）。
- env `SLASH_COMMAND_TOOL_CHAR_BUDGET` が truthy に parse できれば、それが予算そのもの（文字数）になる。window・fraction の計算は飛ばす。`lj` の parse 規則は未読。J2t の `budgetFromEnv` 欄も同じ env を見る。
- 1 token あたり字数（`Eh`）:

```js
rF=new Set(["claude-3-opus","claude-3-sonnet","claude-3-haiku","claude-3-5-sonnet","claude-3-5-haiku","claude-3-7-sonnet","claude-opus-4-0","claude-opus-4-1","claude-opus-4-5","claude-opus-4-6","claude-sonnet-4-0","claude-sonnet-4-5","claude-sonnet-4-6","claude-haiku-4-5"]);
function Eh(e){if(!e)return 4;let n=Dt(e),r=Ot(We(n)).replace(/[._]/g,"-");return rF.has(r)?4:3}
```

  - model 未指定なら 4。
  - 正規化後の model 名が上の 14 個の set にあれば 4、無ければ 3。
  - Opus 5.5（`claude-opus-5-5`）は set に無いので 3。
- caller は `eYt(z, score, X=im(mainLoopModel, Gf()), Eh(mainLoopModel), [...])` を呼ぶ。

台帳 C7 との比較:

- 一致: 式、fraction 0.01、window 不明時 200,000、「4 と 3」の二値。
- 不一致気味: 台帳は「Claude 3〜4.6 の model id は 4」と範囲で書く。実装は 14 個の列挙。`claude-opus-4-7` のような列挙外は 3 になる。
- 台帳に無い: env による予算の直接上書き（`SLASH_COMMAND_TOOL_CHAR_BUDGET`）。`skillListingMaxDescChars` の settings 上書き。

### 2. Opus 5.5 の window と予算

逐語（model catalog）:

```
claude-opus-5-5",family:"opus",display_name:"Opus 5.5", ... context:{window:1e6,native_1m:!0,supports_1m_beta:!0,supports_1m_suffix:!0}
```

- catalog の window は 1e6、`native_1m:true`。
- 予算 = 1,000,000 × 3 × 0.01 = **30,000 文字**。ただし window がそのまま 1e6 で `ntt` に届くなら。
- 実際に届く値は `im()`:

```js
function im(e,n){let r=Jv();if(r!==void 0)return r;if(Nyo(e,n))return m8;return Qv(e,n)}
function Nyo(e,n){return iMt()&&Jv()===void 0&&Qv(e,n)>m8}
function Qv(e,n){if(RUn(e,n))return 1e6;let r=Lyo(e);if(r!==void 0)return xUn(e)??r.believed;if(wE(e))return 1e6;...
function qv(e){let n=Ot(e);return ol(n)?.context?.native_1m===!0||n===XOt}
function V0(){return a.CLAUDE_CODE_DISABLE_1M_CONTEXT}
function wE(e){return!V0()&&Dyo(e)}
```

- 経路は 3 つある。
  - (i) `Jv()` が値を返す。`DISABLE_COMPACT` が真かつ `CLAUDE_CODE_MAX_CONTEXT_TOKENS` > 0 のとき、その値が window になる。
  - (ii) `Nyo` が真なら `m8` = 200,000 に固定される。条件は `iMt()` が真、(i) が無効、かつ `Qv` が 200,000 超。`iMt` は未読。
  - (iii) `Qv`。`native_1m` の model は、`CLAUDE_CODE_DISABLE_1M_CONTEXT` が無ければ `wE` が真になり、1e6 を返す経路がある。
- (iii) のうち `Lyo` / `rc` / `xUn` を通る分岐は未読。`Qv` の末尾も抜粋で切れている。
- 判定: Opus 5.5 で **30,000 になりうることは実装で確認できた**（catalog 1e6 + native_1m + `Eh`=3）。ただし台帳 C9「1M window か」は**抜粋だけでは確定できない**。
  - `iMt()` が真だと 200,000 に落ち、予算は 200,000 × 3 × 0.01 = 6,000 になる。
  - `CLAUDE_CODE_DISABLE_1M_CONTEXT` を設定していても、同様に 200,000 側へ落ちうる（`Lyo` が believed 200,000 を返す分岐。推測）。
  - 確定させる方法: debug log の "Skill listing over budget: N skills, M chars > B budget" の B を見る。または settings / env を確かめ、`iMt` を読む。
- 間接証拠（推測）: 付録 A に書いた。doctor 出力の合計が before / after とも約 7.1〜7.3k（doctor の token 推定）で飽和していて、4 字/token なら約 29k 字。30,000 と矛盾しない。ただし doctor の token 推定式は未読なので、証拠としては弱い。

### 3. listing に載る条件

caller（逐語）:

```js
s=$he().filter((_e)=>!_e.disableModelInvocation&&!c5(_e)), h=sV(e.getMcp().commands), ...
let b=Fne(n,h), w=xzt(r.length>0?vae(Ui([...b,...s,...r],"name")):Ui([...b,...s],"name"));
if(e.agentId===void 0)w=Ane(w,uG());
let M=UPr(y,e.agentId,w); ... let{newSkills:z,isInitial:V}=M;
```

- `disableModelInvocation` が真の skill は、listing に渡す前に除かれる。
- もう 1 つ `c5(_e)` のフィルタがある（未読）。
- name-only は、`eYt` 内で `CC(Te)==="name-only"` で判定する。`- ${name}` だけの行を作り、full も nameOnly も同じ文字列にする。
  - `CC` が `skillOverrides` を読むかは抜粋では見えない。台帳の「skillOverrides: name-only」は設定名として未確認。`CC` を読むこと。
  - 予算超過時、name-only は「予算を取り合う対象外」（`z` に入る）。常に名前だけで、description は付かない。
- 渡されるのは `newSkills`（`UPr` の返り）。ログ文言は `Sending ${z.length} skills via attachment (${V?"initial":"dynamic"})`。
  - 推測: 初回（initial）と、あとから増えた skill（dynamic）で、それぞれ別に `eYt` が呼ばれ、予算は呼び出しごとに丸ごと使えるように読める。`UPr` を読んでいないので推測。
- 台帳との比較: C12 / C10 の「grill-me と review-to-lint を user-invoked に移す」は、フィルタ `!disableModelInvocation` と整合する。before の context は両方 ~130、after は両方 `-`（付録 B）。

### 4. 幅の数え方と 1 行の形

- 幅: `function ae(e){return Bun.stringWidth(e,z)}`。第 2 引数 `z` は未読（`ambiguousIsNarrow` などの option かもしれない。推測）。
- listing の 1 行（`eYt`、逐語）:

```js
let Ce=`- ${Rwt(Te,h)}`;return{cmd:Te,nameOnly:Ce,full:`${Ce}: ${vFo(Te)}`}
```

  - 形は `- name: description`。重複名のときは `Rwt` が `name (basename)` にすることがある。行は `\n` で連結し、予算の合計に `(w.length-1)` を足す。
- 本文は `Twt`:

```js
function Twt(e){return e.whenToUse?`${e.description} - ${e.whenToUse}`:e.description}
```

  - `whenToUse` があれば `description - whenToUse` になる。
- 1 本の上限: `skillListingMaxDescChars`（既定 1536）。

```js
function vFo(e){let n=Twt(e),r=Awt();return n.length>r?n.slice(0,r-1)+"…":n}
```

  - 上限は `.length`（UTF-16 の code unit 数）で切る。`stringWidth` ではない。超えたら `r-1` 字 + `…`。
  - 上限の判定は幅、予算の判定は `ae()` の幅で、物差しが違う。
- 台帳との比較: 「全角 2」は `Bun.stringWidth` の一般的な挙動で、抜粋が示すのは `ae` が `Bun.stringWidth` であることだけ。全角の実測は台帳の lint（`east_asian_width` による近似）が根拠で、`z` の option 次第でずれる余地がある。台帳 C8 の「幅は Bun.stringWidth」は一致。1536 は一致。

### 5. 予算超過時

`eYt` の流れ（逐語から整理）:

1. 全 entry の幅合計 `M = Σ ae(full) + (n-1)` が予算 `y` 以下なら、全部 full で返す。
2. 超えたら `t("Skill listing over budget: ${e.length} skills, ${M} chars > ${y} budget — descriptions will be truncated. Run /skills to disable some, or raise skillListingBudgetFraction in settings.", {level:"warn"})`。
3. 固定集合 `z` = name-only の index + `type==="prompt" && source==="bundled"` の skill。
4. `V` = `z` に入らない skill。`V` が空なら全部 full で返す。
5. 固定費 `_e` = `Σ(z に入る ? ae(full) : ae(nameOnly)) + (n-1)`。残り `ke = y - _e`。
6. `V.sort((Te,Re)=>n(e[Re])-n(e[Te]))`: 使用スコアの降順。
7. 順に見て `Re = ae(full) - ae(nameOnly)`。`Re <= ke` なら採用して `ke -= Re`。収まらなければ**飛ばして次へ進む**（打ち切らない）。
8. 出力は、`z` に入るか採用された skill は full、それ以外は nameOnly。

- 常に description 付きで残る: bundled のみ。name-only は常に名前だけ。
- description は**部分的に切られず、全部付くか名前だけか**の二択。ただし 1 本が 1536 字を超える分だけは、上限で先に切られる（`vFo`）。警告文の "truncated" は、実装の挙動（all-or-nothing）より緩い言い方。
- 使用スコア（逐語）:

```js
function xwt(e){let n=Oa(ce().skillUsage??{},e);if(!n)return 0;let r=(Date.now()-n.lastUsedAt)/86400000,s=Math.pow(0.5,r/7);return n.usageCount*Math.max(s,0.1)}
```

  - 使用記録が無ければ 0。あれば `usageCount × max(0.5^(経過日/7), 0.1)`。半減期 7 日、下限 0.1。
  - 台帳 C8 の式と一致。`Oa` の lookup（名前の別名の扱い）は未読。
  - caller は `(_e)=>xwt(_e.name)` を渡す。
- 同点（スコア 0 が多数）の順序: `Array.prototype.sort` は現行の JS エンジンで安定なので、入力順のまま（推測。エンジン仕様に依拠）。入力順は `Ui([...],"name")` の出力で、未読。
- 「長い description が入らず、後ろの短いものが先に入る」: **成り立つ**。7 の `else` は `continue` 相当で、後続の安い skill は残り予算に収まれば採用される。「後ろ」は入力順でなく**スコア順で後ろ**。
  - 使われていない（スコア 0 の）skill のうち、description が長いものから順に落ちるわけではない。「その時点の残り予算に収まるか」だけで決まる。同点の中では入力順が先のものほど先に判定される。
- 台帳 C8 との比較: 「bundled と name-only 以外を使用スコアで並べ、残り予算に収まるものにだけ description を付け、残りは名前だけ」は、**一致**。台帳の「技術的発見」節の「使われない skill は名前だけ → 呼ばれない → スコア 0 のまま」のうち、実装が示すのは前半だけ。
  - 名前だけの skill も、listing に名前が出る限り呼べる。「呼ばれない」は実装でなく台帳の推論。
  - スコア 0 でも、予算に余りがあれば description は付く（after の出力で多数が付いている）。

### 6. J2t（/skill-doctor の集計）と eYt（builder）

同じ規則の部分:

- 予算は `ntt(r, h)`（env 上書きも `budgetFromEnv` として見る）。
- 固定集合: `wFo(Ce) = type==="prompt" && source==="bundled"`、または引数 `s` の name 集合（eYt の name-only と対応）。
- 並べ替え: `ke.sort((Ce,$e)=>n($e.cmd)-n(Ce.cmd))`（使用スコア降順）、`$e = entryLen - (nameLength+2)` が `Te` 以下なら採用、収まらなければ `Re` に積んで続行。
- 1 本の上限は `Awt()`（`Math.min(He.length, w)`）、`Twt` で `whenToUse` を連結。

違う部分:

- **J2t は `.length`、eYt は `Bun.stringWidth`**。J2t の `entryLen = $e + 4 + ze`（`$e` は `Rwt(...).length`）で、全角は 1 と数える。eYt は `ae()`（幅）で数えるため、全角は 2。日本語の description が多いほど、J2t は eYt より小さく見積もる。結果として J2t が「収まる」と判定しても、実際の builder は収まらない場合がある。
- J2t は `rawLen`（上限で切る前の長さ）の降順で `cappedSkills`（上限超過の一覧）を返す。eYt にはこの集計が無い。
- J2t は `V.length===0` の早期 return を持たない（結果は同じになるはず）。
- J2t の window `r` と bytesPerToken `h` は caller 次第（抜粋に caller 無し）。eYt の caller は `im(mainLoopModel, Gf())` と `Eh(mainLoopModel)`。doctor が同じ値を渡しているかは**未確認**。doctor の `claude -p` はその session の model で走るので同じと推測するが、確認していない。
- eYt の入力は `newSkills`（初回 / dynamic の差分）、J2t は skill 全体を受けると推測（caller 未読）。
- 「J2t は eYt と同じ規則」と書けるのは、選別の骨格（固定集合 → スコア降順 → 収まれば採用、収まらなければ飛ばす）まで。数え方（長さ vs 幅）は別。

### 7. /skill-doctor の前後の生出力

集計（生出力を直接数えた。台帳 C10 / C11 と一致）:

| | description 付き（`~N`） | 名前だけの候補（`< 20`） | listing 外（`-`） | 計 |
|---|---|---|---|---|
| before | 45 | 29 | 20 | 94 |
| after | 66 | 6 | 22 | 94 |

- before の `< 20` 29 本の内訳: 自前 4（jev-judgment-design、loop-design-check、mono-color、repair-discipline）、hookify 2（help / list）、pr-review-toolkit 1、codex 5、session-report 1、codex の skill 3 本（cli-runtime など）は上の codex 5 に含めず別集計せず、cowork 2、claude.ai 同期 14（anthropic-skills:* の 13 + learn）。合計 29。
- after の `< 20` 6 本: hookify:help、hookify:list、anthropic-skills:{pptx, skill-creator, xlsx, learn}。
- after の `-` 22 本には grill-me と review-to-lint が加わる（before は ~130 / ~130）。

5 の規則で説明できる点:

- before の自前 4 本は、使用 0・description が 1,000 字級（台帳 C13 の表）で、スコア 0 の末尾で残り予算に収まらなかった、と読める。同じく使用 0 の claude.ai 同期の長い description も名前だけ。
- 使用実績のある skill が全部 description 付きになっているのも整合する（学習済みの上位から先に入る）。
- after で自前 0 本になり、description 付きが 45 → 66 に増えたのは、自前の description 縮小で空いた予算が、スコア 0 の plugin / claude.ai 同期の description に回った、と読める。after のスコア 0 の description 付きの合計は、before より増えている。
- 予算飽和の目安（推測）: doctor の context 列の合計は before で約 7.1k（description 付き 45 本）、after で約 7.3k（66 本）。縮めた分が他の skill に回って、合計がほぼ同じ水準で止まっているように見える。予算が固定で、そこまで埋めている読みと整合する。doctor の token 推定式は未読なので、字数への換算は付録 A の推測。

5 の規則で説明できない / 台帳の読みに疑いがある点:

- **`anthropic-skills:learn`（83 回、最終使用 210 日前）が before / after とも `< 20`**。スコア = 83 × max(0.5^30, 0.1) = 8.3 で、same 表の `refactor-clean`（40 回 / 56 日 → 4.0）、`wiki-query`（14 回 / 31 日）より高い。5 の規則なら、スコア降順の前の方で判定されるので、残り予算が十分あるうちに採用されるはず。にもかかわらず名前だけ（または極短）。可能性は 3 つ: (a) `Oa` の使用記録の key が `anthropic-skills:learn` と一致せずスコア 0 になっている、(b) `CC` で name-only 扱い（skillOverrides など）、(c) description が元々極短で `< 20` に入る。どれも抜粋では確定できない。
- **`hookify:help` / `hookify:list` が「名前だけ」とは言いにくい**。この 2 本は before / after とも `< 20` で変化が無い。スコア 0 の中で入力順が早く（claude.ai 同期や codex より前）、同じ表で後ろの `~300` 級の description が after で採用されている。もし 2 本が名前だけなら、より後ろで大きな description が収まったことと矛盾する（飛ばしてよい規則でも、小さく早い順のものが落ちる理由が無い）。説明として自然なのは、**description が元々極短（token 推定が `< 20` の帯に入る）**こと。つまり `< 20` は「名前だけ」でなく「20 token 未満」の帯で、短い description も含みうる。台帳 C11「名前だけ 6（hookify 2・claude.ai 同期 4）」は、doctor の列の意味が確認できていないので、**名前だけの数としては過大の可能性**がある。doctor の列の定義（名前だけをどう表示するか）は未読。
- 同様に、before の `< 20` 29 本が全部「名前だけ」とは、この出力だけでは断言できない（hookify:help / list 2 本は短い description の可能性）。台帳 C10 の「名前だけ 29」は 27〜29 の幅で読むのが安全。
- 「使われていない自前 skill が名前だけになる」: before の自前 4 本は規則で説明できる（使用 0・長い）。ただし、同じ使用 0 でも `hookify:configure`（~20）のように、短ければ description が付く。「使われていない」だけが理由ではなく、「使用 0 かつ残り予算に収まらない長さ」が条件。after は自前 4 本とも description が付いた（~90 / ~100 / ~250 / ~80）。

### 付録 A. doctor の合計と予算の関係（推測）

- after の context 列（description 付き 66 本）を合計すると約 7,290。before の description 付き 45 本は約 7,140。
- 4 字/token なら約 29,000 字、3 字/token なら約 21,900 字。予算 30,000 と整合するのは 4 字/token の側。doctor が token をどう推定するか（J2t の戻り値 `bytesPerToken` を使うか）は未読。
- よって「30,000 で飽和している」は、**doctor の token 推定が 4 字/token のとき**に成り立つ見立てで、確定ではない。

### 付録 B. 台帳の行との対応

| 台帳 | 判定 | 根拠 |
|---|---|---|
| C5 fraction 0.01 / MaxDesc 1536 | 一致 | `_Fo=0.01`、`SFo=1536`。settings で上書き可 |
| C6 警告文 | 一致 | 逐語（`level:"warn"`）。"truncated" と言いつつ実装は all-or-nothing |
| C7 予算式 | 概ね一致。範囲表現は不一致 | `Eh` は列挙 14 個。env 上書きは台帳に無い |
| C8 順位付け | 一致（skillOverrides の出所のみ未確認） | `xwt`、`eYt` の fill ループ |
| C9 1M window | 未確定（30,000 になる経路は確認、6,000 になる経路も残る） | catalog 1e6 + native_1m、`iMt` と `rc` が未読 |
| 「長い物が入らず後ろの短い物が先に入る」 | 成り立つ（後ろ = スコア順） | fill ループが `else` で続行 |
| C10 / C11 の集計数 | 数え直して一致 | 94 = 29 + 20 + 45、94 = 22 + 6 + 66 |
| C10 / C11 の「名前だけ」の解釈 | 要注意 | `< 20` の列の定義が未確認。hookify 2 本と learn が説明しにくい |
| 「幅は全角 2」 | 半分 | eYt は幅、J2t は `.length`。`z` option 未読 |

## Contradictions

- 台帳 C11（after の名前だけ 6 = hookify 2 + claude.ai 4）と、5 の規則との食い違い。hookify:help / list は、規則どおりなら先に採用されるはずで、名前だけとは読みにくい。`< 20` が「短い description」を含む帯である可能性が高い。根拠の強さ: コード（逐語）+ 出力の並び（直接観察）。ただし doctor の列の定義は未読なので、推論どまり。
- 台帳 C8 / 技術的発見の「使われない skill は名前だけ → 呼ばれない → スコア 0 で固定」は、実装の前半（スコア 0 は後回し）しか示さない。after で、使用 0 の skill が大量に description 付きになっているので、固定されてはいない。残り予算次第。
- `anthropic-skills:learn`: 規則から予測される位置（上位）と、観測（名前だけまたは極短）が合わない。原因は未特定。
- doctor（J2t）が `.length`、builder（eYt）が幅。同じ skill 群でも、日本語の description が多いほど doctor は eYt より緩く見える。doctor の「description 付き」の数が、実際の model 向け listing と一致するかは保証されない。

## Still unknown

- C9: Opus 5.5 のセッションで実際に届く window（`iMt`、`Gf`、`rc`、`xUn`、`gvs` が未読）。debug log の "over budget ... > B budget" の B で確かめられる。
- `Bun.stringWidth(e, z)` の `z` の中身（全角 2 / ambiguous の扱い）。
- `CC()` の元（`skillOverrides: name-only` かどうか）と、`c5()` のフィルタ。
- `/skill-doctor` 本体: context 列の定義（`< 20` の意味、token 推定式）、J2t の caller が渡す window と bytesPerToken。
- `Oa` の使用記録の key（`anthropic-skills:learn` のスコア）。
- 初回 / dynamic の `newSkills` が、実際に予算を何回に分けて使うか（`UPr`）。
- 同点の入力順（`Ui` の出力順）。
- 2.1.286（台帳の作業セッション）と 2.1.295（読んだ本体）で規則が同じか。
