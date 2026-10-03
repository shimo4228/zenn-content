# 執筆用のハーネスを Claude Mods と output-style で組む（Zenn 記事）

## Context

2026-10-03 の 1 日で、harness-scope（repo ごとに Claude に見せる skill / agent / 指示ファイルを選ぶ Mod）と、
zenn-content の出力スタイル zenn-writing・profile zenn-writing を作った。証拠台帳は
`drafts/article-context_harness-scope-output-style_2026-10-03.md`。著者との対話で、素材の束は
「1 harness-scope + 2 出力スタイル」に決まり、中心命題を下の通り確定した。公開と審査（87 MB・credential hold）と
これまでの手（CLAUDE_CONFIG_DIR の記事など）は扱わない。

## Editorial brief（承認後 `docs/plans/harness-scope-writing-harness.md` に置く）

Reader: Zenn — 検索・feed から来た engineer が、数秒で用途を理解し再現または判断できる。著者の原文の読者像は未聴取（brief 確認時に足す）

Channel: Zenn（`articles/harness-scope-writing-harness.md`）

Author's words:
> Claude Codeで記事を書くのはclaude chatとは違うメリットがある。やはりスキルやルールと言ったハーネス設計がかなり自由だし、どのようなコンテキストを渡すかがかなり自由だ。ただし、code用のグローバルのハーネスや指示がコンフリクトするので、今まで色々な手を打ってきたが、外科的処置と留まっていた。、しかし、この度claude modsとoutput-styleを組み合わせればかなりタスク特化したハーネスが組めることがわかってきた。そこでまずはコードとは違う規約が求められる執筆タスクで作ることにした

Central thesis: Claude Code で記事を書く利点は、skill・rule・渡すコンテキストといったハーネスをかなり自由に組めること。
ただ、コード用の global のハーネスや指示とぶつかるので、これまで打ってきた手は外科的処置に留まっていた。Claude Mods
（repo ごとに Claude に見せるものを選ぶ）と output-style（話し方を決める）を組み合わせると、かなりタスク特化した
ハーネスが組めることが分かってきた。最初の 1 つとして、コードとは違う規約が要る執筆タスクで作った。
（確度は「分かってきた」のまま。「指示」は system prompt でなく global のハーネス側と読める書き方にする — C14）

Entry bridge: 執筆 repo（zenn-content）で Claude Code を開くと、Claude に見える skill 一覧は 101 件 26,551 字、agent 一覧は
38 型 18,988 字。そのうちこの repo 自身のものは 7 件と 7 型で、残りはコード用に育てた global のハーネスだった（C1〜C3）。

Figure plan: 内容 GO の後に埋める

Causal spine:
1. 観察 — Claude Code で書く利点はハーネスを自由に組めること。だが執筆 repo でも Claude の目に入るのはコード用の global（C1〜C3）
2. 緊張 — ネイティブ設定で外しても一覧は縮まない（3 件外して 26,551 → 26,534 字）、plugin の skill は残る（C4、C8）。1 段落
3. 機序 1（見せるもの）— Mod の profile で repo ごとに見せるものを選ぶ。主はこの repo の profile zenn-writing（deny 形式）:
   コード用の skill 49 件・agent 23 型・`testing.md`・`coding-style.md` を外し、ビルトインは残す（C25a。著者 11:35
   「仕様が変わると追従コストが大変」）。同梱の allowlist profile `writing` なら 101 件 26,551 字 → 7 件 1,623 字まで縮む、と従で添える（C1、C2）
4. 機序 2（話し方）— 出力スタイルで外すつもりだったコーディング指示は Claude 5 系には無かった（C14〜C16）。
   Opus 5.5 だけの結果の一般化を著者が止め、モデル別に取り直した（10:02）。著者「システムプロンプトは気にしなくていい。
   純粋に執筆用のリポジトリに適したOutput-styleを作ればいい」（10:10）→ 会話の規約 7 項目・526 字、リマインダーで届く（C18、C24）。本文 555 字が届くのは 1 ターン目だけで、以後は 95 字の名前の念押しだけ（C18a。履歴に残るかは未計測で書かない）
5. 著者の判断 — 見せるもの（Mod）と話し方（output-style）を分けて、執筆タスク用のハーネスを組んだ。決めなかったこと:
   他タスクへの展開、未確認の挙動（C12 の 9 回中 1 回の非読み込みは本文で正直に書く）

Selected evidence:
- C1・C2・C3: 観察と、機序 1 の従（同梱 allowlist の上限）
- C4・C8: 緊張（Mod にした理由）
- C25a: 機序 1 の主（profile zenn-writing の中身、2.1.288 で再取得）
- C14・C16: 機序 2 の発見（外す節が無い、変わるのは 1 行目だけ）
- 著者の発言 10:02 / 10:10 / 11:35: 判断の転回点
- C18・C18a・C24: スタイルの届き方と大きさ（本文は 1 ターン目だけ、以後 95 字）
- C17・C19: 読者の再現時の罠（plugin 同梱スタイルは名前空間付き、settings.local.json で外せる）
- install コマンドと `{ "profile": "zenn-writing" }`: 読者の再現導線
- C12: 限界

Out of scope:
- 公開と審査（C13、C26〜C32）、awesome-list・ルーティン・X 返信
- これまでの手（CLAUDE_CONFIG_DIR の記事、repo ごとの skill 配置、出力スタイル単体）— 著者「結局採用してないし、ほとんどが今日の話」
- 出力スタイルを選んだ workflow の規模（C20〜C23。C22・C23 は食い違いあり）
- Mods API の細かな罠（C9〜C11）、予算 1%（C6、出典なし）、821/807（C5、未検証）、先行例（C35）

## 手順

1. branch を確かめる（並行セッション対策）。brief を `docs/plans/harness-scope-writing-harness.md` に置き、`docs(plan): harness-scope-writing-harness` で単独 commit
2. 書く前の再確認（著者指示）:
   - C25: zenn-content で headless の `/harness-scope` を実行し、profile zenn-writing で外れる skill / agent / 指示ファイルの数を一次で取り直す
   - C18: harness-scope の `tools/probe/` を使い、2 ターン以上の headless で `output_style_instructions` が各ターンに届くかを記録する
   - 結果は台帳の該当行に追記
3. outline → `articles/harness-scope-writing-harness.md` に初稿（実用記事の形: Entry bridge の直後に読者が得るものを 1 文、主要節ごとにコードか端末出力、締めは著者の判断）。`published: false`
4. 構造凍結 → panel を各 1 回: `editor`（brief path と AI 生成の旨を渡す）、`fact-checker`（台帳・harness-scope repo・`rfcs/0001-writing-output-style.md`・probe 出力の path を渡す）、`codex:codex-rescue`（read-only、prose-clarity-reviewer の checklist・contract・原稿の path だけ）。指摘ごとに処分記録
5. 著者の通読（private Artifact で渡す）→ 内容 GO。著者の指摘は `drafts/harness-scope-writing-harness.corrections.md` に積む
6. Figure plan を埋めて図（zenn-format）→ 図の差分だけ fact-checker → 著者の確認通読
7. headline-craft → title-reviewer → 著者がタイトル選択 → `/quality-gate` → 著者の公開 GO → `/publish-article`
8. EN は devto-translator（著者 GO 後）

## Verification

- `npm run validate`
- `npm run evidence -- articles/harness-scope-writing-harness.md`（deviations 0、公開直前は `--online`）
- `npm run generate:index` → `npm run check:index`
- commit 後は push を著者に促す
