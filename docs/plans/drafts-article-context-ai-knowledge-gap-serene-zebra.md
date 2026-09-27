# 記事プラン: AI 知識ギャップ診断

## Context

2026-08-15 にスキル増殖問題を「管理ツールの機能不全」と認識して15日間動かなかった著者が、
8/30 に AI へ知識ギャップ診断を依頼。診断基準の「概念の再発明」検出がシステム思考を指し、
推薦書の最初の概念（ストック・フロー）を読み始めて85分後に同じ問題を「上流フローの構造問題」
へリフレームした。この体験を Zenn 記事にする。

証拠台帳: `drafts/article-context_ai-knowledge-gap-diagnosis_2026-09-01.md`

## Editorial Brief

**Channel**: Zenn (`articles/`)
**Reader**: 検索・feed から来た engineer。数秒で用途を理解し再現または判断できる

### Central Thesis（1文）

AI にセッション履歴を分析させて「独自に再発明している概念」を検出させると、行き詰まった問題を
既存学問の語彙でリフレームでき、停滞が動く。

### Causal Spine

| 段階 | 内容 |
|------|------|
| Observation | 8/15、スキル増殖を「管理ツールの機能不全」と認識。15日間動かなかった |
| Tension | 管理を直しても動かない ＝ 問題定義自体が間違っている可能性。だが盲点は自分で見えない |
| Mechanism | AI に約3,000 turn + 72記事を分析させた。診断基準の核「独自に再発明しているが既存学問に成熟した語彙がある概念」がシステム思考を検出。85分後にストック・フロー概念で問題をリフレーム |
| Reader action | 自分の AI 利用履歴に同じ診断パターン（特に「概念の再発明」検出）を適用して盲点を特定できる |

### Evidence Selection

| Claim | 役割 | 使い方 |
|-------|------|--------|
| C10 | Hook (Before) | 8/15 の verbatim「insightsだが…機能していない」 |
| C1 | Mechanism setup | 診断依頼の内容 |
| C2 | Scale proof | 約3,000 turn, 72記事 |
| C3, C4 | 品質基準 | 2種類以上の証拠, 3件以上の独立実例, 不在だけでは不十分 |
| C18 | **核心** | 「概念の再発明」検出パターン — 読者が持ち帰れる方法論 |
| C5 | 結果 | システム思考が検出された（間接確認の範囲で。⚠未検証を超えない） |
| C7 | Timing proof | 06:28 読書開始→07:53 適用 = 85分 |
| C8 | Payoff (After) | verbatim「上流の…フローの中のパターンに問題が潜んでいる」 |
| C9 | Confirmation | AKC フィードバックループとの接続認識 = 再発明パターンの傍証 |
| C12 | 実行導線 | 推薦書籍名 |

### Out of Scope

- 12週カリキュラムの詳細（C13）、tutor contract（C15）、ケーススタディ設計（C14）
- 修了判定（C16）、学習進捗（C17: week 1 未着手）
- 診断の他2分野（C5 ⚠未検証）
- システム思考そのものの解説（ストック・フローは85分の転換を説明する最小限だけ）

## 記事構成（5節）

### 1. 15日間動かなかった問題（Observation）
- C10 verbatim で開く: 8/15 のスキル増殖の行き詰まり
- 管理を改善しても動かなかった事実
- 結論先出し: 15日後に同じ問題をまったく別の角度から再定義していた

### 2. AI に自分の盲点を診断させる（Tension → Mechanism entry）
- 問題定義が間違っている可能性 → AI に履歴分析を依頼
- C1 verbatim、C2（分析対象の規模）
- C6「エンジニアではない」前提（1行）

### 3. 「概念の再発明」を検出する診断基準（Mechanism core）★記事の核
- C3, C4: 診断の品質基準
- C18: 「独自に再発明しているが、既存学問に成熟した語彙がある概念」の検出
- なぜこのパターンが効くか: 不在の知識でなく、すでに使っている概念に体系があるから、学んだ瞬間に接続先がある
- C5: 結果としてシステム思考が検出された
- C12: 推薦教材

### 4. 85分後に起きたこと（Proof/Payoff）
- C7: タイムスタンプ（06:28→07:53）
- ストック・フローの最小限の説明
- C8 verbatim: リフレームの瞬間
- Before/After 対比表: 管理ツールの機能不全 → 上流フローの構造問題
- C9: AKC との接続認識 = 再発明パターンの自己確認

### 5. 再現するための要点（Reader action）
- 必要な入力: 十分な量の AI 利用履歴
- 診断基準の凝縮（特に「概念の再発明」検出）
- 限界の明示: n=1、リフレームの証拠であり学習効果は未実測
- 診断プロンプトの要点

## タイトル候補

1. **「AIに知識の盲点を診断させたら、15日間の行き詰まりが85分で解けた」**（34字）— Before/After の対比が具体的。推奨
2. **「AIに自分の3,000ターンを読ませたら『再発明していた概念』が見えた」**（31字）— 方法の新規性が伝わる
3. **「AI診断で見つけた知識の盲点——概念の再発明を検出する方法」**（27字）— 方法論フォーカス

## 実行手順

1. **Editorial brief 承認** — この構成で著者 GO を取る
2. **Draft** — `articles/ai-knowledge-gap-diagnosis.md` を作成。writing-ecosystem Phase 3
3. **Freeze → Review panel**:
   - `editor`（channel editor）
   - `prose-clarity-reviewer`
   - `fact-checker`（C1-C18 の tier に基づく検証）
   - `codex-review`（cross-model）
4. **著者通読 → Content GO**
5. **Title** — `headline-craft` → `title-reviewer` → 著者選択
6. **quality-gate** → publish GO → `zenn-format` + `publish-article`

## 検証

- `npm run validate` — frontmatter 検証
- `npm run evidence -- articles/ai-knowledge-gap-diagnosis.md` — deviations 0
- 証拠台帳の C tier と本文の主張が一致すること（⚠未検証の C5 を一次ソースとして扱っていないこと）
- 関連リンク 2 行（GitHub 正本 + 著者 GitHub）が末尾にあること

## Critical Files

- `drafts/article-context_ai-knowledge-gap-diagnosis_2026-09-01.md` — 証拠台帳
- `.claude/skills/writing-ecosystem/SKILL.md` — 執筆ワークフロー
- `.claude/rules/publishing-channels.md` — channel contract
- `articles/review-chain-damping.md`, `articles/instrument-consumption-plan.md` — 構造の参考
