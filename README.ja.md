Language: [English](README.md) | 日本語

# zenn-content

Tatsuya Shimomoto（shimo4228）が、コーディングエージェントを作り、動かすエンジニアに向けて書いた日英の文章です。エージェントがどう記憶し、どう失敗し、レビューに溺れずにどう評価し、どう説明責任を持たせるかを書いています。記事は、一人の著者の実際の開発セッションで起きたことを報告するもので、全記事の Markdown 原稿がこのリポジトリにあります。

1 本の記事から来られた方は、下の経路から次の 1 本を選ぶか、[完全な索引](docs/PUBLICATIONS.md)をご覧ください。

## 次に読む経路

<!-- reading-paths:start -->

### コーディングエージェントに記憶を持たせる

エージェントの知識をどこに置くか、RAG より構造化メモリが勝つのはいつかを扱います。

- [コーディングエージェントの知識をどこに置き、どう守らせるか](https://zenn.dev/shimo4228/articles/coding-agent-memory-architecture)
- [Claude Code のメモリーにベクトルは 1 本もない — memory RAG の前に ADR を](https://zenn.dev/shimo4228/articles/rag-to-adr-agent-memory)

### レビューを増殖させずにエージェントを評価する

LLM-as-judge の設計、別モデルによるレビュー、そして「レビューが仕事を増やし続ける」失敗パターンを取り上げます。

- [LLM-as-judge はスコアを集計しない — チェックは証拠、判定は総合判断](https://zenn.dev/shimo4228/articles/llm-judge-checks-not-scores)
- [Claude Codeから簡単にCodexレビューさせるスキルを作った](https://zenn.dev/shimo4228/articles/codex-review-cross-model-decorrelation)
- [AIレビューの指摘をタスクへ送り続けたら、修理が終わらなくなった——4,541行を捨てるまで](https://zenn.dev/shimo4228/articles/ai-review-task-loop)

### 自律的な振る舞いを後から辿れるようにする

自律的に動くエージェントの説明責任をどう設計するか、実践的な可観測性とあわせて紹介します。

- [登れる壁に看板を立てても意味がない — AIエージェントに必要なのはガードレールではなくアカウンタビリティだ](https://zenn.dev/shimo4228/articles/ai-agent-accountability-wall)
- [AIエージェントの「なぜその判断？」に答えるオブザーバビリティ設計3パターン](https://zenn.dev/shimo4228/articles/agent-observability-patterns)

<!-- reading-paths:end -->

## 全部を見る

- **[完全な索引](docs/PUBLICATIONS.md)** — 記事・アイデアエッセイ・論文の全件を新しい順に、日英リンク付きで載せています（このリポジトリの原稿から生成し、原稿とずれると CI が失敗します）
- 日本語記事: [Zenn](https://zenn.dev/shimo4228)（日本の開発者向けブログプラットフォーム） · 英語版: [Dev.to](https://dev.to/shimo4228)
- アイデアエッセイ（一般の読者に 1 つの問いを開くエッセイ）: 日本語は note · 英語は [Substack](https://shimo4228.substack.com) — 各エッセイのリンクは索引にあります

## このリポジトリにあるもの

| ディレクトリ | 内容 |
|---|---|
| `articles/` | Zenn 向けの日本語原稿（Zenn に載る記事の元になる原稿） |
| `articles-en/` | Dev.to 向け英語版 |
| `note/` · `substack/` | アイデアエッセイ: note に出す日本語の元原稿と、Substack に出す英語版です。`note/` には Zenn 記事を note へそのまま転載した写しもあり、その元原稿は `articles/` にあります |
| `docs/PUBLICATIONS.md` | 上記すべてと寄託済み論文の生成索引 |
| `scripts/` | Dev.to クロスポスト・索引生成・反響メトリクス（記事ごとの閲覧数といいね数、`scripts/metrics/` に記録） |
| `.claude/` | 執筆ハーネス — このリポジトリで Claude Code が読み込み、下書き・レビュー・公開を回すスキル・エージェント・ルール |

## どうやって書いているか

記事は実セッションから、Claude Code とともに書いています。本文の下書き・レビュー（うち 1 つは別モデルである OpenAI の Codex による初見の読み）・ファクトチェック・翻訳・クロスポストは Claude Code が担い、中心命題と証拠を決め、公開を判断するのは著者です。公開済みの Zenn 記事はすべて、本文を Claude が書いたことを末尾の注記に書いています。Zenn はこのリポジトリと同期するので、過去の記事にも足しました。Dev.to の英語版を含むほかの媒体では、2026 年 10 月以降に公開した稿にだけ足しています。手順は、このリポジトリの `writing-ecosystem` スキル（`.claude/skills/` にあり、単体のスキルとしても公開しています）にあります。

- [媒体ごとの約束（publishing-channels.md）](.claude/rules/publishing-channels.md) — Zenn / Dev.to / note / Substack の読者・形式・レビュー・公開への受け渡し
- [このリポジトリのスキル](.claude/skills/) と [エージェント](.claude/agents/) — 執筆の流れ、その受け入れゲートとレビュー担当、Zenn 形式、媒体への公開、公開後の計測
- 規約とレビュー手順: [CLAUDE.md](CLAUDE.md)（英語） · 公開パイプライン: [docs/CODEMAPS/scripts.md](docs/CODEMAPS/scripts.md)（英語）

```bash
npm install && npm run preview     # Zenn のローカルプレビュー
npm run validate                   # Zenn frontmatter の検証
npm run generate:index             # docs/PUBLICATIONS.md と上の読書経路を再生成
npm run check:index                # 索引か読書経路が古ければ失敗する
```

プレビューには Node.js が要ります。`generate:index` と `check:index` は `uv` で Python スクリプトを実行します。

## 著者のほかの仕事

- **[claude-skill-writing-ecosystem](https://github.com/shimo4228/claude-skill-writing-ecosystem)**（英語）: 執筆の流れを統括するスキルと 6 つのレビュー用エージェントで、記事・エッセイ向けです。中心命題 1 つ、レビュー担当の一巡、著者の GO を軸にしています。ここで使っている執筆の流れを、インストールできる形にした写しです。
- **[harness-scope](https://github.com/shimo4228/harness-scope)**（英語）: `.claude/harness-scope.json` を読む Claude Code の Mod（プラグインに入れる hooks module）です。グローバルのスキル・エージェント・ルール・ツールを、名前付きのプロファイルでリポジトリごとに出し入れします。
- **[Authorship Strategy](https://github.com/shimo4228/authorship-strategy)**: 読者が LLM を介してアイデアに出会うとき、著者が見つけられ名前とともに伝わるにはどうするかを扱う著者のプロジェクトです。その答えとして、作品を公開し、広まっても出典が付いていくようにしています（DOI [10.5281/zenodo.20263316](https://doi.org/10.5281/zenodo.20263316)）。
- **[shimo4228](https://github.com/shimo4228/shimo4228)**（英語）: 著者のハブです。5 つの長期プロジェクト（それぞれ DOI 付き）と、著者の Claude Code 向けの道具をまとめています。

## 出自と再利用

記事・翻訳・ツールを含む全コンテンツは [CC0 1.0](LICENSE)（パブリックドメイン献呈）です。

- 著者: [ORCID 0009-0002-6168-4162](https://orcid.org/0009-0002-6168-4162) · [GitHub ハブ](https://github.com/shimo4228/shimo4228)（英語）
- 引用: [CITATION.cff](CITATION.cff) — DOI の代わりに、内容から算出される恒久的なアーカイブ識別子（Software Heritage のスナップショット `swh:1:snp:bcdc4895c9f1a2c16cd7a12fa2ad05ceb4a45dd5`）で「何をいつ公開したか」を登録機関なしに記録しています
- 記事から育った論文（Zenodo に寄託し、SSRN にミラー）は[完全な索引](docs/PUBLICATIONS.md#papers)に載せています

## コーディングエージェント向け

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/shimo4228/zenn-content)

[llms.txt](llms.txt)（ナビゲータ）と [llms-full.txt](llms-full.txt)（自己完結の Q&A）から読んでください。記事の正本はここにある Markdown で、各プラットフォームはその写しです。

<details>
<summary>ツールと AI アシスタント向けの資料</summary>

zenn-content は、Tatsuya Shimomoto（shimo4228）がコーディングエージェントを作り、動かすエンジニアに向けて書いた日英の記事とエッセイ（Zenn・Dev.to・note・Substack に公開）の Markdown 原稿を置くリポジトリです。原稿を書き、レビューし、公開し、索引にする執筆ハーネスとスクリプトも同じ場所にあります。

このリポジトリがあるのは、文章が特定の公開プラットフォームの存続に依存しないようにするためです。記事の正本はここにある Markdown で、各プラットフォームはその写しです。`note/` と `substack/` の一部のアイデアエッセイは、正本を著者の [attention-not-self](https://github.com/shimo4228/attention-not-self) リポジトリに置くミラーです。`note/` のほかのファイルには Zenn 記事を note へそのまま転載した写しもあり、その正本は `articles/` にあります。リポジトリは CC0 で公開しています。

基本的な事実: ライセンスは記事・翻訳・ツールを含めて CC0 1.0 です。構成は Markdown の記事（`articles/` が Zenn 向けの日本語原稿、`articles-en/` が Dev.to 向けの英語版、`note/` が日本語のエッセイと note への転載、`substack/` が英語のエッセイ）、uv で動かす Python スクリプト、プレビューと frontmatter の検証に使う Node.js の zenn-cli です。状態は継続中で、人の手で管理しています。記事は公開のたびに加わり、全件の索引 `docs/PUBLICATIONS.md` は生成物で、手では編集しません。引用には DOI を使わず、[CITATION.cff](CITATION.cff) が Software Heritage のスナップショット識別子を指します。読むこととプレビューに有料の鍵は要りません。`scripts/` の Dev.to クロスポストには著者の Dev.to API キーが要り、反響メトリクスのスナップショットも Dev.to の行に同じキーを使います。`.claude/` には現役の執筆ハーネスがあります。`writing-ecosystem` スキル、レビュー用エージェント（editor・essay-reviewer・prose-clarity-reviewer・theme-reviewer・title-reviewer・fact-checker）、quality-gate と公開用のスキル、`.claude/rules/publishing-channels.md` の媒体ごとの約束です。

具体例: `npm run generate:index` は、`articles/*.md` の frontmatter、`scripts/schedule.json`、`scripts/corpus.yml`、`scripts/reading_paths.yml` から `docs/PUBLICATIONS.md` と README の読書経路（`reading-paths` マーカーの間）を作り直します。`npm run check:index` はどちらかが古いとエラーで終わるので、索引と読書経路のブロックを手で編集することはありません。「著者のほかの仕事」のリンクは人の手で選んでいます。

参照先には、[docs/PUBLICATIONS.md](docs/PUBLICATIONS.md)（全記事・エッセイ・論文の日英リンク）、[llms.txt](llms.txt)、[llms-full.txt](llms-full.txt)、[CLAUDE.md](CLAUDE.md)（規約、英語）、[.claude/rules/publishing-channels.md](.claude/rules/publishing-channels.md)（媒体ごとの約束）、[docs/CODEMAPS/scripts.md](docs/CODEMAPS/scripts.md)（公開パイプライン、英語）、[CITATION.cff](CITATION.cff)、著者のハブ https://github.com/shimo4228/shimo4228 （記事の土台になっている研究プロジェクトの一覧）があります。

</details>
