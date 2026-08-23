---
name: writing-team
description: 記事・エッセイの執筆ミッション全体を指揮するオーケストレータ。Mission A（新規）/ B（改稿）/ C（翻訳 + クロスポスト）/ D（アイデア出し）の実行順序、レビュー panel の起動条件と並列構成の**正本**。Use when — 記事を新しく書く / 改稿する / 英訳して出す、「執筆チームを立てて」「/writing-team」、どの順でレビューを回すか迷ったとき。NOT for — 書き方・文体（→ zenn-practical-writing）、記事のレビュー（→ editor / essay-reviewer）、受け入れゲート（→ quality-gate）、公開作業（→ publish-article）、テーマのレビュー（→ theme-reviewer agent）
user-invocable: true
origin: shimo4228
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
/writing-team ideate             # Mission D: アイデア出し
```

---

## ミッション判定

引数なしの場合、ユーザーに意図を確認して適切なミッションを選択する。

---

## Mission A: 新規記事

```
1. [skill: ideation]         — テーマ検討（任意、ユーザーがテーマ持ち込みなら省略）
2. [agent: theme-reviewer]   — テーマ（問い）のレビュー（執筆前・fresh context）
   findings + 深化の問いを返す。**合否・ランクは出ない** — 深めるか、上限を承知で書くか、
   取り止めるかを決めるのは著者
   ⏸ 深化の問いに答えるのは著者（人間の主戦場はテーマ層）
3. [skill: zenn-editorial-judgment] Phase 0 — 記事タイプ + 実装の渡し先（人間向け how-to / agent handoff）を判定
4. [skill: zenn-practical-writing] Phase 1 — 構成案の提示
   ⏸ ユーザー確認: テーマ・方向性・構成案
5. [skill: zenn-practical-writing] Phase 2-3 — 執筆 + 自己プリフライト
   （オーケストレーター本体が直接実行。サブエージェントに委譲しない）
6. 著者素材の最終引き出し（2026-08-13 新設）— panel の前に 1 回だけ、本文の主要主張リストを添えて著者に問う:
   「各主張について、あなたの実体験でまだ書かれていない反例・具体・深化はないか」
   回答があれば本体が反映してから panel を起動する。根拠: 欲望枯渇エッセイの最深部 2 つ
   （パイプライン化・車輪の再発明）が publish 直前の雑談から出た — ハーネスは著者の中の素材を
   引き出す設計を持っていなかった
7. ┌ [agent: editor]                 ─┐
   ├ [agent: fact-checker]            ┤  並列実行
   ├ [agent: zenn-clarity-reviewer]   ┤
   └ codex-review（prompt-driven）    ┘  ← cross-model 検証を兼ねる
   レビュアー間で判断が割れたら ⏸ 人間 routing
8. 修正（panel 指摘の反映。構成が変わったら 7 の panel へ 1 回だけ戻る。
   構成系の指摘は「任意の磨き」に降格しない — 推奨を付けず中立で著者ゲートへ必ず昇格する）
9. [skill: quality-gate]     — 受け入れゲート
10. [skill: title-eval]      — タイトル判定ループ（本文凍結後・投稿直前に単独で回す。headline-craft 生成 → fresh 判定 → Refine 1 回、最終選択は著者。2026-08-13 新設）
   Zenn/Dev.to は続けて [skill: zenn-format]「Topics / Emoji の提案フロー」（内容は変えない）
   ⏸ ユーザー確認: ドラフト全文 + レビュー結果 + タイトル/SEO 提案（一括確認 = publish 前の通読 GO）
11. [skill: publish-article] — 公開チェックリスト（published_at 含む）
12. git push
```

**レビュアー**: step 7 の品質レビュー agent は、出力先チャンネルに対応する行をチャンネル表（`.claude/rules/zenn-writing.md`）で引く。厚さはどのチャンネルでも同じ。

**theme-reviewer（執筆前）**: fresh context の別 agent process で起動する（執筆セッションの文脈を渡さない — 自分のテーマを自分で審査すると self-preference が効く）。合否は出さない。深化の問いに答えるのは著者。

**KPI = 通読指摘数**: 著者通読が panel 通過後に発見した指摘数を、記事ごとに memory `eval-harness-pipeline` へ記録する。この数が panel の真のエラー率であり、レビュアー基準を書き換えるときの主入力（2026-08-13 新設。基準線: ai-desire-exhaustion で 6 件）。

**zenn-clarity-reviewer**: 初見読者（フィード・検索から来たエンジニア）の明瞭性レビュー。editor（構造・コード正確性・AI slop・用語一貫性）と観点が直交するため並列で起動する。verdict が FAIL のままの記事は公開できない（quality-gate のブロッキング条件）。根拠: [ADR-0004](../../../docs/adr/0004-zenn-clarity-reviewer-addition.md)

**codex-review**: 公開記事のため、[根拠: `docs/adr/0003-zenn-practical-channel-axis.md` 決定5] に基づき、editor/fact-checker と並列で prompt-driven モードで起動する。

## Mission B: 改稿

```
1. 変更差分の分析（git diff または手動指定）
2. [skill: zenn-editorial-judgment]「シリーズ記事の整合」— シリーズ記事の場合
3. [skill: zenn-editorial-judgment] — 構造変更なら記事タイプ + 実装の渡し先を再判定
   （テーマ自体が変わる改稿なら [agent: theme-reviewer] も再実行）
4. 改稿実行（オーケストレーター本体が直接編集）
5. ┌ [agent: editor]                 ─┐
   ├ [agent: fact-checker]            ┤  並列実行
   ├ [agent: zenn-clarity-reviewer]   ┤
   └ codex-review（prompt-driven）    ┘
6. [skill: quality-gate]     — 統一品質基準
   ⏸ ユーザー確認: 改稿結果 + レビュー結果（一括確認）
7. [skill: publish-article]  — 公開チェックリスト
```

---

## Mission C: 翻訳 + クロスポスト

```
1. [agent: devto-translator]  — 一気通貫（翻訳→タグ→画像→投稿）
2. [skill: quality-gate]      — 「翻訳記事追加」チェック（コードブロック・リンク・用語一貫性）
   ⏸ ユーザー確認: ドライラン結果
3. schedule.json 更新（`.claude/refs/schedule-schema.md` 準拠）
4. git push
```

## Mission D: アイデア出し

> 旧 Mission D「バッチスケジューリング」は 2026-08-23 に廃止（skill `schedule-publish` を
> Retire）。4 軸 12 点スコアは台帳に一度も書かれず公開処理も読んでいなかった（消費者不在。
> ADR-0008 が llm-as-judge の集計禁止に反する先行事例として記録済み）。複数の未公開稿の
> 公開順は、`.claude/rules/zenn-writing.md`「投稿ペース方針」を見て会話で決める。

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
- title-eval / zenn-format の提案フローは Distribution レイヤーのみ（冒頭文・本文は変えない）
- レビュー指摘は品質向上のため（エンゲージメント最適化のためではない）
- 構成変更の提案は著者の論旨をより正確に伝えるためのもの
