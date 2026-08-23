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

### Step 2: チャンネル routing

種ごとに、どのチャンネル向きかを 1 行で当てる（**記事 type では分けない** — 2026-07 廃止）:

- **Zenn / Dev.to（実用軸）** — 読者が数秒で何かわかり、そのまま手を動かして再現できる種
- **note → Substack（エッセイ）** — 思索・立場表明・組織論。実用手順に落ちない種

チャンネルは優劣でなく routing（ADR-0003）。判断に迷う種は次の step で theme-eval が扱う。

### Step 3: テーマ強度は theme-eval に渡す

**本スキルは強度を判定しない**（2026-08-23 に独自判定表を廃止 — T2 非自明性 /
T3 言説の空白 / T8 トレンド寄生を欠く弱いサブセットで、theme-eval が「厳しさの供給源」と
する T3 を落としていた）。

種ごとに一文でテーマを立て、`theme-eval` skill（T1-T8）へ渡す。verdict と Deepen プロンプトは
あちらが返す。

### Step 4: 提案

```markdown
## テーマ提案

**タイトル案**: [概念を伝えるタイトル]
**コア論点**: [1文]
**チャンネル**: Zenn/Dev.to（実用軸） / note→Substack（エッセイ）
**独自性**: [自分だけが書ける理由]
**想定読者**: [誰が読むか]
**推定ボリューム**: [字数の目安]

### 次のステップ
- [ ] [skill: theme-eval] でテーマ強度を判定する（Write-A/B見込み / Deepen。執筆前ゲート、2026-08-12 追加）
- [ ] 素材を集める（コード、ログ、スクリーンショット）
- [ ] Zenn/Dev.to なら `zenn-practical-writing` Phase 1、note なら `writing-ecosystem` に従って構成案を立てる（オーケストレーター本体が直接執筆）
```

---

## Notes

- テーマの強制はしない。著者が「書きたい」と思えることが最優先
- 検索流入やバズを理由にテーマを推薦しない（Content Integrity 原則）
- 複数のテーマ候補がある場合は、優劣をつけずに並列提示する
