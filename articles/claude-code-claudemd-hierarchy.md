---
title: "Claude Code の CLAUDE.md 階層構造でハマった話 — 正しい使い分け"
emoji: "📂"
type: "tech"
topics: ["claudecode", "ai", "開発環境", "設定"]
published: false
---

## 10日間の配置ミス

Claude Code の設定環境 [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code) を導入したとき、私は GitHub から ZIP をダウンロードしました。rules・skills・agents のテンプレート集を `MyAI_Lab/.claude/` に丸ごと配置したのが間違いの始まりです。

```text
MyAI_Lab/.claude/       ← ワークスペースレベル
├── rules/
├── skills/
├── agents/
├── README.md
├── LICENSE
└── .gitignore
```

10日間この状態で6プロジェクトを開発しました。全プロジェクトが同じ rules/skills/agents を強制共有する状態です。「Zenn 執筆用のスキルが iOS アプリ開発にも読み込まれる」「Python 向けルールが Swift プロジェクトにも適用される」という問題が次第に顕在化しました。

## Claude Code の3層構造

公式ドキュメントを読み直して、`.claude/` ディレクトリには3つの階層があることを理解しました。

```text
~/.claude/                    ← ユーザーレベル（全プロジェクト共通）
├── rules/                      汎用ルール
├── skills/                     汎用スキル
├── agents/                     汎用エージェント
├── commands/                   汎用コマンド
└── settings.json               グローバル設定

MyAI_Lab/.claude/             ← ワークスペースレベル
└── settings.local.json         ワークスペース固有の設定のみ

MyAI_Lab/zenn-content/.claude/ ← プロジェクトレベル
├── skills/                     プロジェクト固有スキル
├── agents/                     プロジェクト固有エージェント
└── settings.local.json         プロジェクト固有の設定
```

設定値（`settings.json`）は同じキーがあれば下位（プロジェクト）が優先です。一方、`rules/`・`agents/`・`skills/` は**全レベルの内容が合算**（additive）されて読み込まれます。

## 各層の役割

### ユーザーレベル (`~/.claude/`)

全プロジェクト共通の設定を置く場所です。私の環境では以下が入っています。

- `rules/common/` — コーディングスタイル、Git ワークフロー、テスト方針など言語非依存のルール
- `rules/typescript/`, `rules/python/` — 言語別の拡張ルール
- `agents/` — planner、code-reviewer、tdd-guide など汎用エージェント14個

これらはどのプロジェクトを開いても参照されます。

### ワークスペースレベル (`MyAI_Lab/.claude/`)

複数プロジェクトを束ねるモノレポやワークスペースの設定です。修正後は `settings.local.json` のみにしました。rules/skills/agents は**置かない**のがポイントです。

### プロジェクトレベル (`zenn-content/.claude/`)

そのプロジェクト固有の設定です。zenn-content では以下が入っています（主なものを抜粋）。

- `skills/zenn-writer/` — Zenn 記事のフォーマットガイド
- `skills/seo-optimizer/` — タイトル・タグ最適化
- `skills/publish-article/` — 公開チェックリスト
- `agents/editor.md` — 辛口レビューエージェント

iOS アプリのプロジェクトにはこれらは読み込まれません。プロジェクトごとに必要なものだけが有効になります。

## CLAUDE.md はどこに置くか

`.claude/` ディレクトリとは別に、`CLAUDE.md` ファイルも階層構造を持ちます。

```text
~/CLAUDE.md                   ← ユーザーレベル（個人のグローバル指示）
MyAI_Lab/CLAUDE.md            ← ワークスペースレベル（Git管理される）
zenn-content/CLAUDE.md        ← プロジェクトレベル（Git管理される）
```

`CLAUDE.md` はプロジェクトルートに置く **Git 管理対象のファイル**です。チームで共有するルールや規約を書きます。一方、`.claude/` ディレクトリ内の設定は個人の環境に閉じます。

Claude Code は起動したディレクトリから**親ディレクトリを順にたどって** `CLAUDE.md` を探します。`zenn-content/` で起動すると、`zenn-content/CLAUDE.md` → `MyAI_Lab/CLAUDE.md` → `~/CLAUDE.md` の順で読み込まれ、すべてが合算されます。

なお、ユーザーレベルの `CLAUDE.md` は `~/CLAUDE.md` でも `~/.claude/CLAUDE.md` でも有効です。`~/.claude/rules/` で分割管理している場合はどちらも不要です。

## 修正でやったこと

```text
1. MyAI_Lab/.claude/ から rules/skills/agents を削除
2. ~/.claude/ に rules/agents を移動（全プロジェクト共通）
3. zenn-content/.claude/ にプロジェクト固有の skills/agents を配置
4. 各レベルに settings.local.json のみ残す
5. README, LICENSE 等の不要ファイルを削除
```

修正後、各プロジェクトが独立した設定を持てるようになり、コンテキストの混線がなくなりました。

## 判断基準

何をどの階層に置くか迷ったら、この基準で判断します。

| 置き場所 | 判断基準 | 例 |
|---------|---------|-----|
| `~/.claude/` | どのプロジェクトでも使う | コーディングルール、汎用エージェント |
| `workspace/.claude/` | ワークスペース固有の設定のみ | settings.local.json |
| `project/.claude/` | そのプロジェクトだけで使う | Zenn 執筆スキル、iOS テストスキル |
| `project/CLAUDE.md` | チームで共有したいルール | プロジェクトの規約、テスト方針 |

10日間の配置ミスが、結果的にこの階層構造を理解する機会になりました。「全部同じ場所に置いても動く。ただ柔軟性を失う」という点がこの問題の厄介なところです。エラーが出ないので気づきにくい。

具体的には、iOS アプリのデバッグ中に Claude Code が「Zenn 記事の textlint ルールに違反しています」と指摘してきたことで、設定の混線に気づきました。ルール自体は正しいのに、適用対象が間違っている。これは配置の問題であり、ルールの問題ではありません。

プロジェクトが増えてきて「設定が混線している」と感じたら、3層構造を見直してみてください。
