# Plan: codemap 退役記事（Scaffold Dissolution 軸）

## Context

`drafts/article-context_codemap-retirement_2026-09-05.md` を素材に Zenn 記事を書く。
2026-09-05 に contemplative-agent の `docs/CODEMAPS/`（6 ファイル 205KB）を全削除し、harness からも
codemap 機構（skill 2 本・hook・ADR-0060 の gate）を撤去した経緯が素材。著者選択:

- **中心命題**: Scaffold Dissolution（substrate = Claude Code の LSP tool が構造導出を native に持った
  瞬間、手書き architecture map という足場は縮めずに消す）
- **公開形**: JP 即時 + EN 即時（直近 4 本と同じ）

Channel は `articles/*.md` → Zenn（`editor` / ですます / 50 字タイトル / `npm run validate` +
`npm run evidence`）。EN は `articles-en/` → Dev.to。

## Editorial brief（案。Step 2 で著者確認を取る）

```
Reader: Claude Code 等で LLM 向けの architecture doc（codemap / repo map）を手書き＋自動更新で
        維持している engineer。「graph 化・自動生成で改善すべきか」と考え始めている
Channel: Zenn（articles/codemap-retirement.md 仮）
Central thesis: 基盤ツールが同じ能力を native に持った時点で、手書きの足場は縮小でなく削除が
        正解になる。判断の入口は「改善案」でなく「そもそも要るか」
Causal spine:
  きっかけ — Archify を試し、生成された図と手書き codemap を並べて「これを graph 化すべきか」と
           考えた（C16。掴みの具体物として Archify の出力画像を貼る。Archify は作図 skill であり
           コードからの導出ではない、の 1 点を正確に書く。ADR-0062 の記述に揃える）
  観察   — 「codemap を graph 化したい」から始めた調査で、前提が 2 点ずれていた
           （5 枚→6 枚、15.6k→30k token。header は 8/1 の値のまま）(C1, C2)
  緊張   — 詰まっている作業は無い。実害候補は肥大だけ。しかも 4 日前に freshness gate を
           script 化する ADR-0060 を accept したばかり (C3, C6, C10)
  機序   — 「LLM の理解」を構造と理由に分解 → 構造は LSP が導出できる（incomingCalls 17 件、
           行番号まで正確）、理由は ADR/docstring/test が既に 25 件中 23 件持つ (C5, C7)
           縮退案 B は architect が「Data Flow 自体が肥大源。hook が残れば 1 か月で再肥大」と却下 (C11)
  判断則 — 削除の結果: 機械的に壊れたのは 3 点、verify rc=0、消費者ゼロで空になる scan 読みを
           FILE_MISSING に (C8, C14, C15)。global 撤去で機構として再生産されない形にした (C12)
           読者へ: 改善案が出たら先に「詰まっている作業」「読んだ証拠」「基盤が代替するか」を問う
Selected evidence:
- C16: Archify 試用が発端（Calm Story。画像 1〜2 枚 + 「何ができて何ができないか」1 段落。
  ⚠未検証 → Step 0 で発端セッション 3cb61678 を trace して確定させる）
- C1, C2: 前提照合（依頼文の数字が古い）
- C3: src 197 / CODEMAPS 159 commit — 更新コストの実測
- C5: LSP probe — 構造は導出できる証拠（核心）
- C7: 監査 25 件中 23 件 COVERED — 理由は既に別の場所にある
- C10: ADR-0060 accepted → 4 日で superseded — 足場が溶ける瞬間の日付
- C11: architect の逐語引用 2 本（B 却下の理由）
- C8, C14, C15: 削除の波及と静かな側の危険（scan が空になる）
- C12: 著者の global 撤去指示（縮退でなく削除、再生産防止）
Out of scope:
- Archify の機能比較・評価記事化（きっかけと「導出でなく作図」の 1 点に留め、良し悪しは論じない）
- C17 外部 code-graph ツール調査（⚠未検証。「調べた」の一言に留めるか省く）
- 他 9 repo の残置、並行セッションの claim 衝突、pre-commit gate の archify origin
- AKC / harness ADR の細部（末尾リンク 1 行に留める）
- 「読まれていない」は不在の証拠であり読まなかった証明ではない → 本文では「読まれた証拠が無い」
  の言い方を保つ
```

注意: 「Scaffold Dissolution」「downward」は内部語彙。本文は「足場」「溶ける」など日常語で言い、
固有名は末尾 1 回まで（prose-clarity-reviewer の内部語彙密度が検出器）。

## Steps（writing-ecosystem Canonical workflow に従う）

0. **Archify 発端の確定と画像受け取り** — 発端セッション `3cb61678-….jsonl` を dossier の
   再抽出 helper で trace し、Archify で何をしたか（入力・出力・所感）を一次ソースで確定。
   `~/.claude/skills/archify/SKILL.md` を読み「作図 skill」の記述を裏取り。著者から画像の
   場所を受け取り `images/codemap-retirement/` へ配置（個人 path・credential・未 sanitize の
   screenshot が無いことを目視）。Zenn は `/images/...` 相対参照、Dev.to は GitHub raw URL
1. **Theme review** — `theme-reviewer` agent に問い一文 + dossier を渡し findings と深化の問いを受ける
   （合否なし）。findings を brief に反映
2. **Editorial brief** — 上の brief を提示し **著者確認で停止**
3. **Outline + draft** — `articles/codemap-retirement.md`（slug 仮）を執筆。実用記事型:
   読者が得るものを冒頭で明示、主要節ごとに端末出力 / 数値を置く。frontmatter は `zenn-format`
   （`published: false`、`published_at` は即時公開のため省略）。末尾 `## 関連リンク` に contract 必須の
   2 行 + シリーズ前作（instrument-consumption-plan / lint-as-subtraction）+ ADR-0062 公開 mirror
4. **Freeze → review panel**（本文へ並列）: `editor`、`prose-clarity-reviewer`、`fact-checker`
   （Claims Register を渡す。特に C5 の LSP tool と C10 の日付、mirror URL）、`codex-review`
   （著者が明示要求した場合のみ。未実行なら quality-gate に理由と fallback を記録）。
   機械検査: `npm run validate`、`npm run evidence -- articles/codemap-retirement.md`（deviations 0）
5. **反映 → Final structural pass → 著者通読・内容 GO**（brief の spine を変えた場合は 1 へ戻る）
6. **Title** — `headline-craft` で候補 → `title-reviewer` findings → 著者選択（50 字以内）
7. **Acceptance** — `/quality-gate articles/codemap-retirement.md` → PASS → 著者の公開 GO
8. **Publish JP** — `/publish-article`（即時公開）
9. **EN** — `devto-translator` で `articles-en/codemap-retirement.md` を生成 → EN 稿へ `editor` +
   `prose-clarity-reviewer` 再実行 → `devto_crosspost.py post <slug> --dry-run` → 著者 GO → 投稿
10. **Index / verify** — `npm run generate:index`、`npm run validate`、`npm run check:index`、
    schedule.json の devto URL 書き戻し、commit、**push を著者に促す**

## Critical files

- 素材: `drafts/article-context_codemap-retirement_2026-09-05.md`
- 新規: `articles/codemap-retirement.md`、`articles-en/codemap-retirement.md`
- 更新: `scripts/schedule.json`、`docs/PUBLICATIONS.md`（生成）
- 規範: `.claude/skills/writing-ecosystem/SKILL.md`、`.claude/rules/publishing-channels.md`

## Verification

- `npm run validate` / `npm run evidence -- articles/codemap-retirement.md` が deviations 0
- reviewer 証跡: editor CRITICAL 0、prose-clarity PASS、fact-checker INACCURATE 0・未解決 PARTIALLY 0、
  title-reviewer 実行済み
- `/quality-gate` PASS、`npm run check:index` drift 0
- 公開後: Zenn URL と Dev.to URL が schedule.json に書き戻されている
