---
name: writing-ecosystem
description: 人間向け記事・エッセイ・ブログポスト・ニュースレターの唯一の執筆 orchestrator。project の publication channel contract を読み、中心命題 1 つの editorial brief、因果線、証拠の選択と除外、構成、執筆、review panel、著者の内容 GO、title-reviewer、quality-gate までを統括する。Use when — 「この記事を書いて」「このテーマでエッセイにして」「原稿の論点を一つに絞って構造改稿して」のような新規執筆・全体改稿・全文の別 channel 展開。NOT for — 一文や段落だけの翻訳（→ prose-translation）、title だけ（→ headline-craft / title-reviewer）、SNS 下書き（→ x-draft）、公開 thread 返信（→ public-comment）、AI 向け docs、README、paper、媒体固有の公開操作。
compatibility: Designed for Claude Code (or similar agent products). Orchestrates the review agents under <project>/.claude/agents/.
user-invocable: true
origin: shimo4228
---

# writing-ecosystem — 人間向け執筆の手順

人間読者向けコンテンツ（記事・エッセイ・ブログポスト・ニュースレター）を書く手順と、関わる skill・agent の
役割分担の正本。

**書き始める前に `~/MyAI_Lab/zenn-content/.claude/rules/writing-principles.md`（執筆の背骨: 著者の方針と原理 6 本）を読む。**
この repo で作業していれば rules として常駐しているが、別 repo からの `--add-dir` や他 skill からの参照では載っていない。
判断は背骨から導き、本 skill は手順・役割・受け入れの規律だけを持つ。

## Scope

**人間 primary のコンテンツのみ扱う**。AI-facing ドキュメント（`llms.txt` / `llms-full.txt` / FAQ ページ等）には `llms-txt-writer` skill を使う。audience 判定と役割分担は `~/.claude/skills/llms-txt-writer/SKILL.md` の「Audience Separation: Human vs AI」節を読む。

媒体名・語尾・frontmatter・文字数・reviewer 構成・公開 command は channel contract が持つ。記事全体を
扱う task では最初に
`<project>/.claude/rules/*.md` の **publication channel contract** を読み、対象 path を 1 channel
へ解決する。contract が無い、または複数 channel に一致する場合は推測せず停止する。

執筆時の規範は、背骨の rule・local contract・本 skill の手順だけである。ADR と memory は経緯と事例の記録で、
規範は背骨に一本化してある。過去セッションを素材にするときは `session-theme-mining` が選んだ一次
pointer、`collect-context` が作る evidence dossier の順に限定して受け取る。

---

## Ecosystem Map

執筆関連コンポーネントの役割分担。どの phase で誰が何を持つか。

| フェーズ | コンポーネント | 軸 | トリガー |
|---------|---------------|-----|----------|
| **Theme discovery** | `session-theme-mining` skill | Claude / Codex 履歴横断から 0〜3 件の同格な問いを発見し、著者の選択で止まる | 執筆スコープがまだ決まっていないとき |
| **Theme review** | `theme-reviewer` agent | 選択済みの問いへ findings と深化の問いを返す。合否は出さない | 外部言説に対する新規性を主張する稿で、著者が指示したとき |
| **Pre-write** | `collect-context` skill | 素材収集と証拠台帳（Claims Register / 一次・⚠未検証の tier）。編集判断はしない | 執筆前に素材を集めるとき |
| **Write** | 本 skill「editorial brief と執筆フロー」 | 中心命題・因果線・証拠選択・構成・執筆 | 初稿・改稿 |
| **Title generation** | `headline-craft` skill | 「開かせる一行」の候補生成 | 著者の内容 GO 後 |
| **Title review** | `title-reviewer` agent | 本文との契約を fresh context で点検し findings を返す | headline-craft の後、quality-gate の前 |
| **Review: 品質** | `editor` agent | 議論の動き・説明の質・AI slop・記事内用語（code / path の照合は `fact-checker`） | 実用チャンネルのレビュー時 |
| **Review: 論理** | `essay-reviewer` agent | エッセイの論理構成・過積載・トーン | エッセイチャンネルのレビュー時 |
| **Review: 初見明瞭性（cross-model）** | Codex plugin の `codex:codex-rescue` agent（読み取り専用、checklist は `prose-clarity-reviewer` agent） | 第一画面・中心命題・内部文脈依存・カテゴリのすり替え | 構造凍結後の review panel 時 |
| **Review: 事実** | `fact-checker` agent | 事実主張の Web 検証と、code / path / 出力のローカル照合 | 公開前検証時 |
| **Acceptance** | `quality-gate` skill | local contract の reviewer verdict と機械検査を集約 | 公開直前 |
| **Publish** | project-local publishing skill | platform API / UI / schedule / corpus 更新 | 著者 GO 後 |
| **Overlay** | `<project>/.claude/rules/*.md` | チャンネル固有の事実・配線 | プロジェクト内作業時のみ |

flow の外へ route する先は末尾の Related。

## Canonical workflow

### 1. Route and discover

local contract から出力 channel と読者を決める。テーマ未選択なら `session-theme-mining` が
0〜3 件の同格候補を出し、著者の選択で止まる。選択済みの問いは §2 の中心命題の対話へ進む。
`theme-reviewer` は、稿が外部言説に対する新規性を主張し、著者が指示したときに起動する
（findings と深化の問いだけを返す）。経験の報告では命題が外部言説との差分に依存しないので、
起動しても論点が増えるだけになる。テーマ候補は同格のまま著者に渡し、選ぶのは著者である。

### 2. Collect, then select

過去セッションや複数 repo の記録を素材にするときは `collect-context` で evidence dossier を作る（`fact-checker` に渡す台帳になる）。dossier は lookup material であり、本文へ
全部入れる coverage checklist ではない。

**中心命題は、書く前に著者と話して決める。** brief を書く前に、orchestrator は著者に、何に
引っかかっているか・何を問いたいかを聞く。著者の答えを命題の形で言い返し、著者が違うと言えば
直す。session-theme-mining で選ばれた問いや dossier の Claims は、この対話の材料であって答えでは
ない。合意した著者の言葉は brief の Author's words に原文のまま置く。

構成前に次の **editorial brief** を `docs/plans/<slug>.md` に書いて提示し、著者確認で止まる（reviewer の dispatch prompt に
この path を渡す）。

```markdown
Reader: <channel contract の読者と、中心命題の対話で著者が言った「誰に向けて書くか」の原文 1 行>
Channel: <local contract の channel>
Author's words: <中心命題の対話で著者が言った原文。要約・言い換えをしない>
Central thesis: <Author's words を、この原稿が成立させる命題一文にしたもの。必ず一つ。確度は Author's words のまま（背骨 1）>
Entry bridge: <読者の出発点から、なぜ中心命題を考える意味があるかが伝わる場面・観察・問いを1〜2文で>
Figure plan: <内容 GO の後に埋める。節 → 形（対比 / 流れ / 階層 / 2 軸 / 並列）→ 図の有無。並列は list のまま>
Causal spine: <観察 / 問題 → 緊張 → 機序 → 著者の判断（決めたこと・決めなかったこと）>
Selected evidence:
- <evidence id>: <因果線での役割>
Out of scope:
- <面白いがこの命題を進めない論点。本文に載る未検証の推論は、ここへ落とす前に著者へ聞く（背骨 4）>
```

読者が何を知っているかを確かめるのは著者の通読である。Entry bridge は既存の疑問への接続と、新しい疑問が
生まれる入口の両方を含む。著者の体験も、その問いの意味を読者へ伝えるなら入口になる。

実用 how-to では central thesis を「読者が得る一つの成果または判断則」としてよい。

### 3. Outline and draft

導入は Entry bridge の場面・観察・問いで開く。執筆理由や背景は、読者を場面に置いた後に、その場面が
要る分だけ書く。読者が共有していない前提は本文で補う。各 load-bearing section に causal spine 上の役割を
一つだけ割り当て、採用 evidence を紐付ける。並列の agenda を節として足さない。語・節の切れ目・時間・
証拠の置き方は背骨の 2・5・6 に従う。執筆中に別の中心命題が現れたら混ぜずに停止し、editorial brief を
再確認する（背骨 4）。out-of-scope は本文から外す — `details` に押し込むと、読者には本文の一部として届く。

翻訳は `prose-translation` を使い、承認済み central thesis、causal spine、selected evidence、
out-of-scope を保持する。翻訳先の local contract へ route し直す。

### 4. Freeze, review, and content GO

本文の構造を凍結したら、local contract の channel reviewer、`fact-checker`、初見の読みを本文へ実行する。
reviewer が見るのは本文の内側で判定できること（事実・構造・register・分類の軸・後方参照・矛盾）で、
読者が何をすでに持っているか（何の話か分かるか）は著者の通読だけが持つ。
初見の読みは Claude と別系統のモデルが担う — 同じ系統の reviewer は著者（orchestrator）と同じ所を
読み飛ばす。Codex plugin（openai/codex-plugin-cc）の `codex:codex-rescue` agent を background で起動し、
prompt の先頭に「Read-only review. Do not edit files (no --write).」と書く（書かないと rescue は書き込み可で走る）。
続けて「`.claude/agents/prose-clarity-reviewer.md` の checklist を読み、channel contract の読者として原稿を 1 回だけ読み、
checklist の形式で報告する。加えて本文から弁護できるカテゴリのすり替え・事実の矛盾・帰属の誤りを挙げる。
ヘッジの追加は求めない。日本語で書く」と、checklist・contract・原稿の path だけを渡す。central thesis・
causal spine・成功基準を渡すと、reviewer は答えを持って読み、「何をしたのか分からない」を検出できなくなる。
これが panel の cross-model review を兼ねる（経緯は ADR-0013）。中継役の agent が返ってこないときは、Codex 側の結果を
`node ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs status` → `result <job-id>` で取り出す。
plugin が使えないときは Claude の
`prose-clarity-reviewer` agent で代替し、理由を処分記録に残す。channel reviewer の dispatch prompt には、承認済み brief の path と、AI が本文を生成したかを書く（Author's words と
の確度照合と、開示の要否に使う）。editor と essay-reviewer の両方を
回すのは contract が要求する場合だけ。`fact-checker` の dispatch prompt には証拠台帳と一次資料の
path（repo、出力ファイル）を名指しで渡す — code / path / 出力の照合はこの agent が持ち、channel
reviewer は判断だけを持つ。

採用した指摘は orchestrator が反映し（回数と戻り条件は下の処分規律）、out-of-scope が本文へ戻っていないことを
確認してから著者が本文を通読し、**内容 GO** を出す。内容が確定するのはこの GO であり、タイトル作業はその後に置く。

図は内容 GO の後に起こす（brief の Figure plan をここで埋める。形の選び方と手順は project の format skill — Zenn は `zenn-format` の Figures。
図の規約を持たない channel では Figure plan は「なし」と書く）。
図の文字と本文の差分だけを `fact-checker` に回し、図を足した稿は著者がもう一度通読する。図と
その直後の 1 文の追加は構造変更ではないので、この通読は確認であり、内容 GO と title-reviewer は
やり直さない。

#### 指摘の処分規律

- **CRITICAL の意味**: 読者への約束・事実・中心命題を壊すもののみ。規約と運用実態の衝突は
  CRITICAL でなく「裁定要求」として報告し、裁定者は著者
- **裁定の書き戻し**: 裁定結果は memory でなく channel contract に書く（fresh-context reviewer に
  届く唯一の層）。著者が同種指摘を 2 回却下したら、その場で contract の該当行を更新または削除する
- **著者の通読指摘は種類への指摘**: 1 箇所を指摘されたら、同じ型を全文から探して直す
- **panel の回数**: channel reviewer・初見の読み（Codex）は構造凍結時に各 1 回。レビュー修正を確かめるのは著者の通読で、reviewer ではない。修正を reviewer に読み
  直させると、読むたびに新しい指摘が生まれて終わらず、限定句と段落分割が積もって本文が
  防御的になる
- **処分記録**: orchestrator は指摘ごとに採用・不採用と理由を 1 行ずつ残し、`quality-gate` へ
  凍結稿への report と並べて渡す。受け入れの証跡は「凍結稿への report + 処分記録 + 著者の
  内容 GO」で、反映後の稿への reviewer verdict は要らない
- **brief へ戻った round**: reviewer を走らせ直すのは、修正が central thesis・causal spine・
  主要節を変えて brief へ戻ったときだけ。その round は CRITICAL と変更部分の regression のみを
  blocking とし、新規 MEDIUM/MINOR は集計のみ
- **`fact-checker` の回数**: 著者の通読の前に 1 回。以後は、本文に新しい引用・数値・外部ソースが
  入ったときだけ、その差分を対象に回す。全文の再照合は構造が動くたびに同じ主張を払い直すことになる
- **cross-model 指摘の採用**: 初見の読みの findings と、カテゴリのすり替え・事実誤り・帰属の誤りを
  採用候補にし、ヘッジや限定句の追加を求める指摘は採用しない。全採用は一文ずつ正しくして通読を重くする。
  既定の裁定:

  | finding の型 | 既定 |
  |---|---|
  | ヘッジ済み思弁への「根拠不足」 | 不採用（発見調は仮説明示つきの思弁を許す） |
  | カテゴリのすり替え（実行↔動機、順番づけ↔確率の近さ 等） | 常に採用検討 |
  | 概念・歴史的接続の過大主張、帰属の誤り | 常に採用検討 |
  | 文体規約違反（register 混在・意図外の常体） | 採用（意図的ブレイクと照合の上で） |
  | 構造再設計の提案 | 著者判断へ昇格 |

### 5. Title

内容 GO 済みの本文に対して `headline-craft` で候補を広く作り、`title-reviewer` の findings を見て
著者がタイトルを選ぶ。`headline-craft` には本文のほかに、brief の中心命題と Author's words、
下の Title Conventions を渡す。候補を落とす条件は Title Conventions の「著者が決めること」に従う。
タイトル選択後に本文の構造を変えたら、内容 GO と title-reviewer を
やり直す。表現修正だけなら再実行しない。

### 6. Acceptance

`quality-gate` が local contract の証跡を集約して PASS を出した後、著者が公開 GO を判断する。
公開操作は contract が指す project-local publishing skill に渡す。

---

## Citation & Sources Workflow（出典をエッセイに入れる）

fact-check で確定した一次資料を、**本文の出典セクションに編入する**のがエッセイ公開前の標準ステップ。

### 所有と分離

- **embedding はこのワークフローが所有する**。`fact-checker` は report-only（記事を編集しない / author-reviewer 分離）のままで、検証済みソースを「出典セクションに落とせる形」で返すだけ。本文への編入は著者 / orchestrator が行う。
- `fact-checker` の出力（verdict が ✅ / ⚠️ のソース URL 群）が canonical input。

### 手順

1. fact-check 通過後、verdict が ✅ ACCURATE / ⚠️ PARTIALLY のソースを集める（❌ / ❓ のソースは載せない）。
2. ブロックの構成規則（テーマ別グループ化・重複 URL 排除・一次資料優先）は **`fact-checker` agent が持つ**（report を出す側が実値を持つ）。ここでは再掲しない。
3. 本文末に出典セクションを作る。
4. 本文で著者自身の既発表（DOI / repo / 論文）に言及していれば、それも出典に含める。

### 媒体別ポリシー

| 媒体 | 出典の置き方 |
|---|---|
| エッセイチャンネル | 末尾に `## 出典・参考文献`（ブロック構成は `fact-checker` の出力に従う） |
| 実用チャンネルの記事 / tutorial | 本文中の inline link を基本に、必要なら末尾に補助的な References |
| 学術 paper | 本ワークフローではなく `citation-formatter` agent（in-text ↔ reference の 1:1・format・DOI 検証） |

引用ごとに要る検証の深さ（帰属・中身・評価）は [`references/publication-procedures.md`](references/publication-procedures.md) を読む。

### 翻訳記事の出典

`prose-translation` で訳した記事は、原文の出典セクションを引き継ぐ。**URL / DOI は保持**し、description のみ英訳する。

---

## Genre shapes

どの shape も central thesis と causal spine に従属する。複数論点を統合できるのは、同じ中心命題の因果線で
上下関係を持つ場合だけである。

| genre | 構成 |
|---|---|
| 実用記事 / チュートリアル | Entry bridge の直後に、読者が何を得るかを言う。主要節ごとにコードか端末出力を置く。締めは因果線の著者の判断で終える（背骨 3） |
| エッセイ / オピニオン | 下の 4 段構成。1 節 1 論点、意見を支える実例を置く |
| ニュースレター | 最初の 1 画面を強くする。近況の羅列にせず洞察を混ぜる。節ラベルで走査可能にする |

### エッセイの 4 段構成（Hero's Journey 型）

essay の既定構成（出典: Kaguura 2026、ADR-0007）:

1. **Calm Story** — Entry bridge の場面で開き、低認知負荷で読者を著者の声に慣れさせる
2. **Plunge（緊張）** — 読者が乗ったところで、大きな問題・不都合な真実・パラドックスを提示する
3. **Solution** — フレームワーク・中核ルールを提示して読者を引き上げる
4. **Higher Ground** — 開始時より高い位置で終える。未解決のまま残すこと自体が Higher Ground になりうる

### Environment-dependent implementation handoff

local path・既存設定・認証・権限に依存する変更を読者へ渡す記事では、人間向け本文だけで問題・判断則・
採用境界を完結させた後に、読者の coding agent へ渡す standalone prompt を置ける。prompt は read-only で
環境を調査して実装 plan を返し、人間の承認前に編集・install・commit・publish しない。

### Voice

register と語尾の実値は channel contract が持つ。contract が無い task では推測しない。AI slop と voice
drift の兆候を見つけたときだけ [`references/style-diagnostics.md`](references/style-diagnostics.md) を読む。
AI-mediated writing の開示を contract が求める channel では [`references/publication-procedures.md`](references/publication-procedures.md) の要素で書く。

---

## Title Conventions

### 目的

一覧で題を見た読者が、何についての記事かが分かり、著者の問いに引っかかること。

### 守ること

- **誠実さ**: 本文が回収しない約束をしない。数字は本文の実測値・件数だけを使う — 判定は「その数字は記事の中身の証拠か、器の飾りか」
- **検索語**: 記事の対象であるツール名・固有名詞を題に残す
- **channel 制約**: 字数と記法は project の channel contract が正本で、ここには書かない

### 著者の題の形

第一の形は**前提を問う**。著者や読者が当然としている前提を疑う問いを、著者の言葉のまま題に置く。
問いは、読者も自分のこととして持てるものにする。
素材は editorial brief の Author's words、本文が引用する著者の発言、本文の節見出し。

形を示す例（著者の既存の題。語を写すためのものではない）:

- Claude Codeに「お前自身がLLMだろ」と言った日
- 自律エージェントにオーケストレーション層は本当に必要か
- 業務の中にいる人は、それを「ドメイン」とは呼ばない

成り立つ条件は、その問いに本文が答えているか、答えられなかったことを本文が正直に書いていること。

### 著者が決めること

誠実さ以外の理由では候補を落とさない。語調と文体の印は `title-reviewer` が付け、採否は著者が決める。

*この節は**規範**の正本。候補生成は `headline-craft`、凍結稿との契約点検は `title-reviewer` が
正本。生成と点検は別の context で行う。`title-reviewer` の対抗案と直しは比較のための参照で、
採るなら著者がその場で選ぶ。*

---

## How to Extend (Project Overlay)

プラットフォーム固有の値（文字数上限、タグ仕様、組織固有の禁止表現など）は project の
`.claude/rules/<publishing-channels>.md` に置く。contract は背骨と本 skill の手順を再掲しない。

## Related（この flow の外へ route する先）

- `prose-translation` skill — 日英双方向の voice 保持翻訳。一文・一段落の翻訳はこちらだけで足りる
- `x-draft` skill — X 投稿の下書き（Voice は SNS register への意図的分岐）
- `public-comment` skill — 公開 thread への返信
- `readme-writer` skill — README / repo トップページ（Voice は ですます への意図的分岐）
- `llms-txt-writer` skill — AI 向けドキュメント（llms.txt / FAQ 等）
- `headline-craft` skill — 「開かせる一行」の候補生成。規範は本 skill の Title Conventions
