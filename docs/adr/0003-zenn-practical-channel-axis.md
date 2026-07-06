# ADR-0003: Zenn/Dev.to の実用軸チャンネルへの一本化

## Status

Accepted (2026-07-05)

本 ADR は ADR-0001「存続（変更なし）」表の zenn-writer 行、および ADR-0002 §2 の `writing-standards.md` 参照を一部 supersede する（詳細は Consequences）。

## Context

執筆エコシステムは当初、記事・エッセイ・論文の文体境界が曖昧なまま `writing-team` で運用されてきた。その後、channel ごとに文体と置き場所が確立した:

- **エッセイ** — global `writing-ecosystem` skill（+ Substack mirror corpus）。だ/である × 発見調、結論の問い化（初期経典の語り口）。
- **論文** — `paper-ecosystem` skill。
- **Zenn/Dev.to** — 独自の声が未定義のまま、essay 声（writing-ecosystem の Voice）を借用し、さらに `type`（tech/idea）でレビュアーや文体を分岐させていた。

問題は 3 つ:

1. **声のミスマッチ** — Zenn の記事に essay 声（発見調・問い化・弱化）を適用していた。「読んですぐ手を動かす」実用記事には不適。
2. **不要な type 分岐** — tech/idea で writer skill・レビュアー（editor/essay-reviewer）・文体を分けていたが、Zenn/Dev.to では読者体験の軸は共通であり、分ける理由がない。
3. **冗長の堆積** — frontmatter 仕様が 6 箇所、投稿時刻が 3 ファイルで矛盾（火〜水 7:00 / 火〜木 8:00 / 火・木）、`content-research-writer` ≈ `zenn-writer` の research flow が逐語重複、`chatlog-to-article` は frontmatter 無しで既に inert な orphan。

**きっかけ**: 久しぶりの執筆再開にあたりハーネスを最適化する過程で、「Zenn/Dev.to は独自軸を持つべき」と判断した。読者が即座に何かわかり、すぐ手に取って使えることが、この channel では最も重要。さらに検討を進める中で、「tech/idea で分ける必要はない」「執筆はサブエージェントに委譲しない」という単純化に至った。

## Decision

### 1. Zenn/Dev.to の声は「実用軸」に一本化する（type で分岐しない）

軸: **読者が数秒で何かわかり、そのまま手を動かして再現できる。理解に認知リソースを使わせない。** 低情報密度・実コード/図・即実用・低認知負荷・用途が瞬時にわかる。Diátaxis の how-to / reference 象限に対応（explanation = essay 象限は対象外）。

`zenn-practical-writing` skill を新設し、この軸の正本とする。**tech/idea 問わず全ての Zenn/Dev.to 記事がこのスキルを使う。** Zenn frontmatter の `type` フィールドは platform 要件として残るが、voice・レビュアーの選択には一切影響しない。

genre 中立 canon（AI-slop 禁止・タイトル誠実さ・ネタ 3 軸）は `writing-ecosystem` に defer し、Voice だけ override する。

### 2. 文体を channel で分ける（type では分けない）

| channel | 文体 | 語り |
|---|---|---|
| **Zenn/Dev.to（全記事）** | **ですます調** | 直接指示で言い切る（〜します） |
| エッセイ（Substack corpus） | だ/である | 発見調・問い化（〜ではないか） |
| 論文 | paper-ecosystem に従う | — |

2026-04-13 に「全記事 だ/である × 発見調」へ統一したが、channel ごとに声が確立した今、Zenn/Dev.to は ですます調に切り替える。**tech/idea では分けない** — genuine な思索エッセイを書きたい場合は Zenn ではなく Substack corpus へ出す（channel を分ける。同一 channel 内で type 分岐はしない）。既存記事は遡及変更しない。

### 3. 記事執筆はサブエージェントに委譲しない

これまで `zenn-drafter` agent に執筆を委譲していたが、**Claude Code 本体（オーケストレーター）が直接執筆する**方針に変更する。理由は他のオーケストレーション判断（ADR-0002 §1「新しいエージェントは作らない」）と同型: 執筆はオーケストレーターがすでに持っている能力であり、別エージェントに委譲すると文脈の断絶が起きる。

`zenn-drafter` が持っていた 3 段階プロセス（構成案→確認→執筆→自己プリフライト）は `zenn-practical-writing` skill 内の「執筆プロセス」節に引き継ぎ、オーケストレーター自身が直接実行する。

### 4. voice 資産の再配置

| 資産 | 新しい住所 |
|---|---|
| タイトル・AI-slop・ネタ 3 軸（genre 中立） | `writing-ecosystem`（正本、defer） |
| 実用軸の style spec + 執筆プロセス | `zenn-practical-writing`（新設） |
| 毒humor・刃牙（任意の personality flavor） | `zenn-idea-voice`（新設、type 非依存の opt-in） |
| frontmatter・記法 | `zenn-format`（正本） |
| 投稿ペース・バズタイム・文体規約 | `rules/zenn-writing.md`（正本） |
| research / 素材集めフロー | `zenn-practical-writing`（1 本化） |

`zenn-writer` は既存の参照パスを壊さないため、上記へ振り分ける**声のルーター**に in-place で縮小する。

### 5. レビュアーも type で分岐しない

Zenn/Dev.to の全記事は `editor` agent でレビューする。`essay-reviewer` は Substack essay corpus 専用とし、Zenn/Dev.to のミッションでは使わない（essay-reviewer のトーン一貫性チェックは だ/である × 発見調 を前提としており、ですます調の実用記事には適用できない）。

公開記事であるため、planning.md の Writing Chain「Cross-Model Review（条件付き）: 公開記事は codex-review を並列起動」を適用し、**editor / fact-checker と並列で codex-review（prompt-driven モード）** を起動する。これは新規ルールではなく、既存ルールの配線漏れを埋めるもの。

新しいレビューエージェントは作らない（ADR-0002 §1 を維持）。実用軸の客観チェック項目（runnable code / 図表 ≥1 / 冒頭 utility 宣言 / 前提列挙 / scannable / ですます統一）は `quality-gate` の客観チェックリストに集約する。global `editor` は他 channel と共有のため改変しない。

### 6. ユーザー確認点を 2 点に集約する

`writing-team` Mission A/B のユーザー確認（⏸）は、テーマ・構成案・ドラフト・レビュー結果・published_at と 5 箇所に分散していた。以下の 2 点に集約する:

1. **構成案確認**（着手前）— コア論点・独立論点数・セクション構成・シリーズ重複リスク
2. **一括確認**（editor/fact-checker/codex-review + quality-gate + seo-optimizer が全て完了した後）— ドラフト全文・レビュー結果・SEO 提案をまとめて 1 回で確認し、そのまま publish-article へ

## Consequences

### 新規作成

- `.claude/skills/zenn-practical-writing/SKILL.md` — 実用軸 + 執筆プロセスの正本
- `.claude/skills/zenn-idea-voice/SKILL.md` — 任意の personality flavor（毒humor / 刃牙）

### 廃止（削除。git 管理下のため履歴で復元可能）

- `.claude/skills/content-research-writer/` — 外部 origin。research flow は zenn-practical-writing に 1 本化
- `.claude/skills/chatlog-to-article/` — frontmatter 無しで inert。`_context/` raw-log 規約は zenn-writing.md に保存
- `.claude/agents/zenn-drafter.md` — 執筆委譲を廃止したため不要。プロセスは zenn-practical-writing に引き継ぎ済み

### 変更

- `zenn-writer` — 声のルーターに縮小（参照パス維持、tech/idea 分岐なし）
- `quality-gate` — tech/idea 節を統合し実用軸チェックリストに一本化。だ/である発見調チェックを削除、ですます統一チェックを追加
- `writing-team` — Mission A/B から zenn-drafter 委譲を除去、editor 単一レビュアー化（`writing-team` 実装が持っていた「editor/essay-reviewer を type で選択」という運用ルールの変更であり、ADR-0002 自体が明示的に決定した rule の supersede ではない）、codex-review 追加、確認点を 2 点に集約
- `ideation` — zenn-drafter への参照を zenn-practical-writing の Phase 1 へ repoint
- `seo-optimizer` — タイトル再掲を削除し writing-ecosystem に defer（Distribution 機構のみ残す）
- `schedule-publish` / `publish-article` — 投稿時刻を zenn-writing.md に defer、frontmatter 追加、付随の腐敗修正（個人パス露出・廃止 preset 参照・ファイル内時刻矛盾）
- `rules/zenn-writing.md` — channel ルーティング、文体規約（ですます統一）、`_context/` 規約、dangling MEMORY.md 参照修正
- `CLAUDE.md` / `README.md` — 実用軸・新トポロジ・エージェント一覧を反映

### Supersede（ADR 内部矛盾の解消）

- **ADR-0001「存続（変更なし）」の zenn-writer 行** — 「zenn-writer の文体ガイド（発見調・Voice Pattern）は存続」としていたが、本 ADR で voice 資産は各 channel skill へ再配置され、zenn-writer はルーターに縮小した。Content Integrity 原則そのものは不変（下記 bright-line）。
- **ADR-0002 §2 の `writing-standards.md`** — canonical reference として挙げられていたが、この参照先ファイルは存在せず、canon は global `writing-ecosystem` skill へ移行済み。

### Content Integrity との関係（catchify bright-line）

実用軸は ADR-0001 が葬った catchify（禁止）とは異なる。**実用スタイルは著者が選ぶ draft 時の生成既定**（Content・著者所有・許可）であり、**完成稿へのエンゲージメント目的の事後リライトではない**（それが catchify＝禁止）。判定式は ADR-0001 の「誰のために変えるか」——著者の思考のためか、読者エンゲージメントのためか。`seo-optimizer` / `quality-gate` は「もっと punchy に」の事後改変権限を持たない。

## Notes

- **既存記事は遡及変更しない**（33 tech + 16 idea + 4 essay は legacy 資産）。本 ADR は今後の執筆の既定。
- **シリーズの声**: 継続シリーズ内で新記事が先行記事（旧文体）とトーン不整合になりうる。継続シリーズでは先行記事の声を優先するか、明示的に転換する（`series-checker` で確認）。
- **Dev.to/EN の継承**: `devto-translator` の忠実翻訳で JP 実用軸を自動継承。EN 専用スキルは作らない。
- 廃止コンポーネントは削除前に inbound link を repoint 済み。復元が必要な場合は git 履歴（`git log --follow` / `git show`）から参照する。

## Addendum (2026-07-06): zenn-writer router の削除

「参照パス維持のため router 化」とした `zenn-writer` は、skill-stocktake 監査で **router 経由の実導線が消滅している**ことを確認した（残存参照は CLAUDE.md / codemap の説明文のみで、いずれも振り分け先を直接指していた）。参照を repoint のうえディレクトリを削除。振り分け表の正本は CLAUDE.md「Writing skills」節。
