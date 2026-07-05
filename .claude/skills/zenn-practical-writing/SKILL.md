---
name: zenn-practical-writing
description: Zenn/Dev.to の記事（tech/idea 問わず全て）を書くときの既定スキル。実用軸——「読者が数秒で何かわかり、そのまま手を動かして再現できる」——を正本として保持する。低情報密度・実コード/図・即実用・低認知負荷・用途が瞬時にわかる。文体は ですます調。Zenn/Dev.to は type で声を分けない。AI-slop 禁止・タイトル誠実さ・ネタ 3 軸は writing-ecosystem に defer。genuine な思索エッセイ（だ/である × 発見調）は Substack corpus へ。
user-invocable: true
origin: shimo4228
---

# zenn-practical-writing — Zenn/Dev.to 記事の実用軸

**この記事で守ること**: 読者が記事を開いて数秒で「これは何で、読めば自分に何ができるようになるか」がわかり、そのまま手を動かして再現できる。理解に認知リソースを使わせない。

これが Zenn/Dev.to チャンネルの既定の声。essay（思索・意見）や paper（論文）は別チャンネルに独自の声があり、それらとは意図的に文体を分ける。

---

## Scope — いつ使うか

| 書くもの | 使うもの |
|---|---|
| **Zenn/Dev.to の記事**（tech / idea 問わず全て） | **このスキル（既定）** |
| 学術 paper / preprint | `paper-ecosystem` skill |
| genuine な思索エッセイ（だ/である × 発見調） | essay corpus（Substack）へ。`writing-ecosystem` skill |

**Zenn/Dev.to は type（tech/idea）で声を分けない** — すべて実用軸（ですます・即実用）。Zenn frontmatter の `type` は platform 要件として残るが voice は分岐しない。毒humor/刃牙 の personality は話題が合えば任意で足せる（[zenn-idea-voice](../zenn-idea-voice/SKILL.md)）。

判定: Zenn/Dev.to に出すなら実用軸（このスキル）。だ/である で思索を綴る genuine エッセイは Substack corpus（別 channel）へ。

---

## 継承と上書き（writing-ecosystem との関係）

genre 中立の canon は `writing-ecosystem` skill を正本として **defer**（再掲しない）。essay 固有の Voice だけ **override** する。

| writing-ecosystem の資産 | このスキルでの扱い |
|---|---|
| AI-slop 禁止リスト（日英） | **継承**（defer。実用記事でも誇張語は使わない） |
| タイトルの誠実さ・煽り禁止 | **継承**（defer） |
| ネタ選定 3 軸（検索需要 / 競合 / 一次情報） | **継承**（defer） |
| Voice（発見調・結論の問い化・断定→弱化・初期経典の語り口） | **上書き**（実用軸では使わない。ですます調 × 直接指示。下記「文体」参照） |
| Section Length（1 節が全体の 30% を超えない） | 継承 |

---

## 実用軸の 5 ルール

ユーザーの 5 マーカーを、検証可能な具体ルールに落とす。

| マーカー | 具体ルール |
|---|---|
| **情報密度を抑えめ** | 1 節 1 論点。前置き・throat-clearing を削る。短段落。密な散文より箇条書き/表。読者に再読を要求しない |
| **図や実コード** | 1 記事に図/表を **≥1**。コードは**コピペで動く自己完結**（file path + 言語タグ + input→output を必ず示す） |
| **すぐ使える** | task 志向。再現可能な成果物を渡す。前提（バージョン・必要物）を**冒頭に列挙**。手順は順序付き・欠落なし |
| **低認知負荷** | BLUF：成果物を第一画面で宣言。見出しは outcome を述べる。前方参照禁止。深掘りは `:::details` に progressive disclosure |
| **用途が瞬時にわかる** | title + 冒頭が「これは何 / 読後に何ができるか」に答える。冒頭に「**この記事で作れるもの/わかること**」を 1 行 |

### 「低密度」の誤読を防ぐ（重要）

**情報密度を下げる ≠ 内容を薄くする。** 削るのは冗長・前置き・二重説明であって、技術的実質は削らない。深い記事でも、余計な認知負荷を載せなければ実用軸に乗る。「浅い記事を量産する」ことではない。

---

## 文体：ですます調 × 直接指示（最大の差別化点）

**実用記事は ですます調で書く。** essay（writing-ecosystem）の だ/である × 発見調 とは文体レベルで分ける。ですます調は読者との距離が近く、「教わってすぐ試す」実用軸に合う。

さらに essay が「〜ではないか」と問い化するのに対し、**実用 how-to は直接指示で言い切る**。

| | essay（writing-ecosystem） | 実用（このスキル） |
|---|---|---|
| 文体 | だ/である | **ですます** |
| 語り | 発見調（〜だった、〜に見えた） | 直接指示（〜します、〜してください） |
| 結論 | 問い化（〜ではないか） | 言い切り（〜になります、〜できます） |
| 例 | 「〜と読める」 | 「まず X します」「Y を実行します」 |

- だ/である と ですます を **1 記事内で混在させない**（混在は読者にノイズ）
- AI-slop 禁止と誠実さは essay と共通。「言い切る」と「煽る/誇張する」は別物——`writing-ecosystem` の Title Conventions と禁止リストは実用記事でも守る

---

## Diátaxis での位置づけ

Zenn/Dev.to 実用記事は Diátaxis の **how-to（課題達成）** と **reference（逆引き）** 象限。

- **how-to** — 「X を Y する方法」。ゴール駆動。読者は目的を持って来る
- **reference** — 「X の設定/API 一覧」。lookup 駆動
- **tutorial**（学習 journey）— 副次的に可（初心者向け連載など）
- **explanation**（なぜ論・思索）— **対象外**。essay 象限 → `writing-ecosystem` / Substack へ

---

## 実用記事の構成テンプレート

```markdown
# タイトル（成果物 or 解く課題が一目でわかる）

> **この記事で作れるもの/わかること**: [1 行]

## 前提
- [バージョン・必要なアカウント・前提知識]

## [手順 or 逆引き見出し（outcome を述べる）]
（実コード：コピペで動く。file path + 言語タグ）
（input → output を示す）

## 落とし穴 / Tips
:::details ハマったら
[progressive disclosure。本筋を膨らませない]
:::

## まとめ（次にできること）
```

形式・記法・frontmatter・emoji・topics の詳細は [zenn-format](../zenn-format/SKILL.md) が正本。

---

## 執筆プロセス（サブエージェントに委譲しない）

記事の執筆は Claude Code 本体が直接行う。専用の執筆エージェントには委譲しない。

### Phase 1: 構成案（着手前に確認）

1. 素材を読み込み、**コア論点**を 1 文で書く
2. 独立論点を数える。**4 を超えるなら分割を提案**
3. シリーズ記事なら先行記事との重複リスクを確認
4. セクション構成案を提示し、**ユーザー確認を待ってから執筆に入る**

### Phase 2: 執筆

上記の「実用軸の 5 ルール」「文体」に従って直接執筆する。

### Phase 3: 自己プリフライト（レビューエージェントに渡す前）

- [ ] 独立論点数が 4 以下（超えるなら分割提案）
- [ ] AI-slop スキャン（`writing-ecosystem` の禁止リスト）
- [ ] タイトルが規約に合致
- [ ] 用語が初出で説明されている
- [ ] シリーズ先行記事との重複がない

## 素材集め（書く前の準備）

実用記事は具体素材が命。書き始める前に:

1. **並列リサーチ** — 対象技術 / 組み合わせ先 / 既存記事との差別化ポイントを Task tool で並列に調べる
2. **実体験ログ** — つまずき→原因→解決を表（#, 問題, 原因, 解決）に整理。記事の「オチ」になる気づきを特定
3. **context ファイルに集約** — `drafts/article-context_<topic>-<date>.md` に企画・タイムライン・技術コンテキスト・差別化・リサーチ要点をまとめてから執筆

AI 対話などの**生ログ**は `articles/_context/{slug}-{source}-log.md` に退避する（Zenn の同期対象外。詳細は `.claude/rules/zenn-writing.md`）。

---

## 受け入れチェックリスト（客観・全 Zenn/Dev.to 記事）

公開前に機械的に確認できる項目。`quality-gate` skill がこれを gate する。

- [ ] 冒頭に「作れるもの/わかること」の 1 行がある
- [ ] 前提を列挙している
- [ ] 実コードがコピペで動く（file path + 言語タグ付き）
- [ ] 図/表が ≥1 ある
- [ ] 見出しが outcome を述べている（scannable）
- [ ] 1 節 1 論点、前方参照なし
- [ ] AI-slop なし（`writing-ecosystem` の禁止リスト）
- [ ] 独立論点数が 4 以下（Phase 1 参照）
- [ ] ですます調で統一（だ/である と混在しない）

---

## Anti-Patterns

- ❌ **完成稿の事後リライトでエンゲージ最適化** → これは catchify（ADR-0001 で禁止）。このスキルは**書く時の生成既定**であって、書き上げた文章を読者受け狙いで作り替える pass ではない。「誰のために変えるか」（著者の思考 vs 読者受け）が判定式
- ❌ **情報密度を下げる＝内容を薄くする** → 削るのは冗長・前置きだけ。技術的実質は残す
- ❌ **図を飾りで入れる** → 理解を 1 ステップ短縮する図だけ。装飾図は認知負荷を上げる
- ❌ **essay の問い化・発見調・だ/である調を持ち込む** → それは `writing-ecosystem` の領分（実用記事は ですます調）
- ❌ **動かないコード / 断片だけのコード** → コピペで動かないコードは実用軸違反

---

## Related

- `~/.claude/skills/writing-ecosystem/SKILL.md`（global）— genre 中立 canon（AI-slop / タイトル / ネタ 3 軸）の正本 + essay 声
- [zenn-format](../zenn-format/SKILL.md) — frontmatter・記法・emoji・topics の正本
- [zenn-idea-voice](../zenn-idea-voice/SKILL.md) — 毒humor / 刃牙リファレンス（type 非依存の opt-in personality flavor）
- [quality-gate](../quality-gate/SKILL.md) — Zenn/Dev.to 全記事の受け入れ gate
- `.claude/rules/zenn-writing.md` — Zenn プラットフォーム固有ルール（frontmatter 上限・:::message・投稿ペース）
- 根拠: `.claude/docs/adr/0003-*.md`（channel 軸 + genre-split）
