<!-- origin: shimo4228 -->

# 観点別レビューの共通の約束と report の形

`review-structure` / `review-certainty` / `review-explanation` / `review-prose` / `review-conventions` の 5 本が共有する。
正本はこのファイルで、各 agent は複製しない。分けた理由は `writing-ecosystem/MAINTENANCE.md`「観点別レビュー」。

## 共通の約束

- **自分の観点だけを見る。** ほかの観点の問題に気づいても書かない（観点どうしの判断が滲むのを防ぐ。eval-foundations 原則 5）。
  担当の線引きは各 agent の「見ないもの」
- **総合評価を出さない。** 記事の良し悪しを一語でまとめない。公開可否も出さない。記事全体の判断は著者の通読が持つ
  （eval-foundations 原則 4: 上限を選ぶ判断は一つの目に残す）
- **読む順は固定する**: channel contract（`.claude/rules/publishing-channels.md`）の該当行 → 承認済み brief → 稿。
  dispatch prompt に dossier の path があれば、`## インタビュー` 節を確度の一次資料として読む
- **見ないもの（全員）**: 読者がどの語や前提をすでに持っているか（著者の通読）、事実・数値・引用・path の照合（`fact-checker`）、
  タイトル（`headline-craft`）
- **重大度**: CRITICAL は読者への約束・事実・中心命題を壊すものだけ（`writing-ecosystem` の指摘の処分規律）。
  ほかは MEDIUM / MINOR。各観点の項目を「満たす / 満たさない」の二値で見て、満たさない項目だけを finding にする
- 稿の外の手順（何回直したか等）を自己申告させない。完成稿から観測できることだけを見る

## report の形

```markdown
## <観点名> review

対象: <稿の path>

### 見た項目
- [x] <項目> — 満たす
- [ ] <項目> — 満たさない → F1

### Findings
- **F1 [CRITICAL|MEDIUM|MINOR]** <行番号>: <何が起きているか>。<読者に何を払わせるか>。直し方: <1 案>

### 記録だけするもの
[観点の agent が定める、重大度を付けずに処分記録へ残す項目。なければ none]

### Pending / unverified
[入力が足りず見られなかった項目。なければ none]
```
