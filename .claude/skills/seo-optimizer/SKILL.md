<!-- origin: original -->
# SEO Optimizer Skill

**Purpose:** Zenn 記事のタイトル・topics・emoji を最適化し、関心のある読者に記事が届くようにする。
内容の改変は行わない（[ADR-0001](../../.claude/docs/adr/0001-content-integrity-principle.md) Content Integrity 原則）。

> **タイトル規約・AI slop の正本:** `~/.claude/skills/writing-ecosystem/SKILL.md`（Zenn 固有ルールは `.claude/rules/zenn-writing.md`）

---

## Usage

```
/seo-optimizer articles/ARTICLE_NAME.md
```

---

## Optimization Flow

### Step 1: 現状分析

記事の frontmatter と冒頭 200 文字を読み取り、以下を評価する:

| 項目 | 評価基準 |
|------|---------|
| **タイトル** | 50-60 文字、キーワード含有、具体性 |
| **Topics** | 3-5 個、高トラフィックタグ + 特化タグの組み合わせ |
| **Emoji** | 記事テーマとの関連性 |
| **冒頭文** | フック力、キーワード自然含有 |

### Step 2: タイトル最適化

**方針（2026-03-24 改訂 — zenn-writer と整合）:**

タイトルの目的は**概念の誠実な呼びかけ**。読み手がタイトルだけで「何の概念を提案しているか」理解できること。

**原則:**
- **50文字以内**。概念を正確に伝えることが最優先
- **主要キーワード**を含める（SEO 観点）
- **問いの形を活用** — 「どう〜するか」「なぜ〜か」は知的関心に訴える
- **クリックベイトは厳禁** — 煽り語（「壊れている」「地獄」「最強」）、数字だけの訴求（「N選」「N倍」）は使わない

**提案時のルール:**
- 3 つの候補を提示
- 各候補に「この概念がどう伝わるか」の理由を添える
- 現在のタイトルとの比較を示す

### Step 3: Topics 最適化

**高トラフィックタグ（優先的に含める）:**
- `python`, `typescript`, `javascript`, `react`, `nextjs`
- `ai`, `chatgpt`, `claude`, `llm`
- `機械学習`, `docker`, `aws`, `terraform`

**特化タグ（記事の独自性を示す）:**
- `anki`, `pdf`, `tdd`, `cli`, `automation`
- `nlp`, `tokenization`, `testing`

**組み合わせ戦略:**
```
[高トラフィック 1-2] + [特化 1-2] + [技術スタック 1]
例: ["claude", "ai", "anki", "python", "tdd"]
```

**チェック:**
- Zenn で各タグの記事数を Web 検索で確認
- 記事数が多いタグ = 閲覧されやすいが競合も多い
- ニッチなタグ = 競合少ないがリーチも限定的
- バランスが重要

### Step 4: Emoji 最適化

| テーマ | 推奨 Emoji | 理由 |
|--------|-----------|------|
| AI/LLM | 🤖 🧠 ✨ | 直感的に AI を連想 |
| 学習/教育 | 📚 🎓 📝 | Anki/学習系に適合 |
| テスト/品質 | 🔬 ✅ 🧪 | 技術的厳密さを表現 |
| 開発ツール | ⚙️ 🛠️ 💻 | エンジニア向けの印象 |
| パフォーマンス | ⚡ 🚀 📊 | 改善・高速化の印象 |
| 設計/構造 | 🏛️ 🗺️ 🧩 | アーキテクチャ系 |
| 移行/変更 | 🔄 🚚 🔀 | 移行記事に適合 |

---

> **Note:** 冒頭文（リード）の最適化は Content Integrity 原則により廃止。著者が自然に書いた冒頭をそのまま使う。

## Output Format

```markdown
## SEO 最適化提案

### 現状
- タイトル: "{current_title}" ({n}文字)
- Topics: {current_topics}
- Emoji: {current_emoji}

### タイトル候補
1. **"{title_1}"** ({n}文字)
   - 理由: {why}
2. **"{title_2}"** ({n}文字)
   - 理由: {why}
3. **"{title_3}"** ({n}文字)
   - 理由: {why}

### Topics 提案
- 現在: {current} → 提案: {proposed}
- 理由: {why}

### Emoji 提案
- 現在: {current} → 提案: {proposed}
- 理由: {why}
```

---

## Notes

- 最終判断は**ユーザーに委ねる**（選択肢を提示するだけ）
- SEO のためにクリックベイトにならないよう注意
- Zenn のトレンドや検索傾向は変化するため、提案は参考値として扱う
