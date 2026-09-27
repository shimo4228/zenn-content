# Plan: Zenn 記事「非コード資産の『価値』は linter では測れない」

## Context

3つのセッション（`drafts/2026-07-05-145248-textlintgithubwor.txt` = スキル構築、
`drafts/2026-07-05-145504-command-...txt` = zenn-content での実行）を材料に、
`repo-asset-stocktake` スキルを作った話を **Zenn 記事**にする。

grill-me インタビューで6つの設計判断を確定済み（下表）。記事の狙いは、プロジェクト
CLAUDE.md の「読者にとって何を解決し、どうすれば導入・応用できるかが端的に伝わる」——
実用軸（`zenn-practical-writing`）の記事。

種別判定: **writing**（文書自体が一次成果物）→ Writing Chain。
doc 分類 = 記事 → orchestrator（Claude Code 本体）が `zenn-practical-writing` に従って
直接執筆（サブエージェントに委譲しない。project CLAUDE.md 準拠）。

## 確定した設計判断（grill-me 結果）

| # | 論点 | 決定 |
|---|------|------|
| 1 | 記事の主役 | **C** 入口=スキル / 持ち帰り=パターンの両立 |
| 2 | 冒頭の掴み | **A** AI 開発で溜まる非コード資産（plan/handoff .md 量産） |
| 3 | 探索過程の深さ | **A** コンパクト要約ボックス（`:::details` 可） |
| 4 | 主役デモ | **A** g-kentei-ios の33ファイル切断アーカイブ島 |
| 5 | 応用の形 | **A** consumer 分類表＋汎用レシピ＋gotcha |
| 6 | タイトル | **A**「非コード資産の「価値」は linter では測れない —— LLM で棚卸しするスキルを作った」 |

## 声・型

- **声**: `zenn-practical-writing`（ですます・即実用・実コード/図・低認知負荷）。type で分岐しない。
- **frontmatter**: `type: tech` / `emoji: 🧹`（棚卸し）/ `topics: ["claudecode", "llm", "ai", "個人開発"]` /
  `published: false`（レビュー完了までは公開しない）。
- **タイトル**: 「非コード資産の「価値」は linter では測れない —— LLM で棚卸しするスキルを作った」（約40字、煽りゼロ、概念を名指し）。
- **禁止**: AI slop（正本 `writing-ecosystem`）。数値クレームは実測のみ。プロジェクト用語表（`.claude/rules/zenn-writing.md`）遵守。

## 記事構成（概念主導の実用記事。時系列のセッション再生はしない）

1. **掴み** — AI エージェントと開発すると、コードじゃない資産が溜まる：plan/handoff の `.md`、
   使われなくなった設定、恒偽トリガーで死んだ workflow、参照されない runbook。2〜3文で
   「linter は"構文的に正しいか"しか見ない＝"もう価値がないファイル"を検出できない」に着地。

2. **核心概念（two-tier）** — 構造妥当性（YAML が valid か・link が生きてるか）は byte で決まる
   → **code**。価値（この資産はまだ存在に値するか）は意味の理解が要る → **LLM**。
   `when-code-when-llm` の enumerate（列挙=code）/ decide（判断=LLM）分割。

3. **既製品を探した結論（コンパクトボックス / `:::details` 可）** — 構造チェックは
   MegaLinter / super-linter 等が成熟 ＝ 自作するな。意味的な"価値"レビューだけ既製品が薄い
   （Dosu は docs-drift 限定・商用 SaaS）＝ そこだけ薄く足す。※探索の応酬（scout・Dosu 却下）は畳む。

4. **スキルの設計** — two-tier を図/表で：
   - tier-1（code, inline grep/find）: 消費者到達性を列挙して gray-zone を絞る
   - tier-2（LLM, holistic）: 絞った候補だけ価値判断 → Keep / Update / Retire / Merge（数値スコアなし）
   - **consumer 分類表**（記事の転用核）: tool-invocation / CI-trigger / human-navigation → 到達性チェック
   - Reversibility Gate: Retire は soft-delete（`.disabled` rename）先行、confirm-each

5. **導入（Claude Code ユーザー）** — 公開 repo `shimo4228/repo-asset-stocktake`。
   `/skills add` → `/repo-asset-stocktake [path]` で実行。full / changed モード。

6. **主役デモ（g-kentei-ios）** — 5ヶ月前の開発バーストで生まれた plan/handoff/report が33個、
   入口（PROJECT_TIMELINE→INDEX）1本の切断で CLAUDE.md から丸ごと到達不能。
   **一番刺さる結論＝発見は個別ファイルでなく"構造"**。入口を CLAUDE.md に結線して33ファイル救済。
   埋め込む two-tier 証明2例:
   - **Merge 却下**: 同名 `dead-code-analysis.md` 2本を tier-1 が「重複」候補に上げたが、
     tier-2 の内容比較が「別解析（Python vulture vs 手動 Swift）だから merge で情報損失」と却下。
     単純な basename-dedup linter なら誤統合していた。
   - **誤 Retire 回避**: `.claude/skills/*.md` 9本は inbound-link 0 だが消費者は human でなく
     Claude Code の skill loader ＝ orphan ではない。「消費者を正しく定義せよ」が9件の誤削除を防いだ。
   - zenn-content の `.gitignore` 矛盾（archive/ が ignore 宣言に反し tracked＝GitHub 公開継続）は
     「同じスキルが別の資産クラスも拾う」補足として1〜2文。

7. **応用（カスタムスキルを使わない読者向け・記事の持ち帰り）** —
   一般原則「あらゆる非コード資産には消費者がいる。消費者が消えた/奉仕しなくなったら review 候補」＋
   consumer 分類表（どのエージェント/手動でも回せる）＋
   **gotcha「reachability=0 ≠ dead」**: 間接消費（wrapper 経由の prettier / remote `uses:` action /
   mkdocs nav の doc）を見落とすと live 資産を誤って殺す。← cross-model review（codex）が
   同一モデルでは共有する盲点を捕まえた実話として1つ添える（"作った話"の学び＝応用 caveat を同節で両立）。

8. **まとめ** — 持ち帰りパターン：構造は既製 linter に任せ、価値判断だけ LLM を薄く重ねる。
   list は最小限、why を1行添える。

## 事実確認が要る主張（fact-checker 対象）

- MegaLinter / super-linter が yamllint・actionlint・markdownlint 等を束ねる（実在・機能）
- Dosu = 商用・docs-to-code drift 検出（スコープ。scout が blog 由来と明記していた → 断定を弱める or 出典明示）
- foam-cli `foam list orphans` / knip の unused-devDependency（Cat1）挙動
- ※スキル内の学術引用（BinEval / CheckEval arXiv:2403.18771 / TICK arXiv:2410.03608）は
  **実用記事には入れない**（practical 軸に不要。入れるなら fact-check 必須）

## Files

- `articles/non-code-asset-value-stocktake.md` — 新規作成（JP、スラッグ要確定）
- 画像を使うなら `images/` に（当面はテキスト＋Mermaid 図で two-tier / 島構造を表現、外部画像に依存しない）
- `articles-en/` 英訳 + `schedule.json` 登録は公開確定後（devto-translator）。本プランのスコープ外

## Writing Chain（型: writing）

- **執筆**: orchestrator 本体が `zenn-practical-writing` で直接執筆
- **Parallel Group（レビュー）**: `editor`（Zenn 全記事共通）+ `fact-checker`（上記主張）+
  codex-review（公開記事の cross-model、**prompt-driven モード必須**）を並列
- **Verdict マッピング**: MAJOR ISSUES / ❌ INACCURATE → CRITICAL 停止、NEEDS REVISION → HIGH 継続+修正
- **Verify 相当（writing 版）**: (1) frontmatter 検証 `npm run validate`（zenn list:articles）
  (2) fact gate（fact-checker verdict の出典編入）(3) `git status` 確認
- **人間 gate**: `published: true` にする前にユーザー確認（自動公開しない。MEMORY 記録の公開ワークフロー準拠）

## Verification（end-to-end）

1. `cd ~/MyAI_Lab/zenn-content && npm run validate` で frontmatter が通る
2. `npm run preview` で表示崩れ・Mermaid 図・`:::details` の描画確認
3. コードスニペット/コマンド（`/skills add`, `/repo-asset-stocktake`, `git mv ... .disabled`）が
   セッションログの実コマンドと一致（捏造ゼロ）
4. プロジェクト用語表違反ゼロ（pdf2anki 系の書き換え禁止ワードは本記事では非該当だが機械的に確認）
5. editor / fact-checker / codex-review 3並列が CRITICAL 0 で通過
6. 個人パス（/Users/...）・API キー・秘匿情報がスクショ/コード片に無い（PUBLIC repo）
