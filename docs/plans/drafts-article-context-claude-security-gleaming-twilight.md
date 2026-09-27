# 記事執筆プラン: 公式 claude-security で ~/.claude を自己スキャンする

## Context

なぜこの記事を書くか。

Claude Code を長く使う人は hooks・permissions・skills・agents を自作で積み上げます。ところがその設定一式そのものが攻撃面になっていないかを確認する手段がありません。lint も型検査もかからず、hooks に至っては `permissions.allow` の対象外（tool call ではないため確認プロンプトすら出ない）です。

筆者は 2026-07-25 に Anthropic 公式の `claude-security` プラグイン v0.10.0 で `~/.claude` 全体を自己スキャンし、20 findings（HIGH 5 / MEDIUM 15）を得て 7 コミットで修正しました。素材は証拠台帳 `drafts/article-context_claude-security-self-scan_2026-07-26.md`（44 クレーム、tier 付き）に集約済みです。

**読者の問題文**（zenn-practical-writing Phase 1）:
> Claude Code の設定（hooks・permissions・skills）を育ててきたが、それ自体が攻撃面になっていないか確認する手段がない読者が、公式 claude-security プラグインで自己スキャンを回し、結果の読み方と修正の優先順位付けまでできるようになる。

**成果物**: `articles/claude-security-harness-self-scan.md`（JP、`published: false`）。公開日は未定のため EN 翻訳・`schedule.json` 登録・push は本タスクの範囲外。

---

## 執筆前に確定した事実訂正（重要）

台帳の **C11 は誤り**。執筆時はこの訂正版を使う。

| | 台帳 C11 の記述 | プラグイン原文の実際 |
|---|---|---|
| 主張 | ドキュメントは `.claude/` 設定を trust model の前提で**検査対象外**としている | そのような記述は**存在しない** |
| 実際の記述 | — | `SECURITY.md:15` — スキャン対象リポジトリの `.claude/` 設定と hooks は**セッションに読み込まれて効く**（プラグインは分離層を持たない）。「監査しない」ではなく「実行環境として信頼する」 |
| さらに逆 | — | `agents/scan-researcher.md:52` — `.claude/` 配下は**読む対象**であり、そこにある指示文は `prompt-injection` finding として報告せよ |

**差し替える軸**: 「ドキュメントの前提が覆った」ではなく、**レポート自身の Coverage 節**（`CLAUDE-SECURITY-RESULTS.md:9`）が一次ソース。`~/.claude` は 11 コンポーネント（`hooks` / `scripts` / `scheduled-tasks` / `skills-executable-scripts` / `skills-instructions` / `agents` / `rules` / `templates` / `docs` / `notes-and-metrics` / `tests`）に分割され、`rules` や `skills-instructions` のような**自然言語の指示ファイルまで監査対象コンポーネントになった**。これは検証可能で、かつ主張として強い。

**もう 1 件の ⚠ 対応**: 「11.2M トークン」（C6）は会話上の報告値で再集計と一致しないため**記事に書かない**。コストは検証可能な形（サブエージェント 189 体 / 約 2 時間 / effort=medium）と、プラグイン自身の固定文言（"may use a significant number of tokens"）で表現する。

---

## Frontmatter

```yaml
---
title: "Claude Code の設定こそ攻撃面——~/.claude を公式プラグインで自己スキャンする"
emoji: "🔍"
type: "tech"
topics: ["claudecode", "anthropic", "security", "開発環境", "llm"]
published: false
---
```

- title 44 文字（上限 50 以内）。代替案: 「~/.claude を公式 claude-security でスキャンしたら 20 件出た——結果の読み方と直す順番」（48 文字）
- slug: `claude-security-harness-self-scan`

---

## 構成（独立論点 4 個 = 上限ちょうど）

重心は 手順 40% / findings の読み方 30% / 修正判断 30%。

### 冒頭（第一画面）

- `> **この記事でわかること**:` 1 行
- 読者の壁 3 個の箇条書き（hooks に permissions が効かない自覚がない / 設定に lint がかからない / スキャンしても結果の優先順位を付けられない）
- 実測の要約 1 段落（20 findings、根本原因 8 個、うち 2 件が任意コード実行）— 体験談は軸にせず「解決が実在する証拠」として圧縮

### 前提

Claude Code 2.1.220 / plugin v0.10.0 / python3 3.9+ / git checkout / auto mode 推奨（プラグインの固定推奨文言）

### 論点 1: 回し方（手順）

- `/plugin install claude-security@claude-plugins-official` → `/reload-plugins` → `/claude-security`
- **3 ジョブの表**（Scan codebase / Scan changes / Suggest patches）と、それぞれの起動引数
- **effort 4 段階の表**（low / medium / high / max）— 何が増えるか。パネルは全 tier で 3 票固定という設計を明記
- 起動時の固定確認プロンプトと、事前に承諾を渡して直行する文言（`I understand it may take a while and use a significant number of tokens`）
- `~/.claude` 自体を scanRoot にする実際の引数（台帳「コード・コマンド例」の Workflow args）
- パイプライン 6 phase を **Mermaid 図** で 1 枚（Inventory → Threat model → Research → Sweep → Panel →（max のみ）Adversarial）。原文の phase 名を使う
- 実測の shape: 11 components → 42 researchers → 45 候補 × 3 lens = 135 票、合計 189 サブエージェント / 約 2 時間

### 論点 2: 結果の読み方

- **件数をそのまま信じない** — レポート自身が「20 は 20 個の欠陥ではない、根本原因は 8 個」と書いている。クラスタ表（F5/F8/F17 = allowlist / F9/F11/F14 = 1 個の正規表現アンカー / F6/F10/F12–F15 = ガード族）
- **3-lens panel の意味** — REACHABILITY / IMPACT / DEFENSES の 3 票、2-of-3 で keep、集計はモデル外のコードが行う。既定は FALSE_POSITIVE
- **レポートが自分から開示する限界を読む** — 38 候補サイトが未レビュー / 除外 2 領域（vendored venv・`__pycache__`）/ **コードを一切実行していない**（読解のみ）
- **機械可読側を使う** — `RESULTS.jsonl` を 1 行の Python で severity 集計・file 分布に落とすコード（コピペで動く）
- ここで Coverage 節の 11 components を提示し、`rules` / `skills-instructions` のような自然言語ファイルまでコンポーネント化された事実を示す（= 訂正後の軸）

### 論点 3: 直す順番（優先順位付け）

判定表を置く。列: 「先に直す条件」「理由」「実例」。

1. **単独で任意コード実行が成立するもの** — F1（`.sh` 編集をトリガーに `tests/*.bats` を無条件実行。hook は tool call でないので `permissions.allow` が効かず、プロンプトも出ない）/ F2（LLM 生成コマンドの subprocess 実行）
2. **1 個のアンカーに帰着するクラスタ** — 8 findings が「呼び出し文字列を検査し、その呼び出しが実際にどのファイルへ到達するかを計算していなかった」1 点に集約。レポート自身が F13 を "single highest-leverage repair" と呼んでいる
3. **信頼の向きが逆になっている定義** — F20（`agents/fact-checker.md` が生トランスクリプトを信頼順位 1 位に置いていた。WebFetch のページ本文が verbatim 保存される以上、ファイルとしては改竄困難でも中身は信頼できない）
4. **ドキュメントと実態の不一致** — F16（README が「未配線」と書いた無人ジョブが実際は launchctl 登録済みで毎週稼働していた）

### 論点 4: 修正の設計判断（3 つに絞る）

- **deny を足すのでなく allow から外す** — deny は正当な実行まで恒久的に不可能にする。allow から外せば auto mode では確認プロンプトに戻るので、判断をユーザーに返せる。実測: `permissions.allow` 109 → 107、インタプリタ wildcard 8 件除去 → スクリプト単位 6 件を追加（before/after の diff を提示）
- **判定を「コマンド位置」にアンカーする** — 部分文字列一致版の deny 規則は、**その形を説明した自分の導入コミットメッセージで発火して自分をブロックした**。検出対象（実行される形）とそれを記述しているテキストを区別する必要がある。バックティックは区別不能として意図的に除外し、残存する穴としてコメントに明記
- **自分のゲートに止められてもバイパスしない** — secret gate が自分の修正コミットを 3 度止め、いずれも fixture の書き方を直して解消した。バイパスの常用がゲートを空洞化させる

### 落とし穴（`:::details` で progressive disclosure）

- **並行セッションの staged 変更が吸収される** — git の index はセッション間で 1 つ。承認待ちの間 index は安全な待機場所ではない。2 日連続で実証（`git rm` も実行時点で staging される）。対処: 承認待ちで止まる直前に stage しない / commit 後に `git show --stat` で照合
- **スキャナ自身がハーネスのガードを踏んだ** — panel voter の 1 体が Claude Code バイナリを permission-bypass シンボルで検索し、auto-mode-bypass 分類器を発火させた。当該候補は 0-3 で却下されたが、レポートは埋めずに記載している
- **dirty tree だと patch job が拒否される** — `revision.dirty: true` のレポートからは patch を作らせない設計

### まとめ

- 次にできること: `/claude-security` の Scan changes を差分レビューに使う（whole-repo scan と違い数分で返る）
- 未着手として正直に書く: 修正後の再スキャンは未実施 / Bash 側ガードは原理的に不完全なまま（恒久解は permission 層の deny）

### 関連リンク

- `github.com/anthropics/claude-plugins-official`（プラグイン本体）
- **`github.com/shimo4228`（著者 GitHub ハブ。プロジェクト CLAUDE.md により必須）**
- 本文で自作ハーネス repo に言及する場合はその URL

---

## 執筆で守る規約（zenn-practical-writing / project overlay）

- **ですます調で統一**（だ/である と混在させない）
- コードは file path + 言語タグ + コピペで動く自己完結
- 図/表 ≥1 → Mermaid のパイプライン図 + effort 表 + クラスタ表 + 優先順位判定表
- 見出しは outcome を述べる。前方参照なし。1 節 1 論点
- 英語名詞句を 2 つ以上そのまま繋げない（false positive → 偽陽性、trust model → 信頼モデル 等。ただし hook / permissions / findings のような定着語は英語のまま）
- 造語を作らない。専門用語は初出で平易な言い換えを併記
- 制作過程のメタ話（どうレビューを回したか等）は本文に置かない
- AI slop 禁止リスト（`writing-ecosystem`）を適用
- 段落密度: 5 行超 / 3 ビート以上 / 比較の地の文埋め込みを全段落チェック

**セキュリティ規律**: 悪用手順を逐語で書かない。攻撃の「形」は概念レベル（「取得物をインタプリタにパイプする形」）に留め、動く exploit を再現しない。ファイルパスから個人名を伏せる（`/Users/username/` は書かない）。

---

## 手順

1. 記事本文を `articles/claude-security-harness-self-scan.md` に執筆（サブエージェントに委譲せず本体が直接書く）
2. 自己プリフライト（zenn-practical-writing Phase 3 のチェックリスト 6 項目）
3. レビュー 3 本を**並列**起動 — `editor` / `fact-checker` / `zenn-clarity-reviewer`
4. 指摘を反映。`zenn-clarity-reviewer` が FAIL なら再改稿（FAIL は公開ブロック）
5. `npm run validate` で frontmatter 検証
6. 意図の要約をユーザーに提示してからコミット（公開はしないので push 判断は別途）

**本タスクの範囲外**（公開日が決まってから実施）: EN 翻訳（`articles-en/`）、`scripts/schedule.json` 登録、Dev.to 予約、`published: true` 化、カバー画像

---

## 検証

- `npm run validate` — Zenn frontmatter が通ること
- `npm run preview` — Zenn プレビューで表示崩れ・Mermaid 描画を確認
- 記事内の全コマンドを実際に実行して出力が記事の記述と一致することを確認（特に `RESULTS.jsonl` の集計スニペット）
- `fact-checker` の verdict に INACCURATE が無いこと。特に検証させる主張: プラグインのバージョンと作者 / 11 コンポーネントの内訳 / 20 findings の内訳 / 189 サブエージェントの算術（1 + 11 + 42 + 135）/ `permissions.allow` の 109 → 107
- `zenn-clarity-reviewer` の verdict が PASS
- 記事本文に `/Users/` から始まる実パスが含まれないこと（`grep -n "/Users/" articles/claude-security-harness-self-scan.md` が空）
