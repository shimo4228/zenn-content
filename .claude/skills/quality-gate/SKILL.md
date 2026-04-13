---
name: quality-gate
description: 全パス（新規・改稿・翻訳）に統一品質基準を適用する
user-invocable: true
origin: original
---

# Quality Gate Skill

**Purpose:** 記事公開前の統一品質基準。新規・改稿・翻訳のどのパスでも同じ基準を通す。

> 根拠: [ADR-0002](../../.claude/docs/adr/0002-writing-team-orchestration.md) — 品質基準の統一

---

## Usage

```
/quality-gate articles/ARTICLE_NAME.md
```

---

## Quality Checklist

### 必須（全記事）

- [ ] **editor/essay-reviewer の CRITICAL が 0**: レビュー済みで CRITICAL 指摘がすべて解決済み
- [ ] **AI slop なし**: `refs/writing-standards.md` の禁止リストに該当する表現がない
- [ ] **未説明概念なし**: 専門用語・自作概念が初出時に説明されている
- [ ] **セキュリティ**: API キー、個人パス（`/Users/`）、機密情報が含まれていない
- [ ] **frontmatter 完備**: title, emoji, type, topics, published が正しく設定されている

### idea 記事追加

- [ ] **fact-checker 完了**: 事実主張が検証済み
- [ ] **過積載なし**: 独立論点が 4 つ以下
- [ ] **トーン一貫**: だ/である調 × 発見調が全体で維持されている

### tech 記事追加

- [ ] **コードスニペット検証**: すべてのコードが実行可能
- [ ] **ファイルパス正確**: 参照されているファイルパス・行番号が現在のコードと一致

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
- レビューエージェント（editor/essay-reviewer）が未実行の場合は、先にレビューを促す
