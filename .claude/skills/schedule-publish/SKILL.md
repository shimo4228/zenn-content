---
name: schedule-publish
description: 記事バッチの公開順序と日程を 4 軸スコアリングで決定し schedule.json に反映する。投稿タイミングの値は zenn-writing.md が正本。
user-invocable: true
origin: shimo4228
---

# Schedule Publish Skill

**Purpose:** 記事バッチの公開順序と日程を、データに基づくスコアリングで決定し、`schedule.json` に反映する。

---

## Usage

```
/schedule-publish                    # published: false の全記事を評価
/schedule-publish --start 2026-03-01 # 開始日を指定
```

---

## Decision Framework

### 1. スコアリング（4軸 × 0-3点 = 最大12点）

各記事を以下の基準で評価する。**高スコア = 先に公開**。

#### A. 発見可能性（Discoverability）: 0-3

関心のある読者がこの記事を見つけられるか。

| Score | 基準 | 例 |
|-------|------|-----|
| 3 | 特定の問題を抱えた読者が検索で到達できる | 「Invalid regular expression: invalid escape」 |
| 2 | 具体的なテーマで探している読者が見つけられる | 「Zenn Qiita クロスポスト」 |
| 1 | 一般的なトピック（関心層は広いが特定しにくい） | 「Claude Code の使い方」 |
| 0 | 著者の思索（見つけた人が読む、検索到達は期待しない） | 「マルチLLM戦略」 |

#### B. アンカー度（Anchor）: 0-3

他の記事が前提知識として参照する度合い。

| Score | 基準 |
|-------|------|
| 3 | 3本以上の記事が前提として参照 |
| 2 | 1-2本の記事が前提として参照 |
| 1 | 独立（参照なし） |
| 0 | 他の記事に依存（先に出すべき記事がある） |

#### C. 公開準備度（Readiness）: 0-3

レビュー・品質ゲートの完了状態（prose lint は 2026-07 に全撤去済み。機械チェックは frontmatter 検証のみ）。

| Score | 基準 |
|-------|------|
| 3 | editor レビュー済み、CRITICAL・MEDIUM なし、frontmatter 検証パス |
| 2 | レビュー済み、MEDIUM 修正が残る |
| 1 | レビュー未実施 |
| 0 | CRITICAL 未修正 |

#### D. 話題性（Freshness）: 0-2

トピックのタイムリーさ。

| Score | 基準 |
|-------|------|
| 2 | 直近のトレンド・リリースに関連 |
| 1 | エバーグリーン（時期を問わない） |
| 0 | 古い情報を含む可能性あり |

### 2. 同点時のタイブレーク

スコアが同じ場合、以下の順で優先:

1. **カテゴリ交互配置**: 連続する2記事が同カテゴリにならないよう調整
2. **文字数が少ない方を先**: 短い記事は読了率が高く、初期フォロワー獲得に有利

### 3. 日程割り当てルール

| 項目 | ルール | 根拠 |
|------|--------|------|
| 曜日・時刻 | `.claude/rules/zenn-writing.md`「投稿ペース方針」が正本（バズタイム：火〜水 7:00-9:00 JST）。ここでは再掲しない | 値の二重管理を避ける |
| 間隔 | 最低2日空ける | 各記事の「新着」フィード露出時間を確保 |
| 上限 | `.claude/rules/zenn-writing.md`「投稿ペース方針」が正本（週2-3本）。ここでは再掲しない | 値の二重管理を避ける |
| クロスポスト | EN (Dev.to) は JP の**前日 22:00 JST**（日米ペア既定の正本: `.claude/rules/zenn-writing.md`「投稿予約タイミング」） | Dev.to(EN) のみ |

---

## Workflow

### Step 1: 対象記事の収集

`published: false` の記事を一覧化する。

```bash
grep -rl 'published: false' articles/*.md
```

### Step 2: スコアリング

各記事を4軸で評価し、テーブルで出力する。

```markdown
| # | slug | Discover | Anchor | Ready | Fresh | Total | Order |
|---|------|--------|--------|-------|-------|-------|-------|
```

**重要:** スコアの根拠を1行ずつ明記する。根拠なしのスコアは不可。

### Step 3: 日程割り当て（launchd 予約）

スコア順に投稿日時を決め、各記事を one-shot launchd ジョブとして仕込む（旧 `plan_schedule.py` は廃止）。JP はバズタイム（火水 09:00 JST）に寄せ、EN はその**前日 22:00 JST**（≈ 米国 09:00 ET）。**日時は `--at` 引数で JST 明示で渡す**（schedule.json には保存しない。正本: `.claude/rules/zenn-writing.md`「投稿予約タイミング」）。

```bash
# JP が 2026-07-08 09:00 JST なら、EN はその前日 22:00 JST
cd scripts && uv run python devto_crosspost.py schedule {slug} --at "2026-07-07 22:00 Asia/Tokyo"
```

### Step 4: ユーザー確認

生成されたスケジュールを表形式で提示し、承認を得る。

### Step 5: schedule.json 更新

承認後、`schedule.json` にエントリを追加する。

---

## Output Format（schedule.json エントリ）

> **正本:** `.claude/refs/schedule-schema.md` を参照。

`refs/schedule-schema.md` のスキーマに準拠してエントリを追加する。

**スコアは台帳に書かない**（2026-08-23 に `score` フィールドを廃止 — 112 エントリに 1 件も
書かれておらず、公開処理も読んでいなかった）。スコアリングは**会話で順序を提示するための
判断材料**であって、永続化しない。

**Zenn 公開は `published_at` 予約投稿方式:**
- frontmatter に `published: true` + `published_at: YYYY-MM-DD HH:MM` (JST) を設定
- `git push` すれば指定時刻に自動公開。**⚠ 予約登録自体がレートリミットに計上される**（正本: `.claude/rules/zenn-writing.md`）

---

## Cross-Post Timing

**Zenn 公開:** `published_at` 予約投稿（push 時点で予約、指定時刻に自動公開）

**Dev.to クロスポスト:**
- `devto_crosspost.py schedule {slug} --at "<日時 IANA/Tz>"` で記事ごとの one-shot launchd ジョブを仕込む。指定時刻に発火 → Dev.to へ POST → schedule.json に実 URL を書き戻し → plist 自己削除（GitHub Actions cron / 毎日ポーリングは廃止済み）
- `devto-translator` エージェントで翻訳→投稿を一気通貫も可
- Dev.to API レートリミット: 30秒間隔

---

## Sources

スコアリング基準の根拠:

- Zenn 220記事データセット: 火水がビューピーク、短文/長文が中間より高パフォーマンス
- HubSpot 13,500社調査: 一貫した投稿頻度 > 一括大量投稿
- Pillar-Cluster SEO モデル: アンカー記事を先に公開し、後続記事からリンク
- Qiita 2025比較データ: Zenn がエンゲージメントで Qiita を逆転
