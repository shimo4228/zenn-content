# Zenn 執筆の判断・価値観スキル化プラン（2 スキル構成）

## Context

過去 3.5 週間・33 セッション（人間発話 約 300 turn）には、著者の Zenn 記事執筆における判断・価値観の実例が豊富に残っている（読者志向・情報密度・誇張排除・タイトル・レビュー採否・公開判断など）。一方、memory の `feedback_*` 8 本には構造化済みだが**スキルに未昇格**の判断体系（記事タイプ判定・構造自己審問・主張型記事の裏取りなど）が眠っており、既存スキル（zenn-practical-writing / writing-ecosystem 等）はこれらをカバーしていない。

ユーザー決定事項:
1. **全量パス** — 33 トランスクリプトの人間発話約 300 turn を通読して判断を抽出する
2. **2 スキル構成** — 「価値観リファレンス」と「判断ゲート集」を別スキルとして両方作る
3. **フルセット** — ADR 新規 + 既存ファイル縫合 + memory 昇格マークまで含める

## 成果物の全体像

| 成果物 | 役割 | 正本として持つもの |
|---|---|---|
| **Skill B: `zenn-authorial-values`**（新規） | 価値観リファレンス。「著者が何を大事にしているか」の読み物 + 判断の背景 | 価値観 7 項（実セッション引用付き）、著者ペルソナ規約、内容ランク A/B/C 基準 |
| **Skill A: `zenn-editorial-judgment`**（新規） | 判断ゲート集。執筆タイムラインに沿った「いつ・何を判断するか」 | タイプ判定・軸ずれ検出・フレーム再交渉・具体性の取捨・構造自己審問・裏取り作法・レビュー採否 |
| ADR-0006 | 2 スキルの設計判断の記録 | 二層分割の理由・memory 残置ポリシー・quality-gate 非統合・装置免除 |

相互 defer: A の各ゲートは「なぜ」を B へポインタ、B は「どう運用するか」を A へポインタ。価値観の本文は B のみが持つ（A には再掲しない）。

## 実装ステップ

### Step 0: 全量抽出パス（トランスクリプト発掘）

- 対象: `~/.claude/projects/-Users-<user>-MyAI-Lab-zenn-content/*.jsonl`（33 本、memory/ 除く）
- 検証済み jq パターンで人間発話を全抽出:
  ```bash
  jq -r 'select(.type=="user" and .origin.kind=="human" and (.isSidechain|not))
    | (.message.content | if type=="string" then .
       else (map(select(.type=="text").text)|join(" ")) end)
    | select(length>0)' <file>.jsonl
  ```
  - 補完 1: `origin` なし human 発話（compact/resume 後）— `select(.origin.kind==null and (.message.content|type=="string") and (.message.content|startswith("<")|not))`
  - 補完 2: `.type=="queue-operation"` の `.content`
- 出力: scratchpad にセッション別の抽出台帳（発話 + ファイル名）を作り、判断・価値観の発話をテーマ分類。既知 8 領域（a〜h）+ 価値観 7 項に該当しない**新規発見**があれば A / B のどちらに入れるか割り付ける
- 抽出台帳は scratchpad のみ（コミットしない）。スキル本文に採用する verbatim 引用は原文を必ずこのパスで確認する

### Step 1: ADR-0006 を切る

`docs/adr/0006-authorial-values-and-editorial-judgment-skills.md` + `docs/adr/README.md` 索引更新。決定内容:
1. 著者の判断・価値観を **2 スキルに分割**して正本化（価値観リファレンス = B / 運用ゲート = A。分割理由: 発火文脈が異なる — B は方針議論・企画時、A は執筆・改稿時）
2. feedback memory は削除せず**一次資料（事例台帳）として残置**、先頭に昇格マークのみ付す
3. **quality-gate に統合しない**（判断層を機械 gate 化するとテンプレート化の弊害 — feedback_reader-problem-not-author-framing 自身の警告）
4. zenn-practical-writing の装置チェックに**タイプ別免除条項**を追加（形式矛盾の解消)

### Step 2: Skill B `zenn-authorial-values`（価値観リファレンス）

`.claude/skills/zenn-authorial-values/SKILL.md` 新規。frontmatter: `user-invocable: true` / `origin: shimo4228`、description は長文・defer 宣言込み型（「Use when: 記事の方向性・テーマ選定・ハーネス設計の議論で著者の価値観を参照するとき。NOT for — 執筆・改稿時の運用判断 → zenn-editorial-judgment」）。

構成:
- `> 根拠: ADR-0006`
- **価値観 7 項**（各項: 原則 1 文 + 実セッション verbatim 引用 1-3 個 + 運用先ポインタ）:
  1. 記事の主語は常に読者（→ 運用は zenn-practical-writing「体験談の置き場所」+ Skill A 軸ずれ検出）
  2. 削除より退避（:::details・脚注へ。情報は捨てず人間の主判断面から退ける）
  3. 言い過ぎを許さない(断定刈り取り・自リポ誘導の抑制 → writing-ecosystem + Skill A)
  4. タイトルは商品（→ 生成技法は headline-craft、文字数は rules/zenn-writing.md）
  5. 構成が変われば全レビュー再実行、ただし指摘の採否は著者が決める（→ Skill A）
  6. 公開は必ず人間の明示 GO
  7. 一度出た指摘はハーネスへ昇格（同じ指摘を二度させない）
- **著者ペルソナ規約**（「非エンジニア」自称廃止・エージェント構築実績で語る — feedback_branding-shift の昇格先）
- **内容ランク A/B/C 基準**（memory article-quality.md 冒頭から昇格。判定台帳は memory のまま）
- Step 0 の新規発見があれば追加
- `## Related`

引用は Step 0 で原文確認したものだけ使う。価値観の記録として引用は多め（B の存在意義）だが、既存スキルが正本の運用規則は**再掲せずポインタ**。

### Step 3: Skill A `zenn-editorial-judgment`（判断ゲート集）

`.claude/skills/zenn-editorial-judgment/SKILL.md` 新規。frontmatter 同様、description にタイミング語を入れる（「Use when: 構成案を作る前のタイプ判定 / 改稿・レビュー指摘の採否 / 軸ずれの疑い / 全レビュー通過後の最終著者パス。NOT for — 文体・実用軸 → zenn-practical-writing、価値観の背景 → zenn-authorial-values、機械チェック → quality-gate」）。

構成（タイムライン順、各節末に「判定:」1 行 — zenn-practical-writing 流）:
- `> 根拠: ADR-0006`、冒頭に「なぜ → zenn-authorial-values」の 1 行（価値観テーブルは持たない。B に defer）
- **Phase 0: 記事タイプの事前判定**（how-to / reference / 立場表明・マニフェスト / ツール実測レポート / 主張型 idea。装置 = わかること行・壁の箇条書き・判断表・診断コマンドの採否表。立場表明なら装置を全部外し声だけ適用）← feedback_reader-problem-not-author-framing
- **軸の設定: 自分の環境の出来事は素材であって軸でない**（内部語彙密度 = 軸ずれ検出器。軸を付け替えたら素材の取捨も変わる）← feedback_reader-open-axis-for-tool-reports
- **執筆中: フレーム再交渉と具体性の取捨**（核心が変わったらドラフトに固執しない / 実名許可 ≠ 全ディテールを出す義務）← feedback_writing-as-thinking + feedback_specificity-vs-clarity
- **レビュー後: 構造の自己審問セット**（一般則と筆者事情の区別・キャッチ用語最小・骨格宣言・判断の地図は前方・比較対象を dismiss しない。レビュー指摘の採否は著者が決める / 構成が変われば全レビュー再実行）← feedback_article-structural-review-patterns
- **主張型記事の裏取り作法**（業界フレームで Deep Research → spectrum で弱める / 経験範囲と業界視点の語彙分離 / 優劣比較でなく必然性論 / 引用は原文確認）← feedback_architectural-argument-deep-research
- Step 0 の新規発見（運用判断系）があれば該当タイムライン位置に追加
- `## Related`

### Step 4: zenn-practical-writing への縫い目（最重要の整合ポイント）

`.claude/skills/zenn-practical-writing/SKILL.md` に 2 箇所:
1. Phase 1 手順の**前**に「Phase 0: 記事タイプ判定は `zenn-editorial-judgment` を先に通す。立場表明と判定されたら本スキルの装置系チェック（わかること行・壁の箇条書き等）は免除し、声だけ適用」を 1-2 行追記（現行の受け入れチェックリストは「冒頭にわかること行」を無条件必須にしており、免除条項なしでは新スキルと形式矛盾する）
2. `## Related` に 2 スキルを追加

### Step 5: CLAUDE.md（Writing skills 表）

2 行追加:
- 「執筆前のタイプ判定・軸ずれ検出・改稿時の構造自己審問・レビュー採否 | `zenn-editorial-judgment`」
- 「著者の価値観・ペルソナ規約・内容ランク基準のリファレンス | `zenn-authorial-values`」

### Step 6: memory の昇格マーク

- `MEMORY.md` — 「執筆プロセスの学び（feedback）」節冒頭に「正本は `.claude/skills/zenn-editorial-judgment` + `zenn-authorial-values`（2026-07-28 昇格）。以下は事例の一次資料台帳」を 1 行追加。各行は残す（リンク台帳として）
- `feedback_*.md` 7 本 — 各先頭に「昇格済 → zenn-editorial-judgment / zenn-authorial-values」1 行のみ追記（本文は残置 — 一次資料）
- `article-quality.md` — 冒頭の A/B/C 判定基準を「基準の正本: `zenn-authorial-values`」参照に書き換え（台帳機能・article-stocktake / ideation の読み先は不変）

### Step 7: メタスキル化 — この手法自体をスキルにする（2 スキル完成後）

ユーザー追加要望: 「このスキル化の手法自体も、スキル作成後スキル化したい」。

- **配置: global** `~/.claude/skills/session-judgment-mining/SKILL.md`（手法は Zenn 固有でなく任意 repo で再利用可 → 配置基準「2+ repo で使う → global」。Change Target 規則により global 版のみに作成）
- frontmatter: `user-invocable: true` / `origin: shimo4228`
- 内容（Step 0〜6 を**実際に実行した後**に、実地で効いた手順として書く — 机上の手順書にしない）:
  1. **対象特定**: `~/.claude/projects/<project-dir>/*.jsonl` の規模把握（件数・サイズ・期間）。全量 or サンプリングの判定基準（人間発話 turn 数で決める。数百 turn なら全量）
  2. **人間発話の抽出**: 検証済み jq パターン（`origin.kind=="human"` 主弁別 + origin なし補完 + queue-operation 補完。content の string/array 両対応）
  3. **テーマ分類**: 判断・価値観の発話を分類し、頻出テーマと単発を分ける
  4. **既存カバレッジ照合**: 既存 skills / rules / ADR / memory と突合し「既に正本があるもの（defer）」と「未昇格の空白」を分離 — 重複再掲の禁止がこの手法の要
  5. **二層設計**: 価値観リファレンス（why・引用多め）と運用判断ゲート（when/what・タイムライン順）を分けるか判断する基準
  6. **縫合と昇格マーク**: 既存スキルとの矛盾解消（免除条項）、memory への昇格マーク（一次資料は残置）、ADR 記録
  - 既存 global skill との境界を description に明記: NOT for — 現行セッションからの単発パターン抽出 → `learn-eval`、skill 品質監査 → `skill-stocktake`、skill 群からの rule 蒸留 → `rules-distill`
- `learn-eval` との関係: learn-eval は「今のセッションから 1 パターン抽出」、本スキルは「過去セッション群の遡及一括発掘」。役割が異なるため新規スキルとし、相互に Related で参照

## 変更ファイル一覧

新規:
- `.claude/skills/zenn-authorial-values/SKILL.md`
- `.claude/skills/zenn-editorial-judgment/SKILL.md`
- `docs/adr/0006-authorial-values-and-editorial-judgment-skills.md`
- `~/.claude/skills/session-judgment-mining/SKILL.md`（global メタスキル — Step 7。zenn-content repo にはコミットしない）

編集:
- `.claude/skills/zenn-practical-writing/SKILL.md`（Phase 0 参照 + 装置免除条項 + Related）
- `CLAUDE.md`（Writing skills 表 2 行）
- `docs/adr/README.md`（索引）
- memory: `MEMORY.md` / `feedback_*.md` 7 本（1 行ずつ）/ `article-quality.md`

## 検証

1. **矛盾チェック**: zenn-practical-writing の受け入れチェックリストと Skill A の免除条項が両立して読めるか、A/B 間で価値観本文が重複していないか通し読み
2. **ground truth 遡及テスト**: OTel 記事（agent-logs-to-opentelemetry）の改稿前ドラフトを git 履歴から取得し、Skill A の自己審問セットだけで既知の欠陥（一般則混同・キャッチ用語過多・骨格宣言欠落・地図後置）を再発見できるか確認
3. **タイプ判定の非回帰**: 立場表明の代表例（small-llm-by-choice）で「装置を外す」側に、通常 how-to 記事で「装置維持」側に倒れるか机上確認
4. **発火テスト（手動 3 本）**: 「新しい記事の構成案を作って」「この記事、軸がずれてる気がする」「レビュー指摘を反映して」で Skill A が想定タイミングで参照されるか（厳密には後日 global `skill-comply` で測定可）
5. 記事ファイル変更なしのため `npm run validate` への影響なし

## Human gate

スキル・ADR・CLAUDE.md は behavior-shaping artifact のため、コミット前の意図確認では**本文を提示**する（human-gate.md）。コミットは 1 決裁に束ね、push はユーザーに促す（本 repo の Git Push Reminder）。
