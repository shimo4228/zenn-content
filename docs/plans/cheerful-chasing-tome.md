# 記事執筆プラン — 消費者ゼロの計器（instrument-dissolution-duty）

## Context

`session-theme-mining` で著者が選んだ問い:
**「計器・skill・doc は『消費者ゼロ』でも lint に落ちない。畳む判定はどこから来るのか」**

証拠台帳は収集済み: [article-context_instrument-dissolution-duty_2026-08-30.md](../../MyAI_Lab/zenn-content/drafts/article-context_instrument-dissolution-duty_2026-08-30.md)（Claims Register C1–C27、セッション索引 6 本、Before/After 12 行、すべて 2026-08-30 に live 再測定済み）。

書く理由は、前記事 [lint-as-subtraction](https://zenn.dev/shimo4228/articles/lint-as-subtraction)（2026-08-30 に著者が Zenn 上で手動公開）が置いた分類表 —「未使用コード = 決定論 = 機械へ」— を、その翌日の実測が反証したこと。repo 自身の週次 dead-code intake は候補 **0 件**を返し、ruff（C901 込み）も **0 件**、しかし翌日 **2,065 行**が「消費者ゼロ」を理由に消えた。さらに複雑度予算の drain は Python 行数を **+815 行増やした**。機械が指す場所と、著者が減らしたかった場所が一致していない。

著者判断（2026-08-30、本セッション）:

- **続編として書く** — 前記事を読んだ読者を前提にしてよい
- **スコープはコード内の計器に絞る** — skill 縮退（`python-patterns` 1,050→377 行）と台帳の blocked 5 件 withdrawn は最後に 1 段落だけ
- **EN は JP 確定後** — 内容 GO・タイトル確定の後に `prose-translation` → `devto-translator`

## Channel routing

`.claude/rules/publishing-channels.md` の channel 表で解決:

| 項目 | 値 |
|---|---|
| Channel | Zenn（`articles/*.md`） |
| Reader promise | 検索・feed から来た engineer が数秒で用途を理解し再現または判断できる |
| Register | 日本語ですます。直接指示・具体観察・判断則を優先し、修辞疑問で結論を弱めない |
| Channel editor | `editor` agent |
| Deterministic checks | `npm run validate`; `npm run evidence -- articles/<slug>.md`（deviations 0、公開直前は `--online` も） |
| Title | 原則 50 字以内、正確さに必要なら 60 字まで |
| Publish handoff | `zenn-format` → `publish-article` |
| AI 開示 | Zenn は適用外（2026-08-23 著者判断） |

slug 案: `instrument-consumption-plan`（確定はタイトル決定時）。

## Editorial brief（着手時に著者確認で止まる）

```markdown
Reader: エージェントに書かせたコードベースが膨れ、lint と dead-code 検出を
        すでに入れているのに行数が減らない人。「次に何を検査すればいいか」を探している

Channel: Zenn（articles/*.md）

Central thesis:
  消費者のいない読み値は、到達性を測る検査には原理的に映らない。
  畳むかどうかを決められるのは「誰が・何回読んで・何を決めたら降ろすか」だけで、
  それは事後の検出ではなく新設時に書かせるしかない。

Causal spine:
  観察: レビューを減らし複雑度 lint を入れた翌日も、コードは膨れたままだった
    → 緊張: repo 自身の dead-code intake は候補 0 件、ruff も 0 件。なのに翌日
            2,065 行が「消費者ゼロ」で消えた。しかも lint の drain は +815 行増やしていた
    → 機序: 検出器が測るのはシンボルの参照であって読み値の消費ではない。
            テストが厚いほど検出されなくなる（設計上 scan path に tests/ を含むため）。
            「読んだ人間が誰もいない」ことはどのシンボルにも現れない
    → 判断則: 消費計画（読み手 / 判断に要る読み回数 / 満了時の撤去条件）を新設時に
            書かせ、書けないものは受理しない。新しい機構は作らない

Selected evidence:
- C2  週次 dead-code intake が削除直前 rev で候補 0 件 … 緊張の核。開きに置く
- C1  a06c6be の内訳（912+726+296+129 行、−2,065 / .py −1,934） … 消えた実体
- C4  同 3 ファイルに ruff（C901 込み）→ All checks passed! … 検出漏れが 1 ツールの癖でない
- C3  vulture 素の出力は 60% confidence の未使用ローカル変数 1 件だけ … 同上
- C5  C901 drain が .py を +815 行増やした … 「入れた lint は別の量を最適化していた」
- C17 dead_code_scan.py docstring（scan-wide, report-narrow） … 検出漏れの機序
- C7  ADR 99 本中 Review-when を持つのは 4 本 … 非対称の実測
- C16 coselection_families.py は「出力がちょうど 1 回読まれた」計器 … 消費者の定義
- C11 ADR-0101 Decision 1 の (a)(b)(c) … 判断則そのもの
- C12 Decision 6「機構を作らない」 … 前 2 記事の「増やさない」路線との接続
- C13 Decision 2（Review-when 内の Consumption plan 小見出し、登録簿を作らない）
- C14/C15 tranche 全体の Before/After … 効果の実測（誇張しない材料）
- C10 ADR-0097 の建立 +6,355 / 退役 −5,672 … 「効かない場合」節の自己批判に使う

Out of scope:
- C23 RFC-0017 の skill listing 降ろし（常駐コスト軸。消費者ゼロではない）
- C20 51 agent workflow の中身（agent 出力は一次証拠に数えていない。存在の 1 行のみ）
- C9  成長窓 +64,541 行（ADR-0101 自身が「計器が総量を支配するとは言っていない」と
      限定している。使うなら背景 1 文まで）
- C21/C22 台帳 withdrawn と skill 縮退（最後の 1 段落だけ）
- ADR-0100（chaos-TDD mandate 退役）— 別の問いなので触れない
```

## 構成案（各節に因果線上の役割を 1 つだけ）

具体物を先、説明を後。各節に採用 evidence を紐付ける。

| # | 節 | 役割 | 具体物（先頭に置くもの） | evidence |
|---|---|---|---|---|
| 1 | 削除の前日、検出器は 0 件と答えた | 緊張の提示 | `dead_code_scan.py` の JSON 出力（`"count": 0`）と、翌日の `git show --stat`（−2,065） | C2 / C1 |
| 2 | 前編で機械に振ったものが、指されていなかった | 前提の接続（前編リンクは本文 1 回） | 前編の分類表から「未使用コード → 機械」の 1 行を引用 | — |
| 3 | 上限を刈ったら、行が増えた | 反証その 2 | `git show --numstat 009baee -- '*.py'` → +1,901 / −1,086 | C5 |
| 4 | 検出器は何を測っているのか | 機序 | `dead_code_scan.py` docstring の "Scan-wide, report-narrow" と、ruff / vulture の出力 | C17 / C3 / C4 |
| 5 | 消費者は静的に現れない | 機序の一般化 | 「出力がちょうど 1 回読まれ、数値は ADR に凍結された」計器の実例 | C16 |
| 6 | 建立は必須で、溶解は任意だった | 非対称の実測 | ADR 99 本中 4 本という grep の結果 | C7 |
| 7 | 新設時に 3 つ書かせる | 判断則（Solution） | 消費計画 (a)(b)(c) の実物と、拒否のされ方（draft が理由 1 行つきで未受理のまま留まる） | C11 / C13 |
| 8 | 機構を作らないことが条件だった | 前 2 記事との接続 | Decision 6 の原文 | C12 |
| 9 | 何行減ったのか | 効果の実測 | tranche の Before/After 表（94,882 → 92,723 等） | C14 / C15 |
| 10 | この判断が効かない場合 | 正直さ | ADR-0097 の +6,355 / −5,672、ADR-0101 自身の限定、遡及棚卸し T4 が未到来 | C10 / 台帳の未解決節 |
| 11 | 自分の環境に移すなら | Higher Ground | 読者が自 repo で回せる手順（「読み手を名指しできない読み値」を数える） | — |

- 節 11 の末尾に、skill・台帳へ同じ判定が効いた話を **1 段落**だけ（C22 / C21）
- 節 1 と節 3 は再現コマンドをそのまま置く（台帳の「コード・コマンド例」節がそのまま使える）
- 1 節が全体の 30% を超えないこと。節 7 が厚くなりやすいので注意

## 執筆・受け入れチェーン

`writing-ecosystem` の canonical workflow に従う。

1. **theme-reviewer** — 選択済みの問い一文 + 台帳を渡し、非自明性・外部言説との差分の findings を受け取る（合否は出ない）
2. **editorial brief を著者へ提示 → 確認で停止**（上の brief 案がたたき台）
3. **outline → 初稿** — `articles/<slug>.md`。frontmatter は `zenn-format` が正本、`published: false` で開始
4. **構造凍結 → review panel**（並行）
   - `editor`（Zenn の channel editor）
   - `prose-clarity-reviewer`
   - `fact-checker` — C26 / C27 を含む主張リストを渡す
   - `codex-review`（著者が明示指示したときのみ。実行不能なら理由と fallback を記録）
5. **機械検査** — `npm run validate`、`npm run evidence -- articles/<slug>.md`（deviations 0）
6. **著者が本文通読 → 内容 GO**
7. **タイトル** — `headline-craft` で候補生成 → `title-reviewer` の findings → 著者が選択（50 字以内、必要なら 60 字）
8. **`quality-gate <file>`** で証跡集約
9. 著者の公開 GO → `zenn-format` → `publish-article` → `npm run generate:index` → `npm run validate` && `npm run check:index`
10. **EN** — JP 確定後に `prose-translation` → `devto-translator` → `publish-article`

## 着手前に潰す項目

- [ ] **前編の公開状態を確認する。** `articles/lint-as-subtraction.md` は repo 上まだ `published: false` だが、著者が 2026-08-30 に Zenn 上で手動公開した。repo をこのまま push すると Zenn 側の記事を非公開に戻す可能性がある。**本記事の作業より先に**、前編の frontmatter（`published: true` + `published_at`）と `scripts/schedule.json` / `docs/PUBLICATIONS.md` を実態へ合わせる。同じ状態の `articles/review-chain-damping.md` も確認する
- [ ] **C26 を再測定するか引用に落とす。** ADR-0101 の「週次機構 17,769 行」は scripts 側だけ live 一致（5,975 + ヘルパー 179）。src / tests の内訳は未再現。本文で使うなら再測定し、使わないなら落とす
- [ ] **C27（外部言説）を埋める。** 「AI レビュー連鎖でコードが増える」現象の先行事例を未収集。`theme-reviewer` か `fact-checker` の WebSearch で as-of 日付つきに当てる。差分が出ないなら中心命題を「自 repo の 1 事例」として明示的に限定する
- [ ] **本文中の self-link は 1 記事 1 回まで。** 前編リンクは節 2 に置き、それ以外（contemplative-agent repo、ADR）は末尾の関連リンク / References へ寄せる
- [ ] **末尾の関連リンク 2 行**（Markdown 正本 + 著者 GitHub）を忘れない

## 検証

- `npm run evidence -- articles/<slug>.md` が deviations 0（公開直前は `--online` も）
- `npm run validate` が通る
- 台帳の再現コマンドを記事に載せる場合、載せた形のまま実行して出力が一致することを確認する（特に節 1 の `dead_code_scan.py` と節 3 の `git show --numstat`）
- `quality-gate` が PASS
- 公開後: `npm run generate:index` → `npm run check:index` に drift なし、commit を push（未 push だと Zenn の予約に届かない）
