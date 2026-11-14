# cover-art — maintenance notes

## Origin

2026-11-02、note エッセイ（impression-full-swing）の見出し画像を作る段で、著者が「記事のカバーアートは何がいいのか
リサーチしようかな。スキル化するから」と判断した。調査依頼文は Claude が書き、著者が Deep Research で実行し、
結果を会話に貼った。依頼文と結果は非公開の `drafts/` に置いてある（`deep-research-prompt_article-cover-art_2026-11-02.md`、
`deep-research-result_article-cover-art_2026-11-02.md`）。

依頼の前提: 閲覧数・クリック率を最大化する数値ループは避ける。知りたいのは「題と本文に正直で、読者が開く前に何の
話か分かる入口」を作る知見。

## Consolidation

それまでカバーの規約は 2 か所にあった。この skill を作ったときに両方をここへの参照 1 行に置き換えた。

- note-publishing の「見出し画像（カバーアート）」節 — 1280×670・10MB・中央寄せ・文字なし・定番の絵を避ける・2〜3 案・sips の検査
- substack-publishing §4 — core metaphor を 1 つ視覚化・文字なし・実在人物と暴力を描かない・16:9

substack-publishing の「core metaphor を描く」と「16:9」は、調査結果（具体物を第一候補にする、Substack 公式の
1200×630）と食い違うので引き継がなかった。

## Evidence behind the rules（調査結果の主要資料、as-of 2026-11-02）

- 画像付きリンクのクリック: 地方ニュースサイト 7 つ・約 450 万訪問の無作為フィールド実験（Journal of Computer-Mediated Communication, 2021）。初期報告で平均 63% 増（Center for Media Engagement, 2018）
- 画像が見出しの真実らしさを上げる: 4 実験 N=659（Applied Cognitive Psychology, 2020）
- 誤誘導的な見出しは本文を読んだ後も残る（Journal of Media Psychology, 2021）
- クリックベイトは操作されている知覚を介して発信元の信頼を下げる（Journal of the Academy of Marketing Science, 2022）
- 画像と本文の整合性が信頼に関与する（Journalism & Mass Communication Quarterly, 2026）
- サムネイルの文字量は消費と負の相関（Information & Management, 2024、約 50 万枚の観察）
- 画像化した文字を避け、意味のある画像に alt を付ける（W3C WAI Images Tutorial）。コントラスト基準（WCAG 2.2）
- AI 生成と見られると媒体品質・購読需要が下がる（英国成人 2,870 人の事前登録実験, 2025）。AI 広告は「AI 利用の明記」が受容条件の最多 37.6%（JIAA 2026-02）
- 連載は同じトーンの画像に揃えると続きだと気づかれやすい（note 編集部の公式ガイド, 2026）

## Review-when

- note・Substack・DEV のカバー仕様のページが改訂されたとき（媒体の仕様の表を直す）
- 著者がシリーズで画風を揃えると決め直したとき（2026-11-14 に「揃えない」と判断。SKILL.md の「画風は前の記事に揃えない」段落と則の強さの表を直す）
- Codex の画像生成（`$imagegen`、gpt-image-2）の呼び方や出力の比率が変わったとき（SKILL.md の「生成」節を直す）
- note 編集部が見出し画像を「2:1 で表示」と説明しているという調査の報告を、一次資料で確かめたとき（仕様の表を直す。未確認の間は 1280×670 の公式ヘルプに従う）
- 「期待の一致」の点検を 3 本以上回したとき（サブエージェントの読みが著者の読みとずれるかを見て、点検 4 の扱いを直す）

## Changes

- 2026-11-14: 主題を「本文の具体物」から「本文から取った比喩 1 つ」に反転、画風を記事ごとに選ぶ、プロンプトに「用途と命題」の行、Codex で 3 案を並列に生成する節を足した（human-eval-final-artifact の見出し画像で、著者が 1 回目の 3 案を「なんとも言えない」と止めた後）
