# Wikidata BAN 記事 — 執筆プラン(介入点 1: 構成案の承認)

## Context

`drafts/article-context_wikidata-ban-adr-0021_2026-07-16.md`(/collect-context 済み証拠台帳、Claims C1–C17 + commit 一次ソース付き)を素材に、Wikidata governance revocation の postmortem 記事を書く。本日 2026-07-30 発効の ADR-0007(Kaguura 原則取り込み)により導入規約が「一瞬でわかる → 掴み → 緊張 → 解決 → Higher Ground」に改定されており、この記事が新規約の初適用となる。

## Phase 0 判定(zenn-editorial-judgment)

**タイプ: 実測レポート系 postmortem ／ 装置: 採用(わかること行・判断表・図表)／ 統合候補: なし**(zenn-content に Wikidata/GEO 既存記事 0 件 — 台帳で確認済み)

- **読者の問題文**(構成の従属先): 「GEO 文献の『Wikidata 被言及が AI 引用に効く』を読んで自分の作品を Wikidata に登録しようとしている読者が、この記事を読むと、self-created 経路がアカウント粒度の governance 判定で全損する構造を理解し、自分の発見可能性戦略を earned 経路前提で設計し直せる」
- **コア論点**(3 つ ≤ 4、OK): ①効果と経路の分離 — Wikidata 被言及は効くが self-created では作れない ②全損当日の事故対応の実務(purge・機械検証・謝罪の設計) ③失敗を ADR + rule に変換する方法
- **軸の設定**: 著者の事故は証拠。主語は「self-created 経路そのもののリスク構造」に置く。内部語彙(AAP・OQ9・carrier・ecosystem・ADR 番号群)は軸を読者側に付け替える過程で最小化する(下記「内部語彙の扱い」)

## 記事構成案(ADR-0007 新規約適用)

frontmatter は台帳のドラフトを維持(title 仮・emoji 🚫・type: tech・topics: wikidata/llm/knowledgegraph/geo/postmortem・**published: false のまま**)。

### 導入(一瞬でわかる → 掴み → 緊張 → 解決)

1. **わかること 1 行**: 「Wikidata 被言及は AI 引用に効く — ただし自分で登録する経路(self-created)では作れない。109 item 全損の一次資料でその理由と後始末・再発防止の設計を示します」の趣旨
2. **掴み(具体的シーン)**: 2026-07-16 朝。block 画面。理由は "Promotion-only account"。deletion log を引くと 02:00:48–51 UTC の **1 分間で 109 item が一括削除**されている。6 週間の構築が一夜で消えた — 読者接続: 「Wikidata に登録すれば AI に引用される」という GEO の定石を検討したことがあるなら、これは同じ経路の話
3. **緊張(パラドックス)**: 個別の編集は規約準拠のつもりだった — 出典付き statement・constraint lint PASS・talk page への警告ゼロ(C4 は「警告・名指しが無かった」に絞って一次化)。それでも全損した。なぜか
4. **解決宣言 + 骨格宣言**: 「この記事でやることは 3 つです」— なぜ全損したかの構造 / 当日中に閉じた事故対応 / 失敗から抽出した設計原則

### 本文セクション(見出しは outcome 形で執筆時に確定)

| # | 節 | 内容 | 主要 Claims |
|---|---|---|---|
| 1 | 何を作っていて、何が起きたか | 6 週間の federation 構築史(時系列表)→ block と 1 分間の削除。deletion log 取得コマンド(実行可能な curl 例)を「読者が事実を検証できる起点」として提示 | C1–C3, C5, 構築史 |
| 2 | なぜ全損したか — 判定はアカウント粒度 | 編集単位の準拠が防御にならない構造(aggregate pattern)。velocity の読み(rate-limit 連発 → 数時間後 block。**C6 は「著者の観測」と明示**)。batch 承認による gate 希釈 | C1–C4, C6 |
| 3 | 誤解はどこから来たか | 4 つの出所(政策の緩さ C15・生存者バイアス・検証軸の取り違え・DOI 誤認)+ 最も痛い事実「半分知っていた」(C12 Skip list / C13 Wikipedia 側は却下済み → 境界を prose/構造化データで誤って引いた) | C12–C15 |
| 4 | その日のうちにやったこと | 判断表(appeal でなく retire + doctrine 化、の Why と Alternatives)。意味差分ゲート付き purge(Python 要点)。count guard が人手レビューの見落とし 6 件を検出した話(bash 例)。謝罪の設計(unblock 要求なし・block 中でも own talk page は書ける C10/C11) | C7–C11 |
| 5 | 失敗を規範に変換する | ADR-0021 骨子(revocation-control / earned-only / purge 規律 / 回避の全面禁止)。「登るな看板は登る側に効かない」— absence(削除の実装)> 仕組み > 看板の順で対応した話(C17 は平易語で、AAP 固有名は出さない)。rule + learned note への 3 層 harness 化(C16) | C7, C16, C17 |
| 6 | まとめ(Higher Ground) | 経路 vs 効果の区別が核: 被言及の効果は否定しない、self-created では作れない。読者が持ち帰るもの = **bulk 書き込み前の aggregate-pattern チェックリスト**(learned note の 5 項を読者向けに一般化)。earned 経路だけが残った状態は「生きた実験」として測定継続 | 総括 |
| 7 | 関連リンク | ADR-0021・謝罪ページ・implementation-log + **著者 GitHub ハブ(必須・CLAUDE.md 規約)** | — |

図表: 構築史タイムライン表・Before/After 表(109→0 等)・判断表(retire vs appeal)で ≥1 を大幅充足。

## 未検証 Claims の落とし方(執筆時に解決)

| Claim | 方針 |
|---|---|
| C4(lint PASS 履歴が memory 由来) | 主張を「個別編集への警告・名指しは無かった」(talk page で一次検証可)に絞る。lint PASS は「著者の運用記録」と明示 |
| C6(rate-limit 連発) | 「著者の観測」と本文で明示。断定せず velocity の「読み」として書く(global debugging.md の原則と整合) |
| C14(GEO meta-finding) | 執筆時に WebSearch で当該 GEO 論文(一次)に遡って個別 cite できれば採用。遡れなければ具体的数値・文献名を出さず「GEO 系の分析で Wikidata/Wikipedia 言及の寄与が強調されている」程度の一般言及に弱める(要約経由の数値は書かない) |
| C15(Wikidata 政策の緩さ) | 執筆時に Wikidata:Autobiography / Wikidata:Notability を WebFetch し現行文言を引用 |

## トーン制約(台帳の技術メモ + global 正本との照合結果)

- 管理者名は事実として書くが**批判・皮肉ゼロ**。判定は公正だった、が本記事の立場(公開済み謝罪文と矛盾する記述は書けない)
- 巻き添え削除(他者論文の書誌 item)は「commons への負債」として自責側で書く
- 回避(別アカ・代理)の全面禁止は ADR-0021 文言と整合させる
- global 正本(debugging.md「Rate limit は警報」/ platform-governance-aggregate-pattern.md 6 原則)と主張の食い違いなし — 記事はこれらの rule の worked instance として書く

## 内部語彙の扱い(軸ずれ検出器)

読者の判断に不要な内部語は落とすか平易化: AAP(固有名を出さず「別 repo で先に定式化していた原則」程度)/ OQ9(「未解決の問い」と平易化 or 削除)/ carrier(「数値を記載している全ファイル」等)/ ecosystem(「研究 repo 群」)。残すのは論点を支える最小限: ADR-0021(記事の主産物なので実名)・federation(初出定義付き)。

## 実行手順(承認後)

1. **未検証解決**: C15 の WebFetch、C14 の一次遡行(WebSearch)。C4/C6 は表現側で解決
2. **執筆**: 本体が zenn-practical-writing に従い直接執筆(ですます・コピペで動くコード・段落密度閾値・10% 編集パス)。`articles/` に新規ファイル作成、published: false
3. **自己プリフライト**: Phase 3 チェックリスト(AI-slop・用語初出・段落密度・論点数)
4. **レビュー並列**: editor + fact-checker(Claims Register 直行)+ zenn-clarity-reviewer、+ codex-review。指摘の採否は根拠付きで記録
5. **構造自己審問 + 通読ゲート**(zenn-editorial-judgment レビュー後 5 問)
6. **介入点 2(人間 gate)**: 記事本文をユーザーに提示 — 公開ドキュメントは behavior-shaping artifact なので本文提示。published: true・タイトル確定(headline-craft/seo-optimizer)・英訳・schedule 登録はすべてこの gate の後、ユーザー判断

## 検証方法

- レビューエージェント 3+1 の verdict(zenn-clarity-reviewer FAIL は公開ブロック)
- `npm run validate`(frontmatter 検証)
- Claims Register の ⚠ 4 件がすべて「一次化 or 明示的弱化」で解消されていることを最終稿で確認
