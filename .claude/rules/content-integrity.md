# Content Integrity 原則

> 根拠: [ADR-0001](../docs/adr/0001-content-integrity-principle.md)

## ルール

**内容は著者の思考が決める。配信戦略は内容を変えずに最適化する。**

## Content / Distribution の判定

| 操作 | レイヤー | 許可 |
|------|---------|------|
| タイトルの語選び・キーワード調整 | Distribution | OK |
| タグ・emoji の最適化 | Distribution | OK |
| 投稿タイミングの調整 | Distribution | OK |
| 冒頭文の書き換え | Content | NG |
| 見出しの「エモーショナル化」 | Content | NG |
| 構成の「キャッチー」化 | Content | NG |
| editor/essay-reviewer の品質指摘に基づく修正 | Quality | OK（品質向上であり改変ではない） |

## 適用タイミング

- 記事のレビュー・修正時
- seo-optimizer 実行時
- 新しい執筆支援スキル・エージェントの設計時
