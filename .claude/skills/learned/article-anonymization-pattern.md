---
name: article-anonymization-pattern
description: "実在サービスの技術記事を匿名化して公開する際の置換・削除・検証パターン"
user-invocable: false
origin: auto-extracted
---

# Article Anonymization Pattern（記事の匿名化パターン）

**Extracted:** 2026-03-07
**Context:** AEON ネットスーパーの Playwright 自動化ドラフト2本を、サイト固有情報を排除した1本の汎用記事に再構成した

## Problem

実在サービスを対象とした技術記事を公開すると:
1. 認証後ページの操作手法公開 → 悪用リスク
2. サイト固有セレクタ・URL 構造の詳細 → 攻撃ベクトル
3. 著者の信頼性への悪影響 → 「グレーなことをする人」という印象

## Solution

### 3段階の匿名化

1. **削除**: 認証突破・SSO・セッション管理の詳細は丸ごと削除
2. **置換**: サイト固有セレクタを OSS フレームワークの汎用クラスに置換
   - `.order-product-item`（サイト固有）→ `.products-grid .product-item`（Magento 共通）
3. **再フレーミング**: データ取得手段への言及を回避
   - 「スクレイピングで取得」→「CSV/JSON で手元にある」

### 検証 grep（必須）

記事完成後に以下を必ず実行:

```bash
# サービス名・ドメイン
grep -iE "AEON|aeon|shop\.aeon|gate\.aeon" articles/TARGET.md

# サイト固有セレクタ
grep -E "order-product-item|cw-item-product|/sales/order" articles/TARGET.md

# 認証関連
grep -E "SSO|認証突破|認証回避|セッション.*寿命" articles/TARGET.md
```

### OSS フレームワーク名の扱い

- Magento, KnockoutJS 等の **OSS 名は出してよい**（公知の情報）
- 「Magento ベースの EC サイト」で特定サイトを推測させない

## When to Use

- 実在サービスを対象に開発した自動化・スクレイピングの記事を書くとき
- 認証後ページの操作手法を含む記事を公開するとき
- 特定サイトの DOM 構造に言及するコード例を汎用化するとき
