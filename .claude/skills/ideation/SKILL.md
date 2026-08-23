---
name: ideation
description: 記事のネタの種を見つけ、チャンネル（Zenn 実用 / note エッセイ）へ routing して提案する。Use when 「記事のネタ出し」「何を書くか迷っている」「テーマ候補を出して」/ideation。NOT for — テーマ強度の判定（→ theme-eval）、構成案（→ zenn-practical-writing Phase 1）、タイトル生成（→ headline-craft）
user-invocable: true
origin: shimo4228
---

# Ideation Skill

**Purpose:** 記事のテーマを検討し、著者の思考を引き出す。

---

## Usage

```
/ideation                        # 対話的にテーマを探る
/ideation "エージェントの記憶"    # 特定テーマの記事化を検討
```

---

## Process

### Step 1: 種を見つける

以下の情報源からテーマの種を収集する:

1. **最近の作業**: git log から直近の開発活動を確認
2. **未公開ドラフト**: `drafts/` や `published: false` の記事
3. **ユーザーの関心**: 対話で「最近何を考えているか」を聞く
4. **既存記事の隙間**: 公開済み記事を一覧し、カバーされていないテーマを探す
5. **実測フィードバック**: `article-stocktake` の最新サマリ（memory: article-quality.md 冒頭）— 過去に読者へ届いたテーマ・構造の**事実**。推薦理由・優劣づけには使わない（下記 Notes の禁止条項は維持）

### Step 2 以降は他 skill が持つ（2026-08-23 縮約）

本 skill の固有分は **Step 1 の 5 情報源だけ**。以下はポインタで、ここに手順を再掲しない:

- **チャンネル routing**（Zenn 実用 / note→Substack エッセイ。記事 type では分けない — 2026-07 廃止）
  → `theme-eval` Step 1.5 が判定と一緒に扱う
- **テーマ強度の判定**（T1-T8 / Write-A・B見込み / Deepen）→ **`theme-eval` skill を読んで実行する**。
  本 skill は判定しない（2026-08-23 に独自判定表を廃止 — T2 非自明性 / T3 言説の空白 /
  T8 トレンド寄生を欠く弱いサブセットで、theme-eval が「厳しさの供給源」とする T3 を落としていた）
- **構成案** → Zenn/Dev.to は `zenn-practical-writing` Phase 1、note は `writing-ecosystem`
- **タイトル候補** → `headline-craft`（判定は `title-eval`）

種ごとに一文でテーマを立て、`theme-eval` へ渡すところまでが本 skill の仕事。

---

## Notes

- テーマの強制はしない。著者が「書きたい」と思えることが最優先
- 検索流入やバズを理由にテーマを推薦しない（Content Integrity 原則）
- 複数のテーマ候補がある場合は、優劣をつけずに並列提示する
