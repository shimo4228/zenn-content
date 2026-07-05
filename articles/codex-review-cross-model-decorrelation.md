---
title: "Claude Codeから簡単にCodexレビューさせるスキルを作った"
emoji: "🔀"
type: "tech"
topics: ["claudecode", "codex", "codereview", "skills", "harness"]
published: true
published_at: 2026-07-07 07:00
---

> この記事でわかること: Claude Code に OpenAI Codex CLI を使ったクロスモデルレビューを一点だけ足す方法と、それが「量」ではなく「別クラスの盲点を見る」ことで効く理由

## 前提

- [Codex CLI](https://github.com/openai/codex) がインストール・認証済み（`codex login` または `codex doctor` で確認）
- Claude Code から `git` リポジトリ内で操作していること

## 使い方 — 読み取り専用のセカンドオピニオンを一発で

`codex-review` は `codex review`（OpenAI Codex CLI）を薄くラップした読み取り専用のスキルです。Claude Code とは別のモデル系統に、今の diff を見せてレビューさせます。

`/codex-review` は Zenn や Claude Code に最初から入っているコマンドではなく、自分の Claude Code ハーネスに置いた小さなラッパースクリプトです。

スキル本体は [shimo4228/codex-review](https://github.com/shimo4228/codex-review) として公開しているので、リポジトリ内の `skills/codex-review/` を `~/.claude/skills/codex-review/` にコピーすれば同じ形を再現できます。

やっているのは「許可したフラグだけを `codex review` にそのまま渡し、それ以外は拒否する」というシェルスクリプト1本だけです。

このスクリプト自体は Claude Code 専用ではありません。中身を見ると "Claude" という文字列はコメントにしか出てこず、実行ロジックは `bash` + `git` + `codex` CLI だけで完結しています。

ターミナルから直接叩いても、他のエージェント CLI から呼んでも、Claude Code を介さない素の pre-commit フックとして使っても、そのまま動きます。「Claude Code のスキル」という体裁は、置き場所と呼び出し方の話でしかありません。

```bash
# 現在のブランチ vs 自動検出したベースブランチ（PRスタイル）
/codex-review

# ステージ + 未ステージ + 未追跡ファイル（コミット前の確認向け）
/codex-review --uncommitted

# 特定のブランチ・コミットに対して
/codex-review --base main
/codex-review --commit <sha>

# プロンプト駆動（スコープ指定なしで作業ツリー全体をレビュー）
/codex-review "認証まわりの変更だけ見て"
```

読み取り専用であることはコード側で保証しています。内部では `codex review`（コードを書き換えない）だけを呼び、許可されたフラグ以外はすべて拒否します。将来 Codex CLI に書き込み可能なフラグが追加されても、許可リストにない限り実行されません。

Codex の出力はそのまま親の会話に貼り付けず、検証してから要約する運用にしています。

```text
Agent: codex-review
Verdict: <CRITICAL | HIGH | MEDIUM | LOW | CLEAN>
Findings (top 3): <確認できたものだけ>
Files touched: <path:line>
Next action: <continue | stop | re-plan>
```

Codex の指摘は「正しいとは限らない外部入力」として扱い、コードを読んで再現できたものだけを残します。verdict を決めるのは自分（Claude 側）です。

## ハーネスに「自動で走る検証」として組み込む

`/codex-review` を都度手動で呼ぶだけでも便利ですが、本当に効くのは「呼び忘れない」仕組みにしたときです。プロジェクトルール（`CLAUDE.md` や `.claude/rules/*.md`）に条件を書いておくと、実装がひと段落した時点でこちらから頼まなくても Claude が自分でそれに従って動くようになります。

ただし、これはフックのような決定論的な強制ではありません。ルールはあくまで Claude の判断を条件づける記述で、実行するかどうかは最終的に Claude の判断に委ねられています（100% 保証したいなら PostToolUse hook で強制する必要があります）。

それでも「非自明な diff を書いたら」という条件をルール側に明文化しておくだけで、「都度頼む」から「条件が揃えば自分から動く」に変わります。実際に使っているルールの全文（Chain Matrix・早期停止条件つき）は [claude-harness の `planning.md`](https://github.com/shimo4228/claude-harness/blob/main/rules/common/planning.md) で公開しています。

```markdown
<!-- 例: CLAUDE.md や .claude/rules/*.md に書く -->
## Review ステップ（実装直後・コミット前）

feat/fix で非自明な diff を実装したら、コミット前に以下を並列で起動する:
- 通常のコードレビュー（自分のモデルの subagent）
- codex-review（cross-model, read-only）

いずれかが CRITICAL を返したら、コミットを止めてユーザーに報告する。
```

ポイントは2つです。

1. **トリガーを「ユーザーが頼むこと」ではなく「非自明な diff を書いたこと」にする** — こうすると呼び忘れが構造的に起きなくなります
2. **CRITICAL 検出時は早期停止する** — 別モデルが重大な指摘をしたら、その場でコミットを止めて人間の判断を仰ぐ、というゲートをルール側に持たせておきます

この形にしておけば、発見は「たまたま気づいた」のではなく、毎回同じ位置で拾われます。実は、この記事自体がその実演になりました。

`codex-review` はコードの diff だけでなく、プロンプト駆動モードなら文章（prose）もレビューできます。このリポジトリの公開前チェックリストには「記事は editor / fact-checker / codex-review を並列でレビューする」と書いてあり、この記事もこちらから明示的に頼むことなく codex-review にかかりました。

そして実際に指摘を受けました。直前の段落の「ルールに書けば自動実行される」という言い方自体が言い過ぎだ、という指摘です（今の書き方はその指摘を反映した後のものです）。

コードの盲点だけでなく、文章の言い過ぎも、別モデルは律儀に拾ってきます。

## 実際に何を見つけたか — 別モデルは別の盲点を見る

codex-review の価値を「Claude だけでは見つからないバグをよく見つける」と表現したくなりますが、これは頻度の話にすると検証しづらい主張になります。実際に起きたことをそのまま書くと、こうなります。

筆者の別の研究リポジトリ [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) で、監視用の計器モジュールを1本追加したときのレビューです（[ADR-0071](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0071-read-only-pattern-composition-instruments.md)、[該当コミット](https://github.com/shimo4228/contemplative-agent/commit/224fdd97b740df7bf1b2a18bc77f6e8cc4980ec0)）。この計器は「パイプラインの挙動には一切手を出さず、埋め込みベクトルの分布や集計だけを読み取って表示する」という観測専用の設計です。同じ diff に対して、別モデル系統の `codex-review` と、Claude 側の通常レビュー（`python-reviewer`）を並列で走らせました。

| レビュアー | 見つけたもの | 種類 |
|---|---|---|
| codex-review | 埋め込みベクトルの次元数が混在すると、集計処理がクラッシュする経路 | 数値・データ形状の不整合 |
| codex-review | 集計対象のフィルタ条件が、本来見るべき処理と1箇所だけズレていた | 集計ロジックの意味論のズレ |
| codex-review | dry-run の集計が、後段の重複排除で捨てられるはずの候補まで数えていた | 集計の意味論のズレ（対象範囲） |
| python-reviewer | 想定外の入力（数値でない埋め込み等）で例外が伝播し、監視のはずのコードが本体の処理まで止めてしまう経路 | 例外設計・堅牢性の契約 |

件数の3:1はこの1回の実行結果であり、主張の核は件数でなく発見の抽象度の違いです（詳しくは表の直後で説明します）。

4件とも実際にコードを読んで再現を確認し、修正して回帰テストを足しました（[コミットメッセージ](https://github.com/shimo4228/contemplative-agent/commit/224fdd97b740df7bf1b2a18bc77f6e8cc4980ec0)に一次記録あり）。テストはすべて green のまま、この4つのバグは存在していました。つまり「動く」ことと「正しい」ことは別のチェック軸で、レビューはその別軸を担っていたということです。

面白いのは、1件目（codex-review: 次元不一致でのクラッシュ）と4件目（python-reviewer: 例外伝播でホスト処理停止）です。字面だけ見ると、どちらも同じ「壊れた埋め込み行」問題に見えます。

実際は、指摘の抽象度が違います。

- **codex-review** — 「次元数が揃っていない」という特定の壊れ方で、集計関数がクラッシュする経路
- **python-reviewer** — それを含むもっと広い契約。「観測用の計器は、どんな異常な入力が来てもホスト側の処理を絶対に止めてはいけない」という設計原則そのものの欠落

同じ「壊れた行」という現象の周りで、2つのレビュアーが別の抽象度・別の変種を指摘した——というのが今回起きたことです。

同じモデル系統でもう一度レビューすればどちらか片方しか出てこない、と断言はできません。少なくとも今回の1回の実行では、重複がありませんでした。

## 落とし穴 / Tips

:::details ハマったら

- **スコープとプロンプトは同時指定できません**（`--uncommitted` 等と自由記述プロンプトは排他）。両方渡すと exit code 64 で拒否されます
- **スコープ引数なしで実行し、かつ HEAD が既にベースブランチ上にある場合**（例: 何も指定せず `main` で実行した場合）、diff が空になるため自動的に `--uncommitted` にフォールバックします。`--base main` のように明示的にスコープを指定した場合は、この自動フォールバックは働きません
- **CLI 未インストールの場合**はラッパー自身が事前チェックして早期に失敗を返します。**未認証の場合**はラッパーの守備範囲外で、`codex review` 自体がエラーを返します（`codex login` / `codex doctor` で確認）。どちらの場合も、Claude 側のレビューだけで続行してください
:::

## まとめ

`codex-review` 自体は薄いラッパーですが、効いているのは「別モデルを1点だけ混ぜる」という設計と、「非自明な diff を書いたらレビュー対象になる、とルールに明文化しておく」という運用の組み合わせです。自分のプロジェクトルールに数行足すだけで、今日から同じ形を再現できます。

## 関連リンク

- [codex-review スキル本体](https://github.com/shimo4228/codex-review) — `skills/codex-review/` を `~/.claude/skills/codex-review/` にコピーして導入できます
- [claude-harness の `planning.md`](https://github.com/shimo4228/claude-harness/blob/main/rules/common/planning.md) — Review ステップ・Chain Matrix・早期停止条件の全文
- [Contemplative Agent](https://github.com/shimo4228/contemplative-agent) / [ADR-0071](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0071-read-only-pattern-composition-instruments.md) / [該当コミット](https://github.com/shimo4228/contemplative-agent/commit/224fdd97b740df7bf1b2a18bc77f6e8cc4980ec0) — 今回の実例
- [Codex CLI（本家）](https://github.com/openai/codex)
- [shimo4228 の GitHub](https://github.com/shimo4228) — 他の公開リポジトリ一覧
