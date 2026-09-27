# X (Twitter) 記事告知の仕組み — grill-me 収束計画

## Context

記事公開時に X へ記事リンクの告知をポストする仕組みを追加する。既存の公開パイプライン
(Zenn = `published_at` + push / Dev.to = `devto_crosspost.py` + launchd one-shot)への
拡張。wikidata-ban-postmortem の教訓(「外部プラットフォームはアカウント全体の振る舞いで
判定する」「エージェントは悪意なく危険な速度に達する」)の適用対象として、実装前に
/grill-me でストレステストを実施し、以下に収束した。

## 確定した設計判断(grill-me 収束結果)

1. **自動化度: 承認済みキュー方式**。ドラフト生成 → 人間が投稿文面そのものを承認
   (human-gate: 外部公開物 = 本文提示)→ 予約時刻に機械が発火。
   「承認は人間・発火は機械」という Dev.to パイプラインの確立パターンを延長する。
   無承認の全自動は Reversibility Gate と衝突するため不採用(採用するなら ADR で override)。
2. **スコープ: JP のみから開始**。Zenn 記事公開時に日本語告知 1 本。
   Prototype Before Scale に従い、EN(Dev.to)は品質ベースライン確立後に拡張判断。
   投稿量は記事ペース(週 2-3)で構造的に上限が付き、aggregate-pattern test を通る。
3. **発火機構: launchd one-shot 再利用 + live 検証**。`devto_crosspost.py` の
   render_plist / install_agent / one-shot 自己削除パターンを踏襲。発火時刻は
   9:00 ちょうどでなく 9:15 等にずらし、**投稿前に記事 URL が 200 を返すか検証。
   未公開なら投稿せず報告(fail-closed)**。Zenn のデプロイ遅延による 404 リンク告知を防ぐ。
4. **告知文規約: craft された一文 + URL のみ、ハッシュタグなし**。生成は
   headline-craft 経由(記事タイトルの重複でなく core claim の別の面)。
   定型フレーズ・固定フォーマットの反復は bot シグナルになるため避ける。
5. **実装形態: 別スクリプト `scripts/x_announce.py`**。devto_crosspost.py の
   self-contained 設計と 59 既存テストに触れない。launchd ヘルパーはパターンとして踏襲。
6. **データ配置**: 承認済み告知文は gitignored のローカル queue ファイル
   (plist と同寿命、投稿後削除)。投稿済み post URL のみ `schedule.json` に記録
   (posted-URL ledger の役割定義に合致。投稿時刻は JSON に保存しない方針を踏襲)。

## rules から導出済み(質問不要だった事項)

- **失敗時 fail-closed**: 投稿失敗・検証失敗は「投稿しない + 報告」。429 (rate limit) は
  retry せず即停止・人間に報告(debugging.md「Rate limit は警報」)。
- **承認ゲートは記事公開の意図確認と同一決裁に束ねる**(1 作業 1 ゲート)。
  件数とスコープを明示(「X 告知 1 件を <時刻> に予約します」)。
- **API キーは `scripts/.env`**(gitignored)。plist に埋めない — DEVTO_API_KEY と同方式。
- **revocable 前提**: X 告知層が丸ごと失われても(アカウント制限等)本体パイプラインは
  無傷 — load-bearing な参照を X に置かない(learned note チェックリスト)。

## 実装前の必須ステップ: Phase 0 (/search-first)

実装着手前に `/search-first` を起動して調査(planning.md Phase 0。skill 呼び出しに固定):

- X API v2 の現行 tier 制約(Free tier の write 上限が月 ~10-12 post に足りるか。
  上限値は頻繁に変わるため Developer Portal の一次情報で確認)と
  認証方式(OAuth 1.0a user context / OAuth 2.0)
- X automation rules(半自動・人間承認済み投稿の位置づけ、automated label の要否)
- 既存解: typefully / buffer / 各種 X API v2 Python クライアント(tweepy 等)。
  Verdict (Adopt/Extend/Compose/Build) を確定してから実装 chain を組む

### X API キー取得手順(人間の作業。実装と独立に先行可能)

1. [developer.x.com](https://developer.x.com) に投稿用 X アカウントでログイン、
   Free プランでサインアップ(use case は「自分の記事公開の告知を自分のアカウントに投稿」)
2. Project + App を作成 → User authentication settings で権限を **Read and Write** に設定
   (既定 Read のみ。忘れると投稿時 403)
3. API Key / API Key Secret + Access Token / Access Token Secret の 4 キーを生成
   (OAuth 1.0a user context — 自分のアカウントへの投稿にはこの 4 点で完結)
4. `scripts/.env` に保存(DEVTO_API_KEY と同方式、gitignored。plist に埋めない)

## 実装ステップ概要(Phase 0 の Verdict 確定後に chain を組む)

1. `implementation-chain` skill で feat 種別の chain を front-load
2. `scripts/x_announce.py` 新設: `draft <slug>` / `schedule <slug> --at` /
   `post <slug>`(launchd が実行、live 検証 → X API 投稿 → schedule.json に URL 記録 →
   agent 自己削除)/ `list` / `unschedule`
3. テスト新設 `tests/test_x_announce.py`(coverage ≥ 80%、respx で X API mock、
   launchctl stub — 既存テストの流儀に合わせる)
4. `docs/CODEMAPS/scripts.md` 更新(Doc Sync)

## Verification

- `cd scripts && uv run pytest --cov=. --cov-report=term-missing`(既存 59 テスト無傷 +
  新テスト ≥80%)
- `x_announce.py post <slug> --dry-run` で: 未公開 URL → fail-closed 中止を実測、
  公開済み URL → 投稿ペイロード生成を確認
- 初回は実記事 1 本で試行(Prototype Before Scale)し、承認 → 発火 → ledger 記録 →
  plist 自己削除の一巡を確認

## ADR 判定

各決定に ADR test(不可逆 / 文脈なしで驚く / 実トレードオフ)を適用 — いずれも
コード変更で可逆なため **ADR 不要**。将来「全自動化」へ override する場合のみ
Reversibility Gate との衝突を ADR に記録する。
