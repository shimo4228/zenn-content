# Zenn 記事: Claude Code のグローバル CLAUDE.md / rules を特定環境だけ除外する

## Context

2026-08-02 のセッションで、`CLAUDE_CONFIG_DIR` を別ディレクトリに向けても
`~/.claude/CLAUDE.md` と `~/.claude/rules/**`（16 ファイル / 3,404 語）が読み込まれ続ける
ことが実測で判明した。原因は 2 系統が独立していること — config dir が持つのは設定・
プラグイン・認証・履歴で、CLAUDE.md と rules は **cwd の祖先ディレクトリを辿る**別経路で
解決される。ホーム配下で作業する限り祖先の `~/.claude/` が拾われる。

解決は公式設定 `claudeMdExcludes`（絶対パス glob で除外）。設定 3 行で、通常セッションを
一切変えずに、別 config dir のセッションからだけ個人ハーネスを外せる。

証拠台帳: `drafts/article-context_claude-code-harness-isolation_20260802.md`（Claims C1–C22）
生ログ: `drafts/evidence_claude-code-harness-isolation_20260802/session-d73fb350-full.md`

**この記事の狙い**: 過程（symlink 失敗 → worktree 案 → 環境変数案 → Codex 指摘で全面変更）は
全て落とし、読者がそのまま打てる設定紹介の短編にする。ユーザー指示による。

---

## 記事仕様

| 項目 | 値 |
|---|---|
| slug | `claude-code-claudemd-excludes`（暫定） |
| 分類（Phase 0 タイプ判定） | **how-to / reference（設定ガイド）** → 装置は原則採用。ただし短編のため最小構成 |
| 読者の問題文 | 用途別に Claude Code の環境を分けたいのに、グローバルの CLAUDE.md と rules がどのセッションにも入ってくる読者が、この記事を読むと settings.json の 1 キーでそれを止め、止まったことを実測で確認できるようになる |
| 独立論点数 | 4（上限ぴったり。これ以上足さない） |
| 目標分量 | 本文 2,500〜3,500 字 |
| 文体 | ですます調 × 直接指示（`zenn-practical-writing`） |
| 統合候補 | なし（現行 corpus に `CLAUDE_CONFIG_DIR` / `claudeMdExcludes` を扱った記事は 0 件。grep 確認済み） |

### 構成

1. **タイトル**（結果駆動。候補は下記、`/seo-optimizer` で確定）
2. **掴み → 緊張 → 解決**（第一画面）
   - 掴み: 実験用・自律ループ用に別の設定ディレクトリを用意して `CLAUDE_CONFIG_DIR` を
     切り替えた。素のはずなのに、いつものルール通りに動く
   - 緊張: `/context` を見ると個人ハーネスが丸ごと入っている。分けたつもりの環境が分かれていない
   - 解決: settings.json の 1 キーで止まる。しかも repo 固有の CLAUDE.md は残せる
3. **## 前提** — Claude Code のバージョン（執筆時に `claude --version` で実測）/ 設定は
   config dir ごとの `settings.json` / macOS で実測
4. **## なぜ `CLAUDE_CONFIG_DIR` では止まらないのか**（論点 1）
   - 2 系統の対比表（config dir が持つもの / CLAUDE.md 探索が辿るもの）
   - 祖先探索なので、ホーム配下で作業する限り `~/.claude/` が「プロジェクトの .claude」として拾われる
   - 補足 1 行: symlink でホーム外に逃がしても realpath が解決されるので回避できない（C3）
5. **## `claudeMdExcludes` で除外する**（論点 2）
   - JSON コピペ（`**` 1 本）。絶対パスで書く
   - 除外リストは **その config dir の settings.json にだけ**書くので通常セッションは無傷
6. **## 何が消えて何が残るか**（論点 3・表）
   - 消える: 除外パス配下の `CLAUDE.md` と `rules/**`
   - 残る: config dir の `skills/` `agents/` `hooks`、repo の `CLAUDE.md` / `.claude/rules/` /
     `settings.json` / 機械ゲートのスクリプト
   - 含意 1 行: 「repo 固有の取扱説明書は残したまま、個人ハーネスだけ外す」ができる
7. **## 効いたか確認する**（論点 4）
   - `/context` の Memory files 欄（手軽な方）
   - `InstructionsLoaded` hook でロード元を機械的に記録（コピペコマンド + 受け取る JSON 1 行）
   - Before/After 表: 17 ファイル（User 16 + Project 1）→ 1 ファイル（Project のみ）
   - 1 段落だけ: 「システムプロンプトに X はありますか」と LLM に聞く方式は検証にならない
     （同じ語が repo memory・学習知識にもあるため、ロード元の証明にならない）
8. **:::details 応用 — ハーネスは分けるが記憶は共有する**（本筋に数えない）
   - `projects/` の symlink 2 行 + `claude project purge` 警告（丸ごと共有だとリンク先の実体が消える）
9. **## まとめ（Higher Ground）**
   - 「ハーネスを切り替える」のではなく「読み込み経路ごとに制御する」。設定・CLAUDE.md 探索・
     repo 資産の 3 経路は独立していて、別々に開け閉めできる
10. **## 参考リンク** — 公式 memory / env-vars ドキュメント。
    ※本文で著者自身の repo・ツールに言及しない構成なので「関連リンク（著者ハブ）」節は立てない
    （プロジェクト CLAUDE.md の必須条件は「本文で自リポに言及した記事」）

### タイトル候補（`/seo-optimizer` → `headline-craft` で確定。50 字以内）

- A: グローバル CLAUDE.md を読ませない設定 — CLAUDE_CONFIG_DIR では消えません
- B: Claude Code で用途別ハーネスを分ける — claudeMdExcludes の使い方
- C: Claude Code のグローバル CLAUDE.md と rules を特定環境だけ除外する

---

## 執筆時に守る規律（この記事固有）

- **公開 repo なので実パスを出さない** — 台帳の実測値は `~/` を含む。
  設定例・hook の JSON 例ともに `/Users/you/` 系に匿名化する
- **未検証を断定しない**（台帳の ⚠ 行）:
  - `CLAUDE_CONFIG_DIR` が公式 env-vars ページに未記載（C21）→ 執筆時に実際にページを確認し、
    確認できなければその主張は**書かない**
  - `claudeMdExcludes` で `~` が展開されるかは未検証 → 「絶対パスで書きます」とだけ書く
  - `/compact` 後の再注入時に効くかは未検証 → 触れない
- **数値は live 再実測**（`zenn-editorial-judgment` の実測主義）— バージョン番号、16 / 17 / 1 の
  ファイル数は台帳から引き写さず、執筆時にコマンドで取り直す
- **過程・内部語彙を持ち込まない** — Ralph / codex レビュー / worktree 案 / 台帳の finding 番号は
  本文に出さない（軸が著者側に寄る検出器）
- **1 段落 1 ビート**。5 行超・3 ビート以上の段落を作らない

## 主要な参照ファイル

| 用途 | パス |
|---|---|
| 証拠台帳（Claims Register / Before-After / コマンド例） | `drafts/article-context_claude-code-harness-isolation_20260802.md` |
| 会話の生ログ（判断記録の一次資料） | `drafts/evidence_claude-code-harness-isolation_20260802/session-d73fb350-full.md` |
| 執筆の声・構成テンプレ | `.claude/skills/zenn-practical-writing/SKILL.md` |
| frontmatter / 記法 | `.claude/skills/zenn-format/SKILL.md` |
| 出力先（新規） | `articles/claude-code-claudemd-excludes.md` |

---

## 実行順（writing chain）

1. **執筆** — メインループが `zenn-practical-writing` に従って直接書く（サブエージェントに委譲しない）
2. **自己プリフライト** — 論点数 4 以下 / AI-slop / 用語初出 / 段落密度 / 10% 編集パス
3. **レビュー 4 本を並列起動** — `editor` + `fact-checker` + `zenn-clarity-reviewer` +
   codex-review（公開記事の cross-model、prompt-driven モード）
   - 停止条件: MAJOR ISSUES / ❌ INACCURATE / clarity FAIL のいずれかが出たら修正して再レビュー
4. **タイトル確定** — `/seo-optimizer`（英訳より前に確定させる）
5. **人間ゲート（意図確認）** — 記事は本文をそのまま提示して承認を得る。承認前に `published` は立てない
6. **英訳・予約** — 承認後に `devto-translator` で `articles-en/` を作り、`schedule.json` に JP/EN
   両方を登録。**日程は今回未定**（ユーザー指示）。決まった時点で `published_at` と `--at` を入れる
7. **push を促す** — 未 push だと Zenn の予約も Dev.to のクロスポストも動かない（CLAUDE.md の CRITICAL 項）

## 検証

| 何を | どうやって |
|---|---|
| frontmatter が妥当か | `npm run validate` |
| 表示崩れがないか | `npm run preview` |
| 受け入れ基準 | `quality-gate` skill のチェックリスト（第一画面・前提列挙・図/表 ≥1・コピペで動くコード・ですます統一・見出しの専門用語） |
| 機密混入 | 記事全文を `~` で grep して 0 件 |
| 事実主張 | `fact-checker` の verdict が ACCURATE 系（公式ドキュメント 2 本と Before/After 数値） |
| 初見読者の明瞭性 | `zenn-clarity-reviewer` が PASS（FAIL は公開ブロック） |
