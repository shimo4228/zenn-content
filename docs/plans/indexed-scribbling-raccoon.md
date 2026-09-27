# codex-review 記事（Zenn/Dev.to）執筆プラン

## Context

`codex-review` skill（OpenAI Codex CLI を使った read-only なクロスモデルレビュー）は、著者のハーネスで実際に価値を発揮している一方、既存記事には一度も登場していない。grill-me での議論を通じて、単なる「便利ツール紹介」ではなく次の3点を核とする記事にすることで合意した:

1. 汎用的な使い方（誰でも真似できる基本操作）
2. ハーネス固有の仕組み — `planning.md` の Review/Cleanup ステップに組み込むことで、明示指示なしに検証プロセスとして自動実行される
3. 実際に根本的なバグを見つけた具体例 — Contemplative Agent repo（ADR-0071、コミット `224fdd9`）で codex-review が P2×2/P3、python-reviewer が CRITICAL 1件を検出し、互いに異なるクラスの盲点を補完した実演

主張の軸は「見つける頻度が高い」ではなく「同じ diff に対し別モデル系統は別クラスの失敗を見る（脱相関）」という質的なもの。ADR-0013 の設計根拠（同一モデル=スループット軸、別モデル=脱相関軸）と一致し、fact-checker に対しても検証可能な形になっている。

ユーザーからの追加指示（重要）: 実名使用の許可 ≠ 全ディテールを出す義務。読者が前提知識なしで理解できることを優先し、insider な用語（ADR番号・内部フィールド名等）は論点を支えるのに必要な分だけ残す（`feedback_specificity-vs-clarity.md` として memory 済み）。

## 対象規約（確認済み）

- 声・構造: `.claude/skills/zenn-practical-writing/SKILL.md`（ですます・実用軸・テンプレート: タイトル→前提→手順(逆引き見出し)→落とし穴/Tips→まとめ）
- Acceptance checklist: 冒頭1行サマリ / 前提列挙 / コピペで動く実コード / 図表1つ以上 / 見出しはoutcomeを述べる / 1見出し1論点 / AI slop 禁止 / 独立した論点は4つ以内 / ですます統一 / 1セクションが全体の30%を超えない
- frontmatter: `.claude/skills/zenn-format/SKILL.md`（title/emoji/type/topics/published(+published_at)）
- 参考記事: `articles/termius-iphone-claude-code.md`（ですます調の実例として声のトーン確認用。構造モデルとしては使わない — `skill-stocktake-design-journey.md` はだ/である調で構造のみ参考）

## 記事アウトライン（案）

```
# タイトル案: 「Claude Codeのレビューに別モデルの目を混ぜる — codex-reviewという一点連携」
（50-60字以内に収まるよう最終調整。Distribution層の語選びなので執筆時に微調整可）

> この記事でわかること: Claude Code に OpenAI Codex CLI を使った
> クロスモデルレビューを一点だけ足す方法と、それが効く理由

## 前提
- Codex CLI インストール・認証済み（`codex login` / `codex doctor`）
- Claude Code + git リポジトリ

## 使い方 — read-only な second opinion を一発で
- `/codex-review` の基本コマンド表（--uncommitted / --base / --commit / prompt-driven）
- read-only 不変条件（allowlistでコード側に保証、`codex exec -p yolo` は使わない）
- 実コード: 実際のスクリプト呼び出し行 + 出力の fold-don't-dump（構造化サマリ形式）

## ハーネスに「自動で走る検証」として組み込む
- 「明示指示しても毎回頼み忘れる」問題 → プロジェクトルールのReview/Cleanupステップに
  条件を書いておけば、実装が一段落した時点で自動的に発火する、という一般化パターンを提示
  （ユーザー固有の planning.md 全文は出さず、他プロジェクトでも真似できる最小形の
  ルール例だけ抜粋する — insider-context を避ける）
- CRITICAL 検出時は早期停止する、という判断の持たせ方

## 実際に何を見つけたか — 脱相関の実演
- Contemplative Agent（実名、ADR-0071 / commit 224fdd9 で一次確認済み）
- 表: codex-review が見つけたもの（P2×2, P3）vs python-reviewer が見つけたもの（CRITICAL）
  → 「同じ diff、別クラスの盲点」を一目で見せる
- 内部用語（ADR番号・gated・view閾値等）は表の脚注レベルに抑え、論旨に要る分だけ

## 落とし穴 / Tips
:::details ハマったら
- scope と prompt は排他（同時指定は exit 64）
- HEADが既にbase branchの時は自動でuncommittedにフォールバック
- Codex未認証時はexit 3で通知、Claude単独レビューにフォールバック
:::

## まとめ（次にできること）
- 自分のプロジェクトルールに1行足すだけで再現できる、という締め
```

## 執筆後のフロー（既存規約どおり）

1. `editor` + `fact-checker` + `codex-review`（cross-model, prompt-driven, 公開前の高stakes記事のため）を並列起動
2. 修正 → ユーザーに内容確認 → `published: true` + `published_at` 設定
3. `git push`
4. `devto-translator` エージェントで EN 翻訳 → Dev.to 投稿
5. `schedule.json` 更新（週2-3本ペース・火水7-9時バズタイムを考慮して日程調整)

## 検証方法

- `npm run lint`（textlint + markdownlint）
- `npm run preview` で Zenn プレビュー確認
- fact-checker の verdict が ACCURATE であること（特に「脱相関」の質的主張と ADR-0071 引用の正確性）
- editor の verdict が MAJOR ISSUES でないこと
