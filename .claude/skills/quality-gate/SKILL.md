---
name: quality-gate
description: 全パス（新規・改稿・翻訳）に統一品質基準を適用する
user-invocable: true
origin: shimo4228
---

# Quality Gate Skill

**Purpose:** 記事公開前の統一品質基準。新規・改稿・翻訳のどのパスでも同じ基準を通す。

> 根拠: [ADR-0002](../../../docs/adr/0002-writing-team-orchestration.md) — 品質基準の統一

---

## Usage

```
/quality-gate articles/ARTICLE_NAME.md
```

---

## Quality Checklist

### 必須（全記事）

- [ ] **最終判定の article-judge verdict が Publishable**: panel 反映後の**凍結候補**に対する fresh 判定であること（writing-team Mission A step 9）。草稿ゲート時点の Publishable では代用できない — panel・著者修正で判定対象が陳腐化するため。凍結後に修正が入ったら最終判定からやり直し。Fix 残 / Rewrite のままなら公開不可（2026-08-12 追加・同日ドライランで binding 位置を panel 後へ改定、ADR-0008）
- [ ] **editor の CRITICAL が 0**: レビュー済みで CRITICAL 指摘がすべて解決済み（Zenn/Dev.to は editor に一本化。アイデアエッセイ = note/Substack は essay-reviewer）
- [ ] **zenn-clarity-reviewer の verdict が PASS**: 初見読者の明瞭性レビュー済みで FAIL が解消されている（FAIL のままなら公開不可。editor CRITICAL 0 と同格のブロッキング条件）
- [ ] **AI slop なし**: `writing-ecosystem` skill の禁止リストに該当する表現がない
- [ ] **未説明概念なし**: 専門用語・自作概念が初出時に説明されている
- [ ] **セキュリティ**: API キー、個人パス（`/Users/`）、機密情報が含まれていない
- [ ] **frontmatter 完備**: title, emoji, type, topics, published が正しく設定されている

### Zenn/Dev.to 記事追加（type で分岐しない）

- [ ] **fact-checker 完了**: 事実主張を含む場合、検証済み
- [ ] **実用軸チェックリスト**: [zenn-practical-writing](../zenn-practical-writing/SKILL.md) の受け入れチェックリスト（用途の明示・前提列挙・図表 ≥1・scannable・コード動作・独立論点数・ですます統一）を満たしている
- [ ] **エージェント向け引き継ぎ（採用時）**: 前半だけで人間向けナラティブが完結し、後半は読み取り専用調査 → 計画 → 人間承認で停止する。変更対象・非対象・上書き禁止・復旧方法・実測の成功条件が揃っている

### 翻訳記事追加

- [ ] **コードブロック完全性**: 原文と翻訳のコードブロック数が一致
- [ ] **リンク完全性**: すべての URL・画像パスが保持されている
- [ ] **用語一貫性**: 翻訳グロッサリーの用語が正しく使われている

---

## Output

```markdown
## Quality Gate Result

**記事**: [パス]
**判定**: PASS / FAIL

### チェック結果
- [x] CRITICAL 指摘解決済み
- [x] AI slop なし
- [ ] 未説明概念あり: [概念名] (line XX)
...

### FAIL の場合の修正指示
1. [具体的な修正内容]
```

---

## Notes

- FAIL の場合は修正してから再実行
- quality-gate は `publish-article` の前に実行する
- レビューエージェント（editor / zenn-clarity-reviewer）が未実行の場合は、先にレビューを促す
