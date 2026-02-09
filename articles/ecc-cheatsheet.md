---
title: "Everything Claude Code (ECC) 完全チートシート"
emoji: "📚"
type: "tech"
topics: ["claude", "ai", "開発ツール", "チートシート", "生産性"]
published: false
---

## はじめに

**Everything Claude Code (ECC)** は、Claude Codeの完全な設定コレクションです。13個のエージェント、30以上のスキル、30以上のコマンド、そしてルールとフックで構成され、開発の一気通貫したPDCAサイクルを実現します。

このチートシートは、ECCの全機能をクイックリファレンスとして提供します。

:::message
ECC公式リポジトリ: [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
:::

---

## Slash Commands (`/command`)

### Development Workflow

| Command | Description |
|---------|-------------|
| `/plan` | 要件整理 → リスク評価 → 実装計画を作成。コードに触る前にユーザー確認を待つ |
| `/tdd` | TDD ワークフロー強制。テスト先行 → 実装 → 80%+ カバレッジ確認 |
| `/build-fix` | TypeScript / ビルドエラーを段階的に修正 |
| `/code-review` | 未コミット変更のセキュリティ・品質レビュー |
| `/refactor-clean` | デッドコード検出・安全に削除（テスト検証付き） |
| `/test-coverage` | テストカバレッジ分析 → 不足テストを生成 |
| `/verify` | コードベース全体の包括的な検証 |
| `/checkpoint` | ワークフロー中のチェックポイント作成・検証 |

### E2E Testing

| Command | Description |
|---------|-------------|
| `/e2e` | Playwright で E2E テストを生成・実行 |

### Multi-Model Collaboration

| Command | Description |
|---------|-------------|
| `/multi-plan` | デュアルモデルで協調的に計画策定 |
| `/multi-execute` | 計画に基づく協調的な実行 |
| `/multi-workflow` | インテリジェントルーティングで協調開発 |
| `/multi-frontend` | フロントエンド特化の開発ワークフロー |
| `/multi-backend` | バックエンド特化の開発ワークフロー |
| `/orchestrate` | 複雑タスクの逐次エージェントワークフロー |

### Go

| Command | Description |
|---------|-------------|
| `/go-test` | Go の TDD ワークフロー（テーブル駆動テスト） |
| `/go-build` | Go ビルドエラー・vet 警告・リンター修正 |
| `/go-review` | Go コードのイディオム・安全性レビュー |

### Python

| Command | Description |
|---------|-------------|
| `/python-review` | PEP 8・型ヒント・セキュリティの Python レビュー |

### Documentation

| Command | Description |
|---------|-------------|
| `/update-docs` | ソースからドキュメントを同期・更新 |
| `/update-codemaps` | コードベース分析 → アーキテクチャ文書更新 |

### Learning System

| Command | Description |
|---------|-------------|
| `/learn` | セッションから再利用可能なパターンを抽出・保存 |
| `/evolve` | 関連するインスティンクトをスキル・コマンド・エージェントに進化 |
| `/instinct-status` | 学習済みインスティンクトの一覧と信頼度を表示 |
| `/instinct-export` | インスティンクトをエクスポート（共有用） |
| `/instinct-import` | インスティンクトをインポート |
| `/skill-create` | git 履歴からコーディングパターンを抽出 → SKILL.md 生成 |

### Other

| Command | Description |
|---------|-------------|
| `/eval` | 評価駆動開発 (EDD) ワークフロー管理 |
| `/sessions` | セッション履歴の管理（一覧・ロード・エイリアス） |
| `/pm2` | プロジェクト分析 → PM2 サービスコマンド生成 |
| `/setup-pm` | パッケージマネージャーの設定 (npm/pnpm/yarn/bun) |

---

## Agents (自動起動)

エージェントは適切な場面で Claude Code が自動的に使用します。

### Planning & Architecture

| Agent | Trigger |
|-------|---------|
| **planner** | 複雑な機能リクエスト・リファクタリング |
| **architect** | システム設計・アーキテクチャ判断 |

### Code Quality

| Agent | Trigger |
|-------|---------|
| **code-reviewer** | コード変更後のレビュー |
| **python-reviewer** | Python コード変更後 |
| **go-reviewer** | Go コード変更後 |
| **security-reviewer** | 認証・API・機密データ関連の変更 |
| **database-reviewer** | SQL・スキーマ・DB パフォーマンス関連 |

### Testing

| Agent | Trigger |
|-------|---------|
| **tdd-guide** | 新機能・バグ修正時に TDD 強制 |
| **e2e-runner** | E2E テスト生成・実行 |

### Fix & Cleanup

| Agent | Trigger |
|-------|---------|
| **build-error-resolver** | ビルド・型エラー発生時 |
| **go-build-resolver** | Go ビルドエラー発生時 |
| **refactor-cleaner** | デッドコード検出・削除 |

### Documentation

| Agent | Trigger |
|-------|---------|
| **doc-updater** | ドキュメント更新・CODEMAP 生成 |

---

## Skills (参照知識)

スキルはエージェントとコマンドが参照するナレッジベースです。

### 汎用

| Skill | Content |
|-------|---------|
| coding-standards | TypeScript/JS/React/Node.js のコーディング規約 |
| security-review | セキュリティチェックリスト・パターン |
| tdd-workflow | TDD ワークフロー（80%+ カバレッジ） |
| frontend-patterns | React/Next.js/状態管理/パフォーマンス |
| backend-patterns | API 設計/DB 最適化/サーバーサイド |
| eval-harness | 評価駆動開発 (EDD) フレームワーク |
| strategic-compact | コンテキスト圧縮の最適タイミング |

### Python

| Skill | Content |
|-------|---------|
| python-patterns | PEP 8・型ヒント・デコレータ・並行処理 |
| python-testing | pytest・TDD・フィクスチャ・モック・カバレッジ |

### Go

| Skill | Content |
|-------|---------|
| golang-patterns | イディオマティック Go・並行パターン |
| golang-testing | テーブル駆動テスト・ベンチマーク・ファジング |

### Django

| Skill | Content |
|-------|---------|
| django-patterns | DRF・ORM・キャッシュ・シグナル・ミドルウェア |
| django-security | 認証・CSRF・SQLi・XSS 防止 |
| django-tdd | pytest-django・factory_boy・モック |

### Spring Boot

| Skill | Content |
|-------|---------|
| springboot-patterns | REST API・レイヤード設計・非同期処理 |
| springboot-security | Spring Security・認証認可・レート制限 |
| springboot-tdd | JUnit 5・Mockito・Testcontainers |
| jpa-patterns | エンティティ設計・クエリ最適化・トランザクション |

### Database

| Skill | Content |
|-------|---------|
| postgres-patterns | クエリ最適化・スキーマ設計・インデックス |
| clickhouse-io | 分析ワークロード・データエンジニアリング |

### Learning

| Skill | Content |
|-------|---------|
| continuous-learning | セッションからパターン自動抽出 |
| continuous-learning-v2 | インスティンクトベースの学習システム |
| configure-ecc | ECC インタラクティブインストーラー |

---

## Rules (自動適用)

`~/.claude/rules/` に配置され、常に適用されます。

```
rules/
├── common/           # 全言語共通
│   ├── coding-style  # イミュータビリティ、ファイル構成、エラー処理
│   ├── git-workflow   # コミットメッセージ、PR、feat/fix/refactor
│   ├── testing        # 80%+ カバレッジ、TDD 必須
│   ├── performance    # モデル選択、コンテキスト管理
│   ├── patterns       # リポジトリパターン、API レスポンス形式
│   ├── hooks          # PreToolUse/PostToolUse/Stop
│   ├── agents         # エージェント一覧と起動条件
│   └── security       # シークレット管理、OWASP Top 10
├── python/           # Python 固有
│   ├── coding-style  # PEP 8、black/isort/ruff
│   ├── testing       # pytest、カバレッジ
│   ├── patterns      # Protocol、dataclass
│   ├── hooks         # black/mypy 自動実行
│   └── security      # bandit、dotenv
└── typescript/       # TypeScript 固有
    ├── coding-style  # Zod、async/await
    ├── testing       # Playwright E2E
    ├── patterns      # Custom hooks、Repository
    ├── hooks         # Prettier/tsc 自動実行
    └── security      # 環境変数、security-reviewer
```

---

## Configuration

| File | Scope | Purpose |
|------|-------|---------|
| `~/.claude/settings.json` | Global | 全プロジェクト共通の permissions |
| `<project>/.claude/settings.json` | Project (shared) | チームで共有する設定 |
| `<project>/.claude/settings.local.json` | Project (local) | 個人の permissions (gitignore) |
| `<project>/CLAUDE.md` | Project | プロジェクト固有の指示 |

---

## Quick Reference

新機能開発の標準フロー：

```bash
# 1. 計画策定
/plan

# 2. テスト駆動で実装
/tdd

# 3. コードレビュー
/code-review

# 4. 最終検証
/verify
```

ビルドが壊れた時：

```bash
/build-fix     # TypeScript
/go-build      # Go
```

リファクタリング：

```bash
/refactor-clean  # デッドコード削除
/test-coverage   # カバレッジ確認
```

学習・改善：

```bash
/learn           # パターン抽出
/instinct-status # 学習状況確認
/evolve          # スキルに進化
```

---

## まとめ

ECCは、Claude Codeでの開発を劇的に効率化する包括的なフレームワークです。このチートシートを手元に置いて、必要な時にすぐに参照できるようにしておきましょう。

特に重要なのは：
- **開発フロー**: `/plan` → `/tdd` → `/code-review` → `/verify`
- **自動起動エージェント**: 適切な場面で自動的に品質を担保
- **ルール**: 常に適用され、コーディング規約とベストプラクティスを強制

ECCを活用して、AI時代の開発フローを体験してください！

:::message
より詳しい情報は、[ECC公式リポジトリ](https://github.com/affaan-m/everything-claude-code)をご覧ください。
:::
