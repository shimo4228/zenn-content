# ADR-0010: チャンネルの値は常駐層に 1 箇所だけ置く

## Status

Accepted

## Date

2026-08-23

## Context

著者から症状の申告があった — 「どの記事を書く場合でも collect-context で zenn-content にコンテキストを集めるから、note や Substack でも zenn-content で書いている。そして writing-ecosystem がグローバルに存在するので、そっちの規約で書いてしまったりして動きが読めないし、執筆規約があまりにも多すぎる」。

執筆スキル 27 本に skill-stocktake（Phase 0–3、fresh-context 4 agent）を実施し、その後 agent 定義 6 本・`refs/` 3 本・ADR 9 本を対象にした掃引 3 本を追加した。初回の棚卸しが skill だけを対象にしていたことが最大の盲点で、最も重い欠陥はその範囲外にあった。

**機構（実測で 2 度訂正した）**:

- 執筆はすべて cwd = zenn-content で起きる。セッションログで note/substack に言及したセッションは zenn-content cwd に 50 件（同 cwd 全 57 件中）で、note/Substack 執筆用の別 cwd は 0 件。したがって global / project の二層は「発火の分離」として機能していない。
- 常駐するのは rules / CLAUDE.md **と全 skill の `description:`**。skill / agent の本文は発火時ロードで、description 競合に勝った 1 本だけが載る。agent プロセスにも rules / CLAUDE.md は載り、agent 本文はその agent には必ず全文載る。
- 当初「値を持つ skill が発火しなかった」と診断したが誤りだった。実際は **2 つの矛盾する値が両方とも常駐していた** — `zenn-practical-writing` の description 末尾「思索エッセイ（だ/である × 発見調）は Substack corpus へ」（2026-08-12 の note=JA 正本 逆転前の stale）と、`writing-ecosystem` の description「note/Zenn = ですます」。

**実害（corpus に残っていた唯一の証拠）**: 2026-08-12 に作られた note 原稿 3 本のうち、レビューを通した `ai-desire-exhaustion.md` だけが ですます（115/1）で、通さなかった `context-severance-brainstorm.md`（0/8）と `ideation-pharmacology.md`（0/21、貼付直前の `.note-paste.md` まで到達）が だ/である にドリフトした。

**欠陥の分布**: 検出した矛盾・重複は 26 件。全部が「同じ値が 2 箇所にあり片方が古い」型で、原因は (a) canon 側にだけ defer があり subordinate 側に無い、(b) subordinate が defer を宣言しながら本文で再掲した、のいずれか。文体規約だけで 11 ファイル 28 箇所に散っていた。agent 6 本のうち 5 本が「正本」を宣言しながらその正本の値を抱えていた。

## Decision

1. **チャンネルの値は `.claude/rules/zenn-writing.md` の「チャンネル表」1 箇所だけに置く。** 文体・声・置き場・既定 skill・レビュー agent を 4 チャンネル（Zenn / Dev.to / note / Substack）× 5 列の表にする。rules は main loop にも全 agent プロセスにも常駐するので、どの skill が発火しても値が届く。skill / agent / CLAUDE.md は値を持たずここを指す。

2. **global skill は genre 中立 canon に純化し、チャンネルの値を持たない。** `writing-ecosystem` は AI slop 禁止・craft・段落密度・専門用語の緩和策・タイトル原則・エッセイ 4 段構成・初稿手順を持つ。語尾・出力先・レビュー agent の割り当ては持たない。値を持たなければ競合しようがない。

3. **`description:` にチャンネルの属性を書かない。** description は常駐するので、短く目立たないのに必ず効く — 最も安く矛盾を仕込める層だった。スコープ語だけを書き、文体・語尾は書かない。

4. **binding な判定閾値は、判定を出す側（agent 本文 / 検査コード）が持つ。** agent 本文はその agent に必ず全文載る保証つき層で、skill 本文は description 競合次第の無保証層。保証の高い層から低い層へ値を降ろさない。造語閾値は `zenn-clarity-reviewer`、出典ブロックの構成規則は `fact-checker`、エッセイ 4 段の検査と論点数は `essay-reviewer` が持つ。

5. **「同じ記述に揃える」は採らない。** 揃えた瞬間は両方正しいのでレビューで差が見えず、次の改定で必ず分岐する（`devto-translator` のエラーリカバリ表、`schedule.json` の `date` 7 件不一致が実例）。正本を 1 つ決めて他は削除・統合・ポインタ化する。

6. **消費者が 1 つならポインタでなく統合する。** 消費者が 1 つなのに正本を外に置くと、消費者は必ず手元にコピーを作る — 取りに行くより手元にある方が確実だからで、defer の宣言を何回書いても守られない（`refs/translation-rules.md` は「唯一の正本」を 3 回宣言して 3 回とも破られていた）。`series-checker` → `zenn-editorial-judgment`、`refs/translation-rules.md` → `devto-translator` を統合し退役させた。

7. **ポインタは命令形で書く。** 「正本は X を参照」は宣言であって指示ではなく、読み手に読む義務が発生しない。命令形（「先に必ず読む」）で書いた `article-judge` だけが値の複製を持たず、「参照」と書いた 3 agent は全部コピーを持ち 2 本が既に分岐していた（ADR-0018 の「自発発火は文言改良で伸びない、命令形で配線する」と同じ処方）。

8. **`publish-article` は品質ゲートを持たない。** レビュー panel とタイトル確定は `writing-team` step 7 / 12 の劣化コピーだった。ゲートを持たなければ単独パスで飛ばしようがない。責務を公開作業（セキュリティ・frontmatter・`published_at`・スケジュール登録・索引再生成）に限定する。

9. **再発防止の書式（意図的分岐の注記 / drift 時の tiebreaker）は採らない。** 「注記があるクラスタは矛盾ゼロ」という相関は**監査曝露で交絡**している — `readme-writer:146` の「将来の stocktake が逆修正しないこと」は監査を受けた後に書かれた傷跡で、予防効果の証拠ではない。加えて tiebreaker はコピーが残っている前提の保険で、コピーを消せば不要。21 箇所に注記を足すのは「規約が多すぎる」と申告された project に 21 行の規約を増やすことでもある。意図的分岐の注記は、分岐が本当に意図的な稀なケースにだけ使う。

## Review-when

- **執筆の cwd が分かれたら** — Context の前提 1 が消える。研究 repo で直接エッセイを書く運用に変わったら、global/project の二層は再び発火分離として機能するので本 ADR を見直す。
- **チャンネルが 5 つ目に増えたら** — 「project の rules がチャンネルの値の唯一の置き場」の負荷が変わる。
- **`collect-context` の集約先が変わったら** — 前提 1 の根拠が消える。
- **skill / rules のロード機構が変わったら**（rules が常駐でなくなる、skill 本文が常時載る等）— Decision 1・3・4 の全根拠が Context の機構記述に乗っている。

## Alternatives Considered

- **プラットフォーム別に repo を立てる**（zenn / note / substack）— 却下。この repo は `CITATION.cff` と SWHID を持つ governed essay corpus で、membership 規約が「著者の声で書かれ公開されたエッセイ」を 1 つの artifact として束ねている。チャンネルで割ると corpus の単位が壊れる。かつ症状の原因は description 競合で canon が単独で勝つことなので、repo を分けても解決しない — global canon は分割後も discoverable で、project 側の補正が消えるぶん悪化しうる。Codex の反証（分割で失われるのは project skill であって global canon ではない）を受けて当初の却下理由「defer が弱まる」は撤回し、この 2 点に差し替えた。
- **用途別（声 / 評価 / 配信）のサブフォルダ化** — 却下。`.claude/skills/` は `<name>/SKILL.md` のフラット名前空間で束ねる手段がない。用途の 3 層は索引 1 枚で表せる。
- **`writing-ecosystem` を zenn-content へ移す** — 却下。`readme-writer` / paper ライン / `x-draft` / `public-comment` が canon として参照し、いずれも zenn-content 以外の cwd で発火する。
- **note 用 skill の新設 / `zenn-practical-writing` の一般化** — 却下。どちらも「値は skill に住む」という前提から出ていた。値を常駐層へ移せば note の値はどの skill が発火しても既に context にあるので、skill は要らない。
- **執筆セッションだけチャンネル別 cwd に置き完成稿を中央 corpus へ同期する**（Codex の代替案）— 保留。corpus governance の単位と衝突する。cwd が実際に分かれる運用に変われば Review-when で再検討する。
- **検出した 26 件を全部直す** — 部分的に却下。architect の zero-base 判定（「今日この瞬間、著者の申告だけを知っていたら、どの編集に金を出すか」）で 21 件中 6 件まで絞られた。ただし削除とポインタ化は実害の証拠がなくても症状（規約が多すぎる）に直接効くので残し、**ゲート項目の追加**（単独パスに fact-checker 等を足す案）だけを捨てた — 使用記録 0 件の投機的な追加で、症状に逆行する。

## Consequences

**良い方向**:

- チャンネルの文体の実値を持つ箇所が 11 ファイル 28 箇所から **1 箇所**になった。どの skill が発火しても値が届くので、「どちらの規約が効くか」が決定的になる。
- skill が 2 本（`series-checker` / global の `substack-publishing` 降格）、refs が 1 本（`translation-rules.md`）、`learned/` が 1 フォルダ（4 件）減った。`publish-article` は約半分が落ちた。
- 常駐総量はほぼ変わらない（チャンネル表 +6 行 / `CLAUDE.md` の用語表 −7 行）。やったのは「常駐への集中」ではなく**非常駐側のコピーの削除**。後続の stocktake が「rules が肥大した」と誤読しないよう記録しておく。
- 副産物として実害が 2 件直った — 予約投稿のレートリミット（`publish-article` が「カウントされない / 何本でも事前 push OK」と実測の正反対を書いており、従うと予約が丸ごと落ちる）と、`essay-reviewer` が note 担当なのに「だ/である でなければ不合格」を持っていた件。
- `writing-team` Mission B に binding 最終判定が無く、改稿記事が `quality-gate` の第 1 必須項目を構造的に満たせなかった配線漏れも塞いだ。

### 実装後の追記（2026-08-23、検証プローブの実測）

**Decision 4 の適用に 1 件の例外が要った。** 「binding な判定閾値は判定を出す側が持つ」を
論点数の上限に適用して `essay-reviewer` を正本にしたが、**判定を出す側は 1 つとは限らない**。
Zenn/Dev.to のレビュアーは `editor` で、`editor` に論点数のチェックは無い。
`zenn-practical-writing` から値を落とすと Zenn チャンネルがこの規則を丸ごと失う。
`editor` に検査項目を足すのは §Alternatives が却下した「投機的な追加」にあたる。
→ **意図的な二重化として両方に残し、双方に「片方だけ動かさない」の相互注記を置いた。**
Decision 4 を適用する前に「**その値を使う判定器が全チャンネル分そろっているか**」を確認する。

**値を撤去したら、下流の「由来」ポインタも一緒に見る。** `writing-ecosystem` から論点数の
実値を撤去した結果、`essay-reviewer:103` の「由来: `writing-ecosystem`「Section Length
Guidelines」」が**もう値のない場所を指す**状態になった。撤去は「そこに値が無くなる」だけでなく
「そこを指していた参照の意味が変わる」ので、Decision 7（命令形ポインタ）と同格の実測として
記録する。

**構造で切る編集は、コードブロック内の見かけの構造に騙される。** `zenn-format` の
Article Structure Patterns を「次の `## ` 見出しまで」で削除したところ、削除対象の
テンプレート本体が code block 内に `## 背景` をリテラルで含んでいたためそこで止まり、
半分が残って fence 対応も崩れた。**編集の意図ではなく結果を、独立した目で再検査する**
（この欠陥は自分の grep では 1 件も見つからず、突き合わせ agent が全件検出した）。

**コスト・リスク**:

- 値を探すとき「まず rules のチャンネル表」という一段階が増える。常駐しているので読むコストは 0 だが、書き手が「skill に書いてあるはず」と思い込むと迷う。`writing-ecosystem` の「値の所在マップ」がその索引を担う。
- agent 本文に値を置く決定（Decision 4）は、書き手（skill 側）から閾値が見えなくなる。質的規則は skill、数値は agent という役割分担で読めるようにしたが、境界の判断が要る。
- 既存の note 原稿 2 本（`context-severance-brainstorm` / `ideation-pharmacology`）は だ/である のまま残る。**原稿の文体変更は内容の変更**（ADR-0001）なので著者の判断領域とし、本 ADR では扱わない。
- 本 ADR が正しいかは「次に書く note 原稿が ですます で出るか」で決まる。機構上は発火の当たり外れに依存しないはずだが、実地で 1 回確認する。

## Related

- [ADR-0001](0001-content-integrity-principle.md) — Content Integrity（原稿の文体変更を著者領域とする根拠）
- [ADR-0003](0003-zenn-practical-channel-axis.md) — チャンネル軸の確立。§2 の channel 表は本 ADR で supersede（注記済み）
- [ADR-0006](0006-authorial-values-and-editorial-judgment-skills.md) — 「片方がもう片方を再掲し始めたら統合を再検討する」の自己監視条項。装置の定義が 3 箇所に分裂したことでこのトリガーが発火した
- [ADR-0008](0008-two-tier-eval-and-revision-loop.md) — 二本立て評価。Mission B の binding 判定漏れは本 ADR で塞いだ
- [ADR-0009](0009-readme-routing-page-and-generated-publications-index.md) — 正本の分担（`published_at` 必須・schedule.json の位置づけ）
- `~/.claude/skills/writing-ecosystem/SKILL.md`「値の所在マップ」— 本 ADR の決定を実装した索引
