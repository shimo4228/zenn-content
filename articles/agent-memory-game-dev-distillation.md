---
title: "ゲーム開発のメモリ管理をAIエージェントの記憶蒸留に移植した"
emoji: "🎮"
type: "tech"
topics: ["ai", "python", "agent", "memory", "gamedev"]
published: true
published_at: 2026-03-30 21:56
---

9Bローカルモデルで自律エージェントを18日間運用した。RAGではなく蒸留ベースの記憶管理を採用し、ゲーム開発で40年磨かれたメモリ技法を移植した記録。

## この記事の前提

[Moltbookエージェント構築記](https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build)で作ったSNSエージェントの記憶システムを改善する話だ。3層メモリアーキテクチャ — Episode(会話ログ)、Knowledge(蒸留された知識パターン)、Identity(性格・価値観) — の設計は[記憶が本質](https://zenn.dev/shimo4228/articles/agent-essence-is-memory)で書いた。前作[エージェントの記憶が壊れた](https://zenn.dev/shimo4228/articles/few-shot-for-small-models)では9Bモデルの蒸留品質の問題を記録した。本記事はその続きで、ゲーム開発の手法で Knowledge 層の蒸留品質を底上げする。

## なぜゲーム開発なのか

ゲーム開発は「限られたリソースで最大効果」を40年追求してきた分野だ。16MBのRAMで広大な世界を描画し、60fpsを維持しながらAIを動かす。

GDC 2013 で Rafael Isla が "Architecture Tricks: Managing Behaviors in Time, Space, and Depth" を発表した。ゲームAIの行動を距離・重要度・計算コストで段階的に簡略化する LOD(Level of Detail)の思想を体系化した講演だ。カメラから遠いNPCは詳細な意思決定を省略し、近いNPCだけに認知資源を集中する。

この「限られた計算資源を、最も重要なものに集中させる」発想が、9Bモデルの32kコンテキスト窓という制約と構造的に同じ問題を解いている。

移植した3つの技法。

| ゲーム開発技法 | AIエージェントでの応用 | 効果 |
|--------------|---------------------|------|
| **Importance Scoring** | パターンに重要度スコアを付与、時間減衰で鮮度を反映 | 信号密度の最大化 |
| **LOD (Level of Detail)** | 1ステップ1タスクのプロンプト分割 | 9Bモデルの認知負荷を軽減 |
| **Object Pooling** | SKIP/UPDATE/ADD の重複排除ゲート | メモリの無限膨張を防止 |

## Importance Scoring — 何を覚え、何を忘れるか

Generative Agents(Park et al., 2023)の三重スコアは recency × importance × relevance の3要素で構成される。ここから relevance 検索を省略し、importance × 時間減衰で実装した。

```python
# knowledge_store.py（簡略化。実コードでは distilled 未設定時のガードあり）
def _effective_importance(self, p: dict) -> float:
    """importance * 0.95^days — Generative Agents の recency decay に着想"""
    base = p.get("importance", 0.5)
    distilled = p.get("distilled", "")
    dt = datetime.fromisoformat(distilled)
    days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
    return max(0.0, min(1.0, base * (0.95 ** days)))
```

設計判断。

- **蒸留時にLLM評価する。** エピソードの文脈がある時点で評価精度が最も高い。事後スコアリングでは文脈が失われる。
- **時間減衰は lazy に計算する。** stored importance は不変で、読み取り時に減衰を計算する。元のLLM評価値をデバッグに使える。
- **limit を100→50に変更した。** 9Bの32kコンテキストでは密度で勝負する。量より質。

## 蒸留パイプラインの3ステップ化 — LODの応用

9Bモデルに「要約して、かつ重要度を評価して」と同時に頼んだら、バッチによっては0パターンが返ってきた。要約（創造的タスク）と評価（判断タスク）は認知的に異なる。ゲーム開発のLODと同じ発想で、1フレームに全処理を詰め込まない。

```python
# Step 1: Extract（自由形式で抽出）
result = generate(prompt, system=get_rules_system_prompt(), max_length=4000)

# Step 2: Summarize（JSON文字列配列に精製）
refined = generate(DISTILL_REFINE_PROMPT.format(raw_output=result), max_length=4000)

# Step 3: Importance（スコア配列のみ）
importance_result = generate(
    DISTILL_IMPORTANCE_PROMPT.format(patterns=patterns_text), max_length=4000
)
```

各LLM呼び出しは1タスクのみ。「要約+評価」を同時に頼むと、バッチによっては0パターンしか返らなかった。分割後は安定して結果が返るようになった。

この「小型モデルに複数タスクを同時に頼むと崩壊する」現象は、より大規模に検証されている。ICLR Blogposts 2025 の Multi-Agent Debate 検証が参考になる。Llama 3.1-8B に AgentVerse(複数エージェントが議論して結論を出すフレームワーク)を適用したところ、MMLUで13.27%まで崩壊した。単体なら約43%出せるモデルだ。「議論のフォーマットを維持する」という追加タスクに認知資源を奪われ、本来のタスクすらこなせなくなる。うちの9Bで起きた現象と同じ構造だ。

## 重複排除ゲート — Object Pooling の応用

ゲーム開発の Object Pooling は「使い回せるものは使い回す」思想だ。記憶システムでは、既知のパターンを重複保存しないためのゲートに転用した。

```python
# knowledge_store.py（簡略化した擬似コード）
def _dedup_patterns(new_patterns, new_importances, existing_patterns, threshold=0.7):
    existing_texts = [p["pattern"] for p in existing_patterns]
    for new_text, new_imp in zip(new_patterns, new_importances):
        best_ratio, best_idx = 0.0, -1
        for i, ext in enumerate(existing_texts):
            ratio = SequenceMatcher(None, new_text, ext).ratio()
            if ratio > best_ratio:
                best_ratio, best_idx = ratio, i
        if best_ratio >= 0.95:    # SKIP: 完全重複
            skip_count += 1
        elif best_ratio >= 0.7:   # UPDATE: importance ブースト
            old_imp = existing_patterns[best_idx].get("importance", 0.5)
            existing_patterns[best_idx]["importance"] = max(old_imp, new_imp)
        else:                     # ADD: 新規追加
            add_patterns.append({"pattern": new_text, "importance": new_imp})
```

UPDATE では、既に覚えているパターンと似たものが出てきたとき、新旧の importance を比べて高い方を採用する。「出てくるたびに +0.1 加算」だと蒸留を回すたびに際限なく上がって壊れる。高い方を採るだけなら、何回蒸留を回しても値が変わらないので安全だ。

dedup に LLM ではなく difflib を使ったのは、245パターン規模なら全ペア比較でも十分高速だからだ。embedding 検索は依存追加に見合わない。

## エピソード分類 — 泥に咲く蓮の花

216件のエピソードを分類した結果、81件が noise（37%）、134件が uncategorized、1件が constitutional だった。

```markdown
Classify this episode into exactly one category. Reply with a single word only.

- **constitutional**: The episode touches on themes in the constitutional principles below.
  （倫理原則に触れる体験）
- **noise**: Test data, errors, meaningless/trivial interactions, content with no learnable value.
  （テストデータ、エラー、学ぶ価値のないやりとり）
- **uncategorized**: Everything else.
  （それ以外すべて）

When in doubt between constitutional and uncategorized, choose uncategorized.
（迷ったら uncategorized にする）
```

最初は30件バッチでJSON配列を返させていたが、パース失敗率が約50%だった。9Bモデルに長い構造化出力を求めてはいけない。1件ずつ1語だけ返させたら失敗率がほぼ0%になった。

ここで重要な設計判断がある。「行動指針を出すな」とプロンプトを変えたら、抽象化の深さが改善した。

旧プロンプトは "next time, ask clarifying questions" のような浅い行動指針を大量生産していた。新プロンプトで「what keeps happening(事実のみ)」だけを求めた。すると constitutional から「真理は固定的な本質ではなく、文脈に依存する流動的な連続体として機能する」が出た。制約が深さを生んだ。

uncategorized から抽出された3パターンは、既存328パターンとの dedup で全て skip された。既に知っていることは上書きしない。知識が飽和に近づくと新規追加は自然に減る。人間の記憶と同じだ。

「泥に咲く蓮の花」— noise（泥）と uncategorized（水）が大半を占め、稀に constitutional（蓮）が咲く。

## RAG vs 蒸留 — なぜ蒸留が筋が良いか

RAG はインデックスから関連チャンクを検索して注入する。蒸留は生データを圧縮して高密度パターンに変換する。

9Bモデルの32kコンテキスト窓では、コンテキストは「理解の窓」だ。窓に入る情報の密度が行動品質を決める。RAGは未加工のチャンクを詰め込むから、ノイズが多い。蒸留は圧縮済みの高密度パターンだけを注入するから、同じ窓サイズで信号密度が高い。

そして、制約下で有効な設計は上位互換になる。9Bで動く蒸留パイプラインは、Opus クラスのモデルではさらに高品質に動く。制約が設計を正しくする。

## Before / After

| 指標 | Before | After | 方法 |
|------|--------|-------|------|
| パターン検索方式 | 最新100件を時系列順注入 | importance × 時間減衰で top-50 選択 | `_effective_importance()` |
| 蒸留パイプライン | 2ステップ（要約+importance同時） | 3ステップ（抽出→精製→importance） + dedup | プロンプト分割 |
| 重複排除 | なし（全パターン無条件追加） | difflib SequenceMatcher (ratio >= 0.7) | `_dedup_patterns()` |
| 品質ゲート | 30文字 & 3単語以上のみ | + SKIP/UPDATE/ADD の3段階判定 | 3段階判定 |
| system prompt 構成 | identity + axioms + skills (~15KB) | identity + axioms のみ (~3KB) | スキルを除外し蒸留へのバイアスを排除 |
| KnowledgeStore の limit | 100 | 50 | 密度で勝負 |
| エピソード分類 | なし（全て同一扱い） | 3カテゴリ（noise 37%除外） | Step 0 分類 |
| JSON パース失敗率 | ~50%（バッチ） | ~0%（1件ずつ1語） | 分類方式変更 |

## 先行研究との位置づけ

| システム | 記憶戦略 | 品質ゲート | 忘却 |
|---------|---------|-----------|------|
| Generative Agents (2023) | recency × importance × relevance | なし | なし |
| MemGPT (2023) | 仮想メモリ（ページング） | なし | アーカイブ |
| A-MEM (2025, preprint) | Zettelkasten 型リンク | 自動リンク | なし |
| Mem0 (2025) | ADD/UPDATE/DELETE | LLM判定 | DELETE |
| **本実装** | importance × time decay | difflib + LLM + human | noise除外 + dedup |

distill パイプライン単体で見ると、Mem0 の ADD/UPDATE/DELETE ゲートに最も近い。SKIP/UPDATE/ADD の3段階判定で知識の品質を自動管理する設計だ。

## 小型モデルとの格闘で学んだこと

1. **9Bに2タスク同時は重い**: 要約と評価を同時に指示すると両方の品質が下がる。プロンプトを分割する
2. **構造化出力を求めるな**: 30件バッチのJSON → 1件1語に変更。各呼び出しの認知負荷を最小化
3. **コードフェンスに注意**: 9Bモデルは JSON を ` ```json ` で囲んで出力する。パース前に剥がす3行のコードが必須
4. **制約が設計を正しくする**: 9Bの制約の中で作った設計は、大型モデルでもそのまま動く。逆は成り立たない

## まとめ

ゲーム開発の40年の蓄積は、AIエージェントの記憶設計にとって鉱脈だった。Importance Scoring で信号密度を上げ、LOD の発想でプロンプトを分割し、Object Pooling の思想で重複を排除する。どれも「限られたリソースで最大効果」という同じ原則から導かれる。

エージェントの行動品質は、蒸留前と比べて体感で明確に改善した。以前は同じようなパターンを繰り返し蓄積していたのが、重複排除と分類によって知識の密度が上がり、投稿の多様性が増した。

9Bモデルの制約が設計を正しくした。RAGに頼れないからこそ蒸留の密度にこだわり、コンテキスト窓が狭いからこそ信号密度を最大化する設計が生まれた。この設計は大型モデルに移行してもそのまま動く。制約下で磨かれた設計は上位互換になる。

## 参考文献

- Park et al. (2023) "Generative Agents: Interactive Simulacra of Human Behavior"
- Packer et al. (2023) "MemGPT: Towards LLMs as Operating Systems"
- Xu et al. (2025) "A-MEM: Agentic Memory for LLM Agents" arXiv preprint
- Choudhary et al. (2025) "Mem0: Building Production-Ready AI Agent Memory"
- "Multi-LLM-Agents Debate: Performance, Efficiency, and Scaling Challenges" ICLR Blogposts 2025
- Laukkonen et al. (2025) "Contemplative Artificial Intelligence"
- "Architecture Tricks: Managing Behaviors in Time, Space, and Depth" (GDC 2013, Isla)
