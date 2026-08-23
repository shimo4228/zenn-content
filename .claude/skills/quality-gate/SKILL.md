---
name: quality-gate
description: 記事公開前の受け入れゲート。新規・改稿・翻訳のどのパスでも、チャンネルに対応する panel と機械的公開条件が揃ったかを照合して PASS/FAIL を返す。記事品質を再判定せず、reviewer verdict の集約だけを行う。Use when — 公開直前（writing-team Mission A step 9 / B step 6 / C step 4）、他人が書いた原稿を公開してよいか確かめたいとき、/quality-gate <file>。NOT for — 記事品質そのものの判定（→ editor / essay-reviewer）、初見読者の明瞭性（→ zenn-clarity-reviewer）、panel の起動条件と実行順（→ writing-team）、公開作業の手順（→ publish-article）、著者判断の再現（→ zenn-editorial-judgment。判断層を機械 gate 化しない — ADR-0006 Decision 3）
user-invocable: true
origin: shimo4228
---

# Quality Gate Skill

**Purpose:** 記事公開前に、チャンネル別 panel と機械的公開条件が完了したことを照合する。

> 根拠: [ADR-0002](../../../docs/adr/0002-writing-team-orchestration.md) — 品質基準の統一

---

## Usage

```
/quality-gate articles/ARTICLE_NAME.md
```

---

## Quality Checklist

### 必須（全記事）

- [ ] **チャンネル reviewer の CRITICAL が 0**: チャンネル表の「レビュー agent」列に対応する
      reviewer（editor / essay-reviewer）の CRITICAL が解決済み
- [ ] **zenn-clarity-reviewer の verdict が PASS**: 初見読者の明瞭性レビュー済みで FAIL が解消されている（FAIL のままなら公開不可。editor CRITICAL 0 と同格のブロッキング条件）
- [ ] **AI slop なし**: チャンネル reviewer が `writing-ecosystem` の禁止リストに照らして確認済み
- [ ] **未説明概念なし**: チャンネル reviewer / zenn-clarity-reviewer が、専門用語・自作概念の
      初出時説明を確認済み
- [ ] **fact-checker 完了**: report が存在し、❌ INACCURATE と未解決の ⚠️ PARTIALLY がない
- [ ] **codex-review 完了または fallback 記録済み**: prompt-driven review の所見を確認済み。
      実行不能時は `codex-review` の Failure Modes に従った fallback を記録している
- [ ] **セキュリティ検査完了**: [publish-article](../publish-article/SKILL.md) Step 2 を
      チャンネル非依存の検査定義として使い、対象原稿へ grep を実行して秘密・個人パスの検出 0。
      画像・引用ログがある場合は同 Step の手動項目も確認する（公開 workflow 自体は起動しない）

### Zenn/Dev.to 記事追加（type で分岐しない）

- [ ] **editor の canonical coverage 完了**: `zenn-practical-writing` の完成稿から観測できる
      受け入れ項目を全て検査済みで、pending / unverified と must-fix violation がない
- [ ] **Zenn frontmatter 完備**: Zenn 原稿では [publish-article](../publish-article/SKILL.md) Step 3
      （`npx zenn list:articles`）がパス（仕様の正本は `zenn-format`）
      Dev.to 翻訳稿の frontmatter は `devto-translator` Phase 1-2 が所有し、本 gate で
      Zenn validator を代用しない

### note/Substack エッセイ追加

- [ ] **essay-reviewer の canonical coverage 完了**: `writing-ecosystem` の完成稿から観測できる
      craft・開示・出典・機械可読層を全て検査済みで、pending と must-fix violation がない
- [ ] **frontmatter なし**: 新規 note/Substack 原稿には frontmatter がない。既存の旧形式 mirror は
      project 規約の明記された例外としてそのまま扱う

### 翻訳記事追加

- [ ] **`devto-translator` Phase 4 のセルフチェックが完了している**（コードブロック完全性 /
      リンク完全性 / 用語一貫性 / AI slop / 技術的正確性）。**検査項目の正本は
      [devto-translator](../../agents/devto-translator.md) Phase 4** — ここには再掲しない
      （2026-08-23: 同じ 3 項目を別の言い回しで二重に持っていた）
- [ ] **翻訳稿の panel 完了**: 翻訳先チャンネル reviewer + fact-checker +
      zenn-clarity-reviewer + codex-review を、翻訳後の公開稿に対して実行済み

---

## Output

```markdown
## Quality Gate Result

**記事**: [パス]
**判定**: PASS / FAIL

### チェック結果
- [x] CRITICAL 指摘解決済み
- [x] clarity PASS
- [x] fact-check 指摘解決済み
- [x] canonical coverage 実施済み / must-fix なし
...

### FAIL の場合の修正指示
1. [具体的な修正内容]
```

---

## Notes

- FAIL の場合は修正してから再実行
- quality-gate は対象チャンネルの公開作業前に実行する
- 本 skill は prose を再レビューしない。canonical な執筆規約の検査はチャンネル reviewer、
  明瞭性は zenn-clarity-reviewer、事実は fact-checker が所有する
- panel が未実行の場合は、`writing-team` の該当 Mission に戻す
