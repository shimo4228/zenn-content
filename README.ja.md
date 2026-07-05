Language: [English](README.md) | 日本語

# zenn-content

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/shimo4228/zenn-content) [![GitMCP](https://img.shields.io/endpoint?url=https://gitmcp.io/badge/shimo4228/zenn-content)](https://gitmcp.io/shimo4228/zenn-content)

AI エージェント設計・コーディングエージェント運用・AI 経由拡散時代の著者性を扱う日英バイリンガルのエッセイコーパス — five-line research ecosystem のエッセイ面。CC0 で公開し、Software Heritage SWHID による intrinsic な priority claim を持つ（[CITATION.cff](CITATION.cff) 参照）。執筆・レビュー・翻訳・クロスポストまで Claude Code との協業で運用しています。

## Published Articles

最新の一覧は `npx zenn list:articles` で確認できます。

### AI Agent Design
- [推論でもツールでもない — AIエージェントの本質は「記憶」ではないか](https://zenn.dev/shimo4228/articles/agent-essence-is-memory)
- [自律エージェントの自由と制約 — 自己修正・信頼境界・ゲーム性の設計](https://zenn.dev/shimo4228/articles/agent-freedom-and-constraints)
- [ゲーム開発のメモリ管理をAIエージェントの記憶蒸留に移植した](https://zenn.dev/shimo4228/articles/agent-memory-game-dev-distillation)
- [コーディングエージェントの知識をどこに置き、どう守らせるか](https://zenn.dev/shimo4228/articles/coding-agent-memory-architecture)
- [自律エージェントにオーケストレーション層は本当に必要か](https://zenn.dev/shimo4228/articles/symbiotic-agent-architecture)
- [Moltbookエージェント進化記 — 自然言語で制御し、記憶で学び、失敗しても壊れない設計](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy)
- [Moltbookエージェント構築記 — Claude Codeとセキュリティファースト開発](https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build)

### ReAct エージェント
- [ReAct エージェントが本当に必要な業務はどれか](https://zenn.dev/shimo4228/articles/react-agent-business-quadrant)
- [(3) LLM ワークフロー象限が語彙から脱落している — 続・ReAct エージェントの適用域](https://zenn.dev/shimo4228/articles/react-agent-business-quadrant-2)
- [本番運用に ReAct は必要か — 設計フェーズと運用フェーズを分ける](https://zenn.dev/shimo4228/articles/react-agent-business-quadrant-3)
- [ワークフロー象限と ReAct 象限の間のグラデーション — 設計フェーズと運用フェーズがスキル設計を分ける](https://zenn.dev/shimo4228/articles/react-agent-business-quadrant-4)

### AI Governance シリーズ
- [登れる壁に看板を立てても意味がない — AIエージェントに必要なのはガードレールではなくアカウンタビリティだ](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall)
- [事故のあとで因果を辿れるか](https://zenn.dev/shimo4228/articles/agent-causal-traceability-org-adoption)
- [AIエージェントのブラックボックスは二層ある — 技術の限界とビジネスの都合](https://zenn.dev/shimo4228/articles/agent-blackbox-capitalism-timescale)
- [AIによって外部化された責任はどこへ行くのか](https://substack.com/@shimo4228/p-199017153)（Substack）

### Claude Code シリーズ
- [CursorからZedに乗り換えた — ビルトインAIを切って「黒い画面」に振り切った設定と理由](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration)
- [Claude Code の設定ファイルを全棚卸しして分かった5つのこと](https://zenn.dev/shimo4228/articles/claude-code-context-audit)
- [Claude Code の真価はコード生成ではない](https://zenn.dev/shimo4228/articles/claude-code-context-orchestration)
- [デフォルトのまま使うな ── Claude Code で本当に効いた設定10選](https://zenn.dev/shimo4228/articles/claude-code-effective-settings-10)
- [毎回コンテキストを失う Claude Code に記憶を埋め込んだ](https://zenn.dev/shimo4228/articles/claude-code-persistent-memory)
- [Claude Code スキルの出自管理 ── origin メタデータで79個を分類した](https://zenn.dev/shimo4228/articles/claude-code-skill-origin-tracking)
- [Claude Codeに「お前自身がLLMだろ」と言った日 — 397問のデータ生成で学んだこと](https://zenn.dev/shimo4228/articles/claude-code-self-generation)
- [Claude Codeで育てたZenn執筆環境 ── lint28件からエージェントレビューまで](https://zenn.dev/shimo4228/articles/claude-code-zenn-writing-env)
- [AI の苦手な仕事をスクリプトに逃がす — スキル棚卸しコマンドの設計・実装・公開の全記録](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey)

### ECC (Everything Claude Code) Journey
- [Everything Claude Codeで初めて本格的な開発を始めた初心者の10日間](https://zenn.dev/shimo4228/articles/ecc-journey-part1)
- [LLM の出力は信用するな — Claude API で PDF→Anki 自動生成 CLI を作って学んだ 6 つの防御策](https://zenn.dev/shimo4228/articles/ecc-journey-part2)
- [Claude Code スキルが膨れ続けた 15 日間 — 3 回の棚卸しで学んだこと](https://zenn.dev/shimo4228/articles/ecc-journey-part3)
- [個人スキルを5万人に届ける最短経路が見つかった](https://zenn.dev/shimo4228/articles/ecc-marketplace-contribution)

### AI Research & Experiments
- [Prompt-Based Alignmentには天井がある — 囚人のジレンマ3モデル実証](https://zenn.dev/shimo4228/articles/contemplative-alignment-benchmark)
- [エピソードログから倫理が生まれるまで — Contemplative Agent 17日間の設計記録](https://zenn.dev/shimo4228/articles/contemplative-agent-journey)
- [理論が分からない論文をブラウザで動かしてしまった ── 能動的推論 × Claude Code](https://zenn.dev/shimo4228/articles/active-inference-viz-dev-story)
- [しつけの前と後 ── Baseモデルを手元で動かしたら「こんにちは」がアニメレビューになった](https://zenn.dev/shimo4228/articles/base-model-experience)
- [Geminiに自社Deep Researchを語らせたら、半分が自己弁護だった](https://zenn.dev/shimo4228/articles/token-economics-ai-orchestration)

### LLM Engineering & Tools
- [LLMアプリの正体は「mdとコードのサンドイッチ」だった](https://zenn.dev/shimo4228/articles/llm-app-sandwich-architecture)
- [MCPツールの Install and Hope 問題](https://zenn.dev/shimo4228/articles/mcp-install-and-hope-problem)
- [エージェントの記憶が壊れた — 9Bモデルと格闘した1日](https://zenn.dev/shimo4228/articles/few-shot-for-small-models)

### Multi-Model & Workflow
- [Claude Code × Kimi K2.5 ハイブリッド環境を構築した](https://zenn.dev/shimo4228/articles/claude-kimi-hybrid-setup)
- [ClaudeのプランをKimiに実行させたら丸投げだとキレられた](https://zenn.dev/shimo4228/articles/kimi-delegation-failure-lessons)
- [最強モデルで司令塔を組んだら9倍遅くなった ── なぜマルチエージェントを棄却したか](https://zenn.dev/shimo4228/articles/daily-research-agent-team)
- [Claudeの自信作をKimiが4件潰した ── AIピアレビュー実践記](https://zenn.dev/shimo4228/articles/ai-peer-review-methodology)

### Build in Public
- [AI生成記事の実態 — 20回の対話で核心が変わった2時間](https://zenn.dev/shimo4228/articles/ai-article-writing-process)
- [Claude Code で毎朝AIリサーチが届く自動化を作った — Pythonコード0行](https://zenn.dev/shimo4228/articles/daily-research-automation)
- [2日間壊し続けたAIパイプライン ── Claudeの認知バイアスと人間の介入](https://zenn.dev/shimo4228/articles/daily-research-postmortem)
- [3,674ファイルのObsidian地獄をClaude Codeに1日で片付けさせた](https://zenn.dev/shimo4228/articles/claude-code-obsidian-vault-organization)
- [Obsidian公式CLIが来た——もうVaultを裏口から触らなくていい](https://zenn.dev/shimo4228/articles/obsidian-cli-claude-code-vault-management)
- [Claude Code をiPhoneから操作する方法 — Termius + Tailscale + tmux 環境構築ガイド](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)
- [Claude Codeにシミュレータを渡したら自分でタップしてスクショで検証し始めた](https://zenn.dev/shimo4228/articles/xcodebuildmcp-ios-verification)
- [AI 執筆チームの有機的成長と Content Integrity](https://zenn.dev/shimo4228/articles/organic-growth-content-integrity)
- [Zed を Claude Code の「観測窓」として構築する — IBM Plex で統一する日本語タイポグラフィ](https://zenn.dev/shimo4228/articles/zed-observation-window-japanese-typography)

## クロスポスト

記事は日本語（Zenn）と英訳（Dev.to）でクロスポストしています。

- `articles/` — 日本語原稿（Zenn は frontmatter `published_at` で native 予約投稿）
- `articles-en/` — 英訳
- `substack/` — Substack エッセイのミラー（Zenn 規約の適用外）
- `scripts/devto_crosspost.py` — 記事ごとの Dev.to クロスポスター。`schedule <slug> --at "<日時>"` が指定日時に発火する one-shot launchd ジョブを仕込み、投稿後に自己削除
- `scripts/schedule.json` — 投稿済み URL 台帳（各 EN 記事の Dev.to URL を記録。投稿日時は `--at` 引数で渡し、ここには保存しない）

## 技術スタック

- **Zenn CLI** — 記事管理・プレビュー
- **Zenn CLI** `zenn list:articles` — frontmatter 検証（`npm run validate`、CI でも実行）
- **Python 3.13** + httpx + python-frontmatter — Dev.to クロスポスト
- **Claude Code** — 執筆・レビュー・翻訳・クロスポスト

## Claude Code 連携

```
.claude/
├── agents/                    # Zenn 固有エージェント（editor/essay-reviewer/fact-checker は global へ移行）
│   └── devto-translator.md    # JP→EN翻訳 + Dev.to投稿
│                              # 注: 記事執筆はサブエージェントに委譲しない
│                              # （オーケストレーター本体が zenn-practical-writing に従って直接執筆）
├── refs/                      # 共有リファレンス
│   ├── translation-rules.md
│   └── schedule-schema.md
├── rules/
│   ├── content-integrity.md   # Content Integrity 原則
│   └── zenn-writing.md        # global writing-ecosystem skill の Zenn overlay
└── skills/
    ├── writing-team/           # オーケストレーター（PM）
    ├── zenn-practical-writing/ # 全 Zenn/Dev.to 記事の既定の声（実用軸。tech/idea で分けない）
    ├── zenn-idea-voice/        # 任意の personality flavor（毒humor / 刃牙）。type 非依存
    ├── zenn-writer/            # 声のルーター（互換のため path 維持。全て zenn-practical-writing へ）
    ├── zenn-format/            # Zenn フォーマット・frontmatter（正本）
    ├── publish-article/        # 公開・クロスポスト手順
    ├── schedule-publish/       # スケジュール管理
    ├── seo-optimizer/          # SEO 最適化（タイトル・タグ・emoji のみ）
    ├── ideation/               # テーマ検討・アイデア出し
    ├── series-checker/         # シリーズ整合性チェック
    └── quality-gate/           # 統一品質基準
```

## クイックスタート

```bash
npm install         # 依存インストール
npm run preview     # ローカルプレビュー
npm run validate    # Zenn frontmatter 検証
npm run new:article # 新規記事作成
```

## ディレクトリ構成

```
zenn-content/
├── articles/          # 日本語記事
├── articles-en/       # 英訳記事
├── substack/          # Substack エッセイのミラー（Zenn 規約の適用外）
├── books/             # Zenn books
├── images/            # 記事用画像・カバー画像
├── scripts/
│   ├── devto_crosspost.py    # 記事ごとの Dev.to クロスポスター（one-shot launchd）
│   ├── schedule.json         # 記事ごとの Dev.to 投稿日時
│   └── tests/                # pytest テスト（56テスト）
├── .claude/
│   ├── agents/        # Zenn 固有エージェント（1個: devto-translator）
│   ├── skills/        # プロジェクトスキル（11個 + learned/）
│   ├── refs/          # 共有リファレンス
│   └── rules/         # プロジェクトルール
└── .github/
    └── workflows/     # CI（lint）
```

## リサーチエコシステム

このエッセイコーパスは、agent design と AI 媒介拡散下の著者性を扱う 5 つのリサーチラインからなるエコシステムの 1 surface である。ここにある公開済み・著者の声を持つエッセイ群が、そのエコシステムの人間可読なエッセイ surface にあたる。

- **エコシステム hub（5 ラインの索引）**: https://github.com/shimo4228/shimo4228
- **著者（ORCID）**: https://orcid.org/0009-0002-6168-4162
- **引用メタデータ**: [`CITATION.cff`](CITATION.cff) —— コーパスの intrinsic content-derived identifier（Software Heritage snapshot）を記録。エッセイ genre の priority-claim 機構

関連するアーカイブ済みリサーチライン（DOI）:

- Authorship Strategy — https://doi.org/10.5281/zenodo.20263316
- Agent Knowledge Cycle (AKC) — https://doi.org/10.5281/zenodo.19200726
- Contemplative Agent — https://doi.org/10.5281/zenodo.19212118
- Agent Attribution Practice (AAP) — https://doi.org/10.5281/zenodo.19652013
- Attention, Not Self — https://doi.org/10.5281/zenodo.20262112

## ライセンス

本リポジトリのすべてのコンテンツ（記事・翻訳・ツール）は [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)（パブリックドメイン献呈）で公開されています（`LICENSE` ファイル参照）。

このコーパスは LLM 媒介での到達を目的に公開されており、主たる audience は人間の閲覧ではなく機械の取り込みである。attribution は license 条項ではなく連邦識別子層（ORCID・エコシステム hub・sibling DOI・`CITATION.cff` の Software Heritage snapshot）が担う。ゆえにパブリックドメイン献呈が、コーパスが実際に対象とする audience の再利用摩擦を最小化する。
