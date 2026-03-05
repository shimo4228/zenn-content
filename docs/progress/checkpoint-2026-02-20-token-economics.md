# Progress Checkpoint — 2026-02-20 (Final)

## 現在のタスク

記事 `articles/token-economics-ai-orchestration.md` — **公開準備完了**

## 完了した作業

### 1. 初稿作成（chatlog-to-article スキル使用）
- Gemini との対話ログから記事を生成
- 生ログを `articles/_context/token-economics-gemini-log.md` に保存

### 2. editor エージェント 1回目レビュー → B評価
- 主な批判: 「Geminiに聞いてみた記事の域を出ていない」「検証なし」「よいしょを権威に使っている」
- 対話の引用を本文に挿入（身体性の向上）

### 3. ユーザー指示: ディープリサーチで検証 → 全面改稿
- 3つの並列リサーチエージェントで ChatGPT / Claude / Gemini の Deep Research アーキテクチャをファクトチェック
- 記事を「対話 → 検証 → 半分嘘だった」構造に全面改稿
- タイトル変更: 「Geminiに自社のDeep Researchの仕組みを聞いたら、半分嘘だった」

### 4. editor エージェント 2回目レビュー → B+評価
- 改善を認めつつ「ソースURLの完全欠如」が唯一のA阻害要因
- ソースURL を10箇所追加
- 結末を「批判的検証の姿勢」→「公式ドキュメントを開く習慣」に具体化

### 5. ユーザー指摘: モデル情報が古い → 最新情報で再検証
- ChatGPT Deep Research が 2/10 に GPT-5.2 にアップグレードされていた（o3-deep-research は旧モデル）
- GPT-5.2 ではリサーチ中の介入・方向転換が可能に
- Gemini API も Interactions API（2025/12）でステートフル管理を導入
- ただし Gemini App 側のフォローアップ失敗は2026/2でも未解決
- 記事の ChatGPT セクション、構図セクション、まとめテーブルを最新情報に更新

### 6. ユーザー指摘: Gemini は UX 未達を認めていた → ニュアンス修正
- 元の対話ログを確認し、Gemini が「統合的な最適解に到達しきれていない」と認めていた事実を反映
- まとめテーブルの表現を修正

### 7. 語調・対話引用の改修
- だ/である調 → ですます調に全面変更
- 対話引用を5箇所追加（Gemini の具体的な回答文、よいしょの実例、UX未達を認める応答）
- 文字数: 6,697 → 7,726文字

### 8. ステートレスAPI セクションの技術解説を補強
- 「ステートレス」が Deep Research で具体的に何が困るのか（メッセージ履歴 vs 思考コンテキストの区別）
- Thought Signatures の仕組みと限界を具体的に説明

### 9. ChatGPT セクションの時系列誤りを修正
- GPT-5.2 は対話の10日前（2/10）に稼働済み → 「未来を語っていた」は不正確
- Gemini の説明は体験としては概ね正しいが、「スクラッチパッド」は比喩であり実装の説明ではない
- 教訓を「未来を語る」→「他社は雄弁、自社は寡黙」に再構成

### 10. 公開設定
- `published: true` に変更
- `schedule.json` に追加: Zenn 2/24（火）、クロスポスト 2/25〜
- 英訳作成: `articles-en/token-economics-ai-orchestration.md`

## 重要な判断

- 「Gemini に聞いた」記事 → 「聞いた + 検証した + 半分嘘だった」に方針転換。editor の B 評価がきっかけ
- ChatGPT の o3-deep-research はもう使われていない。GPT-5.2 が現行モデル（2026/2/10〜）
- Gemini の「設計思想の違い」主張は、技術的制約（ステートレスAPI）を隠す自己弁護だった。ただし UX 未達自体は認めていた
- 記事タイトル「半分嘘だった」は強いが、本文で誠実に検証しているので問題ない（editor も同意）
- ChatGPT の「スクラッチパッド統合」は GPT-5.2 の体験に概ね合致 → 「不正確」ではなく「比喩」として整理

## 変更したファイル

- `articles/token-economics-ai-orchestration.md` — 記事本体（published: true）
- `articles-en/token-economics-ai-orchestration.md` — 英訳
- `articles/_context/token-economics-gemini-log.md` — 生ログ保存
- `scripts/schedule.json` — スケジュール追加

## lint 状態

- textlint: 0 errors
- markdownlint: 0 errors
