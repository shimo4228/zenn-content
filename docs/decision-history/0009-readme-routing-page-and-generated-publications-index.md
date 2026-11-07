# ADR-0009: README をルーティングページにし、網羅一覧を生成索引 1 つへ集約する

## Status

Accepted

## Date

2026-08-18

## Context

README.md / README.ja.md / llms.txt は公開記事の手書き一覧（シリーズ別 48 本）を持っていたが、`articles/` の published は 65 本で、記事を出すたびに 3 ファイルを人手で追随させる設計のため 17 本分 stale していた。README にはほかにも揮発する事実（「59 tests」「11 skills」「48+」、Python 版）が埋まっており、記事以外の変更でも同じ形で腐る。

一方、記事を投稿するたびにこの repo は目に見える数クローンされる。つまり README の実際の来訪者は「カタログを眺めに来た人」ではなく「1 本の記事を読んで repo に来た人（と LLM クローラー）」で、すでに 1 本のタイトルを知っており、65 本の壁を求めていない。

著者は「一覧の自動化」ではなく「README のあり方の根本的な変更」を求めた。設計相談は Claude（本セッション）と Codex（cross-model、prompt-driven read-only）の両方に投げ、結論は一致した（as-of 2026-08-18）。

現状の事実（実測）: published 65 本のうち `published_at` を持つのは 20 本。`schedule.json` の JP エントリは 52 本で、membership の正本にすると現状の欠落を再生産する。Zenn の仕様上、公開済み記事の `published_at` は「一度しか指定できず変更不可」なので、Zenn 実値でのバックフィルは Zenn 側 no-op で安全。

## Decision

1. **README の仕事を「網羅」から「ルーティング」へ変える。** 最初の 1 画面で答えるのは 5 つ — これは何の repo か / なぜこれらが一緒にあるか / 次に何を読むか / 全部見たければどこか / 誰が作りどう再利用できるか。記事一覧・`.claude/` ツリーダンプ・Tech Stack・Directory Structure・姉妹 DOI 5 本・「dominant audience is machine ingestion」の旧 audience 論（ADR-0022 の人間読者優先と矛盾）は README から外す。DeepWiki / GitMCP バッジは末尾「For coding agents」へ。
2. **「次に何を読むか」は意図ベースの読書経路 3 本（各 2〜3 記事）を `scripts/reading_paths.yml` に著者判断で置く。** 変化率は年単位。新記事を自動追加しない（自動化すると「最新 8 本」になり、identity より速く腐る）。
3. **網羅一覧は生成物 `docs/PUBLICATIONS.md` の 1 つだけ。** Zenn/Dev.to 記事に加え、note/Substack のアイデアエッセイ、寄託済み論文（Zenodo 概念 DOI 正本 + SSRN ミラー、記事から育った論文は `from:` で相互リンク）、5 本の研究ラインを載せる。時系列（新しい順）、topics で series を推定しない。
4. **正本の分担**: `articles/*.md` frontmatter が JP membership・title・topics・slug・`published_at`（published なら必須。欠けると生成が止まる）を持つ。`articles-en/<slug>.md`（旧命名 `<slug>-en.md` も解決）が EN title。`schedule.json` は Dev.to URL のエンリッチ専用で membership に使わない。frontmatter が無いもの（エッセイ・論文・研究ライン）は `scripts/corpus.yml` の手書き台帳。
5. **生成 hook**: `scripts/generate_article_index.py`（決定論。時計・git を見ない）を `npm run generate:index` で publish フローの commit 前に人が走らせる。CI（`validate.yml`）は `npm run check:index` で drift を fail させるだけで **bot commit はしない**。未来日付の記事は除外せず日付のまま載せる（Zenn の時計で公開される瞬間に script は走らないため、"Scheduled" のような時刻依存ラベルも付けない）。
6. **README.ja.md はポインタに縮めず、同じ骨格の実ランディングページとして手で localize する。** 読書経路ブロックだけ marker（`<!-- reading-paths:start/end -->`）で両 README に生成する。llms.txt は記事別セクションを撤去して `docs/PUBLICATIONS.md` を指す navigator に戻し、本数の手書き（「48+」）は全ファイルから消す。
7. 45 本の `published_at` を Zenn API の実公開日時でバックフィルし、以後の published 記事には必須とする。

## Alternatives Considered

- **(a) README 内に marker で一覧を自動生成**: stale は解けるが情報設計は解けない。65 行が identity を fold 下へ押し流し、投稿ごとに README diff がノイズになる。marker 生成は小さな読書経路ブロックにだけ使う。不採用。
- **(b) 生成索引のみ（README から一覧を外すだけ）**: 必要だが不十分。「次に何を読むか」に答えず、65 本の時系列はまだ選択問題のまま。(d) と組み合わせて採用。
- **(c) Zenn/Dev.to プロフィール + `npx zenn list:articles` + llms.txt に委ねる**: 断片化する。プラットフォームは第三者ガバナンス（CLAUDE.md の bound ③: 正本は repo に残す）で、`npx zenn list:articles` は checkout 前提、llms.txt は AI 向け navigator であって人間向けカタログではない。不採用。
- **`schedule.json` を membership の正本にする**: JP 52/65 で網羅性を保証していない（台帳ではなくログ）。不採用。
- **CI が生成物を commit する**: bot commit と push 競合が増え、Zenn の `published_at` モデル（push 時に script が走らない）とも噛み合わない。`--check` のみ。不採用。
- **README.ja.md を英語 README への短いポインタに縮める**: JP が Zenn 正本なので、日本語読者に英語 README を経由させるのは逆。不採用。
- **`.claude/` ツリーダンプを残す**: 25 行の内部実装インベントリは記事から来た読者に役立たず、数値が腐る。ただし Codex 案と分かれた点として、執筆ハーネスを見に来るエンジニアがいる前提で「How the corpus is made」に主要 skill 3 本の 1 行説明だけ残す（構成要素は年単位で安定）。

## Consequences

- 良: 記事を出しても README は変わらない（変わるのは生成索引だけ）。identity と読書経路（年単位）、網羅索引（投稿単位）という**変化率の異なる情報を別ファイルに分けた**ので、速い方が遅い方を腐らせない。
- 良: 記事・エッセイ・論文・研究ラインの全体像が 1 ファイルに集まり、記事 → 論文の系譜（ReAct 象限シリーズ → *Distributing Accountability*、ブラックボックス二層 → *Two-Layer Black Box*）が索引上で辿れる。
- 良: `published_at` が全 published 記事に揃い、索引の日付正本が frontmatter に一本化された（Zenn 実値と数分〜数時間ずれる既存 6 本は Zenn 側変更不可のためそのまま。索引は日付単位）。
- コスト: publish フローに `npm run generate:index` が 1 ステップ増える。忘れると CI が赤になる（fail-closed だが、push 後に気づく形）。note/Substack エッセイと論文は `corpus.yml` への手書き 1 エントリが必要（投稿自体が手動なので同じ動作）。
- リスク: 読書経路の 7 本が古びる。年単位で著者が見直す（`reading_paths.yml` を直して再生成するだけ）。
- 関係: ADR-0001（Content Integrity）— README のルーティング化は distribution 層の変更で、記事内容には触れない。ADR-0005（事後 Eval）— 読書経路の見直しに実測 tier を使ってよい。CLAUDE.md「Publications index」節が運用の正本、`docs/CODEMAPS/scripts.md` が実装の地図。
