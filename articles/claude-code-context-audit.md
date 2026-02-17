---
title: "Claude Code の設定ファイルを全棚卸しして分かった5つのこと"
emoji: "🔍"
type: "tech"
topics: ["claudecode", "ai", "開発環境", "生産性"]
published: false
---

## きっかけ

あるプロジェクトで Claude Code を起動したとき、前回のセッションで教えたはずのゴッチャ（落とし穴）を Claude Code が覚えていませんでした。「memory に保存したはずなのに、なぜ？」

調べてみたら、そのプロジェクトの作業をワークスペースルートで行っていたため、memory が別のディレクトリに紐づいていました。この発見をきっかけに、6プロジェクト分の `CLAUDE.md`・`rules/`・`auto memory` を2日かけて全棚卸ししました。

## 環境

```text
MyAI_Lab/                    ← ワークスペースルート（git repo ではない）
├── swift-app-a/            # Swift 6.0 / SwiftUI
├── swift-app-b/        # Swift 6.0 / SwiftUI
├── nextjs-app/            # TypeScript / Next.js
├── python-cli/                # Python / uv
├── python-tool/             # Python / uv
└── zenn-content/            # Markdown / Zenn CLI
```

Claude Code の設定は3層に分かれます。

```text
~/.claude/                   ← ユーザーレベル（全プロジェクト共通）
├── rules/common/            #   言語非依存ルール
├── rules/python/            #   Python 固有ルール
├── rules/typescript/        #   TypeScript 固有ルール
├── settings.json            #   権限・Hook 設定
└── projects/{path}/memory/  #   プロジェクト別 auto memory（パスエンコーディング）

MyAI_Lab/CLAUDE.md           ← ワークスペースレベル
MyAI_Lab/python-cli/CLAUDE.md  ← プロジェクトレベル（各プロジェクト）
```

## 1. CLAUDE.md は全プロジェクトに配備すべき

棚卸し前の状態: zenn-content だけ CLAUDE.md があり、他の5プロジェクトにはなし。

CLAUDE.md がないと、Claude Code はプロジェクトの Tech Stack や Build コマンドを知りません。毎回「これは Swift プロジェクトで...」と説明するのは無駄です。

5プロジェクトに一括配備しました。各 CLAUDE.md のテンプレートは以下のとおりです。

```markdown
# {project-name}

{1行の概要}

## Tech Stack
- 言語、フレームワーク、主要依存

## Directory Structure
（主要フォルダのみ）

## Build / Test / Run
（コピペで使えるコマンド）

## Conventions
（プロジェクト固有のルール）

## Status
（現在の開発状況）
```

65〜89行程度。「このプロジェクトで作業するために必要な情報」だけに絞ります。ワークスペースレベルの情報（チェックポイントルール等）は上位の `MyAI_Lab/CLAUDE.md` に書き、重複させません。

## 2. ワークスペース CLAUDE.md には「ルールのルール」を書く

個別プロジェクトの CLAUDE.md を量産すると、品質がバラつきます。ワークスペースの `MyAI_Lab/CLAUDE.md` に「新プロジェクト作成時のルール」を追記しました。

```markdown
## 新プロジェクト作成時のルール

新しいプロジェクトフォルダを作成したら、必ず CLAUDE.md を同時に作成する。

### 必須セクション
- プロジェクト概要 (1行)
- Tech Stack
- Directory Structure
- Build / Test / Run
- Conventions
- Status
```

こうしておけば、次にプロジェクトを追加するときに「CLAUDE.md を作って」とリクエストするだけで、Claude Code がテンプレートに沿った CLAUDE.md を生成してくれます。

## 3. グローバル rules の言語別浪費は気にしなくていい

`~/.claude/rules/` に置いたルールファイルは、**言語に関係なく全セッションで読み込まれます**。フィルタリング機能はありません。

Swift プロジェクトの作業中に、Python と TypeScript のルールが無駄に読み込まれている — これが気になって定量調査しました。

```text
~/.claude/rules/
├── README.md          3,030 bytes  ← インストール手順書
├── common/           10,544 bytes  ← 言語非依存（10ファイル）
├── python/            2,843 bytes  ← Python 固有（5ファイル）
└── typescript/        3,288 bytes  ← TS 固有（5ファイル）
                      ──────────
                      19,705 bytes  計21ファイル
```

Swift プロジェクトでの浪費を計算しました。

| 不要な rules | bytes | tokens (概算) |
|-------------|------:|-------------:|
| python/ | 2,843 | ~900 |
| typescript/ | 3,288 | ~1,000 |
| README.md | 3,030 | ~900 |
| **合計** | **9,161** | **~2,800** |

コンテキスト窓 200K tokens に対して **約1.4%**（1 token ≈ 3〜4 bytes で概算）。ただし、セッション序盤のコンテキストが少ない段階ではこの割合は体感で大きくなります。

言語別にプロジェクトレベルへ移動する案も検討しましたが、6プロジェクト × 言語ごとにルールを配置する管理コストに見合いません。**現状維持が最適解**です。

> README.md だけは純粋なインストール手順書なのでセッション中に読む意味がありません。気になるなら削除してもいいですが、約900 tokens の差なので優先度は低いです。

## 4. ~/.claude/CLAUDE.md がなくても問題ない

「ユーザーレベルに CLAUDE.md がないのは設定ミスでは？」と一瞬焦りましたが、問題ありません。

ユーザーレベルの指示は2つの方式があります。

| 方式 | パス | 特徴 |
|------|------|------|
| 単一ファイル | `~/.claude/CLAUDE.md` | 1ファイルに全部書く |
| ルール分割 | `~/.claude/rules/*.md` | トピック別に分割 |

**どちらか一方で十分**。技術的には併用も可能ですが、同じ指示が2箇所に分散すると更新漏れや矛盾のリスクが生まれます。

`~/.claude/rules/` で common / python / typescript に分割管理しているなら、`~/.claude/CLAUDE.md` は不要です。

## 5. ワークスペースルートでの作業は memory が育たない

**これが一番の発見でした。**

auto memory はセッションを開いたディレクトリの**絶対パスをエンコードしたキー**で保存されます。`/` がハイフンに変換され、フラットなディレクトリ名になります。

```text
~/.claude/projects/
├── -Users-me-MyAI-Lab/memory/              ← ワークスペースルート
├── -Users-me-MyAI-Lab-python-cli/memory/   ← プロジェクト別
├── -Users-me-MyAI-Lab-swift-app-a/memory/
└── ...
```

6プロジェクトの MEMORY.md の存在を調べました。

| プロジェクト | Stack | MEMORY.md |
|:-----------|:------|:---------:|
| swift-app-a | Swift | ✅ |
| swift-app-b | Swift | ❌ |
| nextjs-app | TypeScript | ❌ |
| python-cli | Python | ✅ |
| python-tool | Python | ❌ |
| zenn-content | Markdown | ✅ |

**半数の3プロジェクトで MEMORY.md が欠落。**

原因は明確で、これらのプロジェクトの作業をワークスペースルート（`MyAI_Lab/`）で行っていたためです。ルートでセッションを開くと、以下の問題が起きます。

- memory は `MyAI_Lab/` に紐づく
- プロジェクト固有の知見（ゴッチャ、設計判断、ツールチェイン）がそのプロジェクトの memory に蓄積されない
- 次にプロジェクトディレクトリで開いても、過去の知見がない状態から始まる

```bash
# NG: ワークスペースルートから操作
cd ~/MyAI_Lab && claude
# → memory は MyAI_Lab/ に蓄積。プロジェクトの memory は空のまま

# OK: プロジェクトディレクトリで起動
cd ~/MyAI_Lab/swift-app-b && claude
# → memory は swift-app-b/ に蓄積される
```

**対策: 常にプロジェクトディレクトリ内で Claude Code を起動する。**

ワークスペースルートでの作業は、プロジェクト横断の企画・リサーチ時のみに限定します。

## まとめ

| # | 発見 | 影響度 | 対策 |
|---|------|:------:|------|
| 1 | CLAUDE.md が大半のプロジェクトにない | 大 | 全プロジェクトに配備 |
| 2 | 作成ルールがないと品質がバラつく | 中 | ワークスペース CLAUDE.md にテンプレ定義 |
| 3 | グローバル rules の言語別浪費 | 小 (~1.4%) | 不要 |
| 4 | ~/.claude/CLAUDE.md がない | なし | rules/ があれば不要 |
| 5 | ワークスペースルート運用で memory 欠落 | **大** | プロジェクト内で起動 |

気にしていた rules の浪費（#3）より、**CLAUDE.md の未配備（#1）とセッションの起動場所（#5）の方がはるかに影響が大きい**という結果でした。

設定を増やすことより、**既存の仕組みを正しい場所で使う**方が効果的です。
