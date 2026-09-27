# 実測ベースの記事 Eval ループ（Measure）の導入

## Context

「読者が有用・面白いと感じたか、フォローしたいと思ったか」を記事品質アップに繋げたい、というユーザー提案から出発。公開前の予測型レビュアー（面白さ/フォロー意向を LLM が推定）は、(1) Content Integrity / catchify bright-line との衝突リスク、(2) ground truth なし予測の妥当性欠如、(3) 旧バズ分析廃止（2026-03-24）の巻き戻し、の 3 点で不採用とし、**公開後の実測メトリクスで閉じる事後 Eval ループ**を作る（AKC の Measure phase)。grill-me で 5 決定点を確定済み:

1. **還流の線引き**: ideation Step 1 の情報源に実測棚卸し結果を追加。「バズを理由にテーマを推薦しない」（ideation Notes）は維持し、実測は事実提示のみで推薦理由・優劣づけに使わない
2. **メトリクス**: 記事単位 = Zenn liked/bookmarked（非公式 API、認証不要）+ Dev.to reactions/comments/page_views（既存 DEVTO_API_KEY）。加えてフォロワー総数（Zenn/Dev.to）を実行ごとに snapshot
3. **収集トリガー**: 棚卸し skill 実行時に都度取得。launchd 自動化なし（月次目安の人間駆動）
4. **置き場**: 生データ = `scripts/metrics/snapshots.jsonl`（public repo、git 管理）。判定（ランク・所見）= memory `article-quality.md`（非公開）を再開・追記
5. **ランクとの関係**: 実測 tier（相対 上位/中位/下位）を既存 A/B/C（内容品質）と**別軸で並記**。乖離（A×実測低 = 配信問題 / B×実測高 = 読者需要）を棚卸しの主シグナルとする

## 実装

### 1. 収集スクリプト `scripts/metrics_snapshot.py`（新規）

- 既存 `scripts/pyproject.toml`（uv 環境）に追加。依存は既存の requests/httpx 相当（devto_crosspost.py が使うものを再利用 — 新規依存を増やさない）
- **Zenn**: `https://zenn.dev/api/articles?username=shimo4228&order=latest`（ページング）→ slug ごとに liked_count / bookmarked_count / published_at
- **Dev.to**: `/api/articles/me/published`（DEVTO_API_KEY、devto_crosspost.py と同じ取得方法を踏襲）→ slug/URL ごとに public_reactions_count / comments_count / page_views_count。schedule.json の `devto` URL と突合して JP 記事 slug に紐付け
- **フォロワー**: Zenn user API / Dev.to followers API から総数のみ。取れない場合は null で欠損許容（fail-soft）
- 出力: `scripts/metrics/snapshots.jsonl` に append。1 行 = `{ts, source, slug, metrics...}` + 実行ごとに `{ts, type: "followers", zenn, devto}` 1 行。**上書きせず追記**（時系列が自然に貯まる）
- 正規化（いいね/公開後日数 等）は書き込まず、読み出し側（棚卸し）で計算する — 生データは raw のまま
- テスト: `scripts/tests/` に追加。API 応答は fixture/fake で（testing.md: 過剰 mock 回避、ネットワーク境界のみ）。突合ロジックと jsonl append を中心に

### 2. 棚卸し skill `.claude/skills/article-stocktake/SKILL.md`（新規、user-invocable、origin: shimo4228）

`*-stocktake` ファミリーの命名に合わせる。フロー:

1. `uv run python metrics_snapshot.py` を実行して最新 snapshot を追記
2. 正規化して相対 tier（上位/中位/下位。公開後日数で補正した いいね率ベース、Dev.to views は補助）を算出 — **絶対スコアを出さない**（output discipline: 行動を変える乖離だけ提示）
3. **乖離表**を提示: 内容ランク（A/B/C、memory の article-quality.md）× 実測 tier のマトリクスで、乖離セルの記事だけ列挙 + 定性所見
4. ランク・tier の更新案を提示し、**人間の確認後に** memory `article-quality.md` を更新（列追加: 実測 tier / 判定日）
5. ideation が読む前提のサマリ（届いたテーマ・構造の事実 3-5 行）を article-quality.md 冒頭に残す

ガードレールを skill 内に明記: 既存記事のエンゲージメント目的リライトを提案しない（Content Integrity / catchify bright-line）。還流先は企画（ideation）と配信（schedule-publish / seo-optimizer の Distribution 層）のみ。

### 3. `ideation/SKILL.md` の Step 1 に情報源を 1 行追加

「5. **実測フィードバック**: article-stocktake の最新結果（memory: article-quality.md）— 過去に読者へ届いたテーマ・構造の事実。**推薦理由・優劣づけには使わない**（Notes の禁止条項は維持）」

### 4. ADR-0005 `docs/adr/0005-post-publication-eval-loop.md`（新規）+ index 更新

- Decision: 実測事後 Eval ループの採用。公開前の予測型エンゲージメントレビュアーは**不採用**（Alternatives に理由 3 点: Content Integrity 抵触 / ground truth なし / 旧バズ分析廃止の巻き戻し）
- 還流の線引き（情報源 ○ / 推薦理由 ×）と、ランク別軸並記（乖離がシグナル）を記録
- 旧バズ分析（memory: buzz-analysis.md、2026-03-24 廃止）との違い: 還流先がタイトル・インプレッション（Content 改変圧）でなく企画レイヤー

### 5. ドキュメント同期

- `docs/CODEMAPS/skills.md`: skill 表に article-stocktake、Workflow に事後ループ 1 行追加、ヘッダ更新
- `CLAUDE.md`: Writing skills 表に 1 行（任意、最小限）

## Human Gate

skill / ADR / ideation 追記は behavior-shaping artifact — コミット前に本文提示。memory 更新（article-quality.md の形式変更）は棚卸し初回実行時に人間確認。

## Verification

1. `cd scripts && uv run pytest` — 既存テスト含め全 PASS
2. `uv run python metrics_snapshot.py` を実際に 1 回実行（read-only GET のみ）→ `scripts/metrics/snapshots.jsonl` に Zenn/Dev.to/followers の行が生成されることを確認。API 欠損時に fail-soft することを確認
3. 小規模トライアル（Prototype Before Scale）: 記事 3-5 本分の乖離表を手で確認し、tier 算出が直感と大きくずれないことを見てから全記事棚卸しへ
4. `git status` — scripts/metrics/ と新規ファイルのみ
