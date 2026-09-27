# Plan: iPhone 公式アプリで Claude Code を回す実運用記事（Zenn / Dev.to）

## Context（なぜ書くか）

iPhone 公式アプリの Remote Control（数ヶ月前に追加）は UI が優れていて、著者のモバイル操作のメインになっている。だが実運用には**公式機能の2つの穴**がある:

1. **モバイルから新セッションを起こせない**（公式 RC は 1 マシン基本 1 セッション）
2. **OAuth が切れると再認証できない**（認証ブラウザは自宅 Mac 側に出る。外出先の手元には出ない）

著者はこれを自作 `spawn-session` スキル（tmux で detached RC 起動）と **RVNC（RealVNC Viewer）でブラウザ認証だけ通す**運用で塞いでいる。この2つの穴埋めは**既存の公開記事・ドラフトに一切存在しない net-new**（探索で確認済み）。過去の Termius 記事（`termius-iphone-claude-code`）は SSH 一本の環境構築で、公式 RC も spawn も RVNC も未カバー。本記事はその**後継**として、公式アプリ主軸の実運用 playbook を書く。

**タスク種別**: `writing`（一次成果物が文章）→ Writing Chain。doc 分類 = Zenn 記事 → 既定の声は `zenn-practical-writing`（実用軸・ですます）。

## 決定事項（grill-me で確定）

| 論点 | 決定 |
|------|------|
| 記事の背骨 | **公式アプリ主軸の実運用 playbook**。2つの穴 × 2つの穴埋めが meat |
| spawn-session の見せ方 | **生コマンドを核**（`tmux new-session -d ... claude --remote-control "<名前>"`）+ skill はラッパー紹介。再現性最優先 |
| RVNC | **独立した山場の節**。セキュリティ但し書き付き（LAN/VPN 経由、カフェ回線に直接晒さない） |
| 文体 | ですます（Termius 記事・zenn-practical-writing 既定に一致） |
| スコープ | Remote Control 有効・自宅 Mac 常時起動は前提で宣言。Tailscale/環境構築は再解説せず過去記事へリンク |
| 位置づけ | Termius 記事の後継として明示クロスリンク（脱GUI 系譜の続き） |

## 成果物ファイル

- **新規**: `articles/iphone-claude-code-remote-control.md`（JP 本体）
- **後工程・新規**: `articles-en/iphone-claude-code-remote-control.md`（`devto-translator` エージェントで翻訳→タグ→schedule 登録）
- **手動・任意**: `images/covers/iphone-claude-code-remote-control.png`（カバー。無ければ後で。あれば GitHub raw URL で Dev.to 自動参照）
- **更新**: `schedule.json`（JP `date` + `devto` エントリ。スキーマ: `file` / `date` / `devto` / `devto_tags` / `cover_image` / `notes`）

## frontmatter（`zenn-format` 準拠）

```yaml
title: "（下記候補から選定。50字以内・必要なら60字）"
emoji: "📱"
type: "tech"
topics: ["claudecode", "tmux", "remotecontrol", "iphone", "ios"]
published: false   # レビュー通過後に true + published_at を設定
```

タイトル候補（Distribution 層＝最適化可。書く前に確定）:
- 「iPhone公式アプリでClaude Codeを回す — 新セッションと再認証、2つの穴の塞ぎ方」
- 「Claude CodeをiPhoneの公式アプリで運用する — spawn-sessionとRVNC再認証」
- 「モバイルのClaude Codeが詰む2箇所と、その回避策」

## 記事構成（house テンプレ準拠：コールドオープン→前提→成果宣言見出し→表→まとめ→関連リンク）

1. **コールドオープン**（`はじめに` 禁止）: 具体的な詰まり。「公式アプリはUIが良い。でも新セッションが立てられない。しかも数日でOAuthが切れて、再認証のブラウザは"自宅のMac側"に出る——外出先の手元には何も出ない」
2. `## 前提`（箇条書き）: 公式 Remote Control 有効 / 自宅 Mac 常時起動 / Mac に到達できる経路（Tailscale 等）。SSH ルートの環境構築は前回記事に委譲（クロスリンク）
3. `## なぜ公式アプリをメインにするか`（短く）: UI が優れる・RC が数ヶ月前に追加された
4. `## 穴その1：モバイルから新セッションが立てられない`
   - 制約: 公式 RC は 1 マシン基本 1 セッション
   - **核心の生コマンド**（コピペ可）: `tmux new-session -d -s <名前> ... "exec $SHELL -lc 'cd ... && exec claude --remote-control \"<名前>\"'"`
   - なぜ `-d`（detached）/ `-e`（環境変数でクォート回避）/ login shell `-l`（node/claude の PATH）/ tmux が pty 保持で SSH 切断後も生存、の短解説
   - **仕組み**: 生きたセッションが Bash で別 RC を起こす→新プロセスが自分の RC を登録→アプリ一覧に出る
   - skill ラッパー紹介（`/spawn-session [project]` で毎回叩かず呼べる。移植性のため解決知能は SKILL、`spawn.sh` は dumb 起動器）
   - 表: 制約 → 回避策
   - 併記（一手）: Termius で新セッションだけ立ててモバイルに移る運用（前回記事の系譜）
5. `## 穴その2：OAuthが切れて、再認証が手元でできない`（**独立山場**）
   - 症状: spawn 直後に tmux セッションが即消え = auth 切れの典型
   - 手順: RealVNC Viewer で自宅 Mac に入り、**ブラウザ認証だけ**通して抜ける
   - **セキュリティ但し書き**（必須）: VNC はカフェ等の共有回線に直接晒さない。自宅 LAN か Tailscale 等 VPN 経由で。パスワード/暗号化設定
6. `## 認証を切らさない工夫`（防ぐ側・軽め）: tmux 常駐でセッションを生かす等、再ログイン頻度を下げる
7. `## 完成した運用`: 表（端末/役割）+ 日常フロー。正直な制限（iPhone はリモコン、の系譜を継ぐ）
8. `## まとめ`
9. `## 関連記事`（house 固定ブロック + **著者ハブ必須**）:
   - Termius 記事へのクロスリンク（脱GUI 系譜の4本目として）
   - 「道具の話はここまで。一段奥の…」ブリッジ + agent 設計エッセイ 2本
   - 最終行: `研究としての成果物（DOI 付き）は github.com/shimo4228 に。`（言及 repo が1つでも著者ハブ必須：CLAUDE.md canonical）

## 再利用する既存資産

- **spawn.sh の正確なコマンド**: `~/.claude/skills/spawn-session/{SKILL.md, spawn.sh}`（探索で全文抽出済み）
- **house 関連リンクブロック**: 既存公開記事共通の "道具の話はここまで…" + 2 essay links + `github.com/shimo4228` ハブ
- **Termius 記事**: `articles/termius-iphone-claude-code.md`（クロスリンク先。重複させない: Tailscale/tmux 基礎/OAuth URL コピー問題は再解説しない）
- **frontmatter/記法**: `zenn-format` skill、`.claude/rules/zenn-writing.md`（内部リンクはフル URL、`published_at` は `YYYY-MM-DD HH:MM` JST）

## Writing Chain（planning.md 準拠）

```
Draft（オーケストレーター本体が zenn-practical-writing に従い直接執筆。サブエージェント委譲しない）
  ↓
Parallel Review Group: [editor, fact-checker, codex-review(prompt-driven, 公開記事)]
  ↓ Verdict マッピング（MAJOR ISSUES/❌INACCURATE = CRITICAL→停止 / NEEDS REVISION = HIGH→修正）
Human gate（記事内容の承認）→ published: true + published_at
  ↓
EN: devto-translator（翻訳→タグ→schedule.json 登録）
```

- Cross-Model Review: 公開記事なので codex-review を **prompt-driven モード**で editor と並列（prose 対象）
- essay-reviewer は使わない（Substack 専用。Zenn/Dev.to は editor に一本化）

## 公開スケジュール（zenn-writing 正本に従う）

- **JP (Zenn `published_at`)**: 火〜水 09:00 JST のバズタイム（週2-3本ペース内で1枠）
- **EN (Dev.to `--at`)**: その前日 22:00 JST（例 JP `2026-07-14 09:00` → EN `2026-07-13 22:00 Asia/Tokyo`）
- コマンド: `devto_crosspost.py schedule iphone-claude-code-remote-control --at "<前日> 22:00 Asia/Tokyo"`
- **具体日付は執筆・レビュー完了後に確定**（本プランでは枠だけ規定）

## Verify（writing 版・commit 前）

1. `npm run validate`（Zenn frontmatter 検証。prose lint は 2026-07 撤去済み）
2. `npm run preview` で目視（構成・表・コードブロック）
3. **セキュリティ/匿名化**: 本文・コード・スクショに `/Users/username/` 実パス無し、API キー/トークン無し（RVNC 節のスクショは特に注意）
4. Parallel Review 実行確認（editor / fact-checker / codex-review 起動済みか）
5. `schedule.json` に JP+EN エントリ追加済みか
6. `git status` 確認（意図しないファイル混入無し）
7. commit 後、**push リマインド**（未 push だと `published_at` 予約が反映されない — CLAUDE.md CRITICAL）

## End-to-end 検証（記事が「動く」か）

- spawn の生コマンドを実際に Mac で叩き、iPhone アプリ一覧に新セッションが出ることを確認してから本文に載せる（Prototype Before Scale）
- RVNC 手順は実機フロー通りに手順化（RealVNC Viewer 接続→ブラウザ認証→抜ける）
```
