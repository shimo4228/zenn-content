# Plan: 「LLM の判断を Jev に移す研究パイプライン」記事（Zenn + Dev.to）

## Context

素材は jev-research-pipeline（JRP）の 2 台帳:
- build 側 `~/MyAI_Lab/jev-research-pipeline/drafts/article-context_jrp-pilot-autonomy_2026-09-23.md`（C1〜C24）
- judge 側 `~/MyAI_Lab/jev-research-pipeline/drafts/article-context_judge-session-design_2026-09-23.md`（J1〜J38）

※ 1 本目は zenn-content/drafts ではなく JRP repo の drafts にある。

著者が中心命題として **「LLM の判断を Jev に移す構成」** を選択（2026-09-23）。
channel は Jev シリーズ（9/21 ×2、9/24 予約）と同じ Zenn + Dev.to。過去の daily-research 3 部作
（`articles/daily-research-automation.md` / `-agent-team.md` / `-postmortem.md`）の後継に当たる。

執筆は `writing-ecosystem`（project-local）の Canonical workflow に従う。最初の停止点は
editorial brief の著者確認。

## Step 1. Editorial brief（草案 — 著者確認で止まる）

```markdown
Reader: Claude / GPT に「探して・選んで・書く」を丸ごと任せた自動リサーチや定期レポートを
  運用しているエンジニア。Jev（文章を書かず選択肢と確率を返すモデル）の存在は知っている
  か、シリーズ前稿で知った。当然視していること: 判断は LLM がやるもの。問い（仮説）:
  「LLM の判断のうち、どれを安い判定モデルに移せて、どれが残るのか」
Channel: Zenn（articles/*.md）→ Dev.to（articles-en/*.md）
Central thesis: 研究パイプラインの「関係あるか・新しいか・信頼できるか」の判定は Jev に移せる。
  ただし Jev の判定には基準点（問い）が要る。探索と文章生成は本来 LLM の仕事で、今回は探索を
  コードで試しただけ（レポートの品質次第で ReAct の探索に戻す）。どちらも Pydantic AI 越しに
  モデルを差し替えられる形にしてある
  （著者裁定 2026-09-23: 「書く LLM が残ってボトルネック」は採らない／探索＝コードは設計の主張でなく今回の試行）
Entry bridge: 旧 daily-research は Opus に探索も判定も執筆も任せ、1 日 $4〜15 かけて
  238 トピック中 88（37%）が 1 テーマに寄った（J10）。この「全部 LLM」をばらすとどうなるか
First-screen deliverable: 役割分担の流れ 1 行（例: 探索＝コードの 4 net → 判定＝Jev の狭い問いの束
  （問いごと）→ 文章＝Qwen 1 回）+ pydantic-ai で Jev を呼ぶ 1 行
  `Agent('typesafe:jev-1.13.0', output_type=M)`（J6。docs 再照合のうえ実行確認して載せる）
Figure plan: 内容 GO 後に埋める（候補: hero＝役割分担 / 対比＝claim 単位 vs 問い単位 / 流れ＝判定の束）
Causal spine:
  観察 全部 LLM の daily-research は高く、話題が収束した（J10）
  → 緊張 判断を LLM から外すなら、何をどこへ？ 著者の目標は「Jev を減らす」でなく
    「LLM の判断を Jev に移す」（J32、J2）
  → 機序1 分割: 検索先はコードが固定、判定は Jev の狭い関数、Qwen は 2 箇所（packet の
    Judgment map、J3、J6/J7）
  → 機序2 初回 pilot で失敗: 原文の文（claim）単位では Jev に基準点が無く、20,573 問・283 KB・
    橋渡し 2,570 中 2,509 accept、無我のラインで attention 論文が通った（J18、J19）
  → 機序3 全判定を (item, 問い) に anchor（J24）→ 1 ライン 1,435〜1,830 問、note 7〜12 KB、
    橋渡し ≤ 3（C19、J34、Before/After 表）
  → 生成は LLM に残す（設計どおり）: Qwen は query 候補と prose の 2 箇所。prose の質は現状
    Publishable 1/3（C18、J36）で、これは生成モデルの選択の問題。Pydantic AI 越しなので
    Claude / GPT 等へ差し替えて試せる（J31。改善は未計測の見込みとして書く）。短く触れる程度
  → 読者の判断則 Jev に移せる判断＝基準点を state に置けて選択肢が閉じているもの。
    生成は LLM に任せ、モデルを差し替えられる境界にしておく
Selected evidence:
- J10: 入口（全部 LLM の費用と収束）
- J2 / J32: 設計の制約と目標（Jev 使用は増えてよい、LLM 判断を減らす）
- J3 / J6 / J7: Jev の形（3 primitive、pydantic-ai 経由で自作 SDK 境界を削除）
- J18 / J19: claim 単位の失敗（基準点の無い判定）
- J24: 問い単位への転回
- C1 / C19 / J34: Before / After の数値
- C18 / J36 / J31: 生成は LLM の仕事、現状の質と差し替え可能性（短く）
Out of scope:
- 自走 mandate・三役運用（J26、J29、J30、J35、run ごとの条件表）→ 別記事候補
- 並列化・single-flight・TLA+（C2、C5、C6）
- batch 判定の slot bleed（C3、C4）→ 別記事（著者裁定 2026-09-23）
- arXiv 406 / CDN 誤診（C8、C9）、hibernate（C20）、Homebrew（J28）
- 文献探索 recall の外部研究（J11〜J16）、X / xAI 価格（J9、J31）、Qwen 以外の生成モデル（C13〜C15、J38）
- 確信度の取り方で Keep ゼロ（C12）、評価系・used rate（J25）
```

著者に確認したい点（brief と一緒に提示）:
1. 中心命題の後半「書く LLM が残ってボトルネック」を入れるか（入れないと成功談、入れると未解決を含む記事）
2. slot bleed を 1 段落だけ入れるか、完全に別記事へ回すか

## Step 2. 執筆前の証拠の足場

- **J37 が $ 表記の全部に効く**: 運用節の cost は「質問数 × 仮単価」で実課金ではない。
  → 著者が TypeSafe console の請求と突合するまで、本文は **質問数・KB・件数を主** にし、$ は
  「運用節の推定値」と明記するか載せない。Qwen 側の $ は別扱い
- 比較の物差しは 1 本にする（前稿の学び）: daily-research の $4〜15/日 と JRP の 1 ライン cost は
  単位も出力も違うので並べて比較しない。入口の文脈としてだけ使う
- 外部仕様（Jev の primitive・価格・pydantic-ai 連携）は執筆時に docs を再取得し as-of を付ける
- JRP repo は remote なし → 本文から repo へ link できない。コード片は記事内に実行確認済みの形で置く。
  個人 path（`~/.claude/...`、vault path）は本文に出さない
- 時間は一直線・錨 1 本（9/22 夜の設計インタビュー → 翌朝の初回 pilot → 昼の転回 → 午後の最終 run）。
  台帳の時刻は本文に写さない

## Step 3. 構成と初稿

`articles/<slug>.md`（slug 例: `jev-research-pipeline-judgment`）を `published: false` で作成。
節の割り当て（brief の causal spine に 1 節 1 役割）:

1. 第一画面: 流れ 1 行 + pydantic-ai の 1 行 + 結果の数値 2〜3 個
2. 全部 LLM だった daily-research（入口）
3. 探すのはコード、判定は Jev、書くのは Qwen（分担表 — 比較なので表）
4. 原文の文ごとに聞いたら、Jev は何でも通した（J18/J19 の実物 1 件を先に）
5. 問いを基準点にしたら（Before/After 表）
6. 書くのは LLM の仕事として残す（短い節。Pydantic AI で差し替え可能、現状 1/3、改善は見込み）
7. Jev に移せる判断の条件（takeaway）
8. 関連リンク（contract の定型 2 行 + シリーズ前稿 + daily-research 記事）

目安 6,300 字前後。長くなったら表・`:::details` に逃がす。

## Step 4. 凍結 → review panel（各 1 回）→ 著者の内容 GO

- 並列 dispatch: `editor` / `prose-clarity-reviewer`（原稿 path と contract だけ渡す）/
  `fact-checker`（2 台帳・JRP repo・`docs/pilot-log.md`・packet の path を名指し）/ `codex-review`
- 指摘ごとに採否を 1 行で処分記録。反映後は reviewer に戻さず著者通読 → 内容 GO

## Step 5. 図（内容 GO 後）

節ごとに形を 1 語で決め、`/eli5` で 3〜4 枚（hero＝役割分担、対比＝claim vs 問い 等）。
PNG 化は `zenn-format` の手順。図の文字だけ fact-checker に差分で回し、著者が再通読。

## Step 6. タイトル

`headline-craft` → `title-reviewer` → 著者が選択（50 字以内、em dash 不可）。

## Step 7. 受け入れと公開

```bash
npm run validate
```
```bash
npm run evidence -- articles/<slug>.md
```
→ `/quality-gate articles/<slug>.md` → 著者の公開 GO →
`published_at` は cadence（火〜水 7:00〜9:00、burst 回避。9/24 の次）から **9/29(火) または
9/30(水) 08:00** を提案、公開 3 日以上前に push → `devto-translator` で EN（前日 22:00 JST）→
`publish-article` → `npm run generate:index` → `npm run check:index` → push を著者にリマインド、
Zenn デプロイ履歴の確認。

## Verification

- brief 確認時: 著者が中心命題・Out of scope・上記 2 点に回答
- 本文の数値は台帳 ID と 1:1（`npm run evidence` deviations 0、fact-checker の INACCURATE / PARTIALLY 全件処分）
- pydantic-ai の Jev 呼び出しコード片は JRP の環境で実行して出力を確認してから載せる
- public-safety: 個人 path・key・未 sanitize ログ 0
- `npm run validate` / `npm run check:index` が通る
