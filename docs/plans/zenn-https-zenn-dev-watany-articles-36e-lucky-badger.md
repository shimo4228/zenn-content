# Zenn 記事に eli5 図と visual-first craft を足す — pilot 先行

## Context

著者の観察: Zenn ではすぐ使えることが端的に載り、図で認知負荷を下げた記事が伸びる
（watany「Jevでハーネスエンジニアリング」157 likes、nwn「TypeSafeのJevを正しく驚く」178 likes）。
この 2 本と、2026-09-01〜09-22 の Zenn 全記事 4,272 本からいいね上位 30 本を API で取り、本文構造を
著者の直近 12 本と比べた（as-of 2026-09-22）。

### 実測（上位 30 本 vs 著者直近 12 本）

| 指標 | 上位 30 本 | 著者 12 本 |
|---|---|---|
| 本文字数の中央値 | 約 6,300 | 約 9,500 |
| 画像（screenshot / 図）を 1 枚以上持つ | 14 / 30 | 1 / 12 |
| link card / tweet / mermaid の埋め込みを持つ | 24 / 30 | 0 / 12 |
| 表を持つ | 12 / 30 | 9 / 12 |
| 段落長の中央値 | 約 80 字 | 約 77 字 |

段落長と表は差がない。差は **字数・図・埋め込み** に集中する。文体（常体 / ですます）は差にならない。

### 上位記事が共有する装置

1. **第一画面が成果物**: nrs は `## TLDL` にコピペ用プロンプト。mizchi は 1 文目直後に repo link と
   実験結果。jev-lint は「問題 1 文 → 作りました → `npx -y jev-lint`」。tenkei は矢印 1 行の流れ図
2. **構造図**: watany は ChatGPT 生成の対比図（LLM vs Jev）を冒頭に置き本文は約 3,000 字。nwn は
   ASCII の流れ図。a_kadowaki は論文図 5 枚
3. **eli5 比喩を 1 個、構造を運ぶ位置に**: mizchi はタイトルが比喩（「LLM が CPU なら Jev は GPU」）。
   watany「超高速で使える if 文 API」。ml_bear「スライムにメラゾーマ」
4. **証拠は埋め込みへ**: 実験ログ・ADR・実装は link card / tweet に逃がし、本文は判断と数値だけ

### harness の現状

- `.claude/skills/writing-ecosystem/SKILL.md`: 図・表・画像・第一画面の成果物への言及が 0。
  `Craft 規約` L237「見慣れた比喩は使わない」は陳腐な比喩の禁止で eli5 比喩は未規定。
  `references/style-diagnostics.md:26`「prose で足りる箇条書き → 文でつなぐ」が箇条書きへの一方向の圧
- `.claude/skills/zenn-format/SKILL.md`: 画像構文と sanitize (L78-84)、`:::message` / `:::details`
  (L94-110) はあるが、表と図の置き方の節が無い
- `.claude/agents/editor.md:81`「飾りの snippet」は code / 出力だけ。図・表・第一画面の成果物は検査外。
  `prose-clarity-reviewer.md` L24-33 の第一画面基準も文章だけ
- 既存記事 79 本: 表 66、`:::message` 33、画像 8、mermaid 4、TL;DR 0
- `eli5` plugin skill（`~/.claude/plugins/cache/claude-community/eli5/1.0.0/skills/eli5/SKILL.md`）は
  「HTML artifact with big pictures and few words」の 3 行。図の入口はこれを使う（著者決定 2026-09-22）
- Zenn GitHub 連携の画像: `/images` 直下、`.png .jpg .jpeg .gif .webp` のみ、3MB 以内、SVG 不可
  （Zenn 公式 deploy-github-images、as-of 2026-09-22）
- PNG 化: HTML の描画に headless browser が要る。このセッションの Playwright MCP
  （`browser_navigate` / `browser_resize` / `browser_take_screenshot`）で撮る。`magick` は HTML を描画できない

### 著者の方針（2026-09-22）

- 図は **本文を書き終えてから** eli5 で起こし、**対応する節ごとに置く**。書きながら描かない
  （本文修正のたびに図を直す手戻りが無く、panel 凍結時 1 回の運用と噛み合う）
- 図の一覧がそのまま骨格の点検になる。図にできない節は「並列（list）」か「図の要らない節」
- pilot は直近記事 `articles/jev-retrofit-limits.md`（Zenn は rate limit で未デプロイ、404 継続中。
  約 7,700 字、6 節）。図を足した修正版を push する。push は上限解除後の deploy 再 trigger も兼ねる
- 規約（harness）は pilot の後に、pilot で分かった手順から書く

### 境界

CLAUDE.md「metrics must not deform an idea, doctrine decision, or existing article body」。本件は提示
形式の追加で、**本文の文は変えない**（図の直後の 1 文と alt text だけ足す）。Dev.to の EN 版は更新
手段が無いので遡及しない。artifact としての公開はしない（図は repo 内 HTML → PNG）。

## Phase 1 — pilot: `articles/jev-retrofit-limits.md` に eli5 図を置く

### 1-1. 節ごとの図の割り当て（草案。著者が削る）

| 節 | 形 | 図 | eli5 の 1 文 |
|---|---|---|---|
| 冒頭（第一画面、L16 の後） | 並走 | `hero` | 1 行足しても、スキルを選ぶ役は Claude Code が持ったまま。Jev の判定は横を並走している |
| Claude Code のスキル選択は、そのまま走っていました | 対比 | `conditions` | cookbook は弱い選び手（Haiku）に 60 字の索引、Claude Code は強い選び手（Fable）に 1,536 字の全文。メモを渡して効くのは前者だけ |
| スキル一覧を書き換える道 + その道は前日に歩かれていた | 階層（3 つの道） | `three-roads` | 1 行足す（additionalContext）/ 一覧を書き換える（Mods `skill_listing`）/ 公式設定で隠す（`skillOverrides`）。私は 1 つ目で止め、2 つ目は前日に他人が作っていた |
| 選ぶ役を誰が持っているか | 2 軸 | `who-picks` | 選び手が弱い × 助言 = 効く（cookbook）/ 強い × 助言 = 効かない（Claude Code）/ 強い × 選ぶ役に届く = 効く可能性（Mods, pi-jev） |
| 足す前に確かめる 3 つ | 並列（番号 list のまま） | なし | — |
| 関連リンク | — | なし | — |

4 枚。多ければ `who-picks` を落とす（`conditions` と重なる）。

### 1-2. 生成

図ごとに `/eli5 <上の 1 文>` を呼び、制約を添える: 1600×900 の 1 画面、要素 6 個以内、文字は名詞句、
比喩は読者の既知物 1 個、色は 2 色 + 灰、日本語フォントは system-ui。出力 HTML を
`figures/jev-retrofit-limits-<what>.html` に保存する（artifact 公開はしない）。

### 1-3. PNG 化

Playwright で各 HTML を 1600×900 で開き `images/jev-retrofit-limits-<what>.png` に screenshot。
3MB 超なら webp。個人 path・credential が写らないことを確認。

### 1-4. 配置

各節の見出し直後（hero は L16 の段落の後）に次を足す。本文の既存の文は変えない。

```markdown
![<図が示すこと 1 文>](/images/jev-retrofit-limits-<what>.png)
```

図の直後に「この図が示すこと」1 文を置く（editor の「記録で、意味が無い」対象外にする）。

### 1-5. 検収

- `fact-checker` に図の文字（数値・モデル名・字数）と本文の差分だけを照合させる
- `npm run evidence -- articles/jev-retrofit-limits.md`、`npm run validate`
- 著者の通読 GO（図 4 枚の採否と配置）。GO 後に commit、push（公開 = 人間に渡す操作。指示は出ているが
  GO を受けてから）。push 後 Zenn デプロイ履歴を確認

## Phase 2 — pilot の手順を規約化（すべて project-local `.claude/`。global は触らない）

### 2-1. `writing-ecosystem/SKILL.md` — `### 具体物を先、説明を後` の直後に `### 認知負荷の設計`

- **第一画面は成果物**: Zenn / Dev.to は最初の見出しの前に、読者がそのまま使える 1 個
  （コマンド / プロンプト / repo link / 流れ 1 行 / hero 図）。予告文は成果物の代わりにならない
- **図は凍結後に、節ごとに**: 著者の内容 GO の後、節ごとに「形」（対比 / 流れ / 階層 / 並列）を
  1 語で言い、並列以外は `/eli5` で 1 枚起こす。言えない節は図を置かない。1 記事 3〜4 枚まで
- **eli5 比喩は 1 記事 1 個**、タイトル・第一画面・hero 図のどれかに。既存の「見慣れた比喩は使わない」
  との両立条件は、外すと中心命題の形が消えること
- **表 / 箇条書き / 散文**: 比較は表、並列は箇条書き、因果は散文
- **証拠は埋め込みへ**: 実験ログ・設定全文・ADR は link card か `:::details`。本文は判断・数値・trade-off
- **長さの目安**: 上位記事中央値 6,300 字を brief の参照値に。上限ではなく、超えたら「図 1 枚で置き換え
  られる節は無いか」を問う契機

brief（L79 付近、`Entry bridge` の並び）に 2 field:

```
First-screen deliverable: <第一画面で持ち帰る 1 個（コマンド / プロンプト / repo / 流れ 1 行 / 図）>
Figure plan: <凍結後に埋める。節 → 形 → 図の有無。書けない節は「並列」か「なし」>
```

`First-screen deliverable` が埋まらない稿は Zenn でなく note 行きの信号として扱う（規約の一番の価値）。

### 2-2. `zenn-format/SKILL.md` — `### Images` の後に `### Tables` と `### Figures`

- 表: 比較にだけ。列は 3〜4 まで、行頭の列に読者が探す語
- Figures: Phase 1 の 1-2〜1-4 を手順として書く（`/eli5` → `figures/<slug>-<what>.html` →
  Playwright screenshot → `images/<slug>-<what>.png` → 見出し直後に配置 + 1 文）。alt text 必須、
  3MB、sanitize は既存規約のまま。本文を直したら HTML を直して撮り直す
- mermaid: 流れ図で補うときだけ。node 8 個まで

### 2-3. `agents/editor.md`

- §2 に `[ ] 最初の見出しの前に、読者がそのまま使える成果物が 1 個ある`
- L81 を「載せた code / 出力 / 図 / 表は最小で、直前の主張を運んでいる（飾りの snippet と飾りの図を指摘）」
- §3 に `[ ] 比喩は 1 記事 1 個で、外すと中心命題の形が消えるか`

### 2-4. `agents/prose-clarity-reviewer.md` L24-33

「図または成果物があれば、それだけで対象と成果が読み取れるか。本文を読まないと図の意味が分からないなら指摘」を 1 行。

### 2-5. `writing-ecosystem/references/style-diagnostics.md:26`

「prose で足りる箇条書き | 因果を文でつなぐ」→「因果を箇条書きにしている | 文でつなぐ。並列・比較は箇条書き・表のまま」。

### 2-6. `.claude/rules/publishing-channels.md` Zenn 行

Deterministic checks に人手確認 1 行「第一画面の成果物と Figure plan が brief と一致」。機械化しない。

### 2-7. review-when

`writing-ecosystem` の新節に `review-when: 2026-11-01、または Zenn の画像規約変更、または pilot 含む
3 本の article-stocktake で差が出ない`。差が出なければ Scaffold Dissolution で縮める。

## 触らないもの

- `articles/jev-retrofit-limits.md` の既存の文（足すのは図 + 1 文 + alt だけ）と他の公開済み記事
- global `~/.claude/`、`eli5` plugin skill 自体
- 文体（ですます）と reviewer panel の構成
- Dev.to EN 版（更新手段なし）

## 検証

1. Phase 1: 図 4 枚が `/images` 直下に 3MB 以内で出る。日本語が描画されている（目視）。
   `npm run evidence` と `npm run validate` が緑。fact-checker の図 vs 本文差分に INACCURATE 0
2. Phase 1: push 後、Zenn デプロイ履歴で 404 が解消（rate limit 解除待ちの可能性あり。解除まで待つ）
3. Phase 2: `writing-ecosystem/SKILL.md` を fresh context の subagent に読ませ、新節と brief の 2 field が
   1 文で言えるか確認（skill-creator の草稿ゲートに準ずる）
4. Phase 2: `editor` に pilot 記事を読ませ、新項目 3 つが検査として動くことを確認
5. `npm run check:index` が緑（索引に変更なし）
