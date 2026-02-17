# ショート記事 執筆計画

作成日: 2026-02-17
元リサーチ: [research.md](./research.md)
元アクションプラン: [ACTION-PLAN.md](./ACTION-PLAN.md)

## 方針

- 1,000字前後のピンポイント解決型記事
- 全て一次情報（自分の実体験）ベース
- タイトル先頭に「Claude Code」を配置（SEO）
- topics に `claudecode` を必ず含める

## 記事一覧と進捗

| # | 優先度 | slug | タイトル案 | 状態 | 素材ソース |
|---|--------|------|-----------|------|-----------|
| A1 | 1 | claude-code-auto-memory | Claude Code の auto memory でセッションを跨いで学習を蓄積する | **公開済** | MEMORY.md 実物（6プロジェクト分） |
| B1 | 2 | claude-code-claudemd-hierarchy | Claude Code の CLAUDE.md 階層構造でハマった話 — user/workspace/project の正しい使い分け | 未着手 | ecc-journey-part1（配置ミス10日間）、MyAI_Lab MEMORY.md |
| B2 | 3 | claude-code-zenn-lint-hooks | Claude Code × Zenn 執筆に textlint + markdownlint の hooks を設定する | 未着手 | .textlintrc.json, .markdownlint-cli2.jsonc, package.json, prh.yml |
| A2 | 4 | claude-code-crosspost-cli | Claude Code で Zenn→Qiita→Dev.to クロスポストを1コマンドで | 未着手 | scripts/publish.py（630行、Qiita/Dev.to/Hashnode対応） |
| B3 | 5 | prh-nodejs20-regex-error | prh と Node.js 20 で正規表現エラーが出たときの対処法 | 未着手 | MEMORY.md の Key Gotchas セクション |
| A3 | 6 | claude-code-japanese-mcp | Claude Code で日本語テキスト分析MCPサーバーを作った — kuromoji.js | 未着手 | ~/.claude.json mcpServers設定、JapaneseTextAnalyzer MCP |
| C1 | 7 | claude-code-skill-cleanup | Claude Code の learned skills が溜まりすぎた時の棚卸し手順 | 未着手 | ecc-journey-part3、pdf2anki MEMORY.md（Skill Stocktaking Log） |
| C2 | 8 | claude-code-zed-setup | Claude Code を Zed で使う最適設定 — ビルトインAI を切る理由 | 未着手 | cursor-to-zed-migration 記事 |
| C3 | 9 | claude-code-multi-llm | Claude Code でマルチLLM活用 — Gemini/ChatGPT/NotebookLM の使い分け | 未着手 | ecc-journey-part1（マルチLLM活用戦略セクション） |

## 各記事の執筆メモ

### A1: auto memory（完了）
- `articles/claude-code-auto-memory.md` に作成済み
- MEMORY.md 実物、6プロジェクトの独立記憶、CLAUDE.mdとの違い

### B1: CLAUDE.md 階層
- 核心: user(`~/.claude/`) / workspace(`MyAI_Lab/.claude/`) / project(`.claude/`) の3層
- 一次情報: 10日間 MyAI_Lab/.claude/ に全部入れてた配置ミス → 修正
- ecc-journey-part1 の「手動ダウンロードの落とし穴」「修正フェーズ」セクションから切り出し
- 差別化: 既存記事は「正しい書き方」ばかり。失敗→修正の体験談

### B2: Zenn lint hooks
- 核心: husky + lint-staged で pre-commit 時に textlint + markdownlint を自動実行
- 設定ファイル実物: package.json の lint-staged, .textlintrc.json, .markdownlint-cli2.jsonc, prh.yml
- ゴッチャ2つ:
  - markdownlint の config に glob を書くと lint-staged と競合（全ファイルlintされる）
  - Zenn の :::message/:::details の前後に空行がないと MD032

### A2: クロスポスト CLI
- 核心: `python scripts/publish.py articles/xxx.md --platform qiita` で1コマンド
- 変換処理: :::message→blockquote, :::details→HTML, /images/→GitHub raw URL
- 3プラットフォーム対応: Qiita, Dev.to, Hashnode
- `--update auto` でタイトル検索→既存記事更新
- `--canonical-url` でSEO重複回避
- 英語記事ガード: articles/ から devto/hashnode へ投稿しようとすると警告

### B3: prh + Node.js 20 regex
- 核心: Node.js 20+ で unicode regex がデフォルト有効。`\-` がリテラルハイフンとして無効に
- 症状: prh.yml にハイフン含むパターンを書くと textlint が crash
- 解決: ハイフン含むパターンを prh.yml に書かない。代替として正確なパターンを使う
- 超ピンポイント記事。エラーメッセージで検索してたどり着く人向け

### A3: 日本語MCP
- 核心: kuromoji.js ベースの形態素解析MCPサーバー
- 機能: count_chars, count_words, analyze_text（可読性定量評価）
- ~/.claude.json の mcpServers に設定
- Zenn記事執筆で「この記事は何文字？」「読みやすさスコアは？」が聞ける

### C1: skill 棚卸し
- ecc-journey-part3 から切り出し
- 16件→48件の膨張、3回の棚卸し
- 棚卸しトリガー: 各ディレクトリ10ファイル到達時
- 退役基準: 3ヶ月間参照なし
- 3層構造: global / project / learned
- 無効化: disable-model-invocation: true、commands-archive/ への退避

### C2: Zed 設定
- cursor-to-zed-migration から切り出し
- 核心: コードは書かない。エディタは「読む」だけ → 軽さ重視
- ビルトインAI を切る設定
- Claude Code との役割分担

### C3: マルチLLM
- ecc-journey-part1 から切り出し
- 4段階: Claude Code → Gemini/Claude通常 → 例え話で説明 → ディープリサーチ
- 使い分け: Claude Code=実践、Gemini=概念説明、ChatGPT=ベストプラクティス、NotebookLM=情報統合

## 再開時の手順

1. このファイルを読んで進捗を確認
2. 未着手の記事を順番に書く
3. 素材ソースのファイルを読んで一次情報を取得
4. `articles/{slug}.md` に Zenn フォーマットで作成
5. タスクリストを更新
