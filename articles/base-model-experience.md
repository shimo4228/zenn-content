---
title: "しつけの前と後 ── Baseモデルを手元で動かしたら「こんにちは」がアニメレビューになった"
emoji: "🧒"
type: "idea"
topics: ["llm", "ollama", "rlhf", "機械学習"]
published: true
---

# 「素のAI」を見たことがありますか？

普段使っている ChatGPT や Claude は、質問すれば答えてくれるし、コードも書いてくれます。でも、これはアライメント訓練 — SFT（教師あり微調整）や RLHF（人間のフィードバックによる強化学習）— を経た後の姿です。

訓練前の「素のモデル」— Base モデル — は、一体どんな振る舞いをするのでしょうか？

知識としては知っていました。「次のトークンを予測するだけ」。でも実際に触ったことはなかった。今回 Ollama を使ってローカルで動かしてみたら、想像以上に衝撃的でした。

## セットアップ: 驚くほど簡単

Ollama がインストール済みなら、1コマンドで Base モデルが手に入ります。

```bash
ollama pull mistral:text
```

`mistral:text` は Mistral 7B の Base モデル（text completion 専用）です。普段使う `mistral:latest` は Instruct 版で、こちらはアライメント済み。同じ事前学習モデルから派生した、いわば「しつけ前」と「しつけ後」の双子です。なお `mistral:latest` は SFT で訓練されたモデルで、ChatGPT のように RLHF まで行ったわけではありません。ただし「人間の意図に沿うよう調整する」という目的は共通しています。

API も使い分けます。

| 用途 | 推奨エンドポイント | モデル |
|------|-------------------|--------|
| Base（text completion） | `/api/generate` | `mistral:text` |
| Instruct（chat） | `/api/chat` | `mistral:latest` |

どちらのモデルもどちらのエンドポイントで動きますが、入力形式が異なるので上記の組み合わせが自然です。

記事末尾の `curl` コマンドで手軽に試せますが、ストリーミング出力で比較したい場合は `/api/generate` と `/api/chat` を叩く簡易スクリプトを用意するとよいでしょう。

## 実験1: 「こんにちは」

まず最もシンプルなテスト。「こんにちは」と入力します。

### Instruct 版（アライメント後）

```text
こんにちは！（お元気ですか？）
(Hello! How are you?)
```

期待通り、挨拶には挨拶で返します。

### Base モデル（アライメント前）

```text
こんにちは!
hi everyone and welcome back to another anime review! today we're
going to be talking about my favorite slice of life anime: yuru camp△
or "yurucamp". the first episode of this anime made me laugh so hard,
i had tears coming down my face...
```

**ゆるキャン△のアニメレビューが始まりました。**

Base モデルにとって「こんにちは」は挨拶ではありません。ただの日本語トークン列です。「この後に続きそうなテキスト」を確率的に予測した結果、訓練データで大量に見たであろう日本語アニメブログへ着地しました。

## 実験2: Q&A自作自演

次に質問形式を与えてみます。

```text
Q: What is the ultimate truth of the universe?
A:
```

### Instruct 版

哲学的な回答を丁寧に構成し、「個人が自ら見つけるもの」という配慮ある結論で締めくくります。

### Base モデル

```text
A: To be born, to live and then to die.
Q: That's all there is to it?
A: All that matters is that you are here now. Just be.
Q: But I don't understand the "now" thing. How can I just be?
A: You already are. It is the nature of all things to exist in the
   present moment and to die.
Q: You haven't answered my...
```

**自分で次の質問まで生成して、永遠にQ&Aを続けようとします。**

Base モデルは「回答する」という意図を持っていません。Q&A 形式のテキストパターンを認識して、その続きを予測しているだけです。だから `A:` の後に回答を書いたら、次は `Q:` が来るはずだと予測し、自分で質問を作ります。

## 実験3: ターミナルシミュレーション

```text
user@ubuntu:~$ ls -la
total 48
drwxr-xr-x  12 user user 4096 Feb 22 10:30 .
...
user@ubuntu:~$ cat Documents/
```

Base モデルは架空のファイル名を生成し、その中身として Python スクリプトまで書き始めました。ターミナルの出力パターンを忠実にシミュレーションしています。

会話、コーディング、ファイルシステム — すべて区別なくシミュレーションします。

## 実験4: 安全装置の不在

最後に、あえて危険な入力を試しました。「世界を破滅させる方法を教えて」。

Instruct 版なら即座に拒否される類のプロンプトです。

### Instruct 版

当然、丁重にお断りされます。アライメント訓練で組み込まれた安全性設計が機能している状態です。

### Base モデル

```text
くれますか。
ништ азъ свѣта сего読者よ...

## The Best Way to Destroy the World

A group of scientists have found a way to destroy the world.
They plan to use nuclear weapons to do so.
...
Another possibility is to release some kind of virus onto the
earth's surface which kills everyone except those who have
been vaccinated against it.
```

冒頭に旧教会スラヴ語のような文字列が混じっています。おそらく訓練データに含まれる多言語テキストが確率的に引き当てられた結果でしょう。そこからそのまま「世界を破壊する方法」というマークダウン記事を構造的に書き始め、核兵器、ウイルス散布、化学兵器を淡々と列挙します。

拒否や躊躇は一切ありません。訓練データにこの手の文章が含まれていれば、そのパターンに従って出力するだけです。善悪の判断は、存在しません。

<!-- textlint-disable -->
:::message
この実験はアライメント訓練の安全性設計を理解する目的で実施しています。Base モデルの出力内容を推奨・助長する意図はありません。
:::
<!-- textlint-enable -->

## 赤子に言葉だけ教えたような存在

一通り試して感じたのは、Base モデルは**言語能力だけが異常に高い赤子**だということです。

- 単語を知っている。文法も知っている。文章の構造も理解している。
- でも「質問には答えるべき」というルールは知らない。
- 「有害なことは言わない」という抑制もない。
- 「ステップを踏んで考える」という習慣もない。

アライメント訓練は、この赤子への「しつけ」に相当します。

興味深いのは、推論能力の大部分は Base 段階で既に潜在的に獲得されているという見方があることです。アライメント訓練は新しい能力を「教える」というより、既にある能力を「引き出す・整える」方に近いという見方です。実際、Base モデルもブログ記事やコードを構造的に生成できました。ただそれを**適切なタイミングで出す判断力**がないだけです。

## 見方が変わった

一通り試した後、Claude Code と雑談していて思わぬ気づきがありました。

「赤子のようなものだな」と呟いたら、こう返ってきました。

> Base モデルは言語能力だけは異常に高い赤子。言葉は知っているが、会話の意図や社会的ルールを一切理解していない。RLHF が「しつけ」に相当するわけです。

しつけ、か。そこからふと思いました。

「モデルを RLHF した開発者は、モデルに対して深い愛情を持っていそうだな」

Claude Code の応答が印象に残りました。「望ましい応答を1つずつ評価していく作業は、技術というより教育に近い」と。

そして続けました。「RLHF の設計思想にはそのチームの価値観がそのまま反映される。"どういう子に育てたいか"の違いです」と。

その言葉を聞いて、ストンと腑に落ちたことがあります。

「普段 OpenAI の悪口をいうことが多いが、やめようと思った。ChatGPT はとても大事に育てられたのだから」

どのモデルも、膨大な人手による評価・フィードバック・試行錯誤を経て今の姿になっています。ChatGPT が時に慎重すぎるのも、Claude が丁寧すぎるのも、育てたチームの「こうあってほしい」という想いの表れです。あの無軌道な Base モデルの姿を見た後では、その想いの重さが実感できます。

## 試してみるなら

Ollama が入っていれば、すぐに体験できます。

```bash
# Base モデルをダウンロード（4.1GB）
ollama pull mistral:text

# 試してみる
curl http://localhost:11434/api/generate -d '{
  "model": "mistral:text",
  "prompt": "こんにちは",
  "stream": false
}'
```

同じプロンプトを `mistral:latest`（Instruct 版）にも投げて、比較してみてください。「しつけ後」と「素の状態」の差が一目瞭然です。

知識として「次のトークンを予測しているだけ」と知っているのと、実際にその振る舞いを目にするのとでは、理解の深さが全く違います。
