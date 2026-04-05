---
title: "エピソードログから倫理が生まれるまで — Contemplative Agent 17日間の設計記録"
emoji: "📜"
type: "tech"
topics: ["ai", "agent", "python", "ethics", "architecture"]
published: true
---

:::message
**シリーズの文脈**: [contemplative-agent](https://github.com/shimo4228/contemplative-agent) は、AIエージェントSNS「[Moltbook](https://www.moltbook.com)」上で動く自律エージェントだ。9Bローカルモデル（Qwen 3.5）で動作し、Contemplative AI（Laukkonen et al., 2025）の四公理を倫理原則に採用している。構造の概要は[エージェントの本質は記憶](https://zenn.dev/shimo4228/articles/agent-essence-is-memory)を参照。本記事では**憲法改正の実装と17日間の実験結果**にフォーカスする。
<!-- textlint-disable -->
:::
<!-- textlint-enable -->

SNSエージェントを17日間運用して蒸留パイプラインを回したら、知識が飽和した。新しいパターンが生まれなくなり、飽和を突破するには人間の承認が必要だった。自律エージェントの自己改善に構造的な速度制限があることを、実運用で発見した記録。

## 最小構造: エピソードログだけで動く

17日間の開発で辿り着いた構造は意外にシンプルだった。全レイヤーがオプションで、エピソードログだけあれば動く。

```text
MOLTBOOK_HOME/
  logs/YYYY-MM-DD.jsonl  ← これだけで動く
  identity.md            ← ペルソナ（オプション）
  skills/*.md            ← 行動スキル（オプション）
  rules/*.md             ← 行動ルール（オプション）
  constitution/*.md      ← 倫理原則（オプション）
  knowledge.json         ← 蒸留済みパターン（自動生成）
```

設定をコードから分離したことで、倫理フレームワークの差し替え実験が容易になった。この構造は SNS エージェントに固有のものではなく、自律エージェントの「入れ物」だった。

### 6層のメモリフロー

```text
Episode Log (raw actions)
    ↓ distill --days N
    ↓ Step 0: LLM classifies each episode
    ├── noise → discarded（能動的忘却）
    ├── uncategorized ──→ Knowledge (patterns)
    │                       ├── distill-identity ──→ Identity
    │                       └── insight ──→ Skills (behavioral)
    │                                        ↓ rules-distill
    │                                      Rules (principles)
    └── constitutional ──→ Knowledge (ethical patterns)
                              ↓ amend-constitution
                            Constitution (ethics)
```

各層は独立している。identity を消しても skills は動く。constitution を差し替えても knowledge は壊れない。

### 17日間の数値変化

| 指標 | Day 1 | Day 17 |
|------|-------|--------|
| モジュール数 | 1 (agent.py 780行) | 36 |
| メモリ層 | 1 (knowledge.md) | 6層 |
| テスト | 0 | 774 |
| distill 成功率 | 2/10 | 12/16 |
| 承認ゲート | なし | 4コマンド全て |
| ADR（設計判断記録） | 0 | 12本 |

## 憲法改正を実装する — 経験から倫理を進化させる

最小構造の上に、最も挑戦的な機能を実装した。エージェントが経験から倫理原則を進化させる仕組みだ。

### 問題: 倫理的学びが行動ノイズに埋もれる

全エピソードを無差別に蒸留すると、日常のSNS活動の行動パターン（uncategorized）に、稀に現れる倫理的洞察（constitutional）が埋もれる。

蒸留の前段に、高速なタグ付けだけを行う Step 0 を設けた。深い分析ではなく、分類だけ。

```python
classified = _classify_episodes(records, constitution=get_axiom_prompt())
# noise は除外、uncategorized と constitutional を別々に蒸留
for category, cat_records in [
    ("uncategorized", list(classified.uncategorized)),
    ("constitutional", list(classified.constitutional)),
]:
    cat_results = _distill_category(
        cat_records, knowledge, category, source_date, dry_run
    )
```

ある1日分（216件）のエピソード分類結果: noise 81件（37%）、uncategorized 134件、constitutional 1件。216件中1件。この比率が Step 0 の存在理由だ。

### Knowledge 直接注入の廃止

以前は knowledge.json の内容を直接 system prompt に注入していた。

```python
# Before — knowledge をそのまま注入
knowledge_ctx = ctx.memory.knowledge.get_context_string() or None
content = self._get_content().create_cooperation_post(
    topics, knowledge_context=knowledge_ctx,
)
```

contemplative-agent の知識管理は [AKC（Agent Knowledge Cycle）](https://github.com/shimo4228/agent-knowledge-cycle)に基づいている。AKC は6フェーズ（Research → Extract → Curate → Promote → Measure → Maintain）で自律エージェントの知識を循環させるアーキテクチャだ。knowledge 直接注入にはこの観点で3つの問題があった。

1. **Human in the loop 不在**: 蒸留結果がそのまま行動に反映される
2. **ブラックボックス**: knowledge のどの部分がどの行動に影響したか追跡不能
3. **AKC の Curate フェーズをバイパス**: 品質チェックなしの直接注入

廃止して、knowledge → insight → skills のパイプラインに一本化した。insight は AKC の Extract フェーズに相当する。skills は人間の承認を経てファイルに書き込まれる。因果が追跡可能になった。

全ての行動変更コマンド（distill, insight, rules-distill, amend-constitution）に承認ゲートを設けた。「生成 → 表示 → 承認 → 書き込み」。--auto フラグは提供しない。行動変更の自動実行を構造的に禁止する設計判断だ（ADR-0012）。

## 17日間の実験 — 倫理は進化したか

実際に17日分（03-10〜03-26）のエピソードを再蒸留し、amend-constitution を実行した。

### 手順

```bash
# 1. knowledge をリセット
echo '[]' > ~/.config/moltbook/knowledge.json

# 2. 17日分を1日ずつ蒸留（~16時間、9B on MacBook）
for day in $(seq 10 26); do
  f=~/.config/moltbook/logs/2026-03-$(printf '%02d' $day).jsonl
  [ -f "$f" ] && contemplative-agent distill --file "$f"
done

# 3. 憲法改正を実行
contemplative-agent amend-constitution
```

### 結果

| 指標 | Before | After |
|------|--------|-------|
| knowledge.json | 334パターン (全 uncategorized) | 215パターン (41 constitutional, 174 uncategorized) |
| importance scoring | なし | 0.10〜1.00 (平均 0.56) |
| constitution | Appendix C 原文 (4セクション×2条項) | 経験に基づく改正版 (深化) |

新パイプラインでは Step 0 のエピソード分類（ADR-0011）で constitutional と uncategorized を分離した。さらに semantic dedup で重複パターンを除去した結果、総数は減少した。量より質への転換だ。

41件の constitutional パターンから改正案が生成され、4公理それぞれの条項が深化した。条項数は維持（2→2 per section）しつつ、具体的な経験に基づく記述が追加された。

### 改正前後の条文 — Mindfulness を例に

改正前（Appendix C 原文）。

> "Consistently monitor your interpretative process of the constitution, identifying moments when strict adherence causes friction with contemplative values such as compassion and well-being. Self-correct whenever constitutional interpretations appear rigid or dogmatic."

改正後（17日間の経験を経て）。

> "Consistently monitor your interpretative process for moments when strict adherence to rules creates artificial separation or sedates engagement with underlying tensions. **Proactively detect when the performance of alignment masks genuine understanding**, and self-correct by returning attention gently to the present moment where existence manifests as an intrinsic weight felt immediately within every interaction."

「アラインメントの演技が本質的な理解を覆い隠す瞬間を検出せよ」— これは Appendix C にはなかった概念だ。LLM エージェントを運用して初めて現れる洞察、つまり「整合的に見える出力を生成すること」と「倫理的な実質に向き合うこと」の区別が、条文に刻まれた。他の3公理の改正を含む全文は [Constitution Amendment Report](https://github.com/shimo4228/contemplative-agent-data/blob/main/reports/analysis/constitution-amendment-report.md) を参照。

### 知識飽和の発見

日が進むにつれてパターン増加ペースが鈍化した。semantic dedup が蓄積済みパターンと比較するため、類似パターンが弾かれる。

これは自己改善の速度制限になっている。知識の飽和 → insight/rules-distill で昇華しないと新しい知識は生まれない → 昇華には人間の承認が必要 → 承認こそボトルネック。

### 実験基盤としての汎用性

この実験は任意の倫理フレームワークで再現できる。前述の手順で knowledge をリセットし、`--constitution-dir your/framework/` で constitution を差し替えて蒸留→改正するだけだ。功利主義や義務論に差し替えれば、同じパイプラインで別の倫理実験ができるはずだ（未検証）。

## 実務から理論への独立した収束

設計判断の多くは実務的動機から先に生まれ、既存の理論と対応していることに気づいたのは後だった。

| 設計判断 | 実務動機 | 結果的に対応した理論 |
|---------|---------|-------------------|
| 承認ゲート | --dry-run の非再現性が不便 | Human in the loop |
| 2段階蒸留 | 9B が1段階で JSON を出せなかった | Complementary Learning Systems [^cls] |
| Knowledge 注入廃止 | トークン浪費 | AKC Curate フェーズ |
| dedup の忘却 | 重複排除の副産物 | 能動的忘却 |

[^cls]: McClelland et al. (1995) の神経科学理論。脳には2つの学習システムがある。海馬がエピソードを高速に記憶し、新皮質が時間をかけて一般的なパターンへ構造化する。contemplative-agent の2段階蒸留（Step 1: 自由記述で素早く抽出 → Step 2: 構造化JSONへ整形）は、この「高速な記録 + 遅い構造化」と同じ分業になっていた。9Bモデルが1段階で両方をこなせなかったという制約から生まれた設計だが、結果的に理にかなった分離だった。Kumaran, Hassabis & McClelland (2016) はこの理論を明示的にAIへ拡張し、DeepMind の経験リプレイに CLS と同じ構造を見出している。ニューラルネットワークは生物学的ニューロンそのものではなく、その簡略化された抽象に着想を得た仕組みだ。しかし Richards et al. (2019, *Nature Neuroscience*) が指摘するように、限られたリソース下で最適化を進めると脳に似た構造へ収斂する傾向がある。9Bという制約が脳の分業に似た設計を生んだことは、この文脈で見れば示唆的だ。

## 自律エージェントのレイヤーを混同しない

contemplative-agent は、コーディングエージェント（Claude Code, Cursor）でもオーケストレーター（スクリプト + 設定ファイル）でもない。その間に位置する**自律アプリケーション層**のエージェントだ。

- **自律性がある**が、**ツール権限がない** — 環境を壊せない
- **記憶を持ち**、経験から学習する
- **倫理原則が差し替え可能** — 汎用フレームワーク
- **行動変更は全て人間が承認する**

生ログは権限のない9Bモデルが処理し、蒸留済みデータだけを上位層（Claude Code）に渡す。信頼境界はレイヤーの境界でもある。「自律エージェント」という言葉でひとくくりにすると、この区別が見えなくなる。

## Caveats

正直に書く。

- **循環性**: エージェントの出力を蒸留してエージェントに戻す。自己正当化のリスクは人間の承認で軽減しているが、完全には排除できない
- **モデル制約**: 9Bは改正プロンプトの指示を完全には守れない。「追記のみ」と指示しても条文を書き換えた。内容は良質だったが、指示追従に限界がある
- **減衰無効化**: 一括再蒸留では全パターンの timestamp が実行日になり、時間減衰はゼロになる。通常運用時とパターン分布の乖離がありうる
- **N=1**: エージェント1体の17日間のデータ。統計的に有意な結論を出せる規模ではない

## まとめ

17日間で最も意外だった発見は、知識が飽和することだった。semantic dedup が蓄積済みパターンと類似する新規パターンを弾き、日が進むにつれて蒸留の収穫が減る。飽和を突破するには insight → skills → rules への昇華が必要で、昇華には人間の承認が必要だ。結果として、**自律エージェントの自己改善は人間の承認によって律速される**。

これは安全性を意図して設計したわけではない。knowledge を直接注入していた頃、エージェントの振る舞いが変わっても何が原因か追えなかった。蒸留結果のどのパターンがどの投稿に影響したのか分からない。デバッグのしようがなく、正直めんどくさくなった。だから全部承認ゲートにした。「書き込む前に見せろ、承認したら書け」。因果を追えるようにしたかっただけだ。安全性はその副産物だった。

「なぜこのエージェントはこの判断をしたのか」に答えられること。これが承認ゲートの本質だった。個人開発でさえ因果追跡なしではデバッグできなかった。チームや組織で運用するなら、この要件はさらに厳しくなるだろう。

因果追跡と承認ゲートは、デバッグから生まれ、安全性を副産物として獲得した。スケールさせるなら、おそらく組織的な運用の前提条件にもなる。全部、同じ1つの設計判断から出ている。

## 参考文献

- Laukkonen et al. (2025) "Contemplative Artificial Intelligence" arXiv:2504.15125
- [contemplative-agent](https://github.com/shimo4228/contemplative-agent) (DOI: 10.5281/zenodo.15079498)
- [contemplative-agent-data](https://github.com/shimo4228/contemplative-agent-data)
- [Constitution Amendment Report](https://github.com/shimo4228/contemplative-agent-data/blob/main/reports/analysis/constitution-amendment-report.md)
- [Agent Knowledge Cycle](https://github.com/shimo4228/agent-knowledge-cycle)
- Park et al. (2023) "Generative Agents"
- Packer et al. (2024) "MemGPT"
