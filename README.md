# zenn-content

Claude Code を中心とした開発体験の記録。技術記事の執筆から、クロスポスト、品質管理まで、Claude Code との協業で運用しています。

## Published Articles

### Claude Code Series
- [Cursor から Zed + Claude Code に移行した話](https://zenn.dev/shimo4228/articles/cursor-to-zed-migration)
- [Claude Code のコンテキスト設定を全部棚卸しした](https://zenn.dev/shimo4228/articles/claude-code-context-audit)
- [Claude Code の Skill に出自を付けて管理する](https://zenn.dev/shimo4228/articles/claude-code-skill-origin-tracking)
- [Claude Code が自分のスキルを自分で書いた日](https://zenn.dev/shimo4228/articles/claude-code-self-generation)
- [Claude Code で Zenn 執筆環境を仕組み化した話](https://zenn.dev/shimo4228/articles/claude-code-zenn-writing-env)

### Everything Claude Code (ECC) Journey
- [Part 1: 初心者が ECC で本格開発を始めた10日間](https://zenn.dev/shimo4228/articles/ecc-journey-part1)
- [Part 2: スキル大量導入の混乱と棚卸し](https://zenn.dev/shimo4228/articles/ecc-journey-part2)
- [Part 3: Rules と Agents で開発ワークフローを変えた](https://zenn.dev/shimo4228/articles/ecc-journey-part3)

### Daily Research & Others
- [Python コード0行で AI リサーチ自動化パイプラインを作った](https://zenn.dev/shimo4228/articles/daily-research-automation)
- [Termius + iPhone で Claude Code をどこでも使う](https://zenn.dev/shimo4228/articles/termius-iphone-claude-code)
- [Claude Code で Obsidian Vault を整理した](https://zenn.dev/shimo4228/articles/claude-code-obsidian-vault-organization)

## Cross-Posting

記事は日本語（Zenn + Qiita）と英訳（Dev.to + Hashnode）でクロスポストしています。

- `articles/` — 日本語原稿
- `articles-en/` — 英訳
- `scripts/publish.py` — クロスポスト CLI
- `scripts/schedule.json` — 投稿スケジュール管理

## Tech Stack

- **Zenn CLI** — 記事管理・プレビュー
- **textlint** + preset-ja-technical-writing + no-dead-link + prh — 日本語校正
- **markdownlint-cli2** — Markdown 構文チェック
- **husky** + lint-staged — pre-commit フック（textlint + markdownlint）
- **Claude Code** — 執筆・レビュー・翻訳・クロスポスト

## Claude Code Integration

```
.claude/
├── agents/editor.md          # 辛口レビューエージェント
└── skills/
    ├── zenn-writer/           # 記事執筆ガイド
    ├── publish-article/       # 公開・クロスポスト手順
    ├── schedule-publish/      # スケジュール管理
    ├── translate-article/     # 英訳
    ├── seo-optimizer/         # SEO 最適化
    ├── content-research-writer/ # リサーチ執筆
    └── chatlog-to-article/    # チャットログ→記事変換
```

## Quick Start

```bash
npm install        # 依存インストール
npm run preview    # ローカルプレビュー
npm run lint       # textlint + markdownlint
npm run new:article # 新規記事作成
```

## Directory Structure

```
zenn-content/
├── articles/          # 日本語記事
├── articles-en/       # 英訳記事
├── books/             # Zenn books
├── images/            # 記事用画像
├── scripts/
│   ├── publish.py     # クロスポスト CLI
│   ├── schedule.json  # 投稿スケジュール
│   └── .env           # API トークン（gitignore）
├── .claude/
│   ├── agents/        # エディターエージェント
│   └── skills/        # プロジェクトスキル（8個）
└── .github/
    └── workflows/     # CI（lint）
```

## License

Articles are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
