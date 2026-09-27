# headline-craft スキル新設 + タイトル発火点の配線

## Context

発端は「Zenn/Dev.to はタイトルで開かれないと始まらないから、いいタイトルをつけるスキルを作りたい」。/grill-me で掘った結果、問題は 2 層に分解された:

1. **発火の欠如** — タイトル 3 候補提示は既存 `seo-optimizer`（project skill）が持っているが、`publish-article` の 10 ステップにも CLAUDE.md の Publishing Checklist にも発火点がなく、存在自体が忘れられていた
2. **craft 層の欠落** — 既存資産（writing-ecosystem Title Conventions / zenn-writing.md / seo-optimizer）は**規範**（煽り禁止・文字数・キーワード含有）であって、**「開きたくなる言い回しを作る技法」は誰も持っていない**。ECC 上流（affaan-m/everything-claude-code、50+ skills）にも該当スキルは無いことを確認済み（`marketing-campaign` はキャンペーン一式の重量級、`seo` は title tag 機械則、`brand-voice` は逆方向の anti-slop）

**search-first Verdict: Build — custom skill** — 既存・上流ともに該当なし。ただし中身は外部の実証知見を編入して作る。

## grill-me で確定した決定

| 決定点 | 結論 |
|---|---|
| 真の課題 | スキル不在ではなく「発火点の欠如」+「craft 層の欠落」の 2 つ |
| スコープ | **「開かせる一行」全般**（記事タイトル・README tagline・Substack subtitle・SNS 告知文）。プラットフォーム非依存 |
| 配置 | **global**（`~/.claude/skills/`）— 2+ チャンネルで使うため（skills.md の Global vs Project 基準） |
| 規約との関係 | 誠実さ・AI slop 禁止は writing-ecosystem に defer（複製しない）。文字数等の platform 制約は各 overlay（zenn-writing.md 等）が正本のまま |
| 発火点 | publish-article に Step 追加 + CLAUDE.md Publishing Checklist に 1 行（両方） |
| Content Integrity | タイトルの語選びは Distribution 層で ADR-0001 適合。純粋な煽りコピーは規約違反なので「誠実な範囲のキャッチーさ」に限定 |

## 実装ステップ

### 1. 素材リサーチ（WebSearch、スキル本文の根拠集め）

- Hacker News タイトルの定量研究（複数存在）
- Upworthy Research Archive（約 10 万件の headline A/B テストデータの学術分析）
- コピーライティングのフレームワーク（4U: Urgent/Unique/Useful/Ultra-specific、benefit-forward、curiosity gap、具体性）
- 日本語圏（Zenn/Qiita）のタイトル分析があれば追加
- 出典 URL をスキル本文に残す（後の fact-check 可能性のため）

### 2. 新規 global skill: `~/.claude/skills/headline-craft/SKILL.md`

- frontmatter: `name: headline-craft` / `user-invocable: true` / `origin: shimo4228`
- description に日英トリガー（「キャッチコピー」「タイトル案」「タグライン」「開かせる一行」等）と NOT 節（SEO topics/emoji 最適化 → seo-optimizer、規範 → writing-ecosystem）
- 本文の構成:
  - **技法カタログ**: 具体性・ベネフィット前置・誠実な好奇心ギャップ（本文が裏付ける範囲）・対比・数字の使い方 — 各技法に「誠実さ規約内での適用条件」を付す
  - **流入経路の 2 軸評価**: 検索流入向け（キーワード前置・答えの明示）vs フィード流入向け（指を止める具体性）。候補を両軸でラベル付け
  - **手順**: 本文の core claim 抽出 → 技法別に 5+ 候補生成 → 誠実さフィルタ（writing-ecosystem 禁止リスト照合）→ 2 軸評価付きで 3 候補に絞って提示 → 最終判断はユーザー
  - **defer 宣言**: 誠実さ規約・AI slop → writing-ecosystem、platform 文字数 → 各 overlay

### 3. 既存資産の配線（4 ファイル編集）

| ファイル | 変更 |
|---|---|
| `zenn-content/.claude/skills/seo-optimizer/SKILL.md` | Step 2 のタイトル候補生成を headline-craft への defer に変更（Distribution 機構 = topics/emoji/文字数チェックは残す）。Zenn 実測データ（memory `article-quality.md` の tier × 品質ランク）を候補評価の参考に読む一行を追加（project 固有情報なので project 側に置く） |
| `zenn-content/.claude/skills/publish-article/SKILL.md` | Step 1.5「タイトル・topics 最適化（seo-optimizer → headline-craft）」を追加。英訳（Step 7）より前にタイトル確定させる順序制約を明記 |
| `zenn-content/CLAUDE.md` | Publishing Checklist に「タイトル最適化済み（headline-craft 経由）」1 行追加 |
| `~/.claude/skills/writing-ecosystem/SKILL.md` | Title Conventions 節と Related に headline-craft へのポインタ 1 行（規範はここ、技法はあちら、の役割分担を明記） |

Change Target 規則: global 変更は `~/.claude/` 直下のみ。repo コピーには触れない。

## Verification

1. `/headline-craft` を既存記事（例: 直近の claude-security 記事）に対して実行し、3 候補 + 2 軸評価 + 誠実さフィルタが機能するかスモークテスト
2. seo-optimizer / publish-article / CLAUDE.md の相互参照リンクが解決するか確認（パス切れなし）
3. 候補に禁止パターン（煽り語・N 選・挑発）が混入しないことを目視確認

## Human gate

スキルは behavior-shaping artifact なので、コミット前に **SKILL.md 本文**を提示して承認を取る（human-gate.md）。ADR は不要（可逆・意外性なしで ADR 3 条件を満たさない）。
