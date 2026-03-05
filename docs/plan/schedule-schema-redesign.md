# schedule.json スキーマ刷新 — 1記事 = 1エントリ、4プラットフォーム同時投稿

## Context

現状の schedule.json は冗長:
- 日本語エントリと英語エントリが同じ記事なのに別行
- `zenn_date` / `date` の2つの日付
- `devto: "n/a"`, `hashnode: "n/a"` など不要フィールド
- `file`, `canonical_url`, `zenn_published` など導出可能な冗長フィールド

要件:
1. 日本語ベース記事 → Zenn + Qiita に投稿
2. 英語記事（手動で `/translate-article` で事前作成） → Dev.to + Hashnode に投稿
3. 4プラットフォーム同時投稿
4. 英語記事生成はパイプライン外（手動）

---

## 新スキーマ

```json
{
  "articles": [
    {
      "slug": "daily-research-postmortem",
      "publish_date": "2026-02-22",
      "zenn": null,
      "qiita": null,
      "devto": null,
      "hashnode": null
    }
  ]
}
```

### フィールドルール

| フィールド | ルール |
|------------|--------|
| `slug` | 記事の識別子。ファイルパスを自動導出: `articles/{slug}.md`, `articles-en/{slug}.md` |
| `publish_date` | この日に全プラットフォームへ同時投稿（日付は1つだけ） |
| `zenn` | `null` = 未公開、URL = 公開済み |
| `qiita` | `null` = 未投稿、URL = 投稿済み |
| `devto` | `null` = 未投稿、URL = 投稿済み、**フィールドなし = スキップ** |
| `hashnode` | `null` = 未投稿、URL = 投稿済み、**フィールドなし = スキップ** |

### 廃止フィールド

`file`, `canonical_url`, `zenn_date`, `date`, `zenn_published`, `"n/a"` 値

### 自動導出ロジック

```python
ZENN_BASE = "https://zenn.dev/shimo4228/articles"

slug = entry["slug"]
ja_path   = f"articles/{slug}.md"          # Zenn / Qiita のソース
en_path   = f"articles-en/{slug}.md"        # Dev.to / Hashnode のソース
canonical = f"{ZENN_BASE}/{slug}"           # Dev.to / Hashnode の canonical URL
```

### プラットフォーム × ソースファイル

| Platform | ソース | 言語 |
|----------|--------|------|
| Zenn | `articles/{slug}.md` | 日本語 |
| Qiita | `articles/{slug}.md` | 日本語 |
| Dev.to | `articles-en/{slug}.md` | 英語 |
| Hashnode | `articles-en/{slug}.md` | 英語 |

---

## 変更ファイル

### 1. `scripts/schedule.json` — データマイグレーション

日本語エントリ + 英語エントリを slug で統合。
- 同一 slug のエントリを1つにまとめる
- 投稿済み URL は保持
- 廃止フィールドを削除

**変換例:**

Before（2行）:
```json
{
  "file": "articles/daily-research-agent-team.md",
  "canonical_url": "https://zenn.dev/shimo4228/articles/daily-research-agent-team",
  "zenn_date": "2026-02-21",
  "date": "2026-02-21",
  "qiita": "https://qiita.com/...",
  "devto": "n/a",
  "hashnode": "n/a",
  "zenn_published": true
},
{
  "file": "articles-en/daily-research-agent-team.md",
  "canonical_url": "https://zenn.dev/shimo4228/articles/daily-research-agent-team",
  "date": "2026-02-22",
  "devto": "https://dev.to/...",
  "hashnode": "https://hashnode.dev/..."
}
```

After（1行）:
```json
{
  "slug": "daily-research-agent-team",
  "publish_date": "2026-02-21",
  "zenn": "https://zenn.dev/shimo4228/articles/daily-research-agent-team",
  "qiita": "https://qiita.com/...",
  "devto": "https://dev.to/...",
  "hashnode": "https://hashnode.dev/..."
}
```

---

### 2. `scripts/plan_schedule.py` — スケジュール生成

**変更点:**
- `generate_schedule()`: `slug`, `publish_date` ベースに変更
- `articles-en/{slug}.md` が存在すれば `devto: null`, `hashnode: null` を追加
- `--crosspost-delay` オプション削除
- 表示カラム: `Date`, `Slug`, `EN?`, `Score`

**生成エントリ例（英語記事あり）:**
```json
{
  "slug": "new-article",
  "publish_date": "2026-02-25",
  "zenn": null,
  "qiita": null,
  "devto": null,
  "hashnode": null
}
```

**生成エントリ例（英語記事なし）:**
```json
{
  "slug": "ja-only-article",
  "publish_date": "2026-02-25",
  "zenn": null,
  "qiita": null
}
```

---

### 3. `scripts/zenn_publish.py` — Zenn 自動公開

**変更点:**

| 変更前 | 変更後 |
|--------|--------|
| `entry.get("zenn_date")` | `entry.get("publish_date")` |
| `entry.get("zenn_published")` | `bool(entry.get("zenn"))` |
| `entry["file"]` | `f"articles/{entry['slug']}.md"` |
| `entry["zenn_published"] = True` | `entry["zenn"] = f"{ZENN_BASE}/{slug}"` |

公開後に `entry["zenn"]` に canonical URL をセットし、その後クロスポストを呼ぶ（現行の `scheduled_publish.publish_due()` 呼び出しを維持）。

---

### 4. `scripts/scheduled_publish.py` — クロスポスト

**変更点:**

`_is_entry_done()`:
```python
def _is_entry_done(entry: dict) -> bool:
    for platform in ("zenn", "qiita", "devto", "hashnode"):
        if platform in entry and not entry[platform]:
            return False
    return True
```

`_process_entry()`:
- `canonical = f"https://zenn.dev/shimo4228/articles/{entry['slug']}"`
- **qiita**: `parse_zenn_article(f"articles/{slug}.md")`
- **devto/hashnode**: `parse_zenn_article(f"articles-en/{slug}.md")`
- フィールドが存在しないプラットフォームはスキップ
- 英語ファイルが存在しない場合は warning ログ + スキップ

`publish_due()`:
- `entry["date"]` → `entry["publish_date"]`

`show_status()`: 新スキーマに合わせて表示を調整

---

### 5. 変更なし

- `scripts/publish.py` — ライブラリ/CLI、スキーマ非依存
- `scripts/tests/test_publish.py` — publish.py のテストのみ対象

---

## 実装順序

1. `schedule.json` マイグレーション（既存データを新スキーマに変換）
2. `plan_schedule.py` 修正
3. `zenn_publish.py` 修正
4. `scheduled_publish.py` 修正
5. 全体検証（dry-run + テスト）

---

## 検証コマンド

```bash
# スケジュール生成の確認
python scripts/plan_schedule.py --start 2026-02-25 --slugs "test-slug" --dry-run

# Zenn 公開の dry-run
python scripts/zenn_publish.py --dry-run

# クロスポスト状況の確認
python scripts/scheduled_publish.py --status

# クロスポストの dry-run
python scripts/scheduled_publish.py --dry-run

# テスト（publish.py は変更なしなので通るはず）
cd scripts && python -m pytest tests/ -v
```
