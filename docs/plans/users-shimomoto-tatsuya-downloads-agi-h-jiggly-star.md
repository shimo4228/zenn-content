# note エッセイ「AGI の空気の中で、判断の履歴を残す」— 実行計画と editorial brief 案

## Context

2026-10-01 朝の Claude との雑談（`~/Downloads/agi_harness_conversation_log.md`）からテーマが浮かんだ。著者の指示:

- 「このリポジトリの規約になじまない指示は無視しといて」— 貼られた依頼文は素材と著者の言葉として使い、
  手順・register・タイトル工程は repo 規約（`writing-principles.md` / `publishing-channels.md` の note 行 / `writing-ecosystem`）に従う
- 「あくまでこのやり取りから浮かんだテーマだから、別に会話を軸にしなくていい。現在のAGIを取り巻く状況を調査した上で、わたしの所感がセンターに来るような記事にしたい」
- 中心の所感: **蓄積は古びても、判断の履歴は道標**（結びは「今は自分も道標だと思う」、立ち位置は「職業は書かない」）

よって会話ログは「所感の出どころ」の一つに下げ、記事の土台は **as-of 2026-10-01 の AGI を取り巻く状況の調査**、中心は著者の所感にする。

依頼文から外す指示（規約と衝突）:

| 依頼文 | 従う規約 |
|---|---|
| ログの順に沿った往復運動 | 著者の新指示で会話は軸にしない |
| 常体（だ・である） | note の register「ですます、発見調」 |
| 「独立研究者」「エンジニアではない立場」 | practitioner-identity（研究者ではない）、「非エンジニア」廃止。職業も書かない |
| タイトル案 3 つを本文と同時に | 内容 GO 後に `headline-craft` → `title-reviewer` → 著者が選ぶ |
| 別立ての 100 字リード | note 新規稿は frontmatter なし。冒頭段落（Entry bridge）が担う |
| 日常のたとえ話を足す | orchestrator は比喩を作らない（背骨 2） |
| 見出し 4〜6 個 | 目安。節は発見の数で割る（背骨 5） |

残す条件（背骨と一致）: AGI の時期を断定しない・推測は推測と書く、専門用語は一言で説明、Claude の言葉と著者の言葉を混同しない、安っぽい希望で締めない。

## 実行手順

### 1. 調査（search-first、一次資料、全項目に as-of 日付）

skill: `search-first` で、2026-10-01 時点の次を調べ、`drafts/article-context_agi-landscape-2026-10-01.md` に証拠台帳（一次 / ⚠未検証の tier、URL、日付）として残す。fact-checker に渡す台帳を兼ねる。

- **「AGI は近い」言説の現在地**: 主要ラボ（Anthropic / OpenAI / Google DeepMind / Meta 等）トップの直近の時期発言、予測市場・Metaculus、AI 2027 型シナリオとその後の更新、懐疑側（スケーリング頭打ち論、定義論争）
- **能力の現在地**: 直近のフロンティアモデルと、長時間タスク・自律コーディングの計測（METR の task horizon 等）、コーディングエージェントの実態
- **安全性・検証の現在地**: 解釈可能性、AI コントロール（結託・信頼できる監視）、評価中と気づくと振る舞いが変わる報告（evaluation awareness）、欺瞞的アラインメント、ディベート / scalable oversight の系譜（2018 年 Irving ら）、Contemplative AI（Laukkonen et al. 2025）の位置
- **「技法は陳腐化する」側の観察**: プロンプト / ハーネスの技法がモデル世代交代で不要になった例（著者自身の harness の Scaffold Dissolution 記録も一次資料として参照可）

調査結果は記事の材料であって網羅リストではない（dossier は lookup material）。

### 2. 中心命題の対話 → editorial brief 確定（ここで著者確認に止まる）

調査の要旨を著者に見せ、所感がどう動いたかを聞いてから、下の brief 案を `docs/plans/<slug>.md`（slug 案 `agi-judgment-trail`）に確定する。調査で所感の前提が反転したら、継ぎ足さずに著者へ聞く（背骨 4）。

### 3. 執筆 → panel → 内容 GO → タイトル → quality-gate

- `note/<slug>.md` に初稿（ですます・発見調、frontmatter なし、末尾に `## 出典・参考文献` と AI-mediated writing の開示 block）
- 構造凍結 → 並行: `essay-reviewer`（brief path と「AI が本文を生成」を渡す）、`fact-checker`（証拠台帳とログ path）、`codex:codex-rescue`（read-only、prose-clarity-reviewer checklist・contract・原稿 path のみ）
- 処分記録 `drafts/review-disposition_<slug>.md` → 反映 → 著者通読 → **内容 GO**
- `headline-craft` → `title-reviewer` → 著者がタイトル選択 → `/quality-gate note/<slug>.md`
- 公開（`note-publishing`）・commit・push は著者 GO を待つ
- 着手時に `drafts/<slug>.corrections.md` へ C1（規約外の指示は無視）、C2（会話を軸にせず調査＋所感を中心に）、C3（結び「今は自分も道標だと思う」）、C4（職業は書かない）を積み、記事 commit に写す（correction-trailers 規則）

## Editorial brief 案（調査後に確定）

- **Reader**: note の読者約束「一つの問いを自分の問題として考えられる」。AGI の空気の中で、自分が積み上げているものの行方が気になっている人
- **Channel**: note（JA 正本）。Substack EN 版は計画外
- **Author's words**:
  - 「この半年AIコーディングしてきたけど、来年にはその蓄積も無駄になるだろうという気がする。だから、私は判断の履歴だけは残してきたんだけど。なんだかずっと自分の墓を立てている気分だ。existence proofだ」
  - 「この１年は無駄ではないかもな」
  - 「残るといいけど残らないだろうな」
  - 「今は自分も道標だと思う」（結びの確認への回答）
- **Central thesis**: AGI が近いと言われる中で、半年分の技法は古びるかもしれない。それでも、その時々の不確かさの中で何を選び、何を捨てたかという判断の履歴は後から生成できない。墓を立てている気分だったそれを、今は道標だと思う。残るかは分からない
- **Entry bridge**: 「AGI は今年中」という空気（調査で日付つきの具体的発言 1 件に錨を置く）と、半年続けた AI コーディングの蓄積が来年には無駄になる気がする、という著者の実感
- **Causal spine**（調査後に証拠を割り当てる）:
  1. 観察: AGI 言説の現在地（日付つき）と、著者の「無駄になる気がする」
  2. 緊張: 能力が伸びるほど、技法（足場）はモデルに吸収される — 調査の陳腐化の実例
  3. 機序: 一方で、能力が伸びるほど「確かめられない」領域が残り、安全性研究は不完全な仕組みを重ねて検証できない知性とつきあう方向にある。AI に作らせ・疑わせ・人間が判断するこの 1 年の型はその予行演習だったかもしれない（発想自体は 2018 年頃のディベートが先行）
  4. 著者の判断: だから判断の履歴を残してきた。墓の気分 → 今は道標だと思う。決めなかったこと: 残るかどうか
- **Out of scope（仮）**: AGI の定義論争の深掘り、時期の予測、ハーネス実装の詳細、雑談ログの時系列の再現

## Verification

- 調査の全主張に URL と as-of 日付。AGI 時期は発言として日付つきで引き、断定しない
- 公開安全: 本名・職業・個人 path・ログ原本を本文に出さない
- 発言の帰属（著者 / Claude / 外部の人物）を fact-checker が台帳と照合
- `quality-gate` が note 行の証跡（essay-reviewer・codex・fact-checker・処分記録・内容 GO・title-reviewer・開示 block）を集約して PASS
