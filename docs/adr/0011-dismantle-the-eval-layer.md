# ADR-0011: eval 層を解体し、テーマはレビュアーに戻す

## Status

Accepted

## Date

2026-08-23

本 ADR は [ADR-0008](0008-two-tier-eval-and-revision-loop.md) の Decision 1・2・4 を supersede する。
Decision 3（品質バーの基準アンカー）は対象資産ごと消える。ADR-0004 の「新レビュアー追加基準」は維持し、
本 ADR の `theme-reviewer` 新設はその手続きに従う。

## Context

著者の申告（2026-08-23 の grill-me セッション）: 「eval が冗長。テーマ eval は eval に適さない。
記事の eval も手厚いレビュー群に対して冗長。**手順が複雑になりすぎ、評価基準の整合に時間がかかる**」。

棚卸しで次が判明した。

**1. 整合コストの発生源は「評価器の数」ではなく「評価器だけが agent に閉じていないこと」。**
`zenn-clarity-reviewer` / `essay-reviewer` / `fact-checker` は基準がその agent ファイル 1 つに閉じる。
一方 `theme-eval` / `article-judge` は skill + checklist + コード + ループ節 + ゲート条件の
**5 ファイルに分散**していた。同日午前の 3 コミット（重複潰し・自称の一本化・§A の薄化）は
すべてこの部分系が発生源で、**消費者 1 本の資産の内部整合に 1 セッションを使っていた**。

**2. `theme-eval` は最初から eval ではなかった。** Drop は構造上出せない設計（却下ゲートにしない、
ADR-0008 Decision 1）で、通した 2 本とも最終的に A見込み。**verdict が結果を変えた記録はゼロ**。
一方 Deepen の対話は 2 本とも効いている（欲望枯渇エッセイは反証調査で問いが 2 段深くなった）。
中身は執筆前の深化対話で、verdict は付属品だった。

**3. `article-judge` はゲートとして機能していなかった。** 実績 3 本の内訳 —
ai-code-half-year-audit で初回 Fix（K3 排他量化 2 系統 + 見出し循環）→ 改稿 → Publishable。
ai-desire-exhaustion は judge 通過後に**著者の通読が 3 件発見**。transcript-not-ledger は
**judge 2 回通過後に codex が素材との不整合 2 件を検出**。「通った = 大丈夫」が成立しておらず、
実態は 4 人目のレビュアーだった。8/12 の 3 件を見つけたのは judge ではなく著者の通読で、
通読 GO は最上位ゲートとして今も残る。

**4. K1-K4 は原則ではなく 1 日ぶんの欠陥パターン**（2026-08-12）。K1 as-of 整合は fact-checker が
既に publication date と supersession を見ており、K4 指示語の回収は clarity の内部文脈依存と同種。
K2 / K3 は手順を伴わなければ標語に劣化する。著者判断で全て破棄。

**5. checklist は執筆規約の忠実な写像ではなく、3 点で衝突していた。** 根因はチャンネルの概念を
持たないこと — この repo の分岐軸はチャンネル表（ADR-0010）なのに、Substack エッセイストの
単一チャンネル前提のまま「genre 中立」を名乗っていた:

- **B15**（主張を言い切れ / 両論併記に逃げるな）⇄ `zenn-practical-writing` の語りの表
  （essay = 問い化 / 実用 = 言い切り）と `zenn-authorial-values`「強い言い切りが逆効果になる感度」。
  essay に当てると、規約が求める発見調の問い化を「逃げ」として叩く
- **B5**（安っぽい N ステップまとめで終わるな）⇄ 実用 how-to の正当な結論（手順の言い切り）
- **B1**（具体的場面から入れ）⇄「一瞬でわかるは第一画面の機能要件」（結果駆動で先に渡す）

ADR-0008 が risk として挙げた「judge の好みへの文体収束（平坦化 Goodhart）」は、対策の対象ではなく
**checklist 自体に構造として埋まっていた**。

## Decision

1. **`theme-eval` skill を廃止し、`theme-reviewer` agent を新設する**。観点 T1-T8 と深化の問いは
   そのまま移すが、**verdict・ランク・希少性モニタは持たない**。出力は findings と深化の問いだけで、
   深めるか・上限を承知で書くか・取り止めるかを決めるのは著者。fresh context の別プロセスで走る
   （本体が自分のテーマを審査する self-preference を避ける）。
2. **`article-judge` agent を廃止し、K1-K4 を破棄する**。完成稿の評価は panel 4 本
   （チャンネル表のレビュー agent + fact-checker + zenn-clarity-reviewer + codex-review）
   + 著者通読に戻す。
3. **機構を削除する**: craft チェックリスト（`.claude/refs/kaguura-craft-checklist.md`）、
   `scripts/mechanical_checks.py` + テスト、`writing-team` の「改稿ループ」節、
   `quality-gate` の第 1 必須条件。checklist の消費者は article-judge のみ、
   mechanical_checks の消費者も article-judge のみで、判定器が消えると読み手がいなくなる。
4. **執筆側へ移す項目は無い**（照合済み）。§B の craft は `writing-ecosystem`「Craft 規約」
   「語りかけの積極形」「エッセイの 4 段構成」と `zenn-practical-writing`「導入の設計」に既にあり、
   書く側のほうが厚い（段落密度の閾値・専門用語の緩和策 7 種・各節末の「判定」手順は執筆側にしかない）。
   B13 は「体験談は解決の証拠として 1 段落に圧縮」が同義。**B15 は移してはいけない** — 上記の衝突のため。
5. **`title-eval` は維持する**。タイトルは唯一レビュアーが存在しない層で、判定器を置く根拠が残る。
   結果として、この repo の判定器は 3 本から 1 本になる。

## Review-when

- **著者通読を省く運用に変わったら** — 本 ADR の前提（最上位ゲートは人間の通読）が消える。
  自動判定を再導入する根拠が戻る。
- **panel 全通過の原稿に構造欠陥（as-of 不整合・継ぎ接ぎ・偽二分法）が再発したら** — Context 3・4 の
  「観点は panel で足りる」が反証される。その場合は ADR-0004 の手続きで**直交観点のレビュアー**を
  足す（judge 機構の復活ではない）。
- **公開ペースが週 5 本以上に上がったら** — 人間通読が律速になり、自動ゲートの費用対効果が変わる。
- **執筆規約がチャンネル分岐を廃止したら** — Context 5 の衝突 3 点が消え、genre 中立の
  チェックリストが再び成立しうる。

## Alternatives Considered

- **K1-K4 を既存 3 本のレビュアーに配る**（K1→fact-checker / K4→clarity / K2・K3→editor）—
  著者が却下。K1・K4 は既存観点と重複し、K2・K3 は 1 行に落とすと標語になる。editor は既に 6 観点あり、
  ADR-0004 が「観点を足すほど検出力が薄まる」として editor 統合を却下した先例にも反する。
- **`article-judge` を判定器からレビュアーへ変換し K1-K4 だけ持たせる（panel 5 本）** — 著者が却下。
  観点自体がトリビアルで、5 本目を正当化しない。
- **`mechanical_checks.py` を著者の任意ツールとして残す** — 著者が却下。消費者不在の資産を残すと、
  次の棚卸しでまた整合コストを払う。git 履歴から復元できる。
- **theme-eval の 8 問を `ideation` skill 内のチェック節にする** — 不採用。本体（＝書く側）が
  自分のテーマを審査する形になり、self-preference が構造的に効く。fresh context だけは残す。

## Consequences

- 良: 執筆前に走る評価器が 3 本 → 0 本（レビュアー 1 本に置換）。基準の置き場が
  「5 ファイル分散」から「agent 常駐 1 ファイル」になり、整合作業が消える。
- 良: 公開ブロック条件が 1 つ減る（editor CRITICAL 0 / clarity PASS は維持）。
  Content Integrity（ADR-0001）に対しても、判定器による文体の方向づけ経路が 1 本消える。
- 悪/リスク: 完成稿の欠陥検出は panel 4 本 + 著者通読に依存する。**KPI は通読指摘数**
  （`writing-team` に配線済み・memory `eval-harness-pipeline` へ記録）で、この数が増え続けるなら
  Review-when 2 番目が発火する。
- 削除した資産（skill 1 / agent 1 / refs 1 / コード 2）は git 履歴から復元可能。ADR-0007
  （Kaguura 原則の取り込み）は有効のまま — craft 原則は執筆側に翻案済みで、本 ADR は判定側の写像だけを消す。
