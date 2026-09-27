# 人間ゲート第 2 軸（ADR-0019）の Zenn 記事化

## Context

`drafts/article-context_human-gate-second-axis_2026-07-26.md`（証拠台帳）に、
2026-07-25〜26 に `~/.claude` ハーネスで行った「ヒューマンゲートの第 2 軸」導入の一次資料が揃っている。
中身は ADR-0019 + `rules/common/human-gate.md` 新設 + codex による cross-model review の指摘 5 件。

この素材が読者に効くのは、**AI にコードを書かせる量が増えて「コミット前に diff を全部読む」が
現実的でなくなった一方、では人間が何を承認するのかに定説がない**という問題があるため。
台帳の中心的発見は「ゲートには 2 軸ある——**いつ**止まるか（可逆性）と、止まったとき人間は
**何を**判断するか（層）。後者に正本がないと、各所が勝手に空白を埋めて『diff 承認』に落ちる」。

成果物は、**人間ゲートで何を提示させるかを対象から機械的に決める判定表**（読者が自分の
ハーネス／チーム規約にそのまま移植できる形）。ケーススタディではなく how-to 軸（ユーザー確定）。

今回のスコープ: **JP 記事の執筆 + レビュー通過まで**。`published: false` で止める。
EN 翻訳・`schedule.json`・push は別ターンで判断（ユーザー確定）。

## 独立論点（4 つ = zenn-practical-writing の上限内）

1. **症状** — 軸に名前がないと空白が「diff 承認」で埋まる（第 2 介入点の正本が 2 つに割れ、
   artifact 検査の残滓が 5 箇所の skill に独立発生）
2. **判定表**（記事の成果物） — 提示物は対象で分岐する
   - behavior-shaping artifact（rules / skills / identity / 公開ドキュメント）→ **本文**
   - control plane（hooks / permissions / `--allowedTools` / scheduled task 定義）→ **本文**
   - 実装コード・生成物 → **意図の要約**（diff 本文と PASS 一覧は出さない）
   - 決定論ゲートの FAIL → **例外。検出行そのものを提示**
3. **落とし穴 2 つ**（cross-model review が検出した設計の穴）
   - control plane を「実装コード」側に置くと、secret-scan hook の無効化が
     「検査を強化しました」の一文に隠れる
   - 「PASS 一覧も diff も出さない」を徹底すると、secret scan の偽陽性判定
     （`SECRET_SCAN_BYPASS`）の経路まで潰れる → FAIL 例外が必要になった
4. **意図の要約は plan と照合する** — 自由記述として読ませない。照合先を人間由来の referent
   （介入点 1 で承認した plan）に固定しないと、人間は提案者の自己申告を検証することになり、
   gap が artifact 層から語りの層へ移るだけ

## 記事の構成（articles/human-gate-intent-not-diff.md）

```
frontmatter: type tech / published: false / emoji 🚦
> この記事でわかること: 1 行

導入（読者の壁 3 点の箇条書き）
  - AI の出す diff の量に人間のレビューが追いつかない
  - では人間チェックをやめるとして、何を承認すればいいのか決め手がない
  - 結果「一応 diff を見せる」に落ち着き、実際は読まれないゲートが残る

## 前提（Claude Code 2.1.220 / 自作ハーネス構成 / 手順は規約の書き方なのでツール非依存）

## ゲートには 2 軸ある（いつ止まるか / 何を判断するか）
   - 既存の可逆性軸だけでは提示物が決まらないことを表で示す

## 症状: 軸に名前がないと「diff 承認」で埋まる
   - 正本 2 分裂の実物（planning.md「Verify 結果確認」vs implementation-chain「diff 承認」）
   - 5 箇所の残滓の一覧表（何が artifact 検査だったか）
   - 起点は対象を規定しない一文だったこと

## 判定表: 提示物は対象で決める  ← 成果物
   - 4 行の表 + 判定の一言ルール
   - 実際に rules ファイルに落とした本文（36 行の rule から該当部を引用）

## 落とし穴 1: control plane を実装コード扱いにすると検査を緩める変更が隠れる
## 落とし穴 2: 「PASS も diff も出さない」は偽陽性判定の経路を塞ぐ
   - :::details に codex 指摘の原文（P1）を置く

## 要約は自由記述にしない（plan と照合する）

## まとめ（次にできること）— 自分の規約に移植する 3 ステップ
## 関連リンク（ADR-0019 / AKC repo / GitHub ハブ = github.com/shimo4228 必須）
```

図/表は 3 点（2 軸の対比表・残滓 5 箇所の表・判定表）。

## 事実の扱い（台帳の tier に従う）

- 記事に書くのは **一次 tier のクレームのみ**（C1〜C12, C14, C15）。数値は執筆時に再実測する
  （`wc -w`, `git show --stat d16b41a`）
- **C13（companion paper §2.1(b) の引用文字列）は未検証** → 論文の**文言を引用しない**。
  paper は「関連リンクでの参照」に留め、記事の論証は ADR / rule / commit のみに依拠させる
- AKC commit `14c995b` の diff 本文は未読 → 「glossary を sharpen した」までに留め、
  graph.jsonld 更新には言及しない
- ユーザー発言の逐語引用は台帳の「逐語抜粋」節から（表記ゆれ含め原文ママ、引用ブロック）

## タイトル

執筆後に `/seo-optimizer`（→ global `headline-craft`）で確定。ベネフィット前置型・50 字以内。
たたき台:
- 「AI の diff を人間が読む時代は終わった——承認ゲートで何を見せるかの判定表」
- 「diff 承認をやめる——AI エージェントの人間ゲートで提示物を対象別に決める」

## 実行手順

1. 台帳の一次ソースを再確認（`~/.claude/rules/common/human-gate.md` 本文、`git show --stat d16b41a`、
   `wc -w ~/.claude/rules/common/*.md`）— 数値クレームはライブ実測を正とする
2. `articles/human-gate-intent-not-diff.md` を **Claude Code 本体が直接執筆**
   （`.claude/skills/zenn-practical-writing/SKILL.md` の実用軸 5 ルール・ですます調に従う。
   サブエージェントには委譲しない）
3. 自己プリフライト（同 skill Phase 3 のチェックリスト：論点 4 以下・AI slop・段落密度閾値・用語初出）
4. レビューを**並列**で起動: `editor` / `fact-checker` / `zenn-clarity-reviewer`
5. 指摘を反映。`zenn-clarity-reviewer` が FAIL なら PASS するまで改稿（公開ブロック条件）
6. `/seo-optimizer` でタイトル・topics・emoji を確定（Distribution 層のみ。本文は変えない）
7. `npm run validate` で frontmatter 検証
8. 記事本文をユーザーに提示して意図確認（公開ドキュメント = behavior-shaping artifact なので
   要約ではなく本文を出す。奇しくもこの記事の主題どおり）

## 触るファイル

- 新規: `articles/human-gate-intent-not-diff.md`（唯一の成果物）
- 読むのみ: `drafts/article-context_human-gate-second-axis_2026-07-26.md`,
  `~/.claude/docs/adr/0019-human-gate-layer.md`, `~/.claude/rules/common/human-gate.md`
- 今回は触らない: `articles-en/`, `schedule.json`, git commit / push

## 検証

- `npm run validate`（Zenn frontmatter 検証。機械チェックはこれのみ — prose lint は 2026-07 撤去済み）
- `npm run preview` で表・引用ブロック・`:::details` の表示確認
- `zenn-clarity-reviewer` の verdict が PASS であること
- 記事中の全数値が実測コマンドの出力と一致すること（`wc -w` / `git show --stat`）
