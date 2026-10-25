# Zenn 記事: eval とレビューの分かれ目 — 基準が判定の窓の間 固定されるか

## Context

`drafts/article-context_eval-baseline-nonstationarity_2026-08-23.md`（証拠台帳 C1〜C40）+ 本セッションの外部調査（as-of 2026-08-23）から Zenn 記事を 1 本作る。

素材は、この repo の執筆評価機構が 27 日で建てられ 11 日で解体された記録。2026-08-23 の `92e7cdc` で
**18 ファイル / -1151 行**、判定器は 3 本から 1 本になった。

**著者が最も価値を置いたのは「eval とレビューの使い分けが分かったこと」。** 外部調査でその線引きの
根拠が固まった —— 業界の分類（Hamel / LangWatch / Lanham）はすべて「**どこで走らせるか**」で切っている。
今回の線引きは「**判定の窓の間、基準が固定されるか**」で切る。この軸に対応する既存語彙が薄い。

著者選択（本セッション）:

- チャンネル: **Zenn**（`articles/*.md`）
- 中心命題: **correctness / intent 軸で導出し直す**（4 条件はその運用チェックへ降格）
- 掴み: **「業界の処方 3 点セットを実装したら 2 勝 1 敗だった」**
- 未検証項目は中心命題に必要なら本文へ入れ、`fact-checker` に検証させる
- 論文側の作業（ADR-0008 の引用訂正、論文 v2 材料）は**今回スコープ外**。下の「持ち越しメモ」に残す

先行記事との軸の違い: `llm-judge-checks-not-scores`（2026-07-15）は judge を**どう作るか**、本記事は
**そもそも置ける層かをどう判別するか**。`ai-task-loop-judge-bottleneck`（2026-08-20）は対象がタスク台帳。

## Editorial brief

```
Reader: LLM に品質評価をさせる仕組みを workflow に組み込んだ、または組み込もうとしている
        engineer。「fresh context で、固定 rubric で、たまに人間が監査する」という定石を
        知っていて、その通りに作ろうとしている人

Channel: Zenn（articles/*.md、日本語ですます、直接指示・具体観察・判断則）

Central thesis:
  判定器（eval）を置けるのは、判定の決着が判定器の外側でつく層だけ。決着が
  操作者の中にしかない層に置けるのは、findings を返すレビュアーだけである。
  決着が外に無いまま基準を仕様へ凍結すると、却下基準が書けず、条項が増え続け、
  文脈が増えるたびに矛盾する。

Causal spine:
  業界の処方 3 点セット（fresh context / 固定 rubric / 定期的な人間監査）を真面目に実装した
    → 2 勝 1 敗だった。固定 rubric だけが逆効果（掴み・緊張）
    → 判定対象が 2 種類あったから。基準が窓の間固定される層と、自分の中で動く層（中心命題）
    → 動く層で起きた 3 つのこと + 固定される層で 1 本だけ成立した理由（機序）
    → 作る前に照合する 4 つ。満たさないならレビュアーにする（読者の判断則）
```

### 中心命題の骨格（記事の芯）

**判定の決着は、判定器の外側でつくか。それとも操作者の中にしかないか。**

theme-reviewer の指摘（2026-08-23）で旧軸「基準が窓の間固定されるか」を破棄。旧軸では ADR-0011 の
解体理由 6 件のうち 3 件しか説明できず、「基準の固定」と「対象の固定」も混同していた。新軸は 6 件
すべてと title-eval の生存、さらに Anthropic との処方の違いまで説明する。

| 解体で起きたこと | 決着の所在で説明すると |
|---|---|
| Drop を構造上出せなかった | テーマの良し悪しの決着が著者の中にしかなく、却下基準が書けなかった |
| 通っても大丈夫ではなかった | 記事の良さに、完全な観点集合が存在しない |
| 基準が 5 ファイルに散った | 決着がつかないものを仕様化すると条項が増え続ける |
| チャンネルと 3 点で衝突した | 決着がつかないので、文脈が増えるたびに条項どうしが矛盾する |
| K1-K4 が標語に劣化した | 決着がつかないので、事例を原則に昇格できない |
| 最厳版のアンカーを撤去した | 決着が著者の中にあり、その基準が鋭くなり続ける |
| タイトル判定だけ残った | タイトルの良し悪しは凍結済み本文との契約として、判定器の外側で決着する |

読者の持ち帰り（§10 の 4 つ。すべて決着の所在から導く）:

1. **却下の基準が書けるか** — 「これは通さない」と言える条件を今書けるか。書けないならレビュアー
2. **通ったものを見直さずに出せるか** — 出せないなら 4 人目のレビュアーであってゲートではない
3. **今日凍結した基準を、来月も同じ意味で読めるか** — 読めないなら、凍結したのは原則でなくその日の欠陥パターン
4. **基準が 1 ファイルに収まるか** — 散るなら、決着がつかないものを仕様化しようとしている兆候

### 外部知見の採用（as-of 2026-08-23、`fact-checker` へ全件渡す）

| 出典 | 記事での役割 |
|---|---|
| Marcus Chang, Towards AI（2026-08） | **掴み**の 3 点セット（fresh context / 固定 rubric / 定期的な人間監査）と「曖昧な rubric は checker がほぼ全部通す」。⚠ **本文 403 で未取得・検索サマリ経由**。取れなければ LangWatch / TechEmpower / Lanham から処方を再構成する |
| LangWatch（2026-02-02） | 「単に suboptimal なら monitor、有害・禁止なら guardrail」「品質メトリクスを guardrail にするな」 |
| Micheal Lanham（2026-04-25） | 条件 2 に "LLM-as-judge is a scalable weak supervisor, not a self-validating ground truth" と meta-evaluation drift |
| TechEmpower（2026-07-14） | 条件 4 に "The judge is itself a component to evaluate" / **calibration debt** |
| Memex（2026-06-10） | 掴みか §2 に「verifier がボトルネック」「作業した agent に採点させるな」 |
| Alex Wauters（2026-08-06） | **最終節**。人間ゲート自体の実測 — 40,000+ セッション / 409,000 判断で平均 66.3%、"permission fatigue" |
| Hamel Husain（2025-06-29） | §8 の対比表（業界は「どこで走らせるか」で切っている） |
| **Anthropic「Demystifying evals for AI agents」（2026-01）** | **§9。「eval suite は living artifact として扱え。良し悪しを弁別しなくなった eval は役目を終えている」。業界の参照点で、同じ前提から正反対の処方**。https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents |

### 採用する実測証拠（因果線での役割つき）

| 証拠 | 役割 |
|---|---|
| C6 / C8 / C7 | 作った理由と 3 判定器体制。外部実証 4 件に沿って設計した裏づけ |
| C10 / C11d / C15 | 数字は良かった（バックテスト 67 本、A→A 88%、C→Deepen 80%、KPI 6→0） |
| C28 / C9 | 緊張の実測値: 18 ファイル / -1151 行、ADR-0008 から 11 日 |
| C20 / C20c | 照合 1 |
| C21 / C16 | 照合 2・3 |
| C11b / C11c / C23 / C24 / C1（逐語）/ C33 / C35 | 照合 4 |
| C27 | 固定される層で 1 本だけ成立した理由 |
| C18 / C19 | コスト差（5 ファイル分散 vs agent 1 ファイル、内部整合に 1 セッション） |
| C29 / C32 | 判別後の結果: 判定器 3→1、執筆前評価器 3→0、公開ブロック条件 −1 |

### Out of scope

- 論文（`harness-alignment`）の apparatus を本文へ展開すること。**本文では無名で概念を説明し、末尾の
  関連リンクで 1 回だけ出す**（self-link は本文中 1 記事 1 回まで、それ以外は末尾が正規の置き場）
- C4 / C5（ADR-0005 の予測型レビュアー不採用）— 触れるなら 1 文
- C13 / C14（`mechanical_checks.py` の precision）— コスト節に 1 行
- C22（K1-K4 破棄の内訳）、C25 / C26（執筆側へ移す項目ゼロ、B15 の例外）
- C36 / C37（40% 天井の除去と 2 arm 比較）、C31（pytest 84 passed、未再実行のため載せない）
- **C38 / C39（readme-writer への port が生きている件）— 著者判断で除外**（設計判断ではなく単なる未着手のため）
- OpenAI Auto-review、execution drift、`article-quality` 台帳のランク詳細、同日の第 2 次縮小 `45eb8fe`

## 構成（`articles/<slug>.md`、~8,500 字 / h2 9 本）

**これは 27 日間の物語として書く。証拠の羅列にしない。** 各節は「その日に何が起きたか」で進み、
数値・commit・引用はその日の出来事として現れる。判別軸は物語の終盤で初めて言語化される
（読者が著者と同じ順路をたどり、同じ場所で気づく構造）。表は最大 3 つまで。

1. **掴み**（見出しなし）— **場面から入る**。2026-08-06、別リポジトリで eval を作ろうとして手が止まった日。
   そのとき自分が言った言葉「検証器もすぐアップデートするし、実装もすぐアップデートするから
   Baseline が維持できない」。読者への語りかけ + `:::message` で n=1 の断り +
   「読み終える頃には〜を自分で判別できます」
2. `## それを言った 6 日後に、作り始めた` — 8/12 の事件（レビュー全通過の原稿に自分で瑕疵 3 件）。
   6 日前の結論を自分で無視した。C6 / C1
3. `## 定石どおりに作った` — fresh context / 固定 rubric / 定期的な人間監査。外部実証に沿った設計。
   3 判定器体制、67 本の盲検バックテスト（A→A 88% / C→Deepen 80%）。C7 / C8 / C10 / C11d
4. `## 一番厳しい版ができた日に、それを捨てた` — **物語の転換点**。A 率 43% → 27% → 6% と絞り込み、
   最厳版ができた瞬間に著者が撤去。「過去記事を基準にすると天井が過去に固定される」。
   ただしこの時点では一般化できていなかった、と正直に書く。C11b / C11c
5. `## 数字は良くなった。それでも何かが足りなかった` — KPI 6 件 → 0 件。ただし同じ回に、別モデルの
   レビューが判定器の外側で事実誤り 2 件を検出していた。C15 / C16 / C21
6. `## 別のリポジトリで、同じ言葉が戻ってきた` — 8/22、まったく別の作業中に数値ゲートを測定不能として
   撤回。「対象は週単位で改稿され、判定器は版を持たない著者」。8/06 の自分の言葉の一般形。
   C33 / C35 + 撤回ゲートの text block
7. `## 1151 行を消した日` — 8/23 午前、判定器の内部整合に 1 セッション使ったこと。そして 15:35 の解体。
   `git show 92e7cdc --stat` 抜粋 + 契約 diff。C18 / C19 / C28 / C29 / C32 / C20 / C20c / C23 / C24
8. `## 分かったのは、決着がどこでつくかだった` — **ここで初めて軸を言語化する**。
   業界の 3 分類は「どこで走らせるか」で切っている、という対比表 1 つ。
   タイトル判定が生き残った理由をここで回収（凍結済み本文との契約として外側で決着する）。C27
9. `## Anthropic は「更新し続けろ」と言っている` — 同じ前提から正反対の処方。
   なぜ逆になったか = 対象の決着が外側にあるかどうかの違い。**終盤に 1 節、短く**
10. `## 作る前に確かめる 4 つ` — 持ち帰り。判別表 1 つ + 判定器→レビュアーへの移し方。読者への直接の語りかけ
11. `## まだ分かっていないこと` — 解体後の KPI は本記事が 1 本目で未観測、**そして最上位ゲートに戻した
   人間の判断自体が別文脈で 66.3% と測られている**（Wauters）で締める
12. `## 出典・参考` / `## 関連リンク`

### 語りの規律（証拠列挙型に落ちないための判定）

- 各節は**その日の出来事**で開く。数値は出来事の一部として出し、節を数値表で開かない
- 「C○ が示すとおり」型の論証接続詞を使わない。台帳の番号は本文に出さない
- 表は 3 つまで（§8 の業界対比 / §9 の判別 / 必要なら §3 のバックテスト）。
  4 つ目が欲しくなったら地の文か箇条書きに落とす
- **当時分かっていなかったことを、分かっていたように書かない**。§4 と §6 は「後から結びついた」順で書く
- 完成後の判定: 各節の冒頭 1 文だけを抜き出して並べ、それが 1 本の話として読めるか

### code / terminal evidence（実用チャンネル要件）

- `git show 92e7cdc --stat` 抜粋
- `theme-eval` → `theme-reviewer` の契約 diff（判定器→レビュアー変換の具体）
- 撤回された数値ゲートと置き換え + 件数条件の書き方の規約
- 表は 2 つに絞る: 業界 3 分類との対比表 / 4 つの判別表。バックテストと A 率収縮は**地の文か箇条書き**へ

### 執筆時に守る（global `writing-ecosystem`）

- 1 段落 1〜2 文。比較は箇条書き・表に。具体物を先、説明を後
- 掴みと結論の少なくとも一方に読者へ直接向いた文（一般論の問いにしない）
- 中心語は「判定器」「レビュアー」「判定の窓」。初出で定義し、類義語に逃げず反復する。
  内部語彙（`theme-eval` / `article-judge` / K1-K4 / Z4 / T3）は平易に言い換えるか使わない。見出しに出さない
- 英語の名詞句を 2 つ以上そのまま繋げない（`calibration debt` は初出で日本語を併記）
- 自リポ・自論文リンクは本文中 1 回まで。それ以外は末尾へ
- Zenn 内部記事リンクはフル URL（`https://zenn.dev/shimo4228/articles/...`）

## 実行手順

1. `theme-reviewer`（global agent、fresh context）に問い一文と台帳・外部調査結果を渡し、findings と
   深化の問いを受け取る
2. 上の editorial brief を著者に提示して確認を取る
3. 初稿を `articles/<slug>.md` へ執筆。frontmatter は `zenn-format` に従い `published: false` で開始
4. 構造凍結後に `headline-craft` → `title-eval` → **著者がタイトルを選択**
   （仮題: 「その判定、決着はどこでつきますか — eval とレビューの分かれ目」／
   slug 案 `judge-needs-outside-verdict`）
5. 同じ最終タイトル + 本文へ panel を並列実行 — `editor` / `prose-clarity-reviewer` / `fact-checker` / `codex-review`
   - `fact-checker` には**上の外部知見テーブル全件**と、C7 の外部実証 4 件（CheckEval / TICK / BinEval、
     EQ-Bench、Self-Correction Bench の 64.5%、Voice Under Revision）を明示的に渡す
   - **Chang の 3 点セットは掴みの土台なので最優先で検証**。取れなければ掴みを他ソースから再構成する
6. 検証済みソースを inline link / `## 出典・参考` へ編入し、`editor` の focused recheck
7. `/quality-gate articles/<slug>.md`
8. **著者通読 GO**（最上位ゲート。解体後の 1 本目なので通読指摘数を memory `eval-harness-pipeline.md` へ記録）
9. `zenn-format` → `/publish-article articles/<slug>.md` で `published_at` を設定
   - 既定: JP `2026-08-26 09:00` JST / EN は前日 `2026-08-25 22:00` JST
   - ⚠ 予約登録自体が投稿上限に計上される。3 日以上前に push し、**Zenn のデプロイ履歴を確認する**
10. EN 版: `devto-translator` で `articles-en/<slug>.md` → `devto_crosspost.py schedule`
11. `npm run generate:index` → `npm run validate` && `npm run check:index`
12. commit → **push を著者に促す**（未 push は Zenn 予約にも Dev.to ジョブにも届かない）

## 検証

```bash
# 引用した実測値の再確認
git show 92e7cdc --stat | tail -25
git log -1 --format=%ci 92e7cdc               # 2026-08-23 15:35:24 +0900
git log -1 --format=%ci a55afc7               # ADR-0008 → 11 日の差分
git -C ~/.claude log -1 --format=%B c3083f3   # 件数ゲート撤回

# 機械検査
npm run validate
npm run check:index
python3 scripts/devto_crosspost.py post <slug> --dry-run   # EN 版のみ

# 公開安全性
git diff --stat    # 個人 path / 生ログ / 資格情報が混ざっていないこと
```

受け入れ条件（`.claude/rules/publishing-channels.md` の shared acceptance profile）:
`editor` unresolved CRITICAL 0 / `prose-clarity-reviewer` PASS / `fact-checker` INACCURATE 0・未解決
PARTIALLY 0 / `codex-review` 完了 / `title-eval` 済みで著者選択済み / AI-mediated writing の適用可否を記録
（過去記事に開示ブロックの先例はないので著者判断を仰ぐ）/ public-safety scan 0。

## 持ち越しメモ（今回スコープ外・別セッションで扱う）

1. **ADR-0008 の引用訂正** — 「blind spot 64.5%」は Cross-Context Review（arXiv 2603.12123, 2026-03）
   ではなく **Self-Correction Bench（arXiv 2507.02778, 2025-07）** の数値。14 の open-source 非 reasoning
   モデルで 64.5%。CCR は Tae-Eun Song の別論文で、production と review のセッション分離が主題。
   ADR は削除でなく日付つき注記で直す
2. **論文 `harness-alignment` v2 の材料**
   - open question 2（human-side failure twin は未測定）に Wauters（2026-08-06）を当てられる。
     ただし測定対象は security approval であって behavior-shaping write ではない —— この
     スコープ差を書けば、論文の主張はむしろ強まる
   - §6.1 の drift 造語 audit に候補 2 件: **meta-evaluation drift**（Lanham 2026-04、ただし出典が
     Substack なので arXiv audit の枠外）と **execution drift**（2026-08）
   - §5 の attention budget 議論への追加観測: intent 側に自動判定を置くと、消費されるのは判定の
     attention だけでなく**凍結した基準自体の保守の attention**で、コストは判定器の数ではなく
     基準の置き場の分散数で効く（5 ファイル vs 1 ファイル、消費者 1 本の内部整合に 1 セッション）
   - OpenAI Auto-review（2026-04-30）は反例に見えるが、自動化しているのは correctness 側。
     OpenAI 自身の限界表明「strategically hiding its intent」が論文の主張を裏書きしている
3. **証拠台帳の ⚠ 更新** — C7 の外部実証 4 件は本セッションで一次ソース照合済み（1 件訂正あり）
