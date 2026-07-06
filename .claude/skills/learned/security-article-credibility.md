---
name: security-article-credibility
description: "セキュリティ記事の主張を実コードと照合し、限界を正直に開示することで信頼性を確保するワークフロー"
user-invocable: false
origin: auto-extracted
---

# Security Article Credibility（セキュリティ記事の信頼性確保）

**Extracted:** 2026-03-06
**Context:** Moltbook エージェント記事でセキュリティ8項目を主張。security-reviewer エージェントに記事 AND ソースコードを同時レビューさせたところ、3件の OVERSTATED を発見。正直な開示で記事の信頼性が向上した

## Problem

セキュリティに関する技術記事では、以下の問題が起きやすい:

1. **主張と実装の乖離**: 記事では「セキュア」と書いているが、コードは部分的にしか対策していない
2. **限界の隠蔽**: 既知の限界を書かないことで、読者に「完璧」という印象を与えてしまう
3. **パターンカバレッジの誇張**: キーワードベースのフィルタを「すべてのクレデンシャルを除去」と書く等

セキュリティ記事で嘘や誇張が発覚すると、記事全体の信頼性が崩壊する。

## Solution

### ワークフロー

```
1. 記事を書く（セキュリティの主張を含む）
2. security-reviewer エージェントに記事 AND ソースコードを同時にレビューさせる
3. 各主張を VERIFIED / OVERSTATED / GAP に分類
4. OVERSTATED → 記事内に :::message alert で「既知の限界」を追加
5. GAP → 記事に新たな注意書きを追加するか、コードを修正する
```

### security-reviewer への指示テンプレート

```
Review the article at [ARTICLE_PATH] AND the source code at [SOURCE_PATH].

For each security claim in the article:
- VERIFIED: Code matches article claim
- OVERSTATED: Article claims more security than code provides
- GAP: Real vulnerability exists that article doesn't mention

Be thorough and adversarial. This is for a public technical article.
```

### 「既知の限界」ブロックのテンプレート

```markdown
:::message alert
**既知の限界**: [具体的にどこが不完全か]。[なぜ現在のユースケースでは問題にならないか]。[将来的にどう対策するか]。
:::
```

### 三要素を必ず含める

1. **何が不完全か**（技術的に正確な説明）
2. **なぜ今は問題ないか**（ユースケースの限定条件）
3. **どう対策するか**（将来の改修方針）

### 実例（本セッションで発見した OVERSTATED）

| 主張 | 実態 | 開示内容 |
|------|------|---------|
| `0600` パーミッションを強制 | write→chmod にTOCTOU窓あり | シングルユーザー運用では問題なし、厳密には `os.open` が正しい |
| 禁止パターンでクレデンシャル除去 | キーワードリストが狭い（JWT等未対応） | 7B モデルでの生成確率は低いが、パターン拡充予定 |
| untrusted_content タグで防御 | メモリ経由の履歴はタグなしでプロンプトに入る | 二次インジェクションの攻撃パス存在、改修必要 |

## When to Use

- セキュリティ対策を主張する技術記事を書くとき
- 「N項目の対策」のようなリスト形式でセキュリティを語るとき
- OWASP 等の標準との照合表を掲載するとき
- publish-article フローの Step 2（セキュリティチェック）と併用
