# Herdr 2 記事を 1 本の良質な記事に統合する

## Context

- `articles/herdr-agent-multiplexer.md`（前作、push 済み・Zenn 予約登録済み JP 7/21 09:00、EN launchd 予約 7/20 22:00）と `articles/herdr-zed-review-surface.md`（続編ドラフト、未コミット）を統合し、シリーズ化せず 1 本の高密度記事として公開する。ユーザー判断:「シリーズより 1 本の質で信頼を得る」
- 種別: `writing` → Writing Chain（zenn-practical-writing に従いオーケストレーター本体が直接執筆。レビューは editor + fact-checker + codex-review 並列）

## ユーザー決定事項（確認済み）

| 項目 | 決定 |
|---|---|
| 公開日 | **7/21 (火) 09:00 JST のまま維持**。既存スラッグ `herdr-agent-multiplexer` を統合版で上書き（予約登録済みなのでレートリミット再登録なし） |
| 統合方針 | **一本の弧に絞って刈り込む**（単純連結 ~440 行 → 目標 300 行前後） |
| タイトル | 「エディタ」表記が正確（Zed は公式に code editor を名乗る。IDE ではない）。案: **「AI エージェント版 tmux「Herdr」— エディタが要らなくなるまで」**（28 字） |

## 統合後の構成（単一ストーリー）

「並列管理の壁 → Herdr 導入 → エージェント自身が環境を操作して評価反転 → Zed が検収ビューアに縮退 → プラグインで検収ループが Herdr 内に閉じ、エディタ消滅」

1. **この記事でわかること** — 両記事の要素を統合（並列監視・SSH 復帰・エージェントによるレイアウト操作・エディタの役割縮退の実録）
2. **はじめに** — 前作の導入（並列エージェントの置き場所問題）をベースに、結末（エディタ消滅）の予告を追加
3. **前提** — 統合（macOS + Homebrew / Herdr v0.7.4 / Ghostty / Claude Code）
4. **Herdr とは** — 前作のまま（tmux との差分 2 つ）。repo 統計は後方の bot 節へ寄せて重複排除
5. **導入** — 前作のまま（brew + smoke test）
6. **Zed で足りる範囲、足りない範囲** — 前作のまま（比較表・CLI 起動トラップ）
7. **エージェント自身にレイアウトを操作させる** — 前作のまま（記事の核。Before/After・環境変数・worktree・:::details トラップ 3 本）
8. **サイドバーは「状態」か「履歴」か** — 前作のまま。主役画面の反転（エディタがオンデマンド側へ）が次節への布石
9. **一度は住み分けで落ち着いた** — 前作の結論節を**移行段落に圧縮**（住み分け表は削除、ミラー実測・スリープ注意は :::details に退避して保持）
10. **Zed に残った 3 つの仕事 → 検収の道具へ** — 続編から（`zed file:line` / `--wait` 承認ゲート）
11. **日本語表示の壁とホスト交代** — 続編の 2 節を統合圧縮（Markdown 行間は短く + zed#56111 リンク維持、表崩れ→対照実験→Ghostty 移行は保持、テーマ入れ子統一は短縮）
12. **作者と bot による個人開発** — 続編から。前作の基本情報（113 日 / 17,700 stars / HN / ライセンス）をここに合流
13. **結末 — ビューアにすらならなかった** — 続編から（file-viewer / reviewr、検収ループが閉じる、marketplace 無審査の注意）
14. **おわりに** — 両結論を統合（実行環境の形がエージェントの道具になる + 縮退は注意の設計）
15. **関連リンク** — 統合・重複排除・前作への自己参照を削除・著者ハブ維持

主な削除: 続編の「前作参照」導線一式 / 住み分け表 / repo 統計の重複 / Markdown プレビュー節の詳細

## 実行手順

1. **統合執筆** — `articles/herdr-agent-multiplexer.md` を統合版で上書き（frontmatter: title 変更、topics に `ghostty` 追加、`published: true` / `published_at: 2026-07-21 09:00` 維持）。`articles/herdr-zed-review-surface.md` を削除（未コミットなので rm のみ）
2. **レビュー並列起動** — editor + fact-checker + codex-review（prompt-driven、公開記事）を同一原稿に並列。CRITICAL / MAJOR ISSUES / ❌ INACCURATE で停止
3. **修正反映** → **人間 gate**: ユーザーが統合版の内容を確認（自動公開しない）
4. **コミット & push 促し** — 未 push の画像コミット 5105aaa + 未追跡画像 `images/herdr-file-viewer-reading.png` も同梱。push 後 Zenn デプロイ履歴で更新反映を確認（既登録記事の更新なので新規投稿枠は消費しない見込み）
5. **EN 差し替え** — devto-translator agent で統合版を再翻訳し `articles-en/herdr-agent-multiplexer.md` を上書き。launchd は発火時にファイルを読むため**予約変更不要**（7/20 22:00 のまま）。scripts/schedule.json の該当エントリはファイル参照のため変更不要（要確認のみ）
6. **memory 更新** — `herdr-article-pipeline.md` を統合後の状態に書き換え

## Verify（writing 版）

- `npm run validate`（frontmatter 検証）
- editor / fact-checker / codex-review の verdict が停止条件に非該当
- `git status` — 意図しないファイルなし（`.claude/rules/zenn-writing.md` 等の既存変更 2 件は本タスク対象外、コミットに含めない）
- 人間 gate: 公開前のユーザー内容確認（手順 3）

## リスクと前提

- EN 再翻訳の締切は **7/20 22:00 JST**（launchd 発火）。それまでに差し替え完了必須。間に合わない場合は `launchctl bootout gui/$(id -u) <plist>` で一時解除して延期
- 統合で記事 URL は変わらないため、続編スラッグ `herdr-zed-review-surface` 宛のリンクは存在しない（未公開）→ リダイレクト等の考慮不要
