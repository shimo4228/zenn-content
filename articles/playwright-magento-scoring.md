---
title: "click() は3回裏切る — Playwright × Magento 実戦パターン集"
emoji: "🎭"
type: "tech"
topics: ["playwright", "python", "magento", "automation"]
published: true
---

## はじめに

Magento ベースの EC サイトを Playwright で自動操作しようとした。Magento は Adobe が開発するオープンソースの EC プラットフォームで、国内外の多くのネットショップが採用している。配送日時の設定、商品検索、データ取得——やることは単純だ。`click()` して、テキストを読んで、次のページに行く。

3回目に `click()` が裏切られた時点で、「これは入門記事に書いてあるやつと違う」と悟った。

この記事では、Magento/KnockoutJS サイトで遭遇した Playwright のハマりポイント5つを紹介する。KnockoutJS は Magento のフロントエンドで使われている JavaScript フレームワークで、動的な UI を実現するが、自動化の観点では厄介な挙動を生む。後半では、購入データに時間減衰スコアリングを適用して「定番商品リスト」を自動生成する手法も記録した。

<!-- textlint-disable -->
:::message
コード例のセレクタやモジュール名は汎用化してある。Magento サイトごとにテンプレートが異なるため、実際の DOM はサイトに合わせた調査が必要だ。
:::
<!-- textlint-enable -->

## Magento/KnockoutJS の5つの罠

### 罠1: viewport 外の要素はクリックできない

viewport とは、ブラウザウィンドウ上で現在表示されている領域のことだ。Playwright は原則として、この領域内に見えている要素しかクリックできない。

Magento のモーダル（ページ上にポップアップ表示されるダイアログ）でラジオボタンをクリックしようとした。

```python
# NG: 通常の click — "Element is outside of the viewport"
radio.click()

# NG: force=True — Magento モーダル内では同じエラー
radio.click(force=True)

# NG: scroll_into_view_if_needed — モーダルのスクロールコンテナが対象外
radio.scroll_into_view_if_needed()
radio.click(force=True)
```

3つ試して全滅した。

原因は Magento モーダルの構造にある。Magento は `.modal-popup.modal-slide._inner-scroll` という独自のスクロールコンテナを持つ。Playwright の viewport ベースのスクロールとは別系統だ。`scroll_into_view_if_needed()` はページ全体には効くが、モーダル内部には到達できない。

解決策は JavaScript で直接クリックすること。

```python
# OK: JavaScript で直接クリック — viewport 制約を完全回避
radio.evaluate("el => el.click()")
```

`evaluate()` は DOM イベントを直接発火する。要素が viewport 内にあるかどうかは関係ない。Magento のモーダル操作では、これを標準パターンにするのが無難だった。確定ボタンも同じ viewport 外問題を抱えていたので、モーダル内の操作は全て `evaluate("el => el.click()")` に統一した。

### 罠2: text= セレクタが非表示要素にマッチする

```python
# NG: query_selector は非表示要素もマッチする
trigger = page.query_selector("text=配送日時を選択")
trigger.click()  # TimeoutError: element is not visible
```

要素は見つかる。でもクリックできない。

原因は KnockoutJS のテンプレート構造にあった。Magento は同じテキストをデスクトップメニュー、モバイルメニュー、サイドバーなど複数箇所にレンダリングする。`query_selector` は DOM 順で最初にマッチした要素を返すが、それが表示中とは限らない。

```python
# OK: Locator API で可視要素のみ対象
locator = page.locator("text=配送日時を選択").locator("visible=true")
if locator.count() > 0:
    locator.first.click()
```

Locator API の `visible=true` フィルタで、表示中の要素だけに絞れる。KnockoutJS サイトでは `query_selector` より Locator API を優先すべきだ。

### 罠3: 同一サイト内に2種類のカード構造がある

商品カードのセレクタを書いた。サイドバー（ミニカート）では動く。検索結果ページでは0件。

調べてみると、サイドバーとメインコンテンツで異なるカード構造を使っていた。Magento はページの文脈によって異なるテンプレートを適用するため、1つのセレクタでサイト全体をカバーできない。

```python
# ページ種別ごとにセレクタを管理する
SELECTORS = {
    "sidebar": {
        "product_card": ".sidebar .product-item",
        "product_name": ".product-item-name a",
    },
    "main": {
        "product_card": ".products-grid .product-item",
        "product_name": ".product-item-link",
    },
}

def get_selector(page_type: str, element: str) -> str:
    return SELECTORS[page_type][element]
```

セレクタをページ種別ごとに辞書で一元管理する。DOM が変わったときの修正箇所が1ファイルに限定される。

### 罠4: モーダル内の混在行を正規表現でフィルタする

配送日時のモーダルを開くと、十数行のテーブルが現れる。しかし全行が同じ構造ではない。

```text
行0: "○○店"                → 店舗選択行（不要）
行5: "3/7 14:00-16:00 ○"   → 時間帯行（必要）
行8: "\n     \n     "      → 空行（不要）
```

店舗行、時間帯行、空行が混在している。行のインデックスは固定ではないので、内容で判別するしかない。

```python
import re

def is_time_slot_row(row_text: str) -> bool:
    """時間帯パターン（14:00-16:00 等）を含む行だけを抽出する"""
    return bool(re.search(r"\d{1,2}:\d{2}-\d{1,2}:\d{2}", row_text))
```

正規表現で時間帯パターン（`HH:MM-HH:MM`）を検出する。構造が不安定なモーダルでは、DOM セレクタよりテキストパターンの方が堅牢だった。

### 罠5: 日本語記号（○△✕）による状態判定

配送スロットの空き状況は、CSS クラスではなく日本語記号で表現されていた。

```python
def parse_slot_availability(row_text: str) -> dict | None:
    time_match = re.search(r"(\d{1,2}:\d{2}-\d{1,2}:\d{2})", row_text)
    if not time_match:
        return None

    # ○ = 空きあり、△ = 残りわずか、✕ = 満杯
    available = "○" in row_text or "△" in row_text

    return {
        "time_range": time_match.group(1),
        "available": available,
    }
```

`class="available"` のような英語の属性を期待していたが、テキストに埋め込まれた全角記号で判定する必要があった。国内の EC サイト——特に Magento の日本語テーマ——ではよくあるパターンだ。

## 購入データの時間減衰スコアリング

5つの罠を越えて、Playwright で EC サイトの購入データを取得できた。CSV や JSON にエクスポートした商品リストが手元にある。次の問いは「このデータをどう活用するか」だ。

やりたいことは単純で、「よく買う商品」を自動でリストアップしたい。

単純な購入回数だけだと、半年前に10回買った商品と先週3回買った商品の区別がつかない。そこで**時間減衰**を導入する。

### 入力データ

```json
[
  {
    "name": "牛乳 1L",
    "purchased_at": ["2026-01-15", "2026-02-01", "2026-02-15", "2026-03-01"]
  },
  {
    "name": "食パン 6枚切",
    "purchased_at": ["2025-12-01", "2025-12-15", "2026-01-01"]
  }
]
```

各商品に購入日の配列がある。この配列から「最近どれだけ買っているか」をスコア化する。

### アルゴリズム: count × decay^weeks

```python
import math
from datetime import date


def compute_recency_score(
    entry: dict,
    reference_date: date | None = None,
    decay_rate: float = 0.8,
) -> float:
    """score = purchase_count × decay_rate ^ weeks_since_last_purchase"""
    ref = reference_date or date.today()
    purchased_at = entry.get("purchased_at", [])

    if not purchased_at:
        return 0.0

    purchase_count = len(purchased_at)
    last_date = date.fromisoformat(max(purchased_at)[:10])
    weeks_since = max(0, (ref - last_date).days / 7)

    return purchase_count * math.pow(decay_rate, weeks_since)
```

スコアの構成要素は2つだ。

- **purchase_count** — 購入回数が多いほどスコアが高い（定番度）
- **decay_rate ^ weeks** — 最終購入日から時間が経つほどスコアが下がる（鮮度）

たとえば「牛乳 1L」を基準日 `2026-03-07` で計算すると以下のようになる。

<!-- textlint-disable -->

- 購入回数: 4回
- 最終購入日からの経過: 約0.86週
- スコア: `4 × 0.8^0.86 ≈ 3.33`

<!-- textlint-enable -->

一方「食パン 6枚切」はこうなる。

<!-- textlint-disable -->

- 購入回数: 3回
- 最終購入日からの経過: 約9.3週
- スコア: `3 × 0.8^9.3 ≈ 0.38`

<!-- textlint-enable -->

購入回数では食パンが3回で牛乳に近いが、最終購入が2ヶ月以上前なので大幅に減衰する。直感に合う結果だ。

### decay_rate の選び方

`decay_rate` は**半減期**で考えると直感的になる。

| decay_rate | 半減期（スコアが半分になるまで） |
|------------|-------------------------------|
| 0.9 | 約6.6週（1.5ヶ月） |
| 0.8 | 約3.1週（3週間） |
| 0.7 | 約1.9週（2週間弱） |

半減期の計算式: `ln(0.5) / ln(decay_rate)`

週1回の買い物ペースなら `0.8`（半減期 ≈ 3週間）が妥当だった。3週間買わなければ「もう定番じゃないかも」という感覚と一致する。`0.9` だと減衰が緩すぎて季節限定品がいつまでも残り、`0.7` だと1回買い忘れただけでスコアが急落する。

### 差分更新パターン

購入データが増えるたびに全件を再処理するのは無駄だ。既知の ID で差分を管理する。

```python
import json
from pathlib import Path


def update_incrementally(
    new_entries: list[dict],
    meta_path: Path,
) -> list[dict]:
    """既知IDをスキップし、新規エントリだけを返す。

    PRECONDITION: new_entries は時系列降順（新しい順）であること。
    既知IDに到達した時点で残りをスキップするため、順序が保証されない場合は
    break を continue に変更する必要がある。
    """
    if meta_path.exists():
        known_ids = set(json.loads(meta_path.read_text()))
    else:
        known_ids = set()

    unseen = []
    for entry in new_entries:
        entry_id = entry["id"]
        if entry_id in known_ids:
            # 時系列降順なら、既知IDに到達した時点で残りはスキップできる
            break
        unseen.append(entry)

    # 新規IDを保存
    known_ids.update(e["id"] for e in unseen)
    meta_path.write_text(json.dumps(sorted(known_ids)))

    return unseen
```

データが時系列降順（新しい順）で並んでいる前提だが、多くの EC サイトの注文履歴はこの並び順だ。初回は全件処理、2回目以降は新規分だけで済む。

## まとめ

### Magento × Playwright の5つの教訓

1. **`click()` が通らないときは `evaluate("el => el.click()")` を使え** — Magento モーダルの viewport 外問題はこれで一発解決する
2. **`query_selector` より Locator API を優先せよ** — KnockoutJS は同じテキストを複数箇所にレンダリングする
3. **セレクタはページ種別ごとに管理せよ** — Magento はコンテキストでテンプレートを切り替える
4. **不安定な構造にはテキストパターンで対抗せよ** — 正規表現は DOM セレクタより安定することがある
5. **日本語記号をテキスト判定に使う覚悟を持て** — CSS クラスが付いているとは限らない

### 時間減衰スコアリングの応用

`count × decay^weeks` は購入データに限らず、「頻度 × 鮮度」で優先順位を付けたい場面で汎用的に使える。

- **アクセスログ** — 最近よく見るドキュメントを上位に
- **お気に入り操作** — 使わなくなった項目を自動的に沈める
- **検索クエリ** — 最近のクエリほどサジェスト上位に

`decay_rate` をカテゴリごとに変えれば、減衰速度の調整もできる。生鮮食品は `0.7`（半減期2週間）、日用品は `0.9`（半減期1.5ヶ月）など、ドメインに合わせた設計が可能だ。
