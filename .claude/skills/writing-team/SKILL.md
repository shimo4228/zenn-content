---
name: writing-team
description: Claude Code をオーケストレーター（PM）として、執筆チームを編成・指揮する
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
2. [skill: theme-eval]       — テーマ強度判定（執筆前）
   Write-A/B見込み → 3 へ / Deepen → 深化プロンプトを著者と回して再判定（2 回まで。
   上がらなければ見込みランク付きのまま執筆へ — 却下しない）
   ⏸ Deepen の問いに答えるのは著者（人間の主戦場はテーマ層）
3. [skill: zenn-editorial-judgment] Phase 0 — 記事タイプ + 実装の渡し先（人間向け how-to / agent handoff）を判定
4. [skill: zenn-practical-writing] Phase 1 — 構成案の提示
   ⏸ ユーザー確認: テーマ・方向性・構成案
5. [skill: zenn-practical-writing] Phase 2-3 — 執筆 + 自己プリフライト
   （オーケストレーター本体が直接実行。サブエージェントに委譲しない）
6. 改稿ループ = 草稿ゲート（下記「改稿ループ」節）— mechanical_checks + [agent: article-judge]
   Publishable / 上限 2 ラウンド / Rewrite（著者差し戻し）で抜ける
   ※ここの Publishable は panel の入場券にすぎない。公開を担保する binding な判定は 9（2026-08-12 ドライラン改定）
6.5 著者素材の最終引き出し（2026-08-13 新設）— panel の前に 1 回だけ、本文の主要主張リストを添えて著者に問う:
   「各主張について、あなたの実体験でまだ書かれていない反例・具体・深化はないか」
   回答があれば本体が反映して 6 の草稿ゲートを再通過する。根拠: 欲望枯渇エッセイの最深部 2 つ
   （パイプライン化・車輪の再発明）が publish 直前の雑談から出た — ハーネスは著者の中の素材を
   引き出す設計を持っていなかった
7. ┌ [agent: editor]                 ─┐
   ├ [agent: fact-checker]            ┤  並列実行
   ├ [agent: zenn-clarity-reviewer]   ┤
   └ codex-review（prompt-driven）    ┘  ← cross-model 検証を兼ねる（ループ内では回さない）
   article-judge と codex の verdict が割れたら ⏸ 人間 routing
8. 修正（panel 指摘の反映。構成が変わったら 6 へ 1 回だけ戻る。
   構成系の指摘は「任意の磨き」に降格しない — 推奨を付けず中立で著者ゲートへ必ず昇格する）
9. 最終判定【binding】— 凍結した公開候補に対して mechanical_checks + [agent: article-judge]（fresh・質問は新規生成）を再実行
   quality-gate が参照できるのはこの verdict だけ。通読 GO 中の著者修正は**修正ごとに回さずバッチする** — 通読が終わった時点の本文に対して 1 回だけ再実行する（著者が不要と判断すれば省略可。著者通読が常に最上位のゲート — 2026-08-12 著者指示）
11. [skill: quality-gate]    — 統一品質基準チェック（最終判定の article-judge = Publishable を含む）
12. [skill: title-eval]      — タイトル判定ループ（本文凍結後・投稿直前に単独で回す。headline-craft 生成 → fresh 判定 → Refine 1 回、最終選択は著者。2026-08-13 新設）
   Zenn/Dev.to は続けて [skill: seo-optimizer] — topics・emoji 最適化（内容は変えない）
   ⏸ ユーザー確認: ドラフト全文 + レビュー結果 + タイトル/SEO 提案（一括確認 = publish 前の通読 GO）
13. [skill: publish-article] — 公開チェックリスト（published_at 含む）
14. git push
```

**レビュアー**: step 7 の品質レビュー agent は、出力先チャンネルに対応する行をチャンネル表（`.claude/rules/zenn-writing.md`）で引く。厚さはどのチャンネルでも同じ。

**article-judge（改稿ループの判定器）**: fresh context の別 agent process で起動する（執筆セッションの文脈を渡さない — 履歴共有は判定を甘くする）。基準アンカーは `.claude/refs/kaguura-craft-checklist.md`。

**zenn-clarity-reviewer**: 初見読者（フィード・検索から来たエンジニア）の明瞭性レビュー。editor（構造・コード正確性・AI slop・用語一貫性）と観点が直交するため並列で起動する。verdict が FAIL のままの記事は公開できない（quality-gate のブロッキング条件）。根拠: [ADR-0004](../../../docs/adr/0004-zenn-clarity-reviewer-addition.md)

**codex-review**: 公開記事のため、[根拠: `docs/adr/0003-zenn-practical-channel-axis.md` 決定5] に基づき、editor/fact-checker と並列で prompt-driven モードで起動する。

## Mission B: 改稿

```
1. 変更差分の分析（git diff または手動指定）
2. [skill: zenn-editorial-judgment]「シリーズ記事の整合」— シリーズ記事の場合
3. [skill: zenn-editorial-judgment] — 構造変更なら記事タイプ + 実装の渡し先を再判定
   （テーマ自体が変わる改稿なら [skill: theme-eval] も再実行）
4. 改稿実行（オーケストレーター本体が直接編集）
5. 改稿ループ（下記「改稿ループ」節）— mechanical_checks + [agent: article-judge]
   ※ 公開済み記事の改稿では --baseline に公開版を渡して voice 回帰を必ず見る
6. ┌ [agent: editor]                 ─┐
   ├ [agent: fact-checker]            ┤  並列実行
   ├ [agent: zenn-clarity-reviewer]   ┤
   └ codex-review（prompt-driven）    ┘
6.5 最終判定【binding】— 凍結した公開候補に mechanical_checks + [agent: article-judge]
   （fresh・質問は新規生成）を再実行。Mission A step 9 と同形。
   quality-gate が参照できるのはこの verdict だけで、step 5 の草稿ゲートでは代用できない
   （2026-08-23 追加 — 従来 Mission B にこの step が無く、改稿記事は quality-gate の
   第 1 必須項目を構造的に満たせなかった）
7. [skill: quality-gate]     — 統一品質基準
   ⏸ ユーザー確認: 改稿結果 + レビュー結果（一括確認）
8. [skill: publish-article]  — 公開チェックリスト
```

---

## 改稿ループ（2026-08-12 追加。根拠: grill-me 設計 + 外部調査）

```
draft
  → scripts: uv run python mechanical_checks.py <draft> [--baseline <初稿>] [--lang en]   … 決定論の証拠 JSON（EN 記事は --lang en 必須）
  → [agent: article-judge]（fresh context・機械 JSON を渡す）
      ├ Publishable → ループ終了、次の step へ
      ├ Fix         → 本体が span 単位指摘だけを修正（全文書き直し禁止・voice 保全）
      │               → 同一チェックセットで再判定 1 回だけ（質問の再生成禁止）
      └ Rewrite     → ループ中断、⏸ 著者へ差し戻し（構造 or テーマの欠陥）
  上限 2 ラウンド。2 ラウンドで Publishable に達しなければ残指摘を添えて ⏸ 著者判断へ
```

**二つの実行位置（2026-08-12 ドライラン改定）**: 改稿ループは panel 前の**草稿ゲート**（壊れた原稿に高コストな panel を食わせないための前置フィルタ）。panel と修正反映が済んだ凍結候補には、Mission A step 9 の**最終判定**として mechanical_checks + article-judge（fresh・質問新規生成）をもう 1 回実行する。quality-gate が参照するのは最終判定の verdict だけ — 草稿ゲート時点の Publishable は panel 修正で陳腐化するため代用不可。凍結後に 1 文字でも修正が入ったら最終判定を再実行する。

設計制約（外部実証に基づく。as-of 2026-08-12）:
- **自己批評は回さない** — 判定は必ず fresh context の article-judge（同一セッションの自己レビューは検出率が落ちる）
- **上限 2 ラウンド** — 反復は 2〜3 回で頭打ち、以降は voice の正規化ドリフト（劣化）が始まる
- **voice 回帰** — mechanical_checks の voice_delta warn は over-editing シグナル。warn が出たら磨きをやめる側に倒す
- **迷ったら Fix** — judge が Publishable / Fix で迷ったら Fix（theme-eval の「迷ったら B」と対称）
- **人間ゲートの正本は Mission 定義の ⏸ 印**（数をここに書かない — 実際の関与点は Mission A で 5 つある）。改稿ループ**内**で止まるのは judge 間不一致（article-judge vs codex）のときだけ
- **KPI = 通読指摘数**（2026-08-13 新設）— 最終判定 Publishable の**後**に著者通読が発見した指摘数を、記事ごとに memory `eval-harness-pipeline` へ記録する。この数が judge の真のエラー率であり、基準再起草（AUTOCALIBRATE）の主入力。基準線: ai-desire-exhaustion で 6 件（指示語・偽二分法・パッチワーク・機序混同・圧縮過多・トーン誤読）→ 次作でこの数が減っているかが K2/K3/K4 改定の効果測定

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
- title-eval / seo-optimizer は Distribution レイヤーのみ（冒頭文・本文は変えない）
- レビュー指摘は品質向上のため（エンゲージメント最適化のためではない）
- 構成変更の提案は著者の論旨をより正確に伝えるためのもの
