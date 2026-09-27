# Zenn 記事執筆計画: chaos-TDD fault injection

## Context

`drafts/article-context_chaos-tdd-fault-injection_2026-07-13.md`（/collect-context で収集済み、Claims Register 15 件・コード例 4 本・構成案付き）を素材に、Zenn 記事を新規執筆する。

- **種別**: `writing`（記事）→ Claude Code 本体が `zenn-practical-writing`（実用軸・ですます調）に従って直接執筆。サブエージェントには委譲しない
- **読者問題文**: 「テストは通るのに、LLM パイプラインが本番で黙って壊れる」を経験している開発者が、運用障害履歴から fault カタログを起こし、daemon 不要・決定論・pytest ネイティブの fault injection テストを先行（TDD）で書けるようになる
- **コア論点**: 障害カタログ → RED（望ましいガード挙動を先に assert）→ GREEN（最小ガード同 PR）の chaos-TDD を単一プロセスのローカル LLM エージェントに入れたら、初回で silent failure が 3 件露出した
- **前作との導線**: agent-observability-patterns（7/13 公開、「判断を記録する側」）の続編として本文冒頭付近でフル URL リンク（本作は「記録チャネルを assert する側」）

## 成果物

- `articles/chaos-tdd-fault-injection.md`（新規、`published: false` のまま作成）

## 記事構成（独立論点 4 以下に収める）

素材の構成案 8 節を、実用軸テンプレートに沿って 4 論点に束ねる:

1. **導入**: 読者の壁（箇条書き 3〜4 個: silent truncation・shape violation の黙殺・telemetry が全部 error に潰れる 等、C8 の実障害由来）→「この記事でわかること」1 行 → 前提（Python / pytest / hypothesis / responses のバージョン、C10）
2. **論点 1 — chaos-TDD の型**: 分散系 chaos ツール（chaostoolkit/toxiproxy）をそのまま持ち込めない理由（Why 表 1 行目）+ カタログ→RED→GREEN の型 + 前作リンク
3. **論点 2 — fault カタログの起こし方**: 障害履歴 5 件 → F1-F5、既存カバレッジとの diff（Before/After 表を図表として使用）
4. **論点 3 — 実装**: 2 つの seam（ChaosBackend / responses）+ hypothesis 決定論プロファイル。コード例 3 本（素材のコード抜粋をそのまま使用）
5. **論点 4 — 初回で出た silent failure 3 件**: C4（str() 昇格）/ C5（json.loads("null") is None）/ C6（error_kind 不在）を各々「現象→なぜ silent か→ガード」で。ハマりポイント（.hypothesis/ キャッシュ・circuit breaker × property・40→32 訂正）は `:::details` に集約
6. **まとめ + 関連リンク**: 公開 skill repo・ADR-0077・前作・**著者 GitHub ハブ（必須）**

## タイトル

- 推奨: 「**LLM エージェントに chaos-TDD を入れたら silent failure が 3 件出た**」（約 40 字、素材の候補 1 を 50 字以内に短縮）
- 予備: 素材の候補 2「『テストは通るのに本番で黙って壊れる』LLM パイプラインへの chaos-TDD 入門」

## 執筆時の規律（素材の「技術メモ」+ skill 準拠）

- ですます調・AI-slop 禁止・専門用語の初出定義（chaos engineering / fault injection / property-based testing / seam は初出で平易な言い換え）
- Contemplative Agent は「ローカル LLM で動く CLI エージェント」とだけ紹介（思想・公理を出さない）
- **数値の再実測**: 執筆前に Claims Register の軽量コマンドを実測（C2 collect-only 32 本、C10 バージョン、可能なら C1 フルスイート）。実測できない場合はその数値を本文で断定しない
- **C14（agent-chaos の star 数等）**: WebFetch で再確認するまで断定しない。確認できなければ star 数は書かない
- episode log の直読み禁止、素材のコード例は「抜粋・簡約」の旨を保持

## レビューチェーン（執筆後、並列起動）

Parallel Group: [editor, fact-checker, codex-review (prompt-driven)]

- editor: 構造・AI-slop・コード品質
- fact-checker: Claims Register の事実主張検証
- codex-review: 公開記事のため cross-model レビュー（prompt-driven モード）
- Verdict マッピング: MAJOR ISSUES / ❌ INACCURATE → 停止・報告。NEEDS REVISION → 修正して継続

## Verify（writing 版）

1. `npm run validate`（zenn frontmatter 検証）
2. fact-checker verdict の出典編入確認
3. 自己プリフライトチェックリスト（zenn-practical-writing の受け入れ項目）
4. `git status` 確認

## 人間 gate（公開はしない）

- レビュー完了後、**`published: false` のままユーザーに記事内容の確認を依頼**して停止
- 公開日設定（候補: 来週バズタイム 7/21 火 or 7/22 水 09:00 JST — 今週は 7/13・7/14・7/15 で既に 3 本消化、週 2-3 本ルールにより今週の追加予約はしない）・EN 翻訳・schedule.json 更新は確認後の別ステップ
