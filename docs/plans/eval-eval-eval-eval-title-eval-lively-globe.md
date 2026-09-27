# eval 層の解体 — 判定器 3 本 → レビュアー + タイトル判定

## Context

著者の申告: 「eval が冗長。テーマ eval は eval に適さない。記事の eval も手厚いレビュー群に対して冗長。
**手順が複雑になりすぎ、評価基準の整合に時間がかかる**」。

grill-me で棚卸しした結果:

- **整合コストの発生源は「評価器の数」ではなく「評価器だけが agent に閉じていないこと」**。
  clarity-reviewer / essay-reviewer / fact-checker は基準が agent ファイル 1 つに閉じる（低コスト）。
  一方 theme-eval / article-judge は skill + checklist + コード + ループ節 + ゲート条件の
  **5 ファイルに分散**していた。今日の 3 コミット（重複潰し）も全部この部分系が発生源。
- **theme-eval は最初から eval ではなかった**。Drop は構造上出せず（却下ゲートではない設計）、
  通した 2 本とも A見込み。**verdict が結果を変えた記録はゼロ**。効いていたのは Deepen の対話だけ。
- **article-judge はゲートとして機能していない**。3 本中 1 本で Fix を出したが、残り 2 本は
  judge 通過後に著者と codex が別の欠陥を検出。「通った = 大丈夫」が成立していない。
- **K1-K4 は原則ではなく 1 日ぶんの欠陥パターン**（2026-08-12）。K1 は fact-checker、K4 は clarity と
  重複。K2/K3 は手順を伴わなければ標語に劣化する。著者判断で**全て破棄**。
- 8/12 の 3 件を見つけたのは judge ではなく**著者の通読**で、通読 GO は最上位ゲートとして残る。
- **チェックリストは執筆規約の忠実な写像ではなく、3 点で衝突していた**。根因はチャンネルの
  概念を持たないこと（この repo の分岐軸はチャンネル表なのに、Substack エッセイストの単一
  チャンネル前提のまま「genre 中立」を名乗っていた）:
  - **B15**（言い切り必須）⇄ `zenn-practical-writing` の語りの表（essay = 問い化 / 実用 = 言い切り）
    と `zenn-authorial-values` L50（強い言い切りが逆効果になる感度）。essay に当てると規約が
    求める発見調を「逃げ」として叩く
  - **B5**（N ステップまとめで終わるな）⇄ 実用 how-to の正当な結論（手順の言い切り）
  - **B1**（具体的場面から入れ）⇄「一瞬でわかるは第一画面の機能要件」（結果駆動で先に渡す）
  ADR-0008 が risk として挙げた「judge の好みへの文体収束（平坦化 Goodhart）」は、
  チェックリスト自体に構造として埋まっていた。

**意図する結果**: 評価器 3 本（theme / article / title）を 1 本（title）に落とし、テーマ層は
レビュアーへ変換する。基準の置き場は全て agent 常駐にして、整合作業を消す。

## 決定事項

| 層 | 決定 |
|---|---|
| テーマ | `theme-eval` skill 廃止 → **`theme-reviewer` agent 新設**。verdict なし。findings + 深化の問いだけ返す。答えるのは著者と本体 |
| 記事 | `article-judge` agent 廃止。K1-K4 は全て破棄。判定は panel 4 本 + 著者通読に戻す |
| 機構 | craft チェックリスト・`mechanical_checks.py` + テスト・改稿ループ節・quality-gate 第 1 条件を削除 |
| タイトル | `title-eval` は現状維持（レビュアーが存在しない唯一の層のため） |

## 削除

- `.claude/skills/theme-eval/`（ディレクトリごと）
- `.claude/agents/article-judge.md`
- `.claude/refs/kaguura-craft-checklist.md`
- `scripts/mechanical_checks.py` / `scripts/tests/test_mechanical_checks.py`

git 追跡下なので履歴から復元可能（`rules/common/coding-style.md`）。`.notes/` 配下の
バックテスト台帳は git 管理外の私的記録なので残す。

**執筆側へ移す項目は無い**（照合済み）: §B の craft は `writing-ecosystem`「Craft 規約」
「語りかけの積極形」「エッセイの 4 段構成」と `zenn-practical-writing`「導入の設計」に
既にあり、書く側のほうが厚い（段落密度の閾値・専門用語の緩和策 7 種・各節末の「判定」手順は
執筆側にしかない）。B13（一人称は証人として）は「体験談は解決の証拠として 1 段落に圧縮」が
同義。**B15 は移してはいけない** — チャンネル分岐と衝突する（上記）。

## 新設

**`.claude/agents/theme-reviewer.md`**（project agent。`zenn-clarity-reviewer.md` の構成に倣う）

- 入力: テーマ一行 + 素材（所感 / ログ / 証拠台帳）
- 観点: 旧 T1-T8 をそのまま移植（一文化 / 非自明性 / 言説の空白＝**外部検索で照合** /
  一次アクセス / 読者接続 / Dinner Party / 深さ / 非トレンド寄生）
- 出力: findings（各 1 行証拠）+ **深化の問い**（旧 Deepen プロンプト 4 種）。
  **verdict・ランク・希少性モニタは持たない**
- fresh context の別プロセスで走る（本体が自分のテーマを審査する self-preference を避ける）
- チャンネル routing（Zenn 実用 / note エッセイ）は findings の一部として残す

## 編集

- **`.claude/skills/writing-team/SKILL.md`** — Mission A step 2 を `theme-reviewer` 起動へ。
  step 6（草稿ゲート）・6.5・9（binding 最終判定）を削除し番号を詰める。「改稿ループ」節を削除し、
  panel 指摘の反映（step 8）だけ残す。Mission B の step 5 / 6.5 も同様
- **`.claude/skills/quality-gate/SKILL.md`** — 必須条件から「最終判定の article-judge = Publishable」を削除。
  description の judge 参照も更新
- **`.claude/skills/ideation/SKILL.md`** — `theme-eval` への受け渡し（L40-47）を `theme-reviewer` へ
- **`.claude/skills/title-eval/SKILL.md`** — description の「ADR-0008 の第三の eval」「theme-eval /
  article-judge と同格」、L60、Related（L66）を更新。**単独で立つ判定器**として書き直す
- **`.claude/skills/publish-article/SKILL.md`** — L34 の「最終判定（article-judge）」を削除
- **`CLAUDE.md`** — 「二本立て評価 + 改稿ループ」節を書き換え（評価は theme-reviewer + panel + title-eval）
- **`.claude/rules/zenn-writing.md`** — 値の所在マップから 4 行を整理:
  「テーマ強度の質問セット」→ `theme-reviewer` agent 常駐 /「記事品質の質問セット」削除 /
  「改稿ループの制御」削除 /「決定論チェックの閾値・語リスト」削除
- **`docs/CODEMAPS/architecture.md`** — eval 部分系の記述を更新

## ADR

- **`docs/adr/0012-*.md` を新設** — ADR-0008 の Decision 1・2・4 を supersede。
  Context に上の実績（judge 3 本の内訳・theme-eval の verdict が結果を変えていない事実）を記録。
  Review-when: 「著者通読を省く運用に変わったら」「panel が構造的欠陥を見逃す事例が再発したら」
- **`docs/adr/0008`** に日付つき注記（削除しない）。ADR-0004 の追加基準は維持
- `docs/adr/README.md` に行追加 + supersede 関係を追記

## 検証

1. `npm run validate` — frontmatter 検証
2. 孤児参照の掃引:
   `grep -rn "article-judge\|theme-eval\|mechanical_checks\|kaguura-craft" .claude CLAUDE.md docs scripts`
   → ADR の歴史記述以外はゼロになること
3. `/quality-gate <既存記事>` を 1 本走らせ、削除した条件を参照して落ちないこと
4. `theme-reviewer` をテーマ一行 1 件で smoke 実行し、verdict を出さず findings + 問いを返すこと
5. `git status` と memory（`eval-harness-pipeline.md` / `MEMORY.md`）の更新

## 成功基準

- 執筆前に走る評価器: **3 本 → 0 本**（レビュアー 1 本に置換）
- 公開前のブロック条件: article-judge 分が 1 つ減る（clarity FAIL・editor CRITICAL は維持）
- 基準の置き場: **5 ファイル分散 → agent 常駐 1 ファイル**
- 削除される保守対象: skill 1 / agent 1 / refs 1 / コード 2 ファイル

## 非目標

- panel 4 本（editor / fact-checker / clarity / codex）の構成は変えない
- `title-eval` の中身は変えない（参照の更新のみ）
- 著者通読 GO・Content Integrity・ADR-0004 の reviewer 追加基準は維持
