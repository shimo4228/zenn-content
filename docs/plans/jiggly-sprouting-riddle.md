# Herdr 記事執筆プラン（herdr-agent-multiplexer）

## Context

- 素材: `drafts/article-context_herdr-agent-multiplexer_2026-07-18.md`（/collect-context 生成済み。Claims Register 16 件・スクリーンショット 3 枚配置済み・構成案あり）
- タスク種別: **writing** → Writing Chain → 記事 → `zenn-practical-writing`（実用軸・ですます調）に従い Claude Code 本体が直接執筆
- **ユーザー決定事項（2026-07-18 確認済み）**:
  1. **フレーム**: 「Herdr vs Zed」の対決ではなく、**「Zed が弱い多数エージェント管理を Herdr が埋める」補完構図**。タイトル・構成ともこの構図で立てる
  2. **公開日程**: JP Zenn `published_at: 2026-07-21 09:00`（火・バズタイム）。予約登録レートリミット対策で**本日 7/18 中に push 必須**。EN Dev.to は 7/20 22:00 JST 予約
  3. **未検証クレーム**: C12（worktree create）/ C14（スリープ）/ C15（複数クライアント attach）**3 件とも実測**してから書く。C3（star 数等）/ C4（ライセンス）は執筆時に Web で一次確認

## 読者の問題文（構成の主軸）

「Claude Code / Codex を複数並列で回し始め、ターミナルタブの散乱・離席や SSH での継続・エージェント自身が実行環境を触れないことに困っている開発者が、この記事を読むと Herdr を導入して agent 状態監視・セッション永続化・エージェントによるレイアウト操作を再現でき、Zed との住み分けを判断できるようになる」

## Phase 1: 事前検証（執筆前・順不同並列可）

| 対象 | 方法 | 備考 |
|---|---|---|
| C3: 公開日・star 数・Trending・個人開発 | GitHub API / repo ページ + HN スレを WebFetch | 数値は公開時点の値で本文記載 |
| C4: AGPL-3.0 + 商用デュアルの有無 | repo LICENSE / herdr.dev を WebFetch | デュアル未確認なら本文で言及回避 or「要確認」 |
| C12: `herdr worktree create --branch X` | 実行（zenn-content 以外の適当な repo で。作った worktree/branch は検証後に削除） | 記事の socket API 論の裏取り |
| C14: Mac スリープで herdr サーバが止まるか | **ユーザー協力が必要**（スリープ操作は Claude 自身のプロセスも止めるため）。手順を提示し実施してもらう | 実測不能なら「推測」と明示に降格 |
| C15: 複数クライアント attach の focus 挙動 | 2 端末 attach で確認。**2 つ目の attach はユーザーの端末操作が必要な可能性**あり | 同上 |

## Phase 2: 執筆（構成 — 補完構図に調整済み）

タイトル候補（最終確定は人間 gate で。50 字目安・誠実・概念前置）:

1. **（推奨）**「AI エージェント版 tmux「Herdr」— Zed に足りない並列エージェント管理を埋める」
2. 「並列 Claude Code の管理が Zed で破綻したので agent multiplexer「Herdr」を足した」
3. 「Zed の弱点は多数エージェントの管理 — Herdr で監視・永続化・自己再編成を足す」

構成（8 節・独立論点 4 以下: ①Herdr 導入 ②Zed との補完関係 ③エージェントによる環境自己操作 ④状態の投影という UI 論）:

1. **はじめに** — 読者の壁を箇条書き（タブ散乱 / 離席で死ぬ / エージェントがレイアウトに触れない）→「この記事で作れるもの」1 行
2. **Herdr とは** — tmux との差分は「agent 状態の意味的追跡」と「socket API」の 2 点と言い切る（C1, C5）。v0.7.4 時点と明記
3. **導入** — brew 3 コマンド + スモークテスト（コード例 1, 2。curl|sh 不採用理由 1 行）
4. **Zed で足りる範囲、足りない範囲** — Zed Parallel Agents（C10, C11）で足りる場面を先に認める。「冗長では？」の中間評価は補完構図の証拠として本節内に圧縮。Herdr が埋める 3 レイヤー: 永続化 / SSH・モバイル / socket API
5. **エージェント自身にレイアウトを操作させる（クライマックス）** — pane move ×3 のタブ統合（C16、コード例 3）。`--current` の罠と `HERDR_PANE_ID`（C7, C8）。worktree create（C12 実測結果）
6. **サイドバーは状態を映すか、履歴を映すか** — スクリーンショット 1 + 画面レイアウト Before/After（スクリーンショット 2, 3）。「視界に入るものは、いま使っているものだけ」
7. **住み分けの結論** — 表 1 枚（デスク=Zed / 離席・SSH・モバイル=Herdr / エージェント委任=Herdr）。iPhone Termius は既存記事リンク（C13）
8. **おわりに + 関連リンク** — GitHub ハブ github.com/shimo4228 を必ず含める（CLAUDE.md canonical）

執筆時の注意（コンテキストファイル「技術メモ」+ skill 準拠）:
- ペイン ID（w5:p4 等）は「例」と断るか汎化
- tmux 詳細比較は termius 記事と重複させない（prefix 互換に触れる程度）
- ハマりポイント詳細（サーバ寿命・cwd 挙動）は `:::details` で progressive disclosure
- frontmatter: `type: tech` / topics は素材どおり / `published: false` のまま執筆

## Phase 3: セルフプリフライト → レビュー並列

- セルフプリフライト（zenn-practical-writing チェックリスト: AI-slop / 段落密度 / 用語初出 / ですます統一）
- **Parallel Group: [editor, fact-checker, codex-review]**
  - fact-checker は Claims Register から開始させる
  - codex-review は prompt-driven モード（公開記事の cross-model レビュー）
- Verdict マッピング: MAJOR ISSUES / ❌ INACCURATE → 停止・報告。NEEDS REVISION → 修正して継続

## Phase 4: 人間 gate（介入点）

記事全文 + タイトル最終案を提示 → ユーザー確認。**確認前に published: true にしない**

## Phase 5: 公開設定 + Verify + push（本日 7/18 中）

1. `published: true` + `published_at: 2026-07-21 09:00` を設定
2. Verify 相当: `npm run validate`（frontmatter 検証）/ 画像パス・秘匿情報チェック / `git status`
3. コミット → **ユーザーに push を促す**（CLAUDE.md CRITICAL）→ Zenn デプロイ履歴で予約登録成功の確認を依頼

## Phase 6: EN 翻訳 + Dev.to 予約

1. `devto-translator` agent で JP→EN 翻訳（`articles-en/herdr-agent-multiplexer.md`）+ タグ付け
2. `scripts/devto_crosspost.py schedule herdr-agent-multiplexer --at "2026-07-20 22:00 Asia/Tokyo"`
3. schedule.json に JP/EN エントリ追加 → コミット → push 促し
4. カバー画像は任意（`images/covers/herdr-agent-multiplexer.png` を置けば自動参照。無ければ省略可）

## 検証方法

- Phase 1 の実測ログを記事の一次ソースとして Claims Register の ⚠ を解消
- `npm run validate` PASS + `npm run preview` で表示確認（画像 3 枚の表示含む）
- git status に意図しないファイル（`.claude/rules/` 等の既存 modified）を混ぜない — 記事関連ファイルのみコミット
