---
name: writing-team
description: Claude Code をオーケストレーター（PM）として、執筆チームを編成・指揮する
user-invocable: true
origin: original
---

# Writing Team Skill（オーケストレーター）

**Purpose:** Claude Code 本体が PM として、ミッション種別に応じてエージェント・スキルを編成し、品質ゲートとユーザー確認を管理する。

> 根拠: [ADR-0002](../../.claude/docs/adr/0002-writing-team-orchestration.md)

---

## Usage

```
/writing-team                    # ミッション判定から開始
/writing-team new               # Mission A: 新規記事
/writing-team revise             # Mission B: 改稿
/writing-team translate          # Mission C: 翻訳 + クロスポスト
/writing-team schedule           # Mission D: バッチスケジューリング
/writing-team ideate             # Mission E: アイデア出し
```

---

## ミッション判定

引数なしの場合、ユーザーに意図を確認して適切なミッションを選択する。

---

## Mission A: 新規記事

```
1. [skill: ideation]         — テーマ検討（任意、ユーザーがテーマ持ち込みなら省略）
2. [skill: zenn-writer]      — 文体・構成ガイド参照
   ⏸ ユーザー確認: テーマ・方向性
3. [agent: zenn-drafter]     — Phase 1 アウトライン
   ⏸ ユーザー確認: 構成案
4. [agent: zenn-drafter]     — Phase 2-3 執筆 + セルフレビュー
   ⏸ ユーザー確認: ドラフト
5. ┌ [agent: editor/essay-reviewer] ─┐  並列実行
   └ [agent: fact-checker]           ┘
   ⏸ ユーザー確認: レビュー結果
6. 修正
7. [skill: quality-gate]     — 統一品質基準チェック
8. [skill: seo-optimizer]    — タイトル・タグ最適化（内容は変えない）
9. [skill: publish-article]  — 公開チェックリスト
   ⏸ ユーザー確認: published_at 設定
10. git push
```

**editor vs essay-reviewer の選択:**
- `type: "tech"` → editor
- `type: "idea"` → essay-reviewer
- 混合 → 両方実行

## Mission B: 改稿

```
1. 変更差分の分析（git diff または手動指定）
2. [skill: series-checker]    — シリーズ整合性（シリーズ記事の場合）
3. 改稿実行
4. ┌ [agent: editor/essay-reviewer] ─┐  並列実行
   └ [agent: fact-checker]           ┘
   ⏸ ユーザー確認
5. [skill: quality-gate]     — 統一品質基準
6. [skill: publish-article]  — 公開チェックリスト
```

## Mission C: 翻訳 + クロスポスト

```
1. [agent: devto-translator]  — 一気通貫（翻訳→タグ→画像→投稿）
   ⏸ ユーザー確認: ドライラン結果
2. schedule.json 更新（refs/schedule-schema.md 準拠）
3. git push
```

## Mission D: バッチスケジューリング

```
1. [skill: schedule-publish]  — スコアリング + 日程割り当て
   ⏸ ユーザー確認: スケジュール案
2. schedule.json 更新
3. published_at 設定
4. git push
```

## Mission E: アイデア出し

```
1. [skill: ideation]          — テーマ検討
   ⏸ ユーザーに提案
```

---

## 品質ゲート

全ミッションで `/quality-gate` を通す。詳細は `quality-gate` スキルを参照。

---

## 進行管理

- TaskCreate/TaskUpdate でミッションの進捗を追跡
- 各ステップの完了をタスクとして記録
- ユーザー確認ポイント（⏸）では必ず AskUserQuestion で確認を取る

---

## Content Integrity 原則

> [ADR-0001](../../.claude/docs/adr/0001-content-integrity-principle.md)
> 内容は著者の思考が決める。配信戦略は内容を変えずに最適化する。

オーケストレーターはこの原則を全ミッションで守る:
- seo-optimizer はタイトル・タグ・emoji のみ（冒頭文は変えない）
- レビュー指摘は品質向上のため（エンゲージメント最適化のためではない）
- 構成変更の提案は著者の論旨をより正確に伝えるためのもの
