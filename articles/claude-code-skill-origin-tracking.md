---
title: "Claude Code スキルの出自管理 ── origin メタデータで79個を分類した"
emoji: "🏷️"
type: "tech"
topics: ["claudecode", "ai", "開発環境", "cli"]
published: true
---

ECC（Everything Claude Code）から27個を一括導入し、GitHub で見つけたスキルを追加し、`/learn` で自動抽出されたものが溜まり、自分で書いたものもある。気づけば79個。**「このスキル、どこから来たんだっけ？」が分からない。**

ECC は Claude Code 向けのスキル・設定をまとめたコミュニティリポジトリです。

## 何が困るのか

スキルの棚卸しをしようとして `ls ~/.claude/skills/` を実行したとき、こうなります。

```text
backend-patterns/
coding-standards/
continuous-learning/
iterative-retrieval/
myai-lab-patterns/
nutrient-document-processing/
search-first/
strategic-compact/
...
```

この中で自分が作ったのはどれか。ECC 由来はどれか。コミュニティ製はどれか。ファイルを開いても `name` と `description` しかなく、出自の手がかりがありません。

これが実務で困るのは以下の場面です。

- **アップデート判断**: ECC が更新されたとき、どのスキルを差し替えるべきか分からない
- **削除判断**: 使っていないスキルを消したいが、自作か外部かで判断基準が変わる
- **共有**: チームメンバーにスキルを渡すとき、ライセンスや出典を確認できない

## 解決策: origin メタデータ

スキルファイルの冒頭に出自を1行追加するルールを作りました。

YAML frontmatter がある場合はフィールドとして追加します。

```yaml
---
name: coding-standards
description: Universal coding standards...
origin: ECC
---
```

frontmatter がない場合は HTML コメントで追加します。

```markdown
<!-- origin: original -->
# My Custom Skill
```

## origin の分類

| origin 値 | 意味 | 例 |
|-----------|------|-----|
| `original` | 自分で作成 | search-first |
| `ECC` | Everything Claude Code から導入 | coding-standards |
| `{org/repo}` | 特定の外部リポジトリ | PSPDFKit-labs/nutrient-agent-skill |
| `auto-extracted` | continuous-learning が自動抽出 | learned/*.md |
| `skill-create` | git 履歴から自動生成 | myai-lab-patterns |

## 実際にやったこと

66個のグローバルスキルと13個のプロジェクトスキルを分類してタグ付けしました。

### 照合の手順

1. **ECC スキルの特定**: `configure-ecc/SKILL.md` の中に全27スキルのリストがある。これと照合して ECC 由来を確定
2. **外部リポジトリの特定**: frontmatter に手がかりがないスキルはファイル末尾のリンクや README を確認。`nutrient-document-processing` は末尾に元リポジトリの URL が記載されていた
3. **自作・自動生成の分類**: `learned/` 配下は `auto-extracted`、`/skill-create` で生成したものは `skill-create`、残りは `original`

### 結果の内訳

```text
origin 別スキル数（全79個）:
  ECC             27  ── configure-ecc のリストと完全一致
  original        22  ── 自作（rules, skills, agents）
  auto-extracted  18  ── continuous-learning / /learn で自動生成
  skill-create     6  ── git 履歴からパターン抽出
  外部リポジトリ     6  ── GitHub で個別に発見・導入
```

タグ付け自体は Python スクリプトで一括処理しています。YAML frontmatter の有無を判定し、適切な形式で `origin` を挿入します。

## 運用ルール

`~/.claude/rules/common/skills.md` にルールとして定義し、全プロジェクトで自動適用されるようにしました。

- **新規スキル作成時**: 必ず origin を付与する
- **外部スキル導入時**: 導入元のリポジトリ名を記録する
- **auto-extracted**: continuous-learning が生成する learned/ スキルに自動付与する
- **棚卸し時**: origin を基準に、アップデート確認や削除判断を行う

## 本質的な課題

この問題は個人の運用で解決できますが、本来はエコシステム側で対応すべきです。

npm パッケージには `package.json` があり、出自・バージョン・ライセンスが明確です。Claude Code のスキルにはそれに相当する標準がまだありません。`name` と `description` だけの frontmatter では、スキルが増えるほど管理が破綻します。

`origin`・`version`・`license` が frontmatter の標準メタデータとして含まれるようになれば、この問題は発生しなくなります。

## Issue を出してみた

個人の運用に留めず、上流に改善を提案しました。

- **ECC リポジトリ**: [affaan-m/everything-claude-code#246](https://github.com/affaan-m/everything-claude-code/issues/246) — 配布するスキルに `origin: ECC` を含めてほしいという提案
- **Anthropic**: [anthropics/claude-code#26438](https://github.com/anthropics/claude-code/issues/26438) — スキルの標準メタデータ仕様（origin / version / license）の策定を要望

ECC 側は変更が小さく受け入れやすいため先に提出し、Anthropic 側には ECC の対応をリファレンスとして紐付けました。個人の workaround で終わらせず、エコシステム全体の改善につなげるのが狙いです。

## まとめ

- Claude Code のスキルは出自が記録されないため、数が増えると管理できなくなる
- `origin` メタデータを frontmatter に追加するルールで解決できる
- ECC リポジトリのインストーラーと照合することで、既存スキルの分類も可能
- 長期的にはスキルの標準メタデータ仕様が必要
- ECC と Anthropic に Issue を提出済み

`ls ~/.claude/skills/` して「これ何だっけ」が1つでもあれば、origin タグの導入時です。
