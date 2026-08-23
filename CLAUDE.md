# Claude Code Instructions for zenn-content

## Project Overview

This repository contains **Zenn articles and books** for AI agent development, Claude Code workflows, and LLM engineering experiments. All content follows the **"Build in Public"** principle, documenting real development sessions and design decisions.

## Governed essay corpus (membership)

This repository is governed as the **essay-corpus artifact** of a five-line research ecosystem (see `CITATION.cff` and the README "Provenance and reuse" section). The governed corpus is **author-voiced + published** essays: pieces written in the author's own voice and actually published (Zenn / Dev.to / note / Substack). Study or learning drafts without an author voice — for example Claude-written study drafts that were never published — are **not** part of the governed corpus and are kept out of this repository. This is a membership criterion, not a churn rule: it describes what belongs, and is not enforced by reshuffling files.

The corpus rests its priority claim on the **intrinsic content-derived identifier** (the Software Heritage snapshot in `CITATION.cff`), not a registry DOI — this is the essay genre's substitute priority-claim mechanism under the ecosystem's genre-split placement model (authorship-strategy ADR-0016 / ADR-0013). A load-bearing essay idea is promoted to a concept-DOI deposit only when it graduates into a paper.

This corpus is also the **essay layer** of the ecosystem's audience-layer split (authorship-strategy ADR-0022, 2026-08-05): its primary audience is **contemporary human readers**, on a day-to-week time constant, and contemporaneous reception signals (reads / reactions / followers, collected in `scripts/metrics/snapshots.jsonl`) are legitimate **both to observe and to steer writing decisions by** (topics, cadence, language placement). Three bounds: ① reception numbers never steer the ecosystem's doctrine-layer decisions (releases, deposits, federation); ② content is never deformed for numbers — steer *what to write*, never *what the idea is* (ADR-0019); ③ the publishing platforms are third-party-governed, so nothing load-bearing rests on them — the corpus canonical and SWHID above survive platform loss. The production record (`scripts/schedule.json`) and the metrics snapshots are standing inputs to the strategy's next-move review.

## Publications index（README は一覧を持たない）

README は「1 本の記事から来た読者に次の 1 本と全体像を渡すルーティングページ」で、記事一覧は持たない（ADR-0009、2026-08-18）。網羅一覧は生成物 `docs/PUBLICATIONS.md` の 1 つだけ:

- **正本**: `articles/*.md` frontmatter（membership・title・topics・`published_at` — published なら必須）、`scripts/schedule.json`（Dev.to URL のエンリッチのみ。membership には使わない）、`scripts/corpus.yml`（note/Substack エッセイ・論文・研究ライン — frontmatter が無いものの手書き台帳）、`scripts/reading_paths.yml`（README の読書経路。著者判断、年単位）
- **生成**: `npm run generate:index`（記事の追加・URL 書き戻し・エッセイ公開・論文寄託のあと、commit 前に実行）。`npm run check:index` が CI で走り drift を fail させる。bot commit はしない
- README / README.ja.md / llms.txt / llms-full.txt に記事タイトルや本数を手書きしない（stale の再発源）

## Git Push Reminder (CRITICAL)

記事の作成・編集・schedule.json の更新をコミットしたら、**必ずユーザーに push を促すこと**。未 push のコミットがあると、Zenn の `published_at` 予約投稿が反映されず、Dev.to のクロスポストスクリプトも動かない。

## Writing Guidelines

### Zenn Article Format

All articles MUST use Zenn frontmatter. Field-by-field spec is canonical in `.claude/skills/zenn-format/SKILL.md`; the `published_at` scheduling field is documented in `.claude/rules/zenn-writing.md`.

> **執筆スタイルの既定は実用軸**（読者が数秒で何かわかり、すぐ使える）。tech は `zenn-practical-writing`、frontmatter・記法は `zenn-format`、Zenn 固有ルールは `.claude/rules/zenn-writing.md` が正本。以下の Technical Depth は「why を冗長に語る」ではなく、必要な深さを低認知負荷で（詳細は `:::details` に）という意味。

### Content Standards

1. **Technical Depth**
   - Explain **"why"** decisions were made, not just **"what"** was implemented
   - Include real code examples from the repository
   - Discuss trade-offs and alternatives considered

2. **Code Examples**
   - All code snippets MUST be executable and tested
   - Include file paths for context (e.g., `src/pdf2anki/quality.py:322-329`)
   - Use syntax highlighting: ` ```python `, ` ```typescript `, ` ```bash `
   - Add comments for clarity

3. **Terminology Consistency**
   - 書き換え禁止ワードの正本は `.claude/rules/zenn-writing.md`「プロジェクト固有用語」（7 語の完全版）。ここには再掲しない

4. **Tone and Style**
   - **Technical but approachable** - Assume readers are engineers
   - **Honest** - Discuss failures and challenges, not just successes
   - **Human insights** - AI-assisted writing, but human perspective
   - **No AI slop** — 禁止リストの正本は global `writing-ecosystem` skill（語の実値はここに書かない）

5. **Structure**
   - **Introduction** - Hook reader with a problem or insight
   - **Context** - Background and motivation
   - **Implementation** - Technical details with code examples
   - **Lessons Learned** - Reflections and takeaways
   - **Conclusion** - Summary and next steps
   - **Environment-dependent changes** - When commands depend on local paths, existing settings, symlinks, or authentication, finish the human-facing narrative first, then provide a standalone read-only planning prompt for the reader's coding agent. The agent must stop for human approval before implementation. Canonical rules: `zenn-practical-writing`.

### Image Guidelines

- Store images in `images/` directory
- Use descriptive filenames: `tokenization-flow.png` not `image1.png`
- Embed with Zenn syntax: `![Alt text](/images/filename.png)`
- Sanitize screenshots: no file paths like `/Users/username/`, no API keys

### 関連リンク：著者ハブ（毎回必須）

記事末尾に「関連リンク」節を置くとき（本文で著者自身のリポジトリ/ツールに言及した記事）は、紹介した repo が **1つでも**、著者の GitHub ハブ [github.com/shimo4228](https://github.com/shimo4228) を**必ず含める**。ハブは読者を著者の全リポジトリへ送る導線なので、言及 repo の数に依らず付ける。これが canonical。skill 側（`zenn-practical-writing`）はここを参照する。

## アイデアエッセイの正本関係（2026-08-12 著者指示で改定）

**note が日本語アイデアエッセイの正本（初出）。Substack はその英訳の投稿場所。** 旧モデル（Substack 初出 → note 転載）は廃止。フローは一方向:

```
note/<slug>.md（JA 正本・初出）
  → ja-to-en-translation で英訳
  → substack/<slug>-en.md → Substack へ投稿（EN 初出）
```

## `note/` フォルダ（日本語アイデアエッセイの正本。Zenn 規約の適用外）

`note/` は日本語アイデアエッセイの**正本（初出）**置き場。1 ファイル 2 役 — 公開前は「そのまま貼れる原稿」、公開後は note URL を追記して LLM corpus mirror を兼ねる。第三者ドメイン配信による AI 引用リフト（GEO）も狙いに含む。

- **形式**: frontmatter なし。タイトルは本文冒頭の `# 見出し`（note は frontmatter を解釈しない）
- **文体**: `.claude/rules/zenn-writing.md`「チャンネル表」の note 行が正本（2026-08-06 著者指示で日本語公開チャンネルは統一済み）
- **改行**: 正本は `writing-ecosystem`「段落密度の機械的閾値」（全チャンネル共通。値はここに書かない）
- **末尾**: 出典・参考文献（該当時）+「関連リンク」節 — 関連 repo/DOI・GitHub ハブ（著者ハブ規約を適用）・公開後の Substack 英語版 URL。note に canonical URL 設定機能はない（2026-08 検索確認）ため、この節が還流手段
- **レビュー**: Zenn 記事と同じ厚さで公開前に回す（下記 Editor Agent Usage のアイデアエッセイ chain）
- **投稿は人間が手動**。`schedule.json` に載せない（dev.to クロスポスト対象外）
- **貼り付けは HTML 経由**（Markdown 直貼りは note でプレーンテキスト化する）。`tail -n +2 <slug>.md | pandoc -f gfm -t html -s --metadata pagetitle="<タイトル>" -o <slug>.html`（**`-f gfm` 必須** — 既定方言はリストを段落に潰す。`substack-publishing` に実証あり） で貼り付け用 HTML を併置（先頭 h1 はタイトル欄別入力のため除外）。ブラウザで開いて全選択コピー → note エディタへペースト。substack/ の .html 併置と同じ慣例
- **ペース: 週 1〜2 本**。burst しない（2026-07-16 rate limit = policy signal の教訓）
- 公開後、冒頭 or 末尾に note URL を追記して commit（mirror 化）。既存の frontmatter 付き旧 mirror 2 本はそのまま
- 公開後、`scripts/corpus.yml` の `essays:` に 1 エントリ（slug / date / ja.title / ja.url / ja.file）を追記し `npm run generate:index`（EN 版を Substack に出したら同エントリに `en:` を足す）

## `substack/` フォルダ（EN アイデアエッセイ。Zenn 規約の適用外）

`substack/` は Substack（英語）へ投稿する原稿 + 公開後ミラーの置き場。中身は `note/` の日本語正本を `ja-to-en-translation` skill で訳した英語版（public GitHub 上の .md として LLM クローラーに読ませる corpus 拡張用を兼ねる）。**Zenn 記事ではないので、本 repo の記事規約は適用しない**:

- **frontmatter なし**（2026-08-12 著者指示）。タイトルは本文冒頭の `# 見出し`（Substack の Title/Subtitle 欄へは別入力）。Zenn frontmatter・`published`・`published_at` は付けない（Zenn は `articles/` のみ同期するため `substack/` は公開されない）。既存ファイルの Zenn 風 frontmatter は旧慣例の名残でそのまま
- `schedule.json` に載せない（dev.to クロスポストしない）
- 日本語の canonical は note 正本。EN 版の初出は Substack で、記事末に JA 正本（note URL）への参照を置く
- 既存ファイル（旧モデルで Substack 初出だった JA/EN ミラー）はそのまま残す

公開手順（MD→HTML 貼り付け・タグ・配信運用）は project skill `substack-publishing` を参照（2026-08-23 に global から降格 — 対象原稿がこの repo にしかないため）。

## Editor Agent Usage

記事の執筆はサブエージェントに委譲せず、Claude Code 本体が `zenn-practical-writing` に従って直接執筆する。Before publishing, run review agents in parallel: レビュー agent はチャンネル表（`.claude/rules/zenn-writing.md`）の当該行に従う + `fact-checker`（事実主張の検証）+ `zenn-clarity-reviewer`（初見読者の明瞭性、project agent）+ codex-review（公開記事の cross-model レビュー、prompt-driven）。

**アイデアエッセイ（note/ 正本・substack/ 英訳）も同じ厚さでレビューする**（2026-08-12 著者指示）: チャンネル表のレビュー agent + `fact-checker` + `zenn-clarity-reviewer`（初見読者の明瞭性。note/Substack エッセイも対象 — 読者シミュレーションを「note フィードから来た一般読者」に置き換える）+ codex-review。

**二本立て評価 + 改稿ループ**（2026-08-12、ADR-0008）: 全チャンネルの記事は **テーマ評価**（`.claude/skills/theme-eval` — 執筆前の 1 時点。テーマランクが記事の上限を決める。Deepen 2 回まで、却下ゲートではない。2026-08-23 に完成稿での再判定を廃止）と **記事品質評価**（`scripts/mechanical_checks.py` の決定論検出 + `article-judge` agent の二値チェック判定。基準アンカーは `.claude/refs/kaguura-craft-checklist.md`）の二本立てで評価する。改稿ループの正本は `writing-team` skill の「改稿ループ」節（fresh-context 判定・span 指摘のみ・上限 2 ラウンド・voice 回帰監視）。著者の関与はテーマ層（Deepen の問い）と publish 直前の通読 GO に集中する。

```bash
claude --agent=editor --prompt="Review: articles/ARTICLE_NAME.md"
# ファクトチェック（並列実行可）
claude --agent=fact-checker --prompt="Fact-check: articles/ARTICLE_NAME.md"
```

Available agents:
- `editor` — 実用チャンネルの記事の構造・品質・AI slop 検出（4段階評価。担当チャンネルはチャンネル表）
- `essay-reviewer` — エッセイチャンネル用（担当チャンネルはチャンネル表）
- `fact-checker` — 事実主張の Web 検索検証（ACCURATE/PARTIALLY/INACCURATE/UNVERIFIABLE）
- `zenn-clarity-reviewer` — 初見読者の明瞭性（造語予算・タイトル軸・内部文脈依存。project agent、JP/EN 両対応。Zenn/Dev.to 記事と note/Substack エッセイの両方が対象。FAIL は公開ブロック）
- `devto-translator` — JP→EN 翻訳 + Dev.to タグ付け + 投稿

## Writing skills

Zenn/Dev.to の記事執筆は**チャンネル独自の実用軸**が既定 —「読者が数秒で何かわかり、そのまま手を動かして再現できる」。**tech/idea の type で声を分けない**（frontmatter の `type` は platform 要件として残るが、voice は分岐しない）。

| 用途 | 使うスキル |
|---|---|
| **Zenn/Dev.to の記事執筆（既定・全記事）** | `zenn-practical-writing` — 実用軸（即実用・実コード/図・低認知負荷。文体はチャンネル表）。環境依存の変更記事は「人間向けナラティブ → エージェント向け実装契約」の二層構成 |
| **執筆前のタイプ判定・軸ずれ検出・改稿時の構造自己審問・レビュー採否** | `zenn-editorial-judgment` — 著者の編集判断ゲート集（構成案の前に Phase 0 タイプ判定、ADR-0006） |
| **著者の価値観・ペルソナ規約・内容ランク A/B/C 基準** | `zenn-authorial-values` — 実セッション引用付き価値観リファレンス（ADR-0006） |
| **記法・frontmatter** | `zenn-format`（正本） |
| **任意の personality flavor** | `zenn-idea-voice`（毒humor / 刃牙。type 非依存の opt-in） |
| **公開後の実測 Eval ループ** | `article-stocktake` — 実測メトリクス × 品質ランクの乖離棚卸し（月次目安、ADR-0005） |
| **genuine な思索エッセイ** | `~/.claude/skills/writing-ecosystem/SKILL.md`（発見調。文体はチャンネル表が正本）。JA 正本は `note/`、英訳を Substack へ。Zenn には出さない |

genre 中立 canon（AI slop 禁止・タイトル原則・ネタ 3 軸）は global `writing-ecosystem` が正本。根拠: `docs/adr/0003-zenn-practical-channel-axis.md`。

## Testing Workflow

See `docs/CODEMAPS/scripts.md` for the publishing pipeline (single `devto_crosspost.py`, launchd agent, tests).

## Publishing Checklist

Pipeline reference: `docs/CODEMAPS/scripts.md`

- [ ] Code snippets have no API keys
- [ ] Screenshots have no sensitive information (file paths, usernames)
- [ ] File paths are anonymized
- [ ] All code examples are tested and executable
- [ ] レビュー完了（担当 agent はチャンネル表の「レビュー agent」列）
- [ ] タイトル最適化済み（`/seo-optimizer` → global `headline-craft` 経由で候補提示・確定。英訳より前に確定させる）
- [ ] fact-checker でファクトチェック完了（事実主張を含む記事は必須）
- [ ] zenn-clarity-reviewer の verdict が PASS（初見読者の明瞭性。FAIL のままなら公開不可）
- [ ] Zenn frontmatter validates (`npm run validate`)
- [ ] Preview looks good (`npm run preview`)
- [ ] `published_at` を設定（`YYYY-MM-DD HH:MM` 形式、JST）
- [ ] English translation created in `articles-en/`
- [ ] `schedule.json` updated with both Japanese and English entries
- [ ] Cross-post target scheduled: Dev.to (English)
- [ ] `npm run generate:index` 実行済み（`docs/PUBLICATIONS.md` と README 読書経路が最新。CI の `check:index` が赤にならない）

---

**IMPORTANT**: This repository is PUBLIC. Never commit:
- Personal file paths (`/Users/username/`)
- API keys or credentials
- Sensitive screenshots
