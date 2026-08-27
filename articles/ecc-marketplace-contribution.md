---
title: "個人スキルを5万人に届ける最短経路が見つかった"
emoji: "🌐"
type: "tech"
topics: ["claudecode", "oss", "skill", "agentskills"]
published: true
published_at: 2026-03-04 07:32
---

2月に送った PR 8件が全部マージされた。それだけなら普通の話だ。

ただし、マージ先は **57,302 stars** の OSS で、インストールした全ユーザーに自分のスキルが自動で届く仕組みだった。気づいたときには、もう配布が始まっていた。

Claude Code には「スキル」と呼ばれる拡張機能がある。Claude の動作パターンを Markdown で定義したファイルで、「コードを書く前に必ず既存ライブラリを検索する」「テストを先に書く」といったルールを Claude に覚えさせられる。これを自分で書いてリポジトリに置いておくのが、いわば個人の Claude 設定ライブラリだ。

## ECC ── 6週間で 57K stars の異常値

ECC（Everything Claude Code）は `affaan-m/everything-claude-code` で管理されている OSS だ。Claude Code 向けスキル・コマンド・エージェントのコレクションで、2026年1月18日に公開された。作者は Anthropic Hackathon Winner。

何が嬉しいか。**コマンド2行だけ**でインストールが完了し、コミュニティが審査した数十のスキルがローカルキャッシュに一括で入る。あとはキャッシュから必要なスキルを `~/.claude/skills/` へコピーするだけで使い始められる。個別のリポジトリを探す手間がまるごと消える。

公開から6週間で 57,302 stars。1日あたり約 1,350。Zenn のトレンド記事が集める「いいね」を毎日超える勢いだった。

なぜこうなったか。Claude Code の普及速度そのものに乗ったからだ。「使えるスキルをまとめて入れたい」という需要が一点に集中し、ECC がデファクト窓口になった。プロダクトではなくキュレーションが勝つという、エコシステム初期の典型的なパターンだ。

ECC の詳細と実際の使い勝手は以下の記事にまとめてある。

- [Everything Claude Codeで初めて本格的な開発を始めた初心者の10日間](https://zenn.dev/shimo4228/articles/ecc-journey-part1)
- [Claude Code スキルが膨れ続けた 15 日間 — 3 回の棚卸しで学んだこと](https://zenn.dev/shimo4228/articles/ecc-journey-part3)

## 8件全マージ。打率10割の裏側

「自分のスキルも入っているのでは？」と確認したら、2月中に投稿した8件が全部マージされていた。

| PR # | 種別    | 名前                                                                                  | 概要                                                                         |
| ---- | ------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| #219 | skill   | cost-aware-llm-pipeline                                                               | LLM API のコスト最適化。タスク複雑度によるモデル振り分け、予算追跡、リトライ |
| #220 | skill   | swift-protocol-di-testing                                                             | Protocol ベースの DI でテスタブルな Swift コードを書くパターン               |
| #221 | skill   | swift-actor-persistence                                                               | Actor でスレッドセーフなデータ永続化層を構築するパターン                     |
| #222 | skill   | content-hash-cache-pattern                                                            | SHA-256 ハッシュで高コストなファイル処理結果をキャッシュ                     |
| #223 | skill   | regex-vs-llm-structured-text                                                          | 構造化テキスト解析に正規表現と LLM のどちらを使うかの判断基準                |
| #262 | skill   | search-first                                                                          | コードを書く前に既存ツール・ライブラリを検索するワークフロー                 |
| #263 | command | learn-eval                                                                            | セッションからパターンを抽出し、品質評価してから保存する                     |
| #265 | skill   | [skill-stocktake](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey) | スキルの品質を定量スコアで棚卸しするコマンド                                 |

打率10割。ただし、審査基準が明示されているので打てる球しか振っていない。ECC の基準は3つ。「英語のみ」「個人参照なし」「必須セクション完備」。必須セクションは Purpose / When to Use / Workflow / Output の4つだ。1 PR = 1ファイルにするとレビュー負荷が下がる。マージまで数日〜1週間だった。

## PR がマージされた瞬間、配布が始まる

ここが想定外だった。

```bash
claude plugin marketplace add affaan-m/everything-claude-code
claude plugin install everything-claude-code@everything-claude-code
```

筆者が実際に動作を確認した。`marketplace add` でリポジトリ全体がローカルにコピーされ、`plugin install` でスキルがアクティブ化される。つまり **PR がマージされた瞬間、次にインストールする全ユーザーに自分のスキルが届く**。

![ECC インストール後のスキル一覧。search-first、skill-stocktake など自分の貢献スキルが並んでいる](/images/ecc-skills-cache.png)

自分のリポジトリにスキルを置いておくだけでは、誰かが検索で偶然たどり着くのを待つしかない。ECC 経由なら発見コストがゼロになる。同じスキルでも、どこに置くかで届く桁が変わる。

仮に stars の 1% がインストールしたとして約 570 人。自分のリポジトリの月間訪問者が数人だったことを考えると、2桁どころの差ではない。

:::message
余談: 「GitHub Marketplace の ecc-tools」は GitHub Actions 向けのスキル自動生成アプリ（インストール数 123）で、まったく別物だ。検索で混同注意。

<!-- textlint-disable -->

:::

<!-- textlint-enable -->

## 「自分専用」を「誰でも使える」に変える6フェーズ

投稿手順が固まったところで `ecc-contribute` コマンドとして体系化した（`~/.claude/commands/` に置いた自作コマンドで、ローカルで使い続けている）。フロー全体は6フェーズだが、核心は中間の変換と検証だ。

1. **Pre-flight** ── Fork の同期確認
2. **候補選定** ── `/skill-stocktake` のスコア ≥ 20（100点満点）かつ ECC に類似なし
3. **ファイル変換** ── Frontmatter 変換 + 英訳 + 個人参照除去
4. **検証** ── 日本語残存・個人参照残存・必須セクションの機械チェック
5. **PR 作成** ── `gh pr create`（1 PR = 1ファイル）
6. **Post-flight** ── 進捗記録、ブランチクリーンアップ

Phase 3 の変換に一番手間がかかった。具体的に何をするのか。

**Frontmatter**: ローカルスキルには `origin: original` などの管理用メタデータがある。ECC では `description` だけが必要なので、それ以外を削る。

```yaml
# Before（ローカル）
---
name: search-first
description: Research-before-coding workflow. ...
origin: original
---
# After（ECC 提出用）
---
name: search-first
description: Research-before-coding workflow. ...
---
```

**個人参照の除去**: これが厄介だ。スキルの中に自分のプロジェクト名やファイルパスが埋まっている。`baki-trainer` とか `/Users/hanma/` とか。grep で機械的に拾えるものは良いが、「バキアプリで使った」のような文脈依存の記述は手作業で汎化する必要がある。

:::message
`baki-trainer`・`/Users/hanma/` は便宜上の置換例。実際のプロジェクト名・パスはそれぞれ異なる。

<!-- textlint-disable -->

:::

<!-- textlint-enable -->

**英訳**: 日本語で書いたスキルを英語に翻訳する。ここは Claude に任せた。ただし技術用語の一貫性（例: 「棚卸し」→ "stocktake" vs "audit" vs "inventory"）は人間が判断した。

Phase 4 では `LC_ALL=C grep -rn '[^\x00-\x7F]'` で日本語の残存をチェックする（macOS / Linux 両対応）。1文字でも残っていたら差し戻しだ。この機械チェックを入れたおかげで、2ラウンド目からはミスがゼロになった。

## スキルは共有財になる

57,302 という数字の正体は、Claude Code を使っている世界中のエンジニアだ。この全員が、同じ課題にぶつかっている。プロンプトの書き方、コードレビューの自動化、テスト駆動の徹底。解決策をスキルとして書いたなら、共有しない理由がない。

自分のリポジトリに8件のスキルを並べていたとき、見る人は月に数人だった。ECC に入った今、同じスキルが5万人の玄関に並んでいる。経路が存在すると知っていることと、知らないことでは、挑戦の前提がまるで違う。

## 関連リンク

- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/ecc-marketplace-contribution.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧

---

Claude Code のスキルは、書いた人だけが使うものにしておくには惜しい。ECC への PR は 1ファイル、英語に直して、必須セクションを揃えて送るだけだ。自分が解いた問題は、たぶん他の誰かも同じように困っている。スキルを共有して、Claude Code のエコシステムをみんなで育てていけたらいい。
