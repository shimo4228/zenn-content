# Plan: jev-guard-blind-to-local-verify（Zenn、jev-retrofit-limits の続編）— editorial brief

## Context

2026-09-21 から 1 週間、外製の判定モデル Jev を使う 2 つの plugin（belay: 未検証の完了を止める / skill-router: スキルを提案する）を
Claude Code の harness に入れ、9/28 に両方を外した。証拠台帳は
`drafts/article-context_jev-guard-blind-to-local-verify_2026-09-28.md`（以下 C 番号はその Claims Register）。
9/21 公開の前作 `articles/jev-retrofit-limits.md` は「ReAct 型ハーネスでは足しても置き換わる仕事がない」と見立て、
「ログだけ残し、使われなければ外す」と約束して終わっている。本稿はその約束の答えから入り、前作に無かった
belay の実運用と「部品を足した効果が読めない」を新しい芯にする。命題は 2026-09-29 の対話で著者と合意した。
この plan の承認 = brief の著者確認。承認後に構成と本文へ進む。

## Editorial brief

**Reader**: Zenn の engineer で、Claude Code に plugin や hook を足そうか迷っている人（著者確認:「読者はそれでいいよ」）。

**Channel**: Zenn（`articles/jev-guard-blind-to-local-verify.md`、ですます、実用）。reviewer は editor + Codex 初見
（prose-clarity checklist）+ fact-checker。note へは内容 GO 後に原文転載するかを決める（書き直さない）。
Dev.to EN は公開 GO 後に devto-translator。

**Author's words**:
> 結局、思ったのはClaude Codeのネイティブの挙動部分と重複するものはあんまり入れても効果が薄いし、ネイティブの挙動を損なうことによる性能低下が気になるのであまり得策と思えなかったな。Jevを導入するなら、1からJev前提で作ったハーネスで、LLMを生成部分だけで呼ぶみたいなものの方がいいと思った。
>
> それかLanggraphとか固定したパイプラインの部品を組み替えるとかかな。そういう意味ではClaude Codeにも変更できる部品があるともうけど、Claude CodeみたいなReAct前提の動きが固定されていないエージェントは部品を変えることによる効果が読みにくいから慎重になっちゃうね

**Central thesis**: 判定モデルを部品として差し替えて効果を読めるのは、流れが固定されたパイプラインの中だけで、
次の一手をモデルが決める Claude Code に後から差し込むと、小さな違いがその後の動きを変えていくので、
本来の挙動を損なっているかどうかさえ分からず、表面の数字だけでは採用を決められない（2026-09-29 著者の通読で更新）。

**Entry bridge**: 前作の最後に「ログだけ残して、名指ししたスキルが使われなければ外す」と書いた。1 週間後の数字は
539 回の提案のうち使われたのは 28 回で、外した。同じ週、もう 1 つの Jev plugin は、検証を済ませた完了を 8 回止めていた。

**Causal spine**:
1. 観察 — 約束の答え: router は提案 539 / 使用 28（C17, C18）。ネイティブのスキル選択と重なり、置き換わる仕事がなかった（前作の見立ての確認、短く）
2. 緊張 — belay は止めるモードで 1 週間動き、block 8 件すべてが「検査ゼロ」判定（C9, C10）。1 件を追う: verify.sh を 3 回 exit 0 → commit メッセージをファイルに書く → 止められる → verify を約 2 分半やり直す（C14, C26）
3. 機序 — belay の「検査」はランナー名の正規表現と要約行で決まり、この harness の verify.sh も、verify 後にファイルへ commit メッセージを書く運用も知らない（C11, C13）。部品単体の仕様も harness の運用も、それぞれは正しい。衝突はエージェントの中で組み合わさったときにだけ現れ、止められたエージェントの次の動き（再実行）も部品の側からは読めない
4. 判断 — 固定パイプライン（LangGraph 等）なら、部品の入出力と前後がコードで決まっているので差し替えの効果を読める。Jev を使うなら、最初から Jev 前提で組み LLM は生成にだけ呼ぶ構成か、固定パイプラインの部品にする。Claude Code にも差し替えられる口はあるが、ReAct 型では効果が読みにくいので慎重になる。締めはこの判断そのもの（「足す前に確かめること」節は著者の通読で削除、2026-09-29）

**Selected evidence**:
- C17/C18: router の約束の答え（入口）
- C9/C10: belay block 8 件・全件 checks 空（緊張）
- C14/C26: 4ddcf707 の 1 件（仕組みの節は 1 件を追う）
- C11/C12: CHECK 正規表現と未設定（機序。CHECK で足せた事実も隠さない）
- C13: 止まった直前の「変更」の中身（機序）
- C21/C22: 著者の「意味あるかな？」→ 無効化（判断の場面）
- C20: router 1 判定約 2 万 token（損なうコストの補助、1 文）

**Out of scope**:
- Codex が shadow から止めるモードへ自分で切り替えた件（C4/C5/C8）— 委任の話で別命題。本文は「止めるモードで動かした」事実だけ
- fixture だけでの検証報告（C6/C7）
- security-reviewer 未実施（C29）、無効化が既存セッションに効かない件（C23）
- Jev 前提ハーネスや LangGraph 構成を実際に作る話（未実施。判断の選択肢として示すだけ）
- CHECK を設定したら改善したか（未試行。「試していない」と 1 文で正直に）

**Figure plan**（内容 GO 後、4 枚。比喩は hero だけ）:

| 節 | 形 | 図 |
|---|---|---|
| 冒頭（結論段落の後、最初の見出しの前） | 対比 | hero — 流れが決まっているパイプライン（線路）と、次の動きをその場で決める Claude Code（運転席）。前作の hero と同じ運転席の世界 |
| Jevが選んだスキルは、Claude Codeの選択とほとんど重なりませんでした | 階層 | funnel — 判定 1,242 → 選んだ 539 → 使われた 28 |
| 外した後で、使われなかった20件を読みました | 並列 | 図なし（箇条書きのまま） |
| 検証を済ませた完了が止められました | 流れ | 図なし（次節の belay-view が同じ 1 件を描く） |
| 部品も運用も、それぞれは正しかった | 対比 | belay-view — Claude Code がした 5 手順と、jev-belay の数え方 |
| 効果を読めないまま、仕事は重なっていました | 対比 | overlap — 外から足した 2 つの仕事と、既にあった 2 つの仕組み |
| 組み込んだ効果を読めるのは、流れが決まっている場所です | 対比 | 図なし（hero と同じ対比） |

## 未検証で本文に使う前に解くもの

- C27: 残り 6 件の block で verify が走っていたか — 本文で「8 件すべて検証済み」と言わない。確かめた 2 件だけを言う
- C28: commit 時 PreToolUse ゲートの実行記録 — 使うなら「推測」と明示
- C18 の 28 と 26 の差 — commit 値 28 を使い、測り方（30 分以内・同セッション）を添える

## 進め方

1. 構成（節見出し + 各節の役割 + 証拠 ID）を提示 → 著者確認
2. 本文を執筆（`zenn-format`、published: false、関連リンク 2 行を末尾に。前作へのリンクは冒頭 1 回）
3. `npm run validate` / `npm run evidence -- articles/jev-guard-blind-to-local-verify.md`
4. 構造凍結 → editor・Codex 初見・fact-checker（台帳 path を渡す）を各 1 回、処分記録
5. 著者の通読 → 内容 GO → 図（Figure plan）→ headline-craft + title-reviewer → quality-gate → 公開 GO

## Verification

- `npm run validate` と `npm run evidence -- articles/jev-guard-blind-to-local-verify.md`（deviations 0）
- 数値はすべて台帳の再計測コマンドで照合できるものに限る（fact-checker に台帳を渡す）
- 公開後 `npm run generate:index` / `npm run check:index`
