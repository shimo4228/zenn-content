<!-- origin: original -->
# Zenn Writer Skill

**Purpose:** 記事の「どう書くか」——タイトル設計、文体、構成判断、品質チェック。
形式・記法の詳細は [zenn-format](../zenn-format/SKILL.md) を参照。

---

## Title Guidelines

### 基本ルール

- **Length:** メインタイトル40文字以内。サブタイトルは ── で区切って別途
- **Be specific:** "Claude-Native 設計で PDF から Anki カードを自動生成" (good) vs "AI でカード作成" (too vague)
- **Include key terms:** Mention main technologies (Claude, Anki, TDD, etc.)
- **Avoid empty clickbait:** No "必見！", "超簡単！", "たった3分で"（根拠のない煽りはNG）
- **感情語はOK:** 「地獄」「壊す」「棄却」など、記事内容に裏付けのある感情語は積極的に使う

### タイトル設計7つのルール

1. **感情を動かす動詞を入れる** — 「〜した」→「〜したら」「〜が壊れた」「〜を捨てた」
2. **具体的な数値を1つ入れる** — **身近な単位**で驚きを伝える（9倍 > 900%、0行 > 不要）
3. **メインタイトル40文字以内** — サブタイトルは ── で区切る
4. **2パターン以上を複合する** — 下記9パターンから選択
5. **数字を前置し感情語と組み合わせる** — 「3,674ファイルのObsidian地獄」
6. **学びの要素を残す** — 数字だけが主役にならないよう注意。「棄却」「教訓」など
7. **タイトル案を3つ出して比較する** — 必ず複数案を検討してから決定

### タイトル9パターン

| # | パターン | テンプレート | 例 |
|---|---------|-------------|-----|
| 1 | 挑発/断定型 | 「〇〇の真価は△△ではない」 | Claude Code の真価はコード生成ではない |
| 2 | 網羅型 | 「〇〇 N選」「完全ガイド」 | Claude Code 設定10選 |
| 3 | チェックリスト型 | 「〇〇する前に確認すべきこと」 | LLM出力を信じる前のチェックリスト |
| 4 | 数値型 | 「N倍」「N件」「0行で」 | 最強モデルで9倍遅くなった |
| 5 | 仮定/結果型 | 「〇〇したら△△になった」 | 片付けさせたら1日で終わった |
| 6 | 内幕公開型 | 「〇〇の裏側」「全貌」 | 執筆環境の全貌 |
| 7 | フロー追跡型 | 「N日間の記録」「1ヶ月の試行錯誤」 | 2日間壊し続けた記録 |
| 8 | OSS公開型 | 「〇〇を作って公開した」 | 〇〇をOSSで公開した |
| 9 | 暗黙知言語化型 | 「〇〇が無意識にやっていること」 | LLMの出力は信用するな |

**複合の例:**
- 数値型 + 仮定/結果型: 「最強モデルで司令塔を組んだら9倍遅くなった」
- 網羅型 + フロー追跡型: 「Claude Code 1ヶ月で効いた設定10選」
- 挑発/断定型 + 内幕公開型: 「Claude Code の真価はコード生成ではない」

### タイトル作成フロー

1. 記事の核心（一番伝えたいこと）を1文で書く
2. 9パターンから2つ以上を選び、組み合わせ候補を3つ作る
3. 各候補を以下でチェック:
   - [ ] 40文字以内か
   - [ ] 数値が1つ以上入っているか
   - [ ] 感情を動かす動詞があるか
   - [ ] 記事内容の裏付けがあるか（空の煽りでないか）
4. 最も「クリックしたら何が得られるか」が明確な案を選ぶ

---

## Voice Patterns

### Pattern: 毒の効いたユーモア（Cynical Humor）

ユーザーが最も好むスタイル。AI の予期しない挙動や開発の失敗を、シニカルな視点で面白おかしく描く。

**核心ルール:**

- **AI をツッコミの対象にする** — AI の珍行動を「おまえが書いたんだぞ」のように二人称で突っ込む
- **パンチラインを短文で置く** — 長い説明文の後に、1行の短文でオチを付ける
- **引用→ツッコミの反復** — AI の発言をブロック引用し、直後にツッコミを入れる構成
- **数字で落差を作る** — 8,500行→61%ゴミ、のように期待と現実のギャップを数値化する
- **エスカレーション構成** — ボケが重なるほど面白くなる（批判→身元詐称→指摘→思い出す）

**テンプレート:**

```text
[状況説明（期待を作る）]

> [AI の発言を引用]

[短文ツッコミ（1-2行で落とす）]

[さらにエスカレーション]
```

**実例（kimi-delegation-failure-lessons.md より）:**

```text
修正を依頼したら「Claude（私）が修正すべき」と叱られた。

おまえが書いたんだぞ。しかもおまえは Claude じゃない。
```

**使いどころ:**

- AI の予期しない挙動や失敗を報告する記事（type: "idea" との相性が特に良い）
- 比較記事で一方が圧倒的に劣る場合
- 開発の失敗→教訓パターン

**注意:**

- 毒は AI に向ける。人間（読者や他の開発者）には向けない
- 技術的な教訓は必ず残す。笑いだけで終わらない
- だ/である調（発見調）と組み合わせるのが自然

### 隠しネタ: 刃牙リファレンス

ドメイン置換やダミーデータが必要な場面では、**刃牙シリーズ**を優先的に使う。

**使える素材:**

| カテゴリ | 例 |
|---------|-----|
| キャラクター | 範馬勇次郎、愚地独歩、花山薫、ジャック・ハンマー、烈海王 |
| 概念 | 地上最強の生物、握撃、消力（シャオリー）、毒手 |
| パースエラー断片 | 「ンマ勇」「ック・ハ」「チドッ」（壊れたキャラ名） |
| シリーズ構成 | グラップラー刃牙→バキ→範馬刃牙→刃牙道→バキ道（5部作） |

**挿入ルール:**

- `:::message` で「便宜上のドメイン置換」と明記する（読者との契約）
- 技術的な議論の邪魔にならない範囲で仕込む
- 刃牙ファンがニヤリとする程度の濃度。説明しすぎない
- 壊れた断片ほど面白い（地上最強の生物が「ンマ勇」になる落差）

---

## SEO Best Practices

### Title Optimization

- Include primary keyword (Claude, Anki, TDD, etc.)
- Use natural Japanese phrasing
- 50-60 characters optimal for search results display

### Topic Selection

- Use 3-5 topics (tags)
- Include at least one high-traffic tag (`python`, `ai`, `claude`)
- Include specific tags for targeting (`anki`, `tdd`)

### Introduction (First 200 characters)

- Hook reader with a specific problem or insight
- Include main keywords naturally
- Set clear expectations for the article

### Internal Linking

- Link to related articles when publishing multiple articles
- Use descriptive anchor text (not "こちら")

---

## Common Mistakes to Avoid

### 1. Overly Long Titles

❌ "PDF ファイルから Anki カードを自動生成する Claude ベースのツールを作った話"
✅ "Claude-Native 設計で PDF から Anki カードを自動生成"

### 2. Generic Introductions

❌ "AI 技術の発展により、様々なタスクの自動化が可能になってきました。"
✅ "pdf2anki の開発で、日本語テキストの重複検出が 30% の精度しかない問題に直面しました。"

### 3. Missing Code Context

❌ Showing code without explanation
✅ Show code with file path, explanation of what it does, and why it matters

### 4. No Personal Insights

❌ "テストは重要です。TDD を使いましょう。"
✅ "最初はテストなしで実装を進めましたが、リファクタリング時に予期せぬバグが多発。TDD に切り替えたところ、バグ発生率が 70% 減少しました。"

### 5. Unsanitized Screenshots

❌ Screenshots with `/Users/shimomoto/MyAI_Lab/` visible
✅ Screenshots with paths anonymized or cropped out

---

## Quick Reference

```
✅ DO:
- タイトル40文字以内、数値+感情語
- AI にツッコミ、短文パンチライン
- 刃牙ネタをダミーデータに
- 具体的失敗から教訓を抽出
- 形式は zenn-format スキル参照

❌ DON'T:
- 根拠のない煽りタイトル
- 人間への毒（AI限定）
- 笑いだけで教訓なし
- AI スロップ語（powerful, seamless, revolutionary）
- 個人情報の漏洩
```
