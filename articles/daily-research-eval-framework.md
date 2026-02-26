---
title: "AI生成レポートをAIに採点させる：LLM-as-Judge評価フレームワークをシェルスクリプトで実装した"
emoji: "⚖️"
type: "tech"
topics: ["claudecode", "claude", "ai", "llm", "evaluation"]
published: false
---

毎朝5時に自動生成される AI リサーチレポート。でも「ちゃんと良いレポートが出ているのか」を確認する手段がなかった。

この記事では、[daily-research パイプライン](https://zenn.dev/shimo4228/articles/daily-research-automation)に LLM-as-Judge 評価フレームワークを追加した経緯と実装を記録します。G-Eval の考え方をベースに、6次元 × 5点 = 30点満点の自動採点を、追加ライブラリなし・シェルスクリプトだけで実現しました。

---

## 背景：「良いレポート」の定義がなかった

パイプラインは順調に動いていました。Opus がテーマを選定し、Sonnet がリサーチして執筆する2パス方式。毎朝2本のレポートが Obsidian に届く。

問題は、**パイプラインを改善しても「改善されたか」を測る手段がない**ことでした。

前回のエージェントチーム版評価では、アドホックに LLM-as-Judge を使ったブラインド評価を実施しました（[ポストモーテム](https://zenn.dev/shimo4228/articles/daily-research-postmortem)参照）。しかしルーブリックが文書化されておらず、次回以降に再利用できない。毎回手動で評価プロンプトを書き直すのは持続しない。

**評価フレームワークは、パイプラインの継続的改善を可能とする基盤です。** その確信から実装を始めました。

---

## 設計方針：G-Eval ベースの多次元評価

### なぜ LLM-as-Judge か

人間が毎日2本のレポートを採点するのは、現実的ではありません。かといって ROUGE や BERTScore のような自動指標は「良いリサーチレポート」の品質を捉えられない。

LLM-as-Judge（LLM を評価者として使う手法）は 2023〜2024 年に急速に研究が進み、人間の判断との相関の高さが示されています。特に G-Eval（Liu et al., EMNLP 2023）は、次元ごとに独立したルーブリックを使う設計が有効だと示した論文です。

### 3大バイアスと対策

LLM-as-Judge には既知のバイアスがあります：

| バイアス             | 内容                               | 対策                                               |
| -------------------- | ---------------------------------- | -------------------------------------------------- |
| Verbosity bias       | 長い回答を高評価しやすい           | 「長さはスコアに影響させないこと」を明示指示       |
| Self-preference bias | 自分が生成した文章を高評価しやすい | 「自分が生成したかどうかに関わらず採点せよ」と明示 |
| Position bias        | 複数候補の順番に左右される         | 今回は単一レポート評価のため非該当                 |

これらをシステムプロンプト（`judge-system.md`）に明示的に組み込みます。

### 6次元ルーブリック

| #   | 次元              | 1点（最低）           | 5点（最高）                                      |
| --- | ----------------- | --------------------- | ------------------------------------------------ |
| 1   | Factual Grounding | 出典なし / 捏造の疑い | 全主張に一次情報源（査読論文・公式ドキュメント） |
| 2   | Depth of Analysis | プレスリリースの要約  | 専門家レベルの統合・洞察                         |
| 3   | Coherence         | 断片的、論理の飛躍    | シームレスな散文、読みやすいリズム               |
| 4   | Specificity       | 抽象的記述のみ        | 豊富な事例・数値・比較                           |
| 5   | Novelty           | 周知・陳腐            | 非自明で先見性あり                               |
| 6   | Actionability     | 開発アイデアが漠然    | 即座に着手可能なレベル                           |

次元ごとに独立した `judge-*.md` プロンプトを用意し、同じルーブリックを毎回一貫して使います。

---

## 実装：シェルスクリプトだけで動かす

### ディレクトリ構成

```text
daily-research/
├── scripts/
│   └── eval-run.sh              # 評価メインスクリプト
├── evals/
│   ├── prompts/
│   │   ├── judge-system.md      # 共通システムプロンプト
│   │   ├── judge-factual.md     # 次元①プロンプト
│   │   ├── judge-depth.md       # 次元②プロンプト
│   │   ├── judge-coherence.md   # 次元③プロンプト
│   │   ├── judge-specificity.md # 次元④プロンプト
│   │   ├── judge-novelty.md     # 次元⑤プロンプト
│   │   └── judge-actionability.md # 次元⑥プロンプト
│   ├── scores.jsonl             # スコアログ（.gitignore）
│   └── scores.example.jsonl    # スキーマ参照用
└── tests/
    └── test-eval.bats           # 22テスト
```

### judge-system.md：バイアス緩和のコア

```markdown
あなたは自律型 AI リサーチシステムが生成したレポートの品質評価者です。
与えられたレポートを指定された評価次元のルーブリックに従って採点してください。

## 重要: ツール使用禁止

**ツールは一切使用しないこと。** 評価はレポート本文のテキストのみを根拠とする。

## 採点ルール（バイアス緩和）

- **長さ非依存**: 文字数・分量はスコアに影響させないこと
- **流暢さ非依存**: 文体の洗練さに惑わされず内容で判断
- **客観的評価**: 自分が生成したかどうかに関わらず採点
- **独立評価**: この次元だけに集中すること

## 出力フォーマット

必ず以下の JSON のみを出力してください。

{"score": N, "rationale": "根拠を1〜2文で"}
```

「ツール使用禁止」は重要です。理由は後述します。

### eval-run.sh の核心部分

```bash
# Judge 実行（次元ごとに独立した呼び出し）
JUDGE_JSON=$("$CLAUDE_CMD" -p "$FULL_PROMPT" \
  --append-system-prompt-file "$PROMPTS_DIR/judge-system.md" \
  --max-turns 3 \
  --model "claude-opus-4-6" \
  --output-format json \
  --no-session-persistence \
  2>>"$LOG_FILE") || JUDGE_EXIT=$?
```

`--output-format json` を使うことで、`result` フィールドにモデルの応答が入った JSON を取得できます。

スコア抽出は二段階フォールバック方式：

```python
# 1. 直接 JSON パース
try:
    inner = json.loads(result_text)
    score = int(inner.get('score'))
except:
    pass

# 2. raw_decode フォールバック（rationale 内の "score": N への誤マッチ防止）
if score is None:
    decoder = json.JSONDecoder()
    idx = result_text.find('{')
    if idx >= 0:
        obj, _ = decoder.raw_decode(result_text, idx)
        score = int(obj.get('score'))
```

`re.search(r'"score"\s*:\s*(\d+)', ...)` のような正規表現フォールバックは**使いません**。`rationale` に `"score": N` のような文言が含まれていると誤マッチするからです。`raw_decode` で先頭の JSON オブジェクトだけをパースすることで、この問題を回避しています。

### スコアの保存形式（JSONL）

```json
{
    "date": "2026-02-21",
    "pipeline_version": "2pass-opus-sonnet",
    "track": "tech",
    "slug": "xcode-26-agentic-coding-mcp",
    "scores": {
        "factual_grounding": 4,
        "depth_of_analysis": 3,
        "coherence": 5,
        "specificity": 4,
        "novelty": 3,
        "actionability": 4
    },
    "total": 23,
    "judge_model": "claude-opus-4-6",
    "eval_duration_s": 42
}
```

`pipeline_version` を持つことで、将来のバージョン比較が可能になります。

### パイプラインへの統合

`daily-research.sh` の Pass 2 成功後に eval を呼ぶフックを追加：

```bash
# Pass 2 成功後に評価を実行（non-fatal）
if "$PROJECT_DIR/scripts/eval-run.sh" "$DATE" 2>>"$LOG_FILE"; then
  log "Evaluation completed"
else
  log "WARN: Evaluation failed (non-fatal)"
fi
```

`|| true` ではなく明示的な `if/else` で、失敗をログに記録しつつメインパイプラインは継続させます。

---

## ハマったポイント：`--allowedTools ""` は使うな

実装中にハマった罠を記録しておきます。

最初、judge に余計なツールを使わせないために `--allowedTools ""` を試しました。しかし **Opus がツール呼び出しを試みて `max-turns` に引っかかり、`result` が空になる**という問題が発生しました。

```bash
# NG: ツールを空にするとOPusがツール呼び出しを試みてmax-turnsに達する
"$CLAUDE_CMD" -p "$PROMPT" --allowedTools "" --max-turns 3 ...

# OK: システムプロンプトで明示的にツール禁止を指示する
"$CLAUDE_CMD" -p "$PROMPT" \
  --append-system-prompt-file judge-system.md \  # 「ツール使用禁止」を明示
  --max-turns 3 ...
```

`judge-system.md` の「ツール使用禁止」指示が必要なのはこのためです。ツール制限はプロンプトレベルで行う方が安定しています。

---

## ログ取得の強化：`sys.argv` から `stdin` へ

評価フレームワーク実装と同日、既存スクリプトのロギング部分も改善しました。

### 問題：ARG_MAX 超過リスク

以前のコードはシェル変数を `sys.argv` 経由で Python に渡していました：

```bash
# 旧: 大きなJSONをsys.argvで渡す
summary=$(python3 -c "
import sys, json
d = json.loads(sys.argv[1])  # sys.argv[1] に大きなJSONが入る
...
" "$json" "$label")
```

Claude の JSON 出力は数KB〜数十KBになることがあり、`ARG_MAX`（macOS では約 256KB）に近づくリスクがありました。

### 解決：stdin 経由に統一

```bash
# 新: stdin経由で渡す
summary=$(echo "$json" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())  # stdinから読む
...
" "$label")
```

`echo "$json" | python3 -c "..."` のパターンに統一することで、引数の長さ制限を完全に回避できます。

### セキュリティ改善も同時に

今回のリファクタリングで、いくつかのセキュリティ改善も加えました：

**DATE フォーマット検証（パス横断防止）：**

```bash
if ! [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "ERROR: Invalid DATE format: $DATE" >&2
  exit 1
fi
```

**topic/rationale の文字数上限（プロンプトインジェクション緩和）：**

```python
if len(str(t.get('topic', ''))) > 200:
    print(f'Theme {i}: topic too long (max 200)', file=sys.stderr)
    sys.exit(1)
```

Opus が選定したテーマ JSON をそのまま次の claude 呼び出しのプロンプトに埋め込むため、异常に長い文字列でのインジェクションを緩和します。

---

## 初回実行結果

実装完了後の初回スコア（2026-02-21）：

| レポート                  | FG  | Depth | Coh | Spec | Nov | Act | **合計**  |
| ------------------------- | --- | ----- | --- | ---- | --- | --- | --------- |
| tech（Xcodeエージェント） | 4   | 3     | 5   | 4    | 3   | 4   | **23/30** |

**Coherence が5点**というのは納得感があります。Sonnet は構成の一貫性が高い。一方 **Depth が3点**なのは、「なぜ重要か」の説明はあるが専門家レベルの統合・洞察には届いていないという評価です。

これは改善の方向性として明確です：リサーチプロトコルで「既存の知識との統合」「トレードオフの明示」を強化すれば Depth が上がるはずです。

---

## 統計的な注意事項

1日2本のデータでは何も言えません。

バージョン比較には **n ≥ 20**（約10日分）を最低ラインとしています。n < 20 の比較は「暫定シグナル」として扱い、方針決定に使わないのが原則です。

評価フレームワークの価値は、データが蓄積されてから発揮されます。今日始めることで、2週間後に比較ができる。

---

## まとめ

| 項目           | 内容                                            |
| -------------- | ----------------------------------------------- |
| 評価方式       | LLM-as-Judge（G-Eval ベース）                   |
| 次元数         | 6次元 × 5点 = 30点満点                          |
| judge モデル   | claude-opus-4-6                                 |
| コスト         | 2記事 × 6次元 = 12 Opus calls/日（約 $0.50/日） |
| 実行タイミング | Pass 2 成功後に自動実行（non-fatal）            |
| スコア保存形式 | JSONL（`evals/scores.jsonl`）                   |
| バイアス対策   | 長さ非依存・ツール禁止・自己優先禁止の明示指示  |

パイプラインの「感覚的な評価」から「数値的な追跡」へ。評価フレームワークがあることで、次の改善を自信を持って実施できます。

コードは [GitHub](https://github.com/shimo4228/daily-research) で公開しています。

---

## 参考

- [G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment (EMNLP 2023)](https://arxiv.org/abs/2303.16634)
- [A Survey on LLM-as-a-Judge (Nov 2024)](https://arxiv.org/abs/2411.15594)
- [Self-Preference Bias in LLM-as-a-Judge (Oct 2024)](https://arxiv.org/abs/2410.21819)
- [Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge (Oct 2024)](https://arxiv.org/abs/2410.02736)
