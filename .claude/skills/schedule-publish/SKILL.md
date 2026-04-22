<!-- origin: original -->
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

lint・レビューの完了状態。

| Score | 基準 |
|-------|------|
| 3 | lint クリア、CRITICAL なし |
| 2 | 軽微な lint エラーのみ |
| 1 | MEDIUM 修正が残る |
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
| 曜日 | 火曜・木曜（参考） | Zenn のビュー数が火水にピーク（220記事データセット）。強制ではない |
| 時刻 | 8:00-9:00 JST（参考） | 通勤時間帯の閲覧。強制ではない |
| 間隔 | 最低2日空ける | 各記事の「新着」フィード露出時間を確保 |
| 上限 | 週2本まで | 品質シグナルを維持、フィード占有を回避 |
| クロスポスト | Zenn 公開当日または翌日 | Dev.to(EN) のみ |

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

### Step 3: 日程生成

スコア順に `scripts/plan_schedule.py` で日程を割り当てる。

```bash
cd /Users/shimomoto_tatsuya/MyAI_Lab/zenn-content
python scripts/plan_schedule.py --start YYYY-MM-DD --slugs "slug1,slug2,slug3"
```

### Step 4: ユーザー確認

生成されたスケジュールを表形式で提示し、承認を得る。

### Step 5: schedule.json 更新

承認後、`schedule.json` にエントリを追加する。

---

## Output Format（schedule.json エントリ）

> **正本:** `.claude/refs/schedule-schema.md` を参照。

`refs/schedule-schema.md` のスキーマに準拠してエントリを追加する。スコアリング結果は `score` フィールドにトレーサビリティ用に記録:

```json
{
  "file": "articles/example-article.md",
  "date": "2026-04-15",
  "score": { "discover": 2, "anchor": 1, "ready": 3, "fresh": 1, "total": 7 }
}
```

**Zenn 公開は `published_at` 予約投稿方式:**
- frontmatter に `published: true` + `published_at: YYYY-MM-DD HH:MM` (JST) を設定
- `git push` すれば指定時刻に自動公開。レートリミットにカウントされない

---

## Cross-Post Timing

**Zenn 公開:** `published_at` 予約投稿（push 時点で予約、指定時刻に自動公開）

**Dev.to クロスポスト:**
- `devto_crosspost.py` で Dev.to API 経由の自動投稿（GitHub Actions cron 07:00 JST）
- `devto-translator` エージェントで翻訳→投稿を一気通貫も可
- Dev.to API レートリミット: 30秒間隔

---

## Sources

スコアリング基準の根拠:

- Zenn 220記事データセット: 火水がビューピーク、短文/長文が中間より高パフォーマンス
- HubSpot 13,500社調査: 一貫した投稿頻度 > 一括大量投稿
- Pillar-Cluster SEO モデル: アンカー記事を先に公開し、後続記事からリンク
- Qiita 2025比較データ: Zenn がエンゲージメントで Qiita を逆転
