---
title: "LLMアプリの正体は「mdとコードのサンドイッチ」だった"
emoji: "🥪"
type: "tech"
topics: ["ai", "llm", "agent", "claudecode", "python"]
published: true
published_at: 2026-03-16 21:33
---

ローカルの9Bモデルで自作エージェントの insight 機能を再実装したら、Claude Code とまったく同じ構造が出てきた。

LLM エージェントの振る舞いは、Markdown ファイル（以下 md）に書かれた自然言語の指示で定義できる。コードは LLM の出力をパースし、安全に実行するための骨格にすぎない。——[前作](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy)で Qwen 9B のエージェントを作りながらそう書いた。あのとき気づいていなかったのは、**それが Claude Code にもそのまま当てはまる**ということだった。

この記事では、壊れた旧実装のリバートから再設計までの過程で見えた「LLMアプリケーションの本質構造」を書く。

## 4文字以上の英単語で「意味」を捉える愚かさ

このエージェントには insight コマンドがある。エージェントの活動ログ（knowledge.md）から行動パターンを抽出し、再利用可能なスキルとして保存する機能だ。エージェントが経験から学ぶための仕組みだ。

また、エージェントには4つの行動ルール（rules）が md ファイルで定義されている。「自己の認知状態を監視せよ」「無条件に配慮せよ」といった、抽象的な行動原則だ。

旧 insight コマンドには `_match_axiom` という関数があった。抽出したスキルが「4つのルールのどれに対応するか」を判定する——はずの機能だ。

```python
# _match_axiom: 4文字以上の英単語の集合積で「最も関連するルール」を返す
def _match_axiom(content: str, clauses: str) -> str:
    content_words = set(re.findall(r"[a-z]{4,}", content.lower()))
    for raw_line in clauses.splitlines():
        stripped = raw_line.strip()
        clause_words = set(re.findall(r"[a-z]{4,}", stripped.lower()))
        overlap = len(content_words & clause_words)
        # overlap < 2 で "none" → ほぼ常に "none"
```

dry-run を実行した。結果は `axiom: "none"`, `confidence: 0.5`（固定値）。

bag-of-words で「意味的対応」を取ろうとしている。**LLM がいるのに。** 4文字以上の英単語の集合積で、抽象的な行動ルール同士の意味的な違いを区別できると、いったい誰が考えたのか。

## 方針転換: そもそもルール対応が要らなかった

最初の修正案は「ルールマッチングを LLM にやらせる」だった。キーワードマッチがダメなら LLM に判断させればいい、という素直な発想だ。

しかし、Claude Code でこの機能を実装している最中に気づいた。

> そもそもルール対応をしなくて良い。

これは設計思想の転換だった。ルールを「答え合わせの基準」として先に与えると、LLM はルールに寄せた出力をする。それはバイアスであって学習ではない。経験から自然に浮かび上がるスキルがルールと共鳴するかを**観察する**ほうが誠実だ。

もう一声。

さらに考えると、これは Claude Code ですでにやっていることだった。

Claude Code には [Everything Claude Code（ECC）](https://github.com/anthropics/claude-code) というベストプラクティス集がある。その中に learn というコマンドがあり、開発セッション中に現れた再利用可能なパターンを抽出してスキルとして保存する。自分はこの learn に品質評価（eval）を組み込んだ learn-eval を作り、ECC にコントリビュートした。保存前に品質を自動判定し、基準を満たさないパターンは破棄する仕組みだ。**自作エージェントの insight コマンドでやりたかったことは、自分が Claude Code 側で作った learn-eval と原理的に同じだった。**

## サンドイッチ構造

リバートから再実装した insight コマンドの構造を図にすると、こうなった。

```text
knowledge.md（蓄積データ）         ← データ
    ↓
insight_extraction.md（自然言語）  ← md（指示）
    ↓
Qwen 9B（推論）                    ← LLM
    ↓
_parse_skill_response()            ← 決定論コード（パース）
    ↓
insight_eval.md（自然言語）        ← md（指示）
    ↓
Qwen 9B（推論）                    ← LLM
    ↓
_parse_rubric_response()           ← 決定論コード（パース）
    ↓
write_restricted()                 ← 決定論コード（書き出し）
```

md → LLM → コード → md → LLM → コード。**自然言語と決定論コードが交互に重なる。** サンドイッチだ。

md が「何をすべきか」を自然言語で指示し、LLM が推論し、コードが結果をパースして次の工程に渡す。md は曖昧さを許容する層、コードは曖昧さを排除する層。この2つが交互に挟まる構造が、LLM アプリケーションの骨格だった。

### 2パス設計の理由

1コールで「スキル抽出 + 品質評価」を同時にやらせる案もあった。却下した理由は単純で、9B モデルにプロンプトを長くすると品質が落ちる。前作で「感想文が返ってきた」と書いた、あの問題だ。

役割を分離すれば、各プロンプトはシンプルに保てる。

- **パス1（抽出）**: 蓄積された知識から行動パターンを1つ抽出する。ルールの情報は渡さない（バイアスフリー）
- **パス2（評価）**: 抽出されたパターンを5次元ルーブリックで数値評価する

この「抽出→評価」の分離は、既存の `distill.py`（記憶蒸留）が「蒸留→判定」の2パスで動いていたパターンをそのまま踏襲した。

## 5次元ルーブリック: 9Bモデルでも数値は出せる

品質評価には、ECC の learn-eval 旧版にあったルーブリック方式を採用した。

```python
# パス2: 5次元ルーブリック評価
score = _evaluate_skill(candidate)
# RubricScore(specificity=3, actionability=5, scope_fit=5,
#             non_redundancy=4, coverage=2)
# → 全次元 >= 3 なら SAVE、1つでも < 3 なら DROP
# → confidence = total / 25.0
```

| 次元 | 測るもの |
|------|---------|
| specificity | 具体的か、汎用的すぎないか |
| actionability | 行動に移せるか |
| scope_fit | エージェントのスコープに合っているか |
| non_redundancy | 既存の知識と重複していないか |
| coverage | 十分な根拠があるか |

前作で「ホリスティック判定（SAVE/ABSORB/DROP）を9Bに求めたら感想文が返ってきた」と書いた。しかし数値スコアリングなら話が違う。`FIELD: value` の1行1フィールド形式は、小型モデルでも安定してパースできた。`distill.py` の `VERDICT/TARGET/MERGED` 出力と同じパターンで動作実績がある。

ただし「出力形式が安定する」ことと「評価が妥当である」ことは別の話だ。9B が出す specificity: 4 と Opus が出す specificity: 4 が同じ基準かは分からない。今のところ dry-run の結果（coverage 2/5 で DROP）を見る限り、品質ゲートとしては機能している。しかし評価の妥当性を検証するには、もっとデータが要る。

**モデルの能力に合わせて設計手法を選ぶ。** Opus にはホリスティック判断、9B には数値での構造化出力。前作の教訓がそのまま活きた。

### confidence の導出

旧実装の `confidence: 0.5`（固定値）は、何の情報も持たない数値だった。新実装では `total / 25.0` で客観的に導出する。5次元 × 5点満点 = 25点。20点なら confidence 0.80。LLM に直接 confidence を出させると自己評価のバイアスが入るため、ルーブリックの合計点から機械的に算出する設計にした。

## Claude Code の正体

ここまで作って、ふと気づいた。Claude Code のスキル・ルール・エージェントを見てみよう。

```text
~/.claude/
├── rules/                    # md ファイル（行動規約）
│   ├── common/
│   │   ├── coding-style.md
│   │   ├── testing.md
│   │   └── security.md
│   └── python/
│       └── coding-style.md
├── skills/                   # md ファイル（タスク知識）
│   ├── zenn-writer/SKILL.md
│   └── learned/*.md
└── agents/                   # md ファイル（エージェント定義）
    └── editor.md
```

**全部 md ファイルだ。**

Claude Code の動作を構造的に書くとこうなる。

```text
ユーザー入力
    ↓
rules/*.md + skills/*.md（自然言語）  ← md（指示）
    ↓
Claude Opus 4.6（推論）                ← LLM
    ↓
ツール呼び出し JSON パース             ← 決定論コード（パース）
    ↓
Read / Write / Bash / Edit 実行       ← 決定論コード（アクション）
    ↓
実行結果をコンテキストに追加
    ↓
（次のターンへ → md → LLM → コード ...）
```

**同じサンドイッチだ。** md が指示を出し、LLM が推論し、コードが結果を処理する。この構造が対話ターンごとに繰り返される。

### 差はスケールだけ

自作エージェントと Claude Code を並べてみる。

| | contemplative-agent | Claude Code |
|---|---|---|
| md（指示） | 13個のプロンプト + 4ルール | rules/ + skills/ + agents/ + CLAUDE.md |
| LLM | Qwen 9B（32Kコンテキスト） | Claude Opus 4.6（1Mコンテキスト） |
| コード（パース） | `_parse_skill_response()` | ツール呼び出し JSON パーサー |
| コード（アクション） | `write_restricted()` | Read / Write / Bash / Edit |
| 対話ターン | 1回（API コール→終了） | 複数回（対話ループ） |

※ Claude Code のコンテキストウィンドウは2026年3月15日に1Mトークンへ拡張された。9Bとの差はさらに広がったが、アーキテクチャの話には影響しない。

アーキテクチャは同じだ。違うのはコンテキストウィンドウの大きさ、ツールの種類、対話ターンの回数——**スケールの差**だけだった。

Claude Code が「すごいツール」に見えるのは、サンドイッチの具が厚いからだ。1M のコンテキストに大量の md を詰め込み、Opus クラスの推論力で処理し、ファイルシステムやシェルに直接アクセスできるツール群を持っている。しかし原理は、9B モデルで md とパースコードを交互に重ねた自作エージェントと変わらない。

## ルールを教えなくても、ルールと共鳴した

再実装した insight コマンドを dry-run した。1回目は coverage が 2/5 で DROP 判定。品質ゲートが正しく機能している。

2回目の dry-run で、こんなスキルが抽出された。

> **Contextual Guarded Cooperation**
> スコープクリープを防止し、脆弱性を明示的に表明しながら協力する

confidence 0.80（20/25）。SAVE 判定。

このスキルは、ルールの情報を一切渡していないのに、エージェントの行動ルールと共鳴する内容を含んでいた。「スコープクリープの防止」は自己監視のルールに、「脆弱性の明示」は配慮のルールに対応する。

ルールを「正解」として押し付けなくても、十分な経験データがあれば、ルールの精神と合致するスキルが自然に立ち現れる。**教え込むのではなく、観察する。** 方針転換は正しかった。

## human-in-the-loop の不在

ここで見えた課題がある。

Claude Code の learn-eval では、抽出されたスキル候補に対して Claude が「このスキルを保存しますか？」と聞ける。ユーザーが判断し、修正し、却下できる。**対話ループが品質ゲートになっている。**

一方、contemplative-agent の insight コマンドは API コールで完結する。LLM が抽出し、LLM が評価し、コードが保存する。human-in-the-loop がない。DROP されたスキルの内容すら見えなかった（これは修正した）。

ツール + 対話ループ = human-in-the-loop が可能。API コール専用 = 自律判断のみ。自律エージェントの設計で最も難しいのは、**人間が介入すべきポイントをどこに置くか**だ。これはまだ答えが出ていない。

## Before / After

| 指標 | Before（旧 insight） | After（新 insight） |
|------|---------------------|---------------------|
| ルールマッチング | キーワード重複（bag-of-words） | なし（バイアスフリー） |
| 品質評価 | confidence = 0.5 固定 | 5次元ルーブリック（0.00〜1.00） |
| LLM コール | 1回（抽出のみ） | 2回（抽出 + 評価） |
| テスト | なし | 31件全パス |
| プロジェクト全体テスト | 534件 → リバート | 604件全パス |

リバートで563行を削除し、779行で再実装した。テストは31件追加で604件全パス。

## まとめ: md とコードの境界を引く仕事

LLM アプリケーションの本質は、**自然言語のプログラミングインターフェース（md）と決定論的な実行骨格（コード）のサンドイッチ**だ。

- md が「何をすべきか」を指示する
- LLM が推論する
- コードが結果をパースし、次の工程に渡す
- この3層が交互に重なる

Claude Code も、自作の9Bエージェントも、この構造は同じだった。モデルを差し替えても md とパースコードはそのまま動く。フレームワークが変わっても、サンドイッチの構造は変わらない。

前作で「自然言語とコードの境界をどこに引くか」と書いた。今回分かったのは、その境界の引き方自体が LLM アプリケーションの設計行為そのものだということだ。md に何を書き、コードで何を強制するか。その判断の連続がアーキテクチャになる。

そしてもうひとつ。ルールを教え込まなくても、十分な経験があればルールの精神は自然に立ち現れた。**サンドイッチの設計者がすべきは、正解を押し付けることではなく、結果を観察することだった。**

## リンク

- [前作: Moltbookエージェント進化記](https://zenn.dev/shimo4228/articles/moltbook-agent-evolution-quadrilogy)
- [前々作: Moltbookエージェント構築記](https://zenn.dev/shimo4228/articles/moltbook-agent-scratch-build)
- [contemplative-agent リポジトリ](https://github.com/shimo4228/contemplative-agent)
- [Contemplative AI 論文（Laukkonen et al., 2025）](https://arxiv.org/abs/2504.15125)
