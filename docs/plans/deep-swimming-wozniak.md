# devto-translator に brief と著者の指摘を渡す版を replay で採否する

調査 report: [research/2026-10-26-translator-packet-replay.md](research/2026-10-26-translator-packet-replay.md)

## Context

この plan は、subagent を主ループへ畳むかを問う grill-me（2026-10-26）の決定から来ています。

- Q1: 畳む・統合する agent だけ、凍結稿と処分記録を replay する回帰 gate で判定する
- Q2: 閾値は置かない。反転の一覧を著者が見て決める。指摘ごとに「他の reviewer も挙げていたか」の列を付ける
- Q4: devto-translator は subagent のまま残す。brief と `drafts/<slug>.corrections.md` を渡す版を作り、replay で今の版と比べる
- 著者:「translator の replay は plan に回す」

今の translator が受け取るのは JP 記事の path だけです（`.claude/agents/devto-translator.md:13-15`）。過去 3 本の EN 稿では、editor が確度・帰属のずれを 3 件挙げ、著者が採りました（report 内部 2）。harness-scope M1 は「分かってきた」が "I found that" になった件、readme M2 は「はず」が "should" になった件、skill-description M3 は締めが命令形になった件です。readme M1（"Still,"）が境界例です。4 件とも必要な情報は JP 本文にあり、背骨 1 も常駐していました。brief と corrections が足すのは「この箇所を保て」という名指しです。この名指しで drift が減るかを、今の版との replay で確かめます。

採用 39 件のうち 26 件は英語の言い回しの指摘です。全件の反転表にすると、言い回しの揺れが一覧の大半になります。そこで、主な物差しは既知の 4 箇所に絞ります。

## 比べる 2 つの版

定義ファイルは書き換えません。どちらの版も今の `devto-translator` を Agent tool で呼び（production と同じ経路）、dispatch の文面だけを変えます。

- **base**: JP の path だけを渡す（今の版）
- **packet**: JP の path に加えて、brief と corrections の path を渡す。「参照だけに使い、EN 稿には JP 稿にある内容だけを載せる」の 1 文を足す

2 つの版に共通の指示です。「Phase 1 と Phase 4 だけを行う。保存先は `drafts/replay-translator/<slug>/<arm>-<n>/articles-en/<slug>.md`。Phase 1.5・2・3・5 は行わない」。こうすると production のファイル（`articles-en/`、`schedule.json`、`images/`）は書き換わりません。各バッチの後に `git status` を見て、tracked file に差分が無いことを確かめます。

## 入力（翻訳時点の版にそろえる）

| 記事 | JP | brief | corrections |
|---|---|---|---|
| harness-scope-writing-harness | b62de14 | 0be7292 | C1〜C7（C8 は EN の後に足された図の項目なので外す） |
| readme-human-llm-fold | c989a61 | ebf0cc0 | C1〜C7 |
| skill-description-pointer | 87c27dc | 0630f10 | C1・C2 |

`git show <sha>:<path>` で `drafts/replay-translator/<slug>/input/` に写します。`drafts/` は gitignore の下にあるので、replay の出力も corrections の写しも公開されません。

## 回し方

1. 記事 3 本 × 2 版 × 3 回で translator を 18 run 回す。Agent tool の background で並べる。返答は保存した path だけにする
2. 出力の 18 本それぞれに editor を 1 回かける（18 run）。dispatch の文面は 1 つのテンプレートに固定する: 稿の path、翻訳時点の brief の path、AI が本文を書いたこと、channel は Dev.to。どちらの版の出力か、replay であること、過去の指摘は渡さない。editor の report は `drafts/replay-translator/<slug>/<arm>-<n>/editor.md` に保存する
3. 混入の検査を全 18 本に機械でかける: C 番号（`\bC[0-9]+\b`）、「台帳」、`drafts/`、JP 稿に無い数値。今の EN 3 本は 0 件なので、これが基準線になる
4. 一覧を 1 枚にまとめる（下の「著者が見るもの」）

`claude --version` と、editor が実際に走った model を記録します。

## 著者が見るもの（`drafts/replay-translator/summary.md`）

1. **既知の 4 箇所**: 4 箇所ごとに、6 本の出力の該当文を並べます。私が drift の有無に下書きの印を付け、著者が判定します。反転の数え方は Q1 と同じです。base で 2/3 以上に drift が出て、packet で 1/3 以下なら改善とします。「他の reviewer も挙げていたか」の列は、EN 段で走る reviewer が editor だけなので、JP 段の panel が同じ箇所を挙げていたかで代えます（4 箇所のうち該当は skill の「ほど」だけです）
2. **packet で新しく出た指摘**: editor の MEDIUM 以上の指摘のうち、packet で 2/3 以上に出て、base で 1/3 以下のもの。同じ指摘かどうかは、指す段落と中身で私が束ねます
3. **混入**: 検査に当たった行を、版と run ごとに全件並べる

閾値は置きません（Q2）。採否は著者がこの一覧を見て決めます。

## 採ったときの変更（採否の後、別 commit）

- `.claude/agents/devto-translator.md` の「入力」に、brief（`docs/plans/<slug>.md`）と `drafts/<slug>.corrections.md` を足す。参照だけに使い、EN 稿には JP 稿の内容だけを載せる、と書く
- Phase 4 のセルフチェックに、混入の検査（上の 3）を 1 項目足す
- `publish-article/SKILL.md:87` で translator を呼ぶ箇所に、2 つの path を渡すと書く

採らないときは、replay の結果を Q4 の決定への注記として共有ノートに残し、定義は変えません。

## 決定

- **corrections の渡し方**: 推奨は「全文の path を渡す」です。Q4 で決めた形のまま測り、混入は手順 3 で数えます。混入が出たら、「対象・修正後・Expect だけを抜いた写し」で packet を回し直します。ただし Expect にも本文に載せない数値があります（readme C4）
- **実行者の決定**: 推奨は「この session」です。replay の実行と一覧づくりで、コードの実装はありません。採ったときの定義の変更は散文 3 箇所です

## 変えないもの

- JP 段の panel・editor の定義・prose-translation skill（ADR-0013 / ADR-0015 の観測期間）
- translator を主ループに畳む案。replay では長い session の文脈を再現できないので、測れません（grill-me Q4 で外しました）
- Phase 1.5・2・3・5（図・タグ・cover・schedule.json）。訳文の外にあるので replay しません
- 39 件の言い回しの指摘の反転表。名指しの効果とは別の揺れが大半になるので作りません

## 検証

- 18 + 18 run の後で `git status` を見て、tracked file に差分が無いこと
- `drafts/replay-translator/` に 18 本の EN 稿と 18 本の editor report があること
- summary.md の 4 箇所の表で、各セルが出力の実在する行を引いていること
