---
title: "Claude Code の auto memory でセッションを跨いで学習を蓄積する"
emoji: "🧠"
type: "tech"
topics: ["claudecode", "ai", "開発環境", "生産性"]
published: true
---

## auto memory とは

Claude Code にはセッション間で情報を持ち越す **auto memory** 機能があります。プロジェクトごとに `~/.claude/projects/{project-hash}/memory/` へファイルが自動生成され、次回セッション開始時にシステムプロンプトとして読み込まれます。

```text
~/.claude/projects/
└── -Users-me-MyProject/
    └── memory/
        └── MEMORY.md   ← 毎セッション自動読み込み
```

## 何が保存されるか

Claude Code が開発中に学んだことを `MEMORY.md` に蓄積します。私のプロジェクトでは以下が記録されています。

```markdown
# Project Memory: zenn-content

## Zenn Content Toolchain
- textlint + preset-ja-technical-writing + no-dead-link + prh
- markdownlint-cli2 with Zenn-specific config
- husky + lint-staged for pre-commit hooks

## Key Gotchas
- prh + Node.js 20+: `\-` invalid in unicode regex
- markdownlint globs in config + lint-staged = lints ALL files
```

ツールチェインの構成、ハマりポイント、プロジェクト固有の意思決定が残ります。次のセッションでは「prh にハイフンのパターンを追加して」と言われても、自動的に回避してくれます。

## 実運用のコツ

**1. MEMORY.md は200行以内に抑える**

200行を超えるとシステムプロンプトで切り捨てられます。概要は `MEMORY.md` に、詳細は別ファイル（`debugging.md`, `patterns.md` 等）に分けて、MEMORY.md からリンクします。

**2. プロジェクトごとに異なる記憶を持てる**

auto memory はプロジェクトのパスごとにディレクトリが分かれます。

```text
~/.claude/projects/
├── -Users-me-zenn-content/memory/   ← Zenn執筆の知見
├── -Users-me-pdf2anki/memory/       ← Python CLI の知見
└── -Users-me-g-kentei-ios/memory/   ← Swift/iOS の知見
```

私は6プロジェクトを並行開発していますが、各プロジェクトが独立した記憶を持つため、コンテキストの混線が起きません。

**3. 手動で育てる**

auto memory は自動蓄積だけでなく、手動で編集できます。

```text
「この判断を memory に記録して」
「MEMORY.md から古い情報を削除して」
```

と指示すれば、Claude Code が `MEMORY.md` を更新します。重要な設計判断やゴッチャは能動的に記録しておくと効果的です。

## CLAUDE.md との違い

| | CLAUDE.md | auto memory |
|---|-----------|-------------|
| 場所 | プロジェクトルート | `~/.claude/projects/` |
| Git管理 | される（チーム共有） | されない（個人の記憶） |
| 内容 | プロジェクトのルール・規約 | 開発で学んだ知見・ゴッチャ |
| 更新 | 手動 | 自動 + 手動 |

`CLAUDE.md` は「このプロジェクトではこうしてほしい」という指示書。auto memory は「前回こういうことがあった」という経験の蓄積。両方使うことで、Claude Code がプロジェクトの文脈を深く理解した状態でセッションを開始できます。
