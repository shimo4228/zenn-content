# harness-stocktake の告知記事（JP Zenn / EN Dev.to）

調査: [research/2026-11-02-harness-stocktake-article.md](research/2026-11-02-harness-stocktake-article.md)（内部調査。各節の事実と出典、
契約上の制約、記録の食い違い 4 件）。親 plan: `~/.claude/docs/plans/enumerated-petting-beaver.md` の Stage 3 手順 2・3、Stage 4。

## Context

harness-stocktake（plugin v0.1.0 と Action v1.0.0）は 2026-11-02 に公開した。Stage 4 の告知（掲載 PR、X / Bluesky、Show HN）は
記事の URL を前提にしているので、先に記事が要る。集計は既にある（`~/.claude/docs/plans/research/2026-11-01-state-of-aggregate.md`）。
新しい run は回さず、記録に無い数字は作らない。物語の軸は親 session が渡した「系譜と出所」で、2026-02 に ECC へ出した
skill-stocktake が harness 全体の棚卸しになり、その手順が AKC の Curate phase である、という線。

終わりの形: JP と EN の草稿が reviewer を通った状態で止め、著者に公開の OK を 1 回ずつ求める。公開・Buffer・`docs/state-of-2026/`
への配置・release / DOI は、その OK の後に別の作業として行う。

## 著者の判断点（この順に止まる）

1. **中心命題の対話**（brief の前、writing-ecosystem §2）。「この記事で何に引っかかっていて、読者に何を問いたいか」を聞き、
   答えを命題の形で言い返す。著者の原文を brief の Author's words に置く
2. **本文の数字 1 つ**。aggregate 末尾の候補を実物で並べ、推奨を 1 つ付けて聞く。
   - A: 拾われない 48/74（65%、n = 1）
   - B: 正答率 57/60（95%）
   - C: 中央値 134.5 秒
   「数字は一つに絞る」は**記事の看板になる数字を一つにする**と読む。20 本の節にある分布（source 別の 19/20 など）は、その節の
   証拠として最小限だけ置く。この読み方で違っていれば、ここで直す
3. brief の確認（`docs/plans/harness-stocktake-after-doctor.md`）
4. ペルソナ読みと panel を終えた稿の通読 → **内容 GO**
5. タイトルの選択（headline-craft → title-reviewer の後）
6. **JP の公開 OK** / 7. **EN の公開 OK**

## 記事の構成（JP。brief の前の仮の骨組みで、1 の対話の結果で組み替える）

slug（仮）: `harness-stocktake-after-doctor`。因果線は 観察 → 緊張 → 機序 → 著者の判断（背骨 3）。

| 節 | 役割 | 使う事実・数字 | 出典 |
|---|---|---|---|
| 導入（Entry bridge） | 読者が持っている `/doctor` から入る。`/doctor` を回した後の自分の harness に何が残ったかという場面 | 著者の harness の非 Keep 74 件（看板が A ならここで 48/74） | doctor-comparison 結論 1 |
| 1. 1 件ずつ聞かれる棚卸し | 観察。2026-02 に作り ECC に入った skill-stocktake と、192 項目を 1 件ずつ聞かれる不満 | 2026-02-24 の記事、ECC PR #265、著者の発言（2026-10-31） | 過去記事 2 本、ADR-0097 Context |
| 2. 1 枚の report と 2 回の判断 | 機序。7 本の棚卸しが判定までを持ち、承認と適用を 1 つの契約に渡す。AKC の Curate phase という位置づけ | 192 項目 → 判断 2 回（before / after） | plan:12、ADR-0097 Decision 1・2、akc-cycle README:69 |
| 3. `/doctor` との差 | 緊張。native が持つものと持たないもの。逆向き（native だけが出す 22 件）も書き、補完関係として示す | 0 / 26 / 48、逆向き 2 / 4 / 22（数字は看板次第で絞る） | doctor-comparison 結論 1・3・4 |
| 4. 公開 harness 20 本で回した | 他人の harness でも残るか。選定の 1 query と、連絡せず集計だけ出す理由 | 789 / 1979、source 別の分布、大きさとの関係（件数 ρ 0.62 / 割合 ρ 0.06）、見立て 9/10 と「全部 ○」でも 9/10 | aggregate 表 1・3・4 |
| 5. 決めたこと・決めなかったこと | 著者の判断。位置取りは「`/doctor` の後」。n = 20 は母集団ではない、照合役も Claude 系、plugin 形式の harness は入っていない | aggregate「限界」 | aggregate |
| 試す | install の 1 行と `--dry-run`、Action の Marketplace URL | 公開済みの事実（2026-11-02）。directory は審査中なので書かない | plugin / Action の README |
| 関連リンク・AI 開示 | 契約の 2 行、AKC の DOI、開示 block | — | publishing-channels、publication-procedures |

本文に必ず入れる限定（親 session の指示）:
- n = 20 は一つの検索 query から選んだ 20 本で、母集団の推定ではない
- 65% は著者の harness 1 本の数字

repo 名は出さず、一般化した言い方もしない。「研究」「調査報告」の枠では書かず、`State of` は親 plan の語として扱う
（rule `practitioner-identity.md`）。

## 日英の差

- JP（Zenn、`articles/<slug>.md`）が正本。ですます、`published_at` が必須
- EN（Dev.to、`articles-en/<slug>.md`）は JP の内容 GO と受け入れの後に devto-translator で作る。構成と数字は JP と同じにする
- EN の題は translator の推奨案で決める。`description:`・tags・cover を付け、`canonical_url` は付けない
- EN の手順: editor の report を 1 回取って処分し、`devto_crosspost.py post <slug> --dry-run` を回す。persona 読み・初見の読み・
  fact-checker・title-reviewer は EN では回さない（publishing-channels の Shared acceptance profile）
- `docs/state-of-2026/` に置く英語版と CSV は公開 OK の後の作業なので、この plan には入れない

## 進め方（判断点 1〜3 の後）

1. **dossier**: `drafts/article-context_harness-stocktake-2026-11-02.md`（非公開）に、調査 report の §1〜§4 の主張を出典つきで置く。
   drift の `--dossier` と fact-checker の台帳を兼ねる
2. **初稿 r0** を `articles/<slug>.md` に書く。`published: false` のままにする
3. **persona-read-loop**（article preset、作業場所は `drafts/<slug>/persona/`）
   - 読み手は primary（Claude Code の harness を自分で組んでいる engineer）、inflow（`/doctor` や claudecode の topic 検索から来た人）、
     practitioner（日本のハーネス実践者）。brief の Causal spine を照合に使う
   - 依頼文の「3 round」は skill の上限（改稿 3 回、r3 を読んで止まる）として扱う。skill §6 の停止条件に先に当たったら、そこで止めて
     理由を処分記録に 1 行書く。3 回まで回し切ることは強制しない
   - 改稿のたびに `drift_count.py` を回す。exit 1 なら著者に見せる
   - 止めたラウンドで、比較記事を使った practitioner の読みを 1 回だけ回す（記録だけ）
4. **凍結と panel**
   - 凍結稿を `drafts/<slug>/frozen.md` に写す
   - 3 つを並列に回す:
     - editor
     - fact-checker（台帳: dossier、aggregate、doctor-comparison、premise-test、precision、ADR-0097、過去記事 2 本、plugin / Action の
       README。DOI と食い違い 2・3 の確認を名指しで頼む）
     - `codex:codex-rescue`（読み取り専用。checklist は prose-clarity-reviewer）
   - 処分記録を `drafts/<slug>/disposition.md` に書く
5. 著者の通読 → 内容 GO（判断点 4）。`evals/read-through-log.md` に 1 行足す。図は Figure plan で決める（親 plan の画像 1 枚は
   Stage 4 の告知用。本文の図は節の形が対比・流れのときだけ足す）
6. headline-craft → title-reviewer → 著者がタイトルを選ぶ（判断点 5）。仮題は一本の「—」で繋いでいるので、契約の em dash 規則に
   当てて候補に含めるかを決める
7. zenn-format（topics / emoji）、`npm run validate`、`npm run evidence -- articles/<slug>.md`、quality-gate → JP の公開 OK（判断点 6）
8. EN: devto-translator → editor → dry-run → EN の公開 OK（判断点 7）

## Verification

- `npm run validate` と `npm run evidence -- articles/<slug>.md` の deviations が 0
- quality-gate が PASS
- 本文の数字は全部 dossier か aggregate の行に引ける。fact-checker の INACCURATE / PARTIALLY は全件処分済み
- `grep` で次の 2 点を確かめる:
  - 本文に 20 本の repo 名と個人の path が無い
  - 「n = 20」「著者の harness 1 本」の限定が本文にある
- EN の dry-run が通る
- commit は記事ごとに分け、push は著者の公開 OK の後
