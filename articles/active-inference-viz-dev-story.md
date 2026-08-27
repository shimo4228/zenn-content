---
title: "理論が分からない論文をブラウザで動かしてしまった ── 能動的推論 × Claude Code"
emoji: "🧠"
type: "idea"
topics: ["claudecode", "numpy", "streamlit", "python", "ai"]
published: true
published_at: 2026-03-07 08:22
---

毎朝5時に届く AI リサーチレポートの片隅に、「能動的推論（Active Inference）」という単語があった。脳が世界の内部モデルを持ち、予測と現実のズレを最小化するように行動を選ぶ。生物の知覚・行動・意思決定を統一的に説明するフレームワーク——。

読んだ瞬間、なぜか引っかかった。

その日のうちに元論文のコードを clone し、計画から完成まで約 2 時間。PyTorch を全部剥がして純 NumPy に書き換え、さらに元コードにはなかった **ブラウザで動くインタラクティブな可視化 UI** を Streamlit で新規構築した。1550 行。テストカバレッジ 98%。

**数式レベルでは、理論の中身を理解していない。**

---

## なぜこれに惹かれたのか、自分でも分からない

生成 AI の勉強をするうちに、冒頭で触れた能動的推論——Karl Friston の自由エネルギー原理から派生した理論——に出会った。

正直に言う。数式を追っても 3 行目で振り落とされる。変分推論やベイズ推定は、概念としては分かるが手触りがない。

それでも「これを動かしてみたい」という衝動が消えなかった。daily-research（[自動リサーチレポート](https://zenn.dev/shimo4228/articles/daily-research-automation)）に載っていた開発アイデアの 1 つに「能動的推論の可視化ツール」があり、それを見た瞬間に手が動き始めた。

理由を聞かれても答えられない。ちょっと自分でも気が狂ってるなと思いながら作った。

## こんなことができてしまう時代

ここで立ち止まって考えたいことがある。

**計算論的な神経科学の論文を、理論を理解していない人間がブラウザで動く可視化ツールにしてしまった。** PyTorch を NumPy に書き換え、Jacobian を解析的に導出し、テストを書いた。さらにパラメータをいじりながらリアルタイムに挙動を観察できる UI まで載せた。所要時間は約 2 時間。

これは Claude Code のすごさであると同時に、時代の恐ろしさでもある。

「AI 時代に残るのは偏愛だけだ」という言説をよく聞く。スキルや知識は AI で代替できるが、「なぜかこれに惹かれる」という非合理な執着だけは代替できない、と。Claude Code を使い続けるうちに、この言葉が単なるポジショントークではないと分かってきた。

能動的推論のツールを作れる人間は、Claude Code があれば無数に生まれる。でも「毎朝のリサーチレポートの片隅にあった一単語へ引っかかって、理論も分からないのに作り始める人間」は、たぶんそう多くない。実装力が民主化された世界で残る差別化要因は、**何を作るかを決める偏愛**だけだ。

この記事は、その偏愛の記録だ。

---

## 元論文とコード——Claude Code の説明によると

元にした論文は Priorelli et al. (2025) "[Embodied decisions as active inference](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012745)"。PLOS Computational Biology に掲載された論文で、能動的推論を使って「身体化された意思決定」をモデル化している。

Claude Code によると、モデルは 4 つのプロセスが連動する。

1. **離散推論** — 「何を掴むか」を確率的に選ぶ（POMDP）
2. **連続推論** — 「どう手を動かすか」を予測符号化で最適化する
3. **運動学** — 3 関節アームの順運動学（角度→手先位置）
4. **身体** — 脳の信念に従って実際に手を動かす物理モデル

元コードは [PyTorch + Pymunk + Pyglet](https://github.com/priorelli/embodied-decisions) で書かれている。GPU 環境が必要で、ブラウザからは動かせない。研究者がローカルで実験するためのコードであり、**誰でもブラウザで試せるような UI は存在しなかった**。

## 設計判断: なぜ書き換えてブラウザに載せたのか——と Claude Code は言う

普段の私は Claude Code の提案を鵜呑みにしない。「なぜその設計か」「他に検討した選択肢は」「そのトレードオフは」——毎回これを聞く。Claude Code の思考を根掘り葉掘り掘り返し、納得するまで実装に入らない。過去の記事を読んでくれた方は、その姿勢を知っているはずだ。

**今回ばかりは違った。**

元の理論が全く分からないので、Claude Code が「PyTorch を NumPy に書き換えるべきです」と言った理由を検証する手段がない。「Jacobian は閉形式で導出できます」と言われても、Jacobian が何なのか数式レベルでは理解していない。「3 関節なら 2×3 の行列になります」——そうなんだ。

以下の設計判断表は、Claude Code がそう判断した記録だ。私が理解できたのは「Streamlit Cloud で動かしたい」という動機と、「uv は速い」くらいのものだった。

| 判断                     | Claude Code の理由                                                         | 却下した代替案              |
| ------------------------ | -------------------------------------------------------------------------- | --------------------------- |
| PyTorch → 純 NumPy       | Streamlit Cloud で動かすため。3 関節なら Jacobian は閉形式で書ける         | PyTorch 維持 → デプロイ不可 |
| Pymunk → Spring tracking | Streamlit Cloud に C バインディングが入らない。8 行で代替できた            | MuJoCo → 過剰               |
| frozen dataclass         | hashable → `@st.cache_data` が直接使える。精度パラメータの事故変更も防げる | dict → hashable でない      |
| Plotly > Matplotlib      | インタラクティブ操作（ホバー、ズーム）と Streamlit の相性                  | Matplotlib → 静的           |
| uv                       | 高速。`pyproject.toml` 完結。`uv run` で venv 自動管理                     | poetry → 遅い               |

<!-- textlint-disable ja-technical-writing/no-doubled-joshi -->

唯一、自分の意思で加えた動機がある。**「書き換えの過程を見ていれば少しは理解できるのではないか」** という期待だ。Claude Code が PyTorch から NumPy へ書き換えていく様子を隣で眺めれば、「何を計算しているか」くらい見えるだろう、と。結果的にこの期待は半分当たって半分外れた。「何を計算しているか」は見えるようになった。ただ「なぜそれを計算するのか」は、依然として分からない。

<!-- textlint-enable ja-technical-writing/no-doubled-joshi -->

## 最大のハマりポイント: VJP の符号が違う——らしい

書き換え作業の 8 割は淡々と進んだ。Claude Code にドキュメントとして論文記法→コード変数のマッピング表と元コードの構造マップを渡し、ファイルごとに書き換えていった。私は隣で見ているだけだ。「ふーん、そういう構造なんだ」と思いながら。

突然、**シミュレーションの値が爆発した。**

Claude Code 的に言うと「外部ユニット（手の位置の信念）が指数関数的に発散した」ということになる。私の目に見えたのは、値が `1e+15` まで膨れ上がり、数ステップで `NaN` になる画面だ。

Claude Code に聞いても「パラメータの調整を試しましょう」と的外れな提案を繰り返す。3 回聞いて 3 回とも違うことを言われた。普段なら「いや、その根拠は？」と詰めるところだが、今回は私自身に「正しい方向」の判断基準がない。Claude Code の提案が的外れかどうかすら、実は確信を持って言えない。結果的に直らなかったから的外れだったのだろう、という推測にすぎない。

結局、元論文のコードと実装を diff しながら追い、Claude Code が原因を特定した。**PyTorch の `tensor.backward(eps)` が暗黙的に含んでいる `-precision`（精度行列の負号）因子が、手動実装で抜けていた。**

——と説明されて、「そうなんだ」としか言えなかった。以下のコードが修正版だ。

```python
# continuous.py の Unit クラス — PyTorch backward(eps) の正しい NumPy 移植
# self.x[0]: ユニットの信念（手先位置）, self.pi_eta_x: 精度パラメータ
#
# WRONG:   parent.grad += J.T @ eps              ← 発散する
# CORRECT: parent.grad += -precision * (J.T @ eps)  ← 安定

eps_eta_x = (self.x[0] - fk_pred) * self.pi_eta_x
parent_grad = -self.pi_eta_x * (J.T @ eps_eta_x)  # VJP with -π factor
```

<!-- textlint-disable ja-technical-writing/no-doubled-joshi -->

`WRONG` と `CORRECT` の違いは見れば分かる。マイナスが付くか付かないかだ。しかしマイナスが必要な理由は理解できない。

<!-- textlint-enable ja-technical-writing/no-doubled-joshi -->Claude Code は「予測符号化では精度行列の負号が VJP に含まれる」と説明した。予測符号化を理解していない以上、この説明の正しさを判断できない。

この修正が数値的に正しいことだけは検証できた。Claude Code が SciPy の数値微分と解析的 Jacobian を比較するテストを書き、`atol=1e-5` で一致することを確認した。

```python
# 解析的 Jacobian のテスト — 数値微分との比較
def test_jacobian_vs_numerical():
    angles = np.array([0.3, -0.5, 0.1])
    lengths = np.array([0.4, 0.3, 0.2])
    J_analytical = analytical_jacobian(angles, lengths)
    J_numerical = approx_fprime(angles, lambda a: forward_kinematics(a, lengths))
    np.testing.assert_allclose(J_analytical, J_numerical, atol=1e-5)
```

数値が合うことと、理論的に正しいことは別の話だが、分からない人間にとってはこれが唯一の拠り所だった。

## 物理エンジンを捨てた——捨てたのは Claude Code だが

元コードは Pymunk（2D 物理エンジン）でアームの動きをシミュレートしている。Streamlit Cloud では C 拡張が使えないので代替が必要だった。

Claude Code はこう説明した。

> 能動的推論のポイントは「脳の信念が行動を駆動する」ことです。身体は信念に追従するだけで、そのラグが予測誤差を生みます。だから物理エンジンは不要で、8 行の spring tracking で代替できます。

```python
# simulation.py — 物理エンジン不要の spring tracking（8行）
BODY_TRACKING_GAIN = 8.0
actual_angles_norm += (believed_angles_norm - actual_angles_norm) * gain * dt
# → 脳の信念と身体のラグが予測誤差を生み、推論ループを駆動
```

250MB の PyTorch + Pymunk + Pyglet が、50MB の NumPy + SciPy + Streamlit に置き換わった。元コードではローカルで実験スクリプトを回すしかなかったものが、**ブラウザを開くだけでパラメータを変えながらリアルタイムに挙動を観察できる可視化ツール**になった。この判断が理論的に妥当なのかは分からない。ただ、「信念」と名付けられた値が変化し、アームが目標に向かって動くのは見える。それが能動的推論として正しい挙動なのかは、私には判断できない。

## プロジェクト構成

Claude Code が 2 時間で書いた 1550 行の構成を載せておく。計算コアの書き換えに加え、`viz/` 以下と `app.py` が元コードにはなかった新規構築部分だ。

```text
src/active_inference_viz/        # 1550行
├── model/                        # 1113行 — 数学コア
│   ├── config.py     (139行)     — SimConfig (frozen), SimResult
│   ├── math_utils.py (230行)     — Jacobian, FK, softmax, BMC
│   ├── discrete.py   (176行)     — 離散推論 (POMDP)
│   ├── continuous.py  (258行)     — 予測符号化 (Unit/Obs)
│   ├── brain.py      (162行)     — 離散+連続の結合
│   └── simulation.py (148行)     — trial ループ
├── viz/                          # 265行 — 可視化
│   ├── theme.py       (58行)
│   ├── arm_view.py   (122行)     — 2D アーム表示
│   └── belief_panel.py (85行)    — 信念時系列
└── app.py            (176行)     — Streamlit UI

tests/                            # 519行, 50テスト, 98%カバレッジ
```

右側のコメントは Claude Code の注釈そのままだ。「BMC」が何の略かすら知らない（Bayesian Model Comparison だそうだ）。

## 正しくできているのか、分からない

テストは通る。数値微分との比較も合う。Streamlit 上でアームは動く。キューが提示されると信念が変化し、手が目標に向かう。

**でもそれが「能動的推論として正しい」のかは分からない。**

予測符号化の更新式が理論的に正しいのか。離散推論と連続推論の結合タイミングが妥当なのか。EFE（Expected Free Energy）の計算が正しいのか。論文の数式とコードの対応を Claude Code と一緒に確認した——正確には、Claude Code が確認して「問題ありません」と言い、私がそれを信じた。

これは正直に書いておくべきだろう。Claude Code があれば、理論を理解していなくても「動くもの」は作れてしまう。テストが通り、数値的に安定していれば、見た目上は正しく見える。しかしその品質を判別する能力が自分にない以上、**検証されていない実装**であることに変わりはない。

GitHub で公開しているので、能動的推論に詳しい方からのフィードバックをお待ちしている。

https://github.com/shimo4228/active-inference-viz

## なぜこの記事を1週間書けなかったか

私は Claude Code で行ったことは全て記事にしている。実装した当日か翌日には書く。記事を書くことが PDCA サイクルの「Check」になり、自分の学習を助けてくれるからだ。

このプロジェクトだけ、1 週間放置した。

書けなかった理由は単純で、**自分がこのプロジェクトから何かを学んだという実感を持てなかった**からだ。いつもなら「こういう設計判断をした、その理由はこうだ」「ここでハマった、教訓はこうだ」と書ける。今回はそれがない。Claude Code が全部やった。私は隣で見ていた。何が起きたかは分かるが、何を学んだかが分からない。

1 週間経って、「学びがないこと自体に書く価値がある」と気づいた。だからこの記事を書いている。

## 技術的な学び——は、ない

正直に書く。この開発を通じて得た技術的な学びはない。

ここまでの記事に書かれている技術的な内容——VJP、Jacobian、予測符号化、精度行列、chain rule——を私は理解していない。Claude Code の説明をそのまま載せているだけで、「なるほど、そういうことか」と腑に落ちた瞬間は一度もなかった。

唯一学んだことがあるとすれば、**理解していなくてもものは作れてしまう**という事実そのものだ。テストが通り、数値が安定し、画面上でアームが動く。それを見て「できた」と思える。でも「何ができたのか」を自分の言葉で説明しろと言われたら、この記事に書いてある以上のことは何も言えない。

これが学びと呼べるのかは分からない。

## 偏愛が残る時代

この記事を書きながら、改めて考えている。

Claude Code は恐ろしいツールだ。計算論的な神経科学の論文を、素人が 2 時間でブラウザの可視化ツールにしてしまう。計算エンジンの書き換えに加え、元コードには存在しなかったインタラクティブ UI も新規構築した。テストカバレッジ 98%、型チェック完全対応。プロの研究者なら致命的な誤りを指摘するだろうか。それとも「形式的にはよくできている」と言うだろうか。自分にはどちらか判断する力がない。

でも「なぜ能動的推論なのか」は Claude Code には答えられない。毎朝のリサーチレポートに並ぶ数十のテーマの中から、なぜよりによって **これ** に手が伸びたのか。合理的な説明はない。強いて言えば、「脳が世界のモデルを持ち、予測と現実のズレを最小化する」という描像が、AI と人間の関係について何かを示唆しているように感じた——くらいのことしか言えない。

能動的推論を作り終えて実感したのは、実装力が民主化された世界では「何を作れるか」より **「なぜこれを作りたいのか」** の方がはるかに希少だということだ。非合理な執着——偏愛だけが、人間に残された固有値だ。

理論が正しく実装できているかは分からない。でも「分からないのに作りたかった」という事実だけは、間違いなく本物だ。

---

<!-- textlint-disable -->

:::message
**リポジトリ:** https://github.com/shimo4228/active-inference-viz
Streamlit でブラウザからインタラクティブに動かせます。能動的推論に詳しい方、フィードバックをいただけると嬉しいです。
:::

<!-- textlint-enable -->

## 参考文献

- Priorelli, M. et al. (2025). "[Embodied decisions as active inference](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012745)." PLOS Computational Biology.
- [元コード（PyTorch + Pymunk + Pyglet）](https://github.com/priorelli/embodied-decisions)
- [pymdp — Active Inference for Discrete State Spaces](https://github.com/infer-actively/pymdp)
- [Active Inference Institute](https://www.activeinference.institute/)

## 関連リンク

- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/active-inference-viz-dev-story.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
