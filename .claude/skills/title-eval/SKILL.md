---
name: title-eval
description: タイトルの二値チェック判定器（ADR-0008 の第三の eval）。headline-craft が生成した候補群を、記事本文との軸一致・誠実さ・好奇心ギャップ充足・チャンネル軸適合で判定し、named verdict（Adopt 候補 / Refine / Keep-current）を返す。生成は headline-craft、規範は writing-ecosystem Title Conventions、判定形式は llm-as-judge に defer する。Use before publish, after the draft is frozen — タイトルは開封の大半を決めるため、theme-eval / article-judge と同格のループを回す。
origin: shimo4228
---

# title-eval — タイトルの判定ループ

> 生成技法の正本: `~/.claude/skills/headline-craft/SKILL.md`
> 規範（禁止事項）の正本: `~/.claude/skills/writing-ecosystem/SKILL.md` の Title Conventions
> 判定形式の正本: `~/.claude/skills/llm-as-judge/SKILL.md`（二値チェック → 反証プレッシャー → 集計しない named verdict）
> 根拠: Kaguura 2026「タイトルは戦いの 90%」。本文の eval（theme-eval / article-judge）だけ厳格でタイトルが無判定なのは、開封率のボトルネックを未計測のまま残すことになる（2026-08-13 著者指摘で新設）

## 原則

1. **本文凍結後に回す** — タイトルは本文の core claim の圧縮なので、本文が動くうちは判定しない
2. **判定は fresh context** — 執筆セッションの文脈を持つと「作った側の愛着」で甘くなる
3. **最終選択は必ず著者**（Content Integrity: タイトルの語選びは Distribution 層 — 判定器は序列と根拠を出すだけ）
4. **ループは生成 → 判定 → Refine 1 回まで** — それ以上回すと候補が均質化する

## 入力

- 記事本文（凍結稿）と core claim 1 文
- タイトル候補 3〜6 本（headline-craft の手順で生成。現行タイトルがあれば必ず含める）
- チャンネル（note = フィード軸 / Zenn = 検索・フィード両軸 + 50–60 字制約 / Dev.to = EN フィード軸）

## Step 1 — 候補ごとの二値チェック（各 1 行証拠必須）

| # | 質問 |
|---|---|
| TT1 | **軸一致**: タイトルの約束は、本文の最重要主張で回収されるか（副次論点をタイトルにしていないか） |
| TT2 | **具体性**: タイトルだけで「何についての記事か」が分かるか（詩的・教科書調の排除） |
| TT3 | **誠実さ**: 本文以上の約束をしていないか（writing-ecosystem 禁止リスト照合: 煽り・空の数字・挑発・感情語） |
| TT4 | **ギャップ充足**: 好奇心ギャップを作っているなら、本文がそれを完全に埋めるか（埋めないギャップ = クリックベイト） |
| TT5 | **飾り語ゼロ**: ポジティブ形容詞・ヘッジ語尾（「〜の話」「〜について」「〜メモ」）がないか（Upworthy 実証: ポジティブ語は CTR を下げる） |
| TT6 | **具体の検討痕**: 数字・期間・固有名を入れる余地を検討したか（入れない判断は可。未検討は No） |
| TT7 | **チャンネル軸適合**: 対象チャンネルの流入経路（フィード/検索）で指が止まる形か |
| TT8 | **字数帯**: 日本語 20〜36 字目安（platform overlay があればそちら優先。Zenn は 50–60 字上限） |

## Step 2 — 反証プレッシャーテスト（上位候補に必須）

1. **ミスマッチ検査**: このタイトルを見て開かない読者は、本文を読むべき読者か（読むべき読者を弾くタイトルは、開封率が高くても失格）
2. **対抗生成**: 判定器自身が最強の対抗タイトルを 1 本作り、上位候補が勝る理由を 1 行で言えるか。言えなければ Refine

## Step 3 — named verdict（候補ごと + 全体）

| verdict | 意味 | 次アクション |
|---|---|---|
| **Adopt 候補** | TT1–TT8 全 Yes + 対抗に勝る | 序列付きで著者へ提示（最終選択は著者） |
| **Refine** | 特定 TT の No が修正可能 | No の指摘を添えて headline-craft に 1 回だけ再生成させる |
| **Keep-current** | 新候補が現行を上回らない | 現行維持を著者に推奨 |

## 配線

- writing-team Mission A: step 12（seo-optimizer / 公開直前）の中で本 skill を回す。note エッセイは seo-optimizer を使わないため title-eval 単体で回す
- 判定は article-judge と同様 fresh agent で実行し、判定器の対抗タイトルも著者への提示に含める（判定器の生成物も候補プールに入れてよい — 選ぶのは著者）

## Related

- `~/.claude/skills/headline-craft/SKILL.md` — 候補生成（技法カタログ・流入 2 軸）
- `~/.claude/skills/writing-ecosystem/SKILL.md` — Title Conventions（規範）
- `.claude/skills/theme-eval/SKILL.md` / `.claude/agents/article-judge.md` — 同形式の既存 2 判定器
- `.claude/skills/seo-optimizer/SKILL.md` — Zenn の topics/emoji（本 skill はタイトル判定のみ）
