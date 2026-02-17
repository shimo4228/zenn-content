---
title: "Claude Code の learned skills が溜まりすぎた時の棚卸し手順"
emoji: "🗃️"
type: "tech"
topics: ["claudecode", "ai", "開発環境", "生産性"]
published: true
---

## 問題

Claude Code の `/learn` コマンドや continuous-learning スキルを使っていると、`~/.claude/skills/learned/` にスキルが蓄積されます。15日間の開発で16件から48件に膨れました。

スキルの増加は **Character Budget**（スキル一覧の表示に割り当てられた文字数上限）を圧迫します。スキル一覧の表示にはコンテキストウィンドウの約2%（約16,000文字）しか使えません。上限を超えると警告なしで切り捨てられ、使いたいスキルが見えなくなります。

## 棚卸しの判断基準

3つの質問で分類します。

1. **そのスキルは1つのプロジェクトでしか使わないか？** → プロジェクトの `.claude/skills/` に移動
2. **複数プロジェクトで使うか？** → `~/.claude/skills/` にグローバルとして残す
3. **ワンライナーで再導出できるか？** → 削除（必要になったら `/learn` で再生成）

## 具体的な手順

### 1. 現状を把握する

```bash
# グローバルの learned スキル一覧
ls ~/.claude/skills/learned/

# プロジェクト固有のスキル一覧
ls .claude/skills/
```

### 2. プロジェクト固有スキルを移動する

Swift/iOS のパターンは iOS プロジェクトにだけ必要です。Zenn の執筆スキルは zenn-content にだけ必要です。

```bash
# iOS プロジェクトに移動
mv ~/.claude/skills/learned/swift-di-pattern.md \
   ~/MyProject-iOS/.claude/skills/learned/

# Zenn プロジェクトに移動
mv ~/.claude/skills/learned/zenn-textlint-workaround.md \
   ~/zenn-content/.claude/skills/learned/
```

### 3. 使わないスキルを無効化する

Everything Claude Code（ECC）のテンプレートに Django や Spring Boot など使わないスキルが含まれている場合、SKILL.md の冒頭に以下を追加します。

```yaml
---
disable-model-invocation: true
---
```

SKILL.md の YAML フロントマターに追加します。削除ではなく無効化にする理由は、将来使う可能性をゼロにしたくないからです。Discovery で Character Budget を消費しなくなります。

### 4. 退役スキルを削除またはアーカイブする

ワンライナーで再導出できるスキルは削除します。念のためアーカイブしたい場合は別ディレクトリに退避します。

```bash
# アーカイブ
mkdir -p ~/.claude/skills-archive
mv ~/.claude/skills/learned/pbpaste-trick.md \
   ~/.claude/skills-archive/pbpaste-trick.md
```

## 棚卸しのトリガー

「いつやるか」を決めておかないと、気づいた頃には手遅れです。

**1つの層で10件を超えたら棚卸し。** これが私の閾値です。`~/.claude/skills/learned/` が10件を超えたらグローバルとプロジェクトに分類し、プロジェクトの `.claude/skills/` が10件を超えたら統合や退役を検討します。

## 棚卸し後の構成例

```text
~/.claude/skills/
├── learned/              ← 全プロジェクト共通（7件）
│   ├── ai-era-architecture-principles/
│   ├── python-immutable-accumulator/
│   └── ...
└── search-first/         ← 手動作成のスキル

zenn-content/.claude/skills/
├── zenn-writer/          ← Zenn 固有
├── seo-optimizer/        ← Zenn 固有
└── learned/              ← Zenn 固有の学習スキル

pdf2anki/.claude/skills/
└── learned/              ← Python CLI 固有の学習スキル
```

## まとめ

- スキルは増え続ける。棚卸しは「一度きり」ではなく「繰り返すもの」
- 10件超えたら棚卸しをトリガーする
- プロジェクト固有のスキルはグローバルに置かない
- `disable-model-invocation: true` で使わないスキルを無効化する
- 削除を恐れない。`/learn` で再生成できる
