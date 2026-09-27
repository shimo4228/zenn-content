# Dev.to クロスポストの最小再構築 + launchd 自動起動

## Context（なぜやるか）

`scripts/` の Dev.to クロスポスト一式が、実運用の縮退に対してコードが肥大化したまま乖離している。

- **実運用**: schedule.json の due な EN 記事を **手動で** Dev.to へ POST するだけ（cron は 2026-05 廃止、`.github/workflows/` は `lint.yml` のみ、保留投稿は 1 件）。
- **コード**: 本体 1,214 行 + テスト 1,162 行 ≈ 2,400 行。本質は parse/convert/POST/schedule-loop の **~80 行**だけで、残りは (1) 単一媒体への多媒体スキャフォールド（`pyproject` は今も "Qiita, Dev.to, Hashnode"、`.env` に未使用 QIITA/HASHNODE トークン）、(2) `publish.py` の二重人格（ライブラリ + 走らない CLI ~180 行）、(3) 誰も import しない `generate_cover.py`、消費されない JP エントリを吐く `plan_schedule.py`。
- **docstring/README のツリー図は「cron で毎日」のまま stale**。実態（手動）と食い違う。

**目標（ユーザー確定要件）**: 「Dev.to の投稿 API を叩く最小コード」＋「それを **launchd** で自動起動」。cron の代わりに launchd でローカル自動化を復活させ、周辺の肥大コードは削除する。

種別: `refactor`（振る舞いをほぼ保った再構築）+ `chore`（launchd 設定）。Phase 0 は skip（新規依存なし・Dev.to は既存統合・launchd は OS ネイティブ）。

## 設計方針

### 1. 単一スクリプトへ集約: `scripts/devto_crosspost.py`（同名で中身を作り直し）

5 ファイル（`devto_crosspost.py` / `publish.py` / `_schedule_utils.py` / `plan_schedule.py` / `generate_cover.py`）を **1 ファイル ~120-150 行**に集約する。ファイル名は据え置き → README/RUNBOOK/CONTRIB の参照が大きく崩れない。

処理フロー（既存の実証済みロジックを *再ホーム*、regex は再発明しない）:
1. `scripts/.env` から `DEVTO_API_KEY` を読む（`python-frontmatter` + 手書き .env パースは既存 `_load_env` を踏襲）
2. `scripts/schedule.json`（`{"articles": [...]}`）を読む
3. 各 entry をフィルタ: `file` が `articles-en/` 始まり **かつ** `devto` が空 **かつ** `date <= today`
4. `parse_zenn_article` + `_strip_zenn_syntax`（**既存の実証済み変換規則をそのまま移植** — 39 件の成功投稿でテスト済み。ここは regression の温床なので再発明しない）→ Dev.to markdown
5. payload `{article: {title, body_markdown, published:true, tags, main_image?, description?}}` を `POST https://dev.to/api/articles`（header `api-key`）
6. 成功ごとに `entry["devto"]=url` を書き戻し **即 save**（クラッシュ耐性）
7. CLI: `--dry-run` / `--status`（既存の使い勝手を維持）

**捨てるもの（現状の複雑さの源泉）**:
- `publish.py` の CLI 半分（`build_parser`/`_RUNNERS`/`_check_english_translation` 等 ~180 行、cron 経路で走らない第二の入口）
- 多媒体 dispatch（`_RUNNERS` 要素1個、`--platform choices=["devto"]`）
- `find_devto_article_by_title` の upsert（最大 150 件ページング）→ **devto=null チェック + 即 save** で代替
- `map_devto_tags` の 40 エントリ辞書 → **小さな sanitize フォールバック**（lowercase・英数のみ・最大4個）+ schedule の `devto_tags` 明示上書き
- `generate_cover.py`（未 import・カバーは手動運用）、`plan_schedule.py`（消費されない JP エントリ生成）

### 2. JST 日付ゲートのバグ修正

現状 `date.today()`（UTC ランナー基準）で `now_jst()`/`JST` は定義済みだが未使用。`zoneinfo.ZoneInfo("Asia/Tokyo")` で **JST 基準の today** に統一する。launchd はローカル（JST）で走るので実害は小さいが、正す。

### 3. launchd plist（リポジトリ内テンプレート）

`scripts/launchd/dev.shimo4228.devto-crosspost.plist` を **リポジトリ内に置く**（旧 plist はリポジトリ外にあり失われた反省）。

- `StartCalendarInterval`: 毎日 07:00（ローカル=JST）。旧 cron と同挙動、投稿ペース方針のバズタイム（火水 7-9 JST）とも整合
- `ProgramArguments`: venv の Python を **絶対パス**で直指定（launchd は最小 PATH なので `uv`/`python` 名前解決に頼らない）。例: `/Users/.../scripts/.venv/bin/python /Users/.../scripts/devto_crosspost.py`
- `WorkingDirectory`: `scripts/`（.env / schedule.json の相対解決）
- `StandardOutPath`/`StandardErrorPath`: `scripts/devto_crosspost.log`
- 秘匿情報は plist に **書かない**（スクリプトが .env を読む）
- **caveat をプランに明記**: スリープ中に 07:00 を跨ぐと、launchd は次回 wake 時に 1 度だけ実行する（複数回ぶんは溜まらない）。日次投稿には十分
- インストールは人間ゲート: `launchctl load ~/Library/LaunchAgents/dev.shimo4228.devto-crosspost.plist`。**手順は plist 自身のヘッダコメントに自己文書化**（copy/symlink → load → list → start）。runbook を別途持たず、実体の隣に置く

### 4. 掃除（同じ diff で）

- `.env`: 未使用の `QIITA_ACCESS_TOKEN`/`HASHNODE_API_TOKEN`/`HASHNODE_PUBLICATION_ID` を削除（未追跡ファイルなのでローカル編集。DEVTO のみ残す）
- `pyproject.toml`: name/description を Dev.to 専用に、`pillow` 依存を削除（`generate_cover` 消滅で不要）
- **`docs/RUNBOOK.md` と `docs/CONTRIB.md` を削除**（ユーザー指示）。両者は `docs/CODEMAPS/scripts.md` と重複し、今回の再構築で大半が stale（RUNBOOK は `publish.py --platform`・廃止済み `scheduled-publish.yml`・「GitHub UI → Actions」を指す）。ドキュメントの正本を CODEMAPS に一本化する
- 削除に伴う張り替え: **`CLAUDE.md`** が `docs/RUNBOOK.md` を 2 箇所参照（"See docs/RUNBOOK.md for the full testing and publishing workflow" / "Full procedure: docs/RUNBOOK.md"）→ `docs/CODEMAPS/scripts.md` へ repoint。公開済み記事 `articles/ecc-journey-part1.md`・`articles-en/ecc-journey-part1.md` の言及は**遡及変更しない**（历史的 prose）。`.claude/docs/adr/0002` の言及は確認のうえ必要なら注記
- **`docs/CODEMAPS/scripts.md` を今回の正本として更新**: 5 スクリプト → 単一 `devto_crosspost.py`、"No cron" → "launchd 復活（plist 参照）" の 1 行、テスト数を実測値に。手順は流し込まず地図に留める（トークン軽量を維持）
- `README.md`/`README.ja.md`: ツリー図の "cron" 注記を "launchd" に。`docs/CODEMAPS/architecture.md` の投稿経路注記を更新。stale な docstring も修正

### 5. テスト

- 新規 `scripts/tests/test_devto_crosspost.py`（respx で POST モック）: dry-run 不変 / JST 日付ゲート / done・future・JP スキップ / 投稿成功で per-entry save / API キー欠落で異常終了
- 削除ファイルのテスト（`test_publish.py`/`test_plan_schedule.py`/`test_generate_cover.py`/`test_schedule_utils.py`）は対象消滅につき削除
- coverage ≥ 80%（`pyproject` の `fail_under=80` 維持）

## 変更対象ファイル

| 操作 | パス |
|---|---|
| 全面書換 | `scripts/devto_crosspost.py`（5→1 集約先） |
| 新規 | `scripts/launchd/dev.shimo4228.devto-crosspost.plist` |
| 新規 | `scripts/tests/test_devto_crosspost.py`（差し替え） |
| 削除 | `scripts/publish.py`, `scripts/_schedule_utils.py`, `scripts/plan_schedule.py`, `scripts/generate_cover.py` |
| 削除 | `scripts/tests/test_publish.py`, `test_plan_schedule.py`, `test_generate_cover.py`, `test_schedule_utils.py` |
| 削除 | `docs/RUNBOOK.md`, `docs/CONTRIB.md`（CODEMAPS と重複・stale） |
| 編集 | `scripts/pyproject.toml`, `scripts/.env`, `CLAUDE.md`（RUNBOOK 参照の張り替え）, `README.md`, `README.ja.md`, `docs/CODEMAPS/scripts.md`（正本）, `docs/CODEMAPS/architecture.md` |

> schedule.json は **触らない**（新スクリプトが `articles-en/` だけ読むようフィルタ）。JP エントリ39件の掃除は別タスク。データ変更のリスクを本タスクに持ち込まない。

## Chain / 並列化

```
Sequential: 実装（単一スクリプト + plist + テスト） → Review 群 → Verify
Parallel Group (実装後・同一 diff): [code-reviewer, security-reviewer, codex-review]
```
- code-reviewer: 集約スクリプトの品質・可読性
- security-reviewer: DEVTO_API_KEY の扱い・HTTP POST・path 検証（`validate_article_path` 相当の移植）・.env / plist の秘匿境界
- codex-review: cross-model 脱相関（Dev.to へ実 POST する非自明 diff。read-only）
- いずれか CRITICAL で停止・報告

## Verify（コミット前）

1. `cd scripts && uv run pytest --cov=. --cov-report=term-missing`（coverage ≥ 80）
2. `uv run python devto_crosspost.py --dry-run` — due EN の検出結果を目視（今日時点 due=0、7/07 の 1 件が future 判定になること）
3. `uv run python devto_crosspost.py --status` — 投稿済み/保留の一覧が出ること
4. launchd 動作確認（人間ゲート）: plist を `~/Library/LaunchAgents/` に copy → `launchctl load` → `launchctl list | grep devto` で登録確認 → `launchctl start` で 1 回手動発火し、`devto_crosspost.log` にログが出ること（**--dry-run 相当で実 POST しない検証手順**を用意）
5. secret scan: `.env` 未追跡の再確認、plist に鍵が無いこと、削除後にハードコード鍵が残らないこと
6. Doc Sync 確認: RUNBOOK/CONTRIB 削除済み・CLAUDE.md の参照張替済み・CODEMAPS(scripts/architecture) と README が同じ diff で更新済み。`grep -rn "RUNBOOK\|CONTRIB\|publish.py\|plan_schedule\|generate_cover" docs/ README*.md CLAUDE.md` で死んだ参照が残らないこと
7. `git status` — 意図しないファイルが無いこと

全 PASS で **ユーザーに push を促してから**コミット（CLAUDE.md の Git Push Reminder）。

## 早期停止

- Review 群のいずれかが CRITICAL
- Verify の pytest / dry-run が失敗
- Zenn→Dev.to 変換で既存投稿と本文が乖離（移植した strip 規則の regression）
