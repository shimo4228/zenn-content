---
name: quality-gate
description: 記事公開前の受け入れゲート。新規・改稿・翻訳のどのパスでも同じブロック条件を通し、PASS/FAIL を返す。判定は下さず、各レビュアー・判定器が出した verdict が揃って緑かを照合する層。Use when — 公開直前（writing-team Mission A step 10 / B step 7 / C step 2）、他人が書いた原稿を公開してよいか確かめたいとき、/quality-gate <file>。NOT for — 記事品質そのものの判定（→ article-judge）、初見読者の明瞭性（→ zenn-clarity-reviewer）、ループ制御と panel の起動条件（→ writing-team「改稿ループ」）、公開作業の手順（→ publish-article）、著者判断の再現（→ zenn-editorial-judgment。判断層を機械 gate 化しない — ADR-0006 Decision 3）
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

- [ ] **最終判定の article-judge verdict が Publishable**: panel 反映後の**凍結候補**に対する fresh 判定であること（writing-team Mission A step 9 / Mission B step 6.5）。草稿ゲート時点の Publishable では代用できない — panel・著者修正で判定対象が陳腐化するため。凍結後に修正が入ったら最終判定からやり直し。Fix 残 / Rewrite のままなら公開不可（2026-08-12 追加・同日ドライランで binding 位置を panel 後へ改定、ADR-0008）
- [ ] **editor の CRITICAL が 0**: レビュー済みで CRITICAL 指摘がすべて解決済み（担当 agent はチャンネル表の「レビュー agent」列）
- [ ] **zenn-clarity-reviewer の verdict が PASS**: 初見読者の明瞭性レビュー済みで FAIL が解消されている（FAIL のままなら公開不可。editor CRITICAL 0 と同格のブロッキング条件）
- [ ] **AI slop なし**: `writing-ecosystem` skill の禁止リストに該当する表現がない
- [ ] **未説明概念なし**: 専門用語・自作概念が初出時に説明されている
- [ ] **セキュリティ**: [publish-article](../publish-article/SKILL.md) Step 2 の grep パターンを実行し、検出 0（**実行形の正本はあちら**。ここに検査コマンドを再掲しない）
- [ ] **frontmatter 完備**: [publish-article](../publish-article/SKILL.md) Step 3（`npx zenn list:articles`）がパス（仕様の正本は `zenn-format`）

### Zenn/Dev.to 記事追加（type で分岐しない）

- [ ] **fact-checker 完了**: report が存在し、指摘が解決済み（起動条件の正本は `writing-team`（panel で無条件並列）— ここで条件を再定義しない）
- [ ] **実用軸チェックリスト**: [zenn-practical-writing](../zenn-practical-writing/SKILL.md) の受け入れチェックリスト（用途の明示・前提列挙・図表 ≥1・scannable・コード動作・独立論点数・文体）を満たしている
- [ ] **エージェント向け引き継ぎ（採用時）**: 前半だけで人間向けナラティブが完結し、後半は読み取り専用調査 → 計画 → 人間承認で停止する。変更対象・非対象・上書き禁止・復旧方法・実測の成功条件が揃っている

### 翻訳記事追加

- [ ] **`devto-translator` Phase 4 のセルフチェックが完了している**（コードブロック完全性 /
      リンク完全性 / 用語一貫性 / AI slop / 技術的正確性）。**検査項目の正本は
      [devto-translator](../../agents/devto-translator.md) Phase 4** — ここには再掲しない
      （2026-08-23: 同じ 3 項目を別の言い回しで二重に持っていた）

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
