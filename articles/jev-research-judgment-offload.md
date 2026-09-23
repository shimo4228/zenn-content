---
title: "LLMに任せていたリサーチの判定を、判定専用モデルJevに移す"
emoji: "🔬"
type: "tech"
topics: ["jev", "pydanticai", "aiエージェント", "llm"]
published: true
published_at: 2026-09-25 09:00
---

私は毎朝、AIエージェントに論文やリポジトリを探させ、調査レポートを書かせています。エージェントの仕事の大部分は、見つけた資料を1本ずつ読んで「これはいまの関心に関係あるか」「新しいことを言っているか」を決めることです。これまでは、この判断もすべてClaude Opusがしていました。

この「関係あるか」「新しいか」は、はい・いいえか、数段階の評価で答えられます。そこで、この判定だけを、文章を書かない判定専用のモデル[Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)に移しました。ポイントは、Jevに「関係あるか」と聞くたびに、何に対して関係あるか、つまりそのテーマでいま答えを探している問いを一緒に渡すことでした。

JevはPydantic AIから、ほかのモデルと同じ1行で呼べます。

```python
from pydantic_ai import Agent

agent = Agent("typesafe:jev-1.13.0", output_type=Answers)  # Answers は判定項目を並べた Pydantic モデル
```

![資料1件だけを渡すとJevは「何に対して？」になり、資料1件と問い1つを渡すと、別の問題・同じ分野・同じ問題・同じ問いの段階つきで答える](/images/jev-research-judgment-offload-hero.png)

採点係に答案だけを渡しても採点できないのと同じで、Jevにも何に対して判定するかを一緒に渡します。

## 全部Opusに任せていた毎朝のリサーチ

調査のテーマ（以下、ライン）は8本あり、毎朝そのうち3〜4本についてレポートを作ります。これまでの仕組みは、`claude -p`でOpusを起動し、WebSearchやWebFetchを持たせて最大55ターン自由に動かすものでした。どこを検索するか、読んだ資料が関係あるか、何が新しいか、どう書くかを、ラインごとに起動したOpusがすべて決めます。`claude -p`が出力に報告する費用は、直近3日で1日$13〜15でした（新しいパイプラインの費用は、Jev分を請求額で確かめられていないので、この記事では比べません）。

「どこを探すか」「どう書くか」は、答えの形が開いた仕事です。決まった選択肢はありません。一方で「この資料は関係あるか」「強い証拠か」は、答えの形が閉じています。閉じた答えの判定なら、判定専用のモデルに任せられるはずです。

## パイプラインの全体像

既存の仕組みとは別に、次の流れのパイプラインを作りました。表は最終的な形で、1本のラインを処理する流れです。1本のラインにつき、Obsidianにレポートを1本書きます。毎朝の1回の実行では、輪番で3本と、Jevの動向を追うライン1本を処理します。

| ステップ | 名前 | 担当 | やること |
|---|----|------|----------|
| 1 | 問いを読む | コード | 「そのラインでいま答えを探している問い」のファイルを読む。問いは事前にClaude（Opus 5.5）がリポジトリの知識グラフなどから起こし、私が確認したもの |
| 2 | 検索語を読む | コード | 問いごとの検索語を読む。検索語も事前にClaude（Opus 5.5）が問いから作り、試し打ちしてから問いのファイルに書いたもの。問いを変えたら検索語も作り直す |
| 3 | 取得する | コード | arXiv・Hugging Face Papers・GitHub・新着一覧から資料を取る |
| 4 | 資料をふるう | Jev | 問いに関係しそうか、証拠を含むか、指示文が埋め込まれていないか、出典は信頼できるか |
| 5 | 資料 × 問いで判定する | Jev → コード | Jevが資料1件を問い1つと並べて答え、コードがその確率に閾値をかけて採用・要確認・不採用を決める |
| 6 | 文を判定する | Jev・コード | 採用した資料の文ごとに、問いを進めるか、既知かをJevに聞く。資料が本当にそう言っているかは、まずコードが文字列で照合する |
| 7 | 問いごとに書く | LLM → Jev | LLMがその日に証拠が増えた問いの節を書き、Jevが質を点検する |
| 8 | レポートを書き出す | コード | 節を並べ、Obsidianに保存する |

閉じた質問に答えるのはJevで、その答えから次に進むものを決めるのはコードです。Claudeを使うのは、問いと検索語を事前に書くときだけで、毎朝の実行中は1回も呼びません。実行中にLLMが文章を書くのは、ステップ7の本文と、翌日以降の問いの候補を作るときです（検索語をまだ書いていない問いでは、ステップ2でもLLMが候補を作り、Jevが選びます）。この記事で扱うのは、ステップ4〜6の判定です。

![事前にClaudeが問いと検索語を書き、実行中は準備（コード）、判定（Jevが答えてコードが決める）、書く（LLM→Jev）、出す（コード）の順に進む](/images/jev-research-judgment-offload-pipeline.png)

Jevが答えてコードが決める形になっているのは、真ん中の判定の塊だけです。

資料をどこから、どの順で、どれだけ取るかは、今回はコードで決めています。検索語は事前に書いたものを使い、読んだ結果を見て次に探す先を決める仕組みはありません。探索は本来、読んだ結果を見て次に探す先を決める、ReActのようなLLMの仕事だと考えています。今の形でもパイプラインは回っていますが、レポートの質しだいではLLMの探索に戻すかもしれません。

実行中に使うモデル（JevとLLM）は、すべてPydantic AIの`Agent`から呼んでいます。Pydantic AIを選んだ理由は2つです。JevのTypeSafeモデルに早々とネイティブ対応していたこと。それから、モデルを呼んで型で検証し、失敗したら再試行する、というエージェントの実行基盤を自分で一から作りたくなかったことです。モデルは文字列1つで差し替えられます。実際、実行中に使うLLM（AlibabaのDashScope API経由）は、候補を作る側を途中でQwenの軽量版からDeepSeek V4.1 Flashに替えました。無料枠を使い切ったためです。本文を書くのはqwen3.8-maxです。

Jevでは、出力の型を書くと、型ごとにJevへの聞き方が決まります。

| Pydanticの型 | Jevへの聞き方 |
|--------------|---------------|
| `float`（0〜1） | 質問への答えが「はい」である確率 |
| `Literal[...]` | 選択肢から1つ |
| docstring付きの `IntEnum` | 段階評価 |

1つの出力型に並べた項目は、1回のrequestでまとめて送られます（[Pydantic AIのTypeSafe model docs](https://pydantic.dev/docs/ai/models/typesafe/)、2026-09-23時点）。

## 問いと並べて聞く

Jevに「関係あるか」と聞くには、何に対して関係あるかを渡す必要があります。このパイプラインでは、それをラインごとの問いにしています。いま答えを探している問いを3〜5個、ファイルに書いておきます。私が研究しているエージェントの知識運用の枠組み（AKC）を扱うラインでは、問いの1つはこうです。

```markdown
<!-- questions/akc.md から抜粋 -->
## エージェントと運用者の意図整合は、テストで検査できない部分をどう保っているか
- brief: AKC の主張は「テストが検査できない整合を、双方向の成長ループが保つ」。同種の主張を持つ設計（harness 自己進化、記憶アーキテクチャ、承認ゲート）が、整合の劣化をどう検知し、何を根拠に改善したと言っているか
- evidence: 時間軸のある測定。単発ベンチマークは弱い
- not: モデル単体の alignment 訓練（RLHF 等）
```

`brief`は問いの範囲、`evidence`は証拠として数えるもの、`not`はキーワードは重なるがこの問いの対象ではない話題です。実際、この問いに対しては「alignment」を題名に含む論文が21本判定に回ってきました。音声と表現の対応づけ（cross-modal alignment）のように、語が同じだけの論文も多く含まれます。`not`には、隣の話題でとくに紛れやすいもの（ここではモデル単体のalignment訓練）を書いておき、Jevが判定の材料にできるようにします。

判定は、すべて問いと組にして聞きます。ステップ4では、資料1件ごとに、そのラインの問いすべてについて「関係しそうか」をまとめて安く聞き、候補を絞ります。ステップ5では、残った「資料1件 × 問い1つ」の組ごとに詳しく聞きます。ステップ6は「文1つ × 問い1つ」です。

ここからはステップ5の話です。ステップ5では、資料の扱う問題が問いの問題にどれだけ近いかを、4つの段階で聞きます。下から「語を共有するだけの別の問題」「同じ分野だが別の問題」「同じ問題」「同じ問いに答えている」です。

この意図整合の問いに対して、どれも「intent」を題名に含む3本の論文を、Jevは次のように判定しました。

| 論文 | 関係ありの確率 | いちばん確率の高い段階 | その日のレポート |
|------|----------------|------------------------|------------------|
| [AI Persona, Service Consumption, and User Intent Entropy](https://arxiv.org/abs/2609.23274)（AIの人格とユーザーの意図のばらつきを見るフィールド実験） | 0.08 | 別の問題（0.60） | 載らない |
| [FinInteract](https://arxiv.org/abs/2609.24002)（曖昧な金融の質問で意図を確かめる力のベンチマーク） | 0.20 | 同じ分野だが別の問題（0.53） | 載らない |
| [SkillSpec](https://huggingface.co/papers/2609.06052)（エージェントのスキルが仕様どおりかを、意図を伏せて推論させる） | 0.44 | 同じ問題（0.77） | 載らない |

「intent」という語は同じでも、問いと並べると段階が分かれます。SkillSpecは段階では「同じ問題」に置かれましたが、関係ありの確率が0.44で、コードの閾値0.5に届かず載りませんでした。Jevは確率を返すだけで、採否はコードが閾値で決めます。判定の値は手元の実行記録から取りました。実行記録はrepoには含めていません。

![意図整合の問いに対して、User Intent Entropyは別の問題（0.60、関係あり0.08）、FinInteractは同じ分野（0.53、0.20）、SkillSpecは同じ問題（0.77、0.44）に置かれ、関係ありの閾値0.5に届かず3本とも不採用](/images/jev-research-judgment-offload-ladder.png)

Jevが置く段階と、コードが閾値をかける「関係あり」の確率は、別々の答えです。

Jevに渡しているのは、次のstateです（`question_screening.py`の`state()`を簡略化）。これをJSONにして`agent.run()`に渡します。

```python
state = {
    "line": {"name": line.name, "vocabulary": vocabulary},
    "question": {
        "title": question.title,
        "brief": question.brief,
        "method": question.method_constraints,
        "evidence": question.evidence_constraints,
        "not": question.negative_topics,
    },
    "source": source_state(source),  # 資料のタイトル・本文の抜粋・URL など
    "evidence_set": evidence_set,  # この問いで採用済みの証拠
}
```

出力の型はこうです（抜粋。`Probability`は0〜1の`float`です）。descriptionの`question.brief`や`evidence_set`は、上のstateのキーを指しています。

```python
class Overlap(UseEnumMemberDocstrings, IntEnum):
    other_problem = 0
    """It works on a different problem that happens to share vocabulary."""
    same_field = 1
    """Same field as `question`, but not the problem `question` asks about."""
    same_problem = 2
    """It works on the problem `question` asks about, from another angle."""
    same_question = 3
    """It asks what `question` asks and reports an answer to it."""


class Answers(BaseModel):
    """Screen one source against one open research question."""

    on_topic: Probability = Field(
        description="Is `source` about the problem `question` asks about, as `question.brief` "
        "describes it? No if it is about one of `question.not` (neighbouring topics that keep "
        "matching), or if it only shares a word with it."
    )
    problem_overlap: Overlap = Field(
        description="How close is the problem `source` works on to the one `question` asks about?"
    )
    novelty_vs_evidence_set: NoveltyVsSet = Field(
        description="Compared with `evidence_set` (the claims already accepted for this "
        "question), what would `source` add?"
    )
```

表の「いちばん確率の高い段階」は、この`Overlap`の4段階です。1本目の論文は、いちばん下の「語を共有するだけの別の問題」に落ちました。新しさも、この問いで採用済みの証拠に何を足すかで聞きます。

## 最終の実行の数字

レポートは、その日に証拠が増えた問いごとに1節を書く形です。最終の実行では4ラインを処理しました。検索語を事前に書く形に変える前の実行で、検索語はLLMが作りJevが選んでいました。

| 項目 | 値 |
|------|-----|
| 1ラインのJevへの質問数 | 1,400〜1,511問（新着の少なかった1ラインは14問） |
| レポートの大きさ | 7.4〜12.0 KB |
| Claudeの呼び出し | 0回 |

絞り込みが読むべき資料まで落としていないかは、数字だけでは分かりません。そこで、Jevの動向を追うラインの問いには、「これは通るべき」と私が分かっている資料（canary）を4件置き、最終の実行で4件とも通りました。ほかのラインにはまだ置いておらず、落とした資料全体の取りこぼしも測っていません。

## 書くのはLLMの仕事として残す

ステップ7で書いたレポートの質を、パイプラインの外で、実装したセッションとは別のコンテキストのOpusに判定させました。最終の実行で本文を書いた3ライン分のうち、公開してよい質は1本でした。落ちた稿の典型は、証拠を問いの言葉に読み替えるものです。

「agentが自分で書いた規則を自分で破る失敗は、何がすり抜けさせているか」という問いの節で、本文は「存在しない規則への違反をでっち上げる誤検知」の論文を、「規則をすり抜ける見逃し」の説明として書いていました。Jevはこの論文を、この問いに対して境界ぎりぎりで通しています。関係ありの確率は0.54、段階は「同じ問題」が0.51、「同じ分野だが別の問題」が0.35でした。通したこと自体は外れていません。向きを逆にしたのは本文の側です。

文章を書くのはLLMの仕事なので、ここはJevに移す対象ではありません。本文は、指示の直し（根拠の段落に結論を書かせない）と、qwen3.8-maxのthinkingを有効にしたことで良くなりました。残った弱さは、書くモデルの選び方の問題だと考えています。書く側もPydantic AIの`Agent`なので、GPTのように文章の得意なモデルへ文字列1つで差し替えられます。差し替えで改善するかは、まだ測っていません。

## Jevに判定を渡す前に確かめること

- **何に対して判定するかをstateに入れたか。** 「関係あるか」は、何に関係あるかが無いと何でも通ります。問い、その範囲（`brief`）、除外する話題（`not`）、採用済みの証拠を渡します
- **答えが閉じているか。** はい・いいえの確率、選択肢、段階評価のどれかで言える判定だけを移します。段階評価は、各段を具体的な状況で書きます（`same_field`は「同じ分野だが、問いの問題ではない」）
- **語を共有するだけの資料が落ちる段階があるか。** 「別の問題」の段階が無ければ、Jevは近い段階に寄せるしかありません
- **通るべき資料を置いたか。** 量が減っただけでは、落としすぎと区別できません
- **書くLLMも同じ`Agent`で、モデルの文字列を分けたか。** 判定の型を変えずに、書くモデルだけを差し替えられます

コードは[jev-research-pipeline](https://github.com/shimo4228/jev-research-pipeline)で公開しています。

## 関連リンク

- [文章を書かないモデルJevのスキル選択は、0.3秒でOpusにどこまで近づくか](https://zenn.dev/shimo4228/articles/jev-vs-opus-skill-selection)
- [JevのスキルルーターをClaude Codeに足して、スキル一覧を書き換える手前で引き返した](https://zenn.dev/shimo4228/articles/jev-retrofit-limits)
- [Jevの判断をローカルで再現するには何が要るか](https://zenn.dev/shimo4228/articles/local-decision-model-conditions)
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/jev-research-judgment-offload.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
