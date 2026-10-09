<!-- origin: shimo4228 -->
# 通読指摘数の記録（ペルソナ読みの KPI）

Zenn 稿で著者の通読が見つけた指摘の数。`references/persona-read.md` を直すとき・段ごと外すかを決めるときの
主な入力にする。著者の内容 GO の時点で 1 行足す。

比較の基準は「ペルソナ読み: なし」の行。ペルソナ読みを使う前で、panel が今と同じ構成（Codex の初見の読みを含む）の
直近 3 本 — `jev-guard-blind-to-local-verify`・`harness-scope-writing-harness`・`readme-human-llm-fold` — の通読指摘数を、
その稿の処分記録と commit 本文から拾って、次の Zenn 稿の brief を書く前に埋める。拾えない稿は指摘数を「不明」と書き、
その前の Zenn 稿で置き換える。

数え方: その稿の `drafts/<slug>.corrections.md`（著者の指摘の記録）のうち、Trigger が「通読で」の件。brief の対話・
reviewer の指摘・タイトル・公開後の見直しから来た件は数えない。

| 日付 | 記事 | ペルソナ読み | 止めた理由 | 通読の指摘数 | 主な種類 |
|---|---|---|---|---|---|
| 2026-09-29 | jev-guard-blind-to-local-verify | なし | — | 6（C3・C4・C7・C8・C9・C10） | 確度の言いすぎ 1、語（「名指し」・比喩）2、節の長さと順序 3、命題から浮いた締め 1（C7 は語と節の両方） |
| 2026-10-03 | harness-scope-writing-harness | なし | — | 0（公開後の見直しが 1: C8 図の見出しの大きさ） | — |
| 2026-10-09 | readme-human-llm-fold | なし | — | 3（C4・C5・C7） | 理由が読者に渡らない 1、表の見え方 1、畳んだ節が薄い 1。ほかに著者が直した語の連結・台帳の語の写し（C2・C3）は Trigger が通読と書かれていないので数えていない |
