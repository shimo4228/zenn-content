---
name: writing-team
description: Claude Code をオーケストレーター（PM）として、執筆チームを編成・指揮する
user-invocable: true
origin: original
---

# Writing Team Skill（オーケストレーター）

**Purpose:** Claude Code 本体が PM として、ミッション種別に応じてエージェント・スキルを編成し、品質ゲートとユーザー確認を管理する。

> 根拠: [ADR-0002](../../../docs/adr/0002-writing-team-orchestration.md)

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
2. [skill: zenn-practical-writing] Phase 1 — 構成案の提示
   ⏸ ユーザー確認: テーマ・方向性・構成案
3. [skill: zenn-practical-writing] Phase 2-3 — 執筆 + 自己プリフライト
   （オーケストレーター本体が直接実行。サブエージェントに委譲しない）
4. ┌ [agent: editor]                ─┐
   ├ [agent: fact-checker]           ┤  並列実行
   └ codex-review（prompt-driven）   ┘
5. 修正
6. [skill: quality-gate]     — 統一品質基準チェック
7. [skill: seo-optimizer]    — タイトル・タグ最適化（内容は変えない）
   ⏸ ユーザー確認: ドラフト全文 + レビュー結果 + SEO 提案（一括確認）
8. [skill: publish-article]  — 公開チェックリスト（published_at 含む）
9. git push
```

**レビュアー**: Zenn/Dev.to は全記事 `editor` を使用（実用軸に一本化されたため type 分岐なし）。`essay-reviewer` は Substack essay corpus 専用で、Zenn/Dev.to のミッションでは使わない。

**codex-review**: 公開記事のため、[根拠: `docs/adr/0003-zenn-practical-channel-axis.md` 決定5] に基づき、editor/fact-checker と並列で prompt-driven モードで起動する。

## Mission B: 改稿

```
1. 変更差分の分析（git diff または手動指定）
2. [skill: series-checker]    — シリーズ整合性（シリーズ記事の場合）
3. 改稿実行（オーケストレーター本体が直接編集）
4. ┌ [agent: editor]                ─┐
   ├ [agent: fact-checker]           ┤  並列実行
   └ codex-review（prompt-driven）   ┘
5. [skill: quality-gate]     — 統一品質基準
   ⏸ ユーザー確認: 改稿結果 + レビュー結果（一括確認）
6. [skill: publish-article]  — 公開チェックリスト
```

## Mission C: 翻訳 + クロスポスト

```
1. [agent: devto-translator]  — 一気通貫（翻訳→タグ→画像→投稿）
2. [skill: quality-gate]      — 「翻訳記事追加」チェック（コードブロック・リンク・用語一貫性）
   ⏸ ユーザー確認: ドライラン結果
3. schedule.json 更新（refs/schedule-schema.md 準拠）
4. git push
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

記事本文を生成・変更するミッション（A: 新規 / B: 改稿 / C: 翻訳）は `/quality-gate` を通す。D（スケジューリング）と E（アイデア出し）は本文を触らないため対象外。詳細は `quality-gate` スキルを参照。

---

## 進行管理

- TaskCreate/TaskUpdate でミッションの進捗を追跡
- 各ステップの完了をタスクとして記録
- ユーザー確認ポイント（⏸）では必ず AskUserQuestion で確認を取る

---

## Content Integrity 原則

> [ADR-0001](../../../docs/adr/0001-content-integrity-principle.md)
> 内容は著者の思考が決める。配信戦略は内容を変えずに最適化する。

オーケストレーターはこの原則を全ミッションで守る:
- seo-optimizer はタイトル・タグ・emoji のみ（冒頭文は変えない）
- レビュー指摘は品質向上のため（エンゲージメント最適化のためではない）
- 構成変更の提案は著者の論旨をより正確に伝えるためのもの
