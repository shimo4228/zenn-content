# `.claude` ハーネス統合仕上げ（ADR-0003 の積み残し解消）

## Context

ADR-0003（Zenn/Dev.to 実用軸への一本化）で `zenn-practical-writing` / `zenn-idea-voice` を新設し、`zenn-writer` をルーターに縮小、`zenn-drafter` agent と `chatlog-to-article` / `content-research-writer` skill を廃止した。この設計判断自体は正しく、writing-team・quality-gate・ideation・rules/zenn-writing.md・CLAUDE.md・README・llms.txt までは一貫して行き渡っている。

しかし ADR-0003 の Consequences が「変更した」と明記しているファイルのうち、実際には手が回っていない箇所と、リファクタ時に見落とされた既存の壊れたリンクが残っている。これが「ポインタ化したのに統合が中途半端」という実感の具体的な原因。今回は **新しい設計を追加するのではなく、ADR-0003 がすでに決めた設計を最後まで反映させる仕上げ作業**。

調査は Explore agent 1 本 + 主要ファイルの直接読み込みで実施済み。以下はすべて実ファイルを読んで確認した具体的な不整合。

## 確認済みの問題と修正方針

### 1. `refs/schedule-schema.md` — 投稿時刻の値が矛盾したまま残存

ADR-0003 は「投稿時刻が3ファイルで矛盾（火〜水7:00 / 火〜木8:00 / 火・木）」を問題として明記し、Consequences で「`schedule-publish` / `publish-article` — 投稿時刻を zenn-writing.md に defer」と書いた。実際 `schedule-publish/SKILL.md` と `publish-article/SKILL.md` は正しく `rules/zenn-writing.md`（火〜水 7:00-9:00 が正本）を参照するよう直っている。

**唯一 `refs/schedule-schema.md:64` だけが古い値「火〜木の 8:00-9:00 JST」を再掲したまま**残っている。しかも zenn-writing.md 自身が「他スキルはここを参照し、値を再掲しない」と名指ししているファイルの1つがこれ。

**修正**: L60-64 の「投稿ペースガイドライン」セクションの値を削除し、`.claude/rules/zenn-writing.md` への参照のみに置き換える（他の値と同じ defer パターンに揃える）。

あわせて、`schedule-publish/SKILL.md` は schedule.json エントリに `score` フィールド（4軸スコアの記録用）を追加する運用を明記しているが、`schedule-schema.md`（このスキーマの「正本」）にはこのフィールドが定義されていない。スキーマ側に `score`（optional）フィールドの定義を追記する。

### 2. `zenn-format/SKILL.md` — リファクタから唯一取り残されたファイル

他の全 skill（9本）が ADR-0003 で YAML frontmatter・相互参照込みで更新されたのに対し、このファイルだけ以下の点で旧状態のまま:

- **frontmatter がない**（`<!-- origin: original -->` という旧式のHTMLコメント表記のみ）。他の skill は全て `name`/`description`/`user-invocable`/`origin` の YAML frontmatter を持つ。`rules/common/skills.md` の現行規約（YAML frontmatter が標準）に揃え、discoverability を他 skill と一致させる
- **L5 の文体ガイド参照が `zenn-writer` のまま** — `zenn-writer` は ADR-0003 で「声のルーター」に縮小済みなので、直接 `zenn-practical-writing`（+ 任意で `zenn-idea-voice`）を指すべき。1ホップ余分
- **`## Publishing Workflow`（L232-241）が `publish-article` skill と内容重複** — Draft/Preview/Lint/Review/Publish/Sync の8ステップの簡易版が、`publish-article/SKILL.md` の詳細12ステップと重複している。「正本」原則に反するので、このセクションは削除し `publish-article` への1行ポインタに置き換える
- **`## Related Resources` のリンクが壊れている**:
  - `[CLAUDE.md](../../CLAUDE.md)` — `.claude/skills/zenn-format/` からは2階層上がると `.claude/CLAUDE.md`（存在しない）になる。3階層上がる `../../../CLAUDE.md` が正しい
  - `[Editor Agent](../../.claude/agents/editor.md)` — editor.md はプロジェクトの外（グローバル `~/.claude/agents/`）にあるため、そもそも相対リンクが成立しない。他ファイルに揃えて `~/.claude/agents/editor.md` という平文参照に直す（クリック可能なリンクにしない）

### 3. ADR リンクの機械的な破損（3ファイル・5箇所）

以下は全て「`../../.claude/docs/adr/...`」という同一パターンの誤り。`.claude/skills/<skill>/SKILL.md` から `.claude/docs/adr/` へは `../../` （2階層）で到達するのが正しく、リンク文字列中の余分な `.claude/` セグメントが二重になっている（`.claude/skills/x/../../.claude/docs/...` → `.claude/.claude/docs/...` という存在しないパスに解決される）:

- `writing-team/SKILL.md:12`（ADR-0002）, `:116`（ADR-0001）
- `quality-gate/SKILL.md:12`（ADR-0002）
- `seo-optimizer/SKILL.md:11`, `:42`（ADR-0001）

**修正**: 5箇所すべて `../../.claude/docs/adr/` → `../../docs/adr/` に統一。

### 4. `publish-article/SKILL.md` Step 3 — writing-team 経由時に editor が二重実行される

`writing-team/SKILL.md` の Mission A/B では、editor/fact-checker/codex-review を並列実行（Step 4）→ quality-gate（Step 6）→ **publish-article を最終ステップとして呼ぶ**（Step 8）。ところが `publish-article/SKILL.md` の Step 3 は「editor エージェントを起動して記事を包括的にレビューする」と無条件に書かれており、writing-team 経由で呼ばれた場合、数ステップ前に完了済みの editor レビューをそのまま再実行してしまう（fact-checker・codex-review には言及もない）。

**修正**: Step 3 の冒頭に条件分岐を明記する——「writing-team Mission A/B から到達した場合は Step 4（レビュー済み）にスキップ。`/publish-article` を単独で直接呼んだ場合のみ、このステップで editor を起動する」。

### 5.（軽微・任意）`agents/devto-translator.md` に frontmatter がない

グローバル agent（editor/essay-reviewer/fact-checker）は全て `name`/`description` 等の YAML frontmatter を持つが、このプロジェクト固有 agent だけ frontmatter なしの素の Markdown。今回の ADR-0003 差分の対象外だが、「エージェント一覧の整合」を謳う統合作業のついでに揃える。振る舞いは変えず frontmatter 追加のみ（`name: devto-translator`, 既存冒頭文からの `description`, `origin: original`）。

## 対象外（確認済みで問題なし・触らない）

- `zenn-writer` のルーター化・`zenn-idea-voice`/`zenn-practical-writing` の相互参照内容 — 実ファイルを読んで確認、実質的な重複や矛盾はない
- 削除済み（`zenn-drafter` / `chatlog-to-article` / `content-research-writer`）への参照 — grep で確認済み、コード上の参照は残っていない（`articles/organic-growth-content-integrity.md` に言及があるが、これは過去の問題を振り返る公開済み記事の本文であり、修正対象ではない）
- `ADR-0003` 本体 — 設計判断の正本として変更しない

## Verification

1. `grep -rn '../../.claude/' .claude/skills/` — 0件になることを確認（破損リンクパターンの根絶）
2. `grep -rn '火〜木\|8:00-9:00' .claude/` — `refs/schedule-schema.md` 以外に残っていないこと、かつ修正後は同ファイルにも値の再掲がないことを確認
3. 各 SKILL.md の Markdown リンクを目視確認（`../../../CLAUDE.md` 等、実ファイルが実際に存在するパスか）
4. `git diff` で意図しない内容変更（Content Integrity 原則に反する文面変更等)がないか確認
5. `git status` で対象ファイルのみが変更されていることを確認
