Language: [English](README.md) | 日本語

# zenn-content

Tatsuya Shimomoto（shimo4228）が、コーディングエージェントを作り、動かすエンジニアに向けて書いた日英の文章です。エージェントはどう記憶し、どう失敗し、レビューに溺れずにどう評価し、どう説明責任を持たせるか。すべて実際の開発セッションから書いており、全記事の Markdown 原稿がこのリポジトリにあります。

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

- **[Publications index](docs/PUBLICATIONS.md)** — 記事・アイデアエッセイ・論文の全件を新しい順に、日英リンク付きで載せています（このリポジトリの原稿から生成し CI で照合するので、下のプロフィールと歩調がそろいます）
- 日本語記事: [Zenn](https://zenn.dev/shimo4228) · 英語版: [Dev.to](https://dev.to/shimo4228)
- アイデアエッセイ: 日本語は note · 英語は [Substack](https://shimo4228.substack.com) — 各エッセイのリンクは索引にあります

## このリポジトリにあるもの

| ディレクトリ | 内容 |
|---|---|
| `articles/` | Zenn 向け日本語原稿（正本） |
| `articles-en/` | Dev.to 向け英語版 |
| `note/` · `substack/` | アイデアエッセイ — 日本語正本は note へ、英語版は Substack へ |
| `docs/PUBLICATIONS.md` | 上記すべてと寄託済み論文の生成索引 |
| `scripts/` | Dev.to クロスポスト・索引生成・反響メトリクスのスナップショット |
| `.claude/` | 執筆ハーネス — Claude Code で下書き・レビュー・公開を回す skill と agent |

## どうやって書いているか

記事は実セッションから、Claude Code を協働者として書いています。レビュー・ファクトチェック・翻訳・クロスポストは Claude Code が担い、書くことと決めることは著者が担います。その仕組みは `.claude/` にあり、それ自体が記事の題材でもあります:

- [`zenn-practical-writing`](.claude/skills/zenn-practical-writing/SKILL.md) — 全記事の既定の声（実用軸: 数秒で何かわかり、そのまま手を動かせる）
- [`writing-team`](.claude/skills/writing-team/SKILL.md) — レビューループの指揮（editor · fact-checker · clarity reviewer · article judge）
- [`theme-eval`](.claude/skills/theme-eval/SKILL.md) — 執筆前と完成稿の 2 時点でテーマを判定（弱い問いは記事の上限を決めるため）
- 規約とレビュー手順: [CLAUDE.md](CLAUDE.md) · 公開パイプライン: [docs/CODEMAPS/scripts.md](docs/CODEMAPS/scripts.md)

```bash
npm install && npm run preview     # Zenn のローカルプレビュー
npm run validate                   # Zenn frontmatter の検証
npm run generate:index             # docs/PUBLICATIONS.md と上の読書経路を再生成
```

## 出自と再利用

記事・翻訳・ツールを含む全コンテンツは [CC0 1.0](LICENSE)（パブリックドメイン献呈）です。

- 著者: [ORCID 0009-0002-6168-4162](https://orcid.org/0009-0002-6168-4162) · [GitHub ハブ](https://github.com/shimo4228/shimo4228) — 記事の土台になっている著者のほかの研究プロジェクトへのリンクです（それぞれ DOI 付き）
- 引用: [CITATION.cff](CITATION.cff) — DOI の代わりに、内容から算出される識別子（Software Heritage のスナップショット）で「何をいつ公開したか」を登録機関なしに記録しています
- 記事から育った論文は [Publications index](docs/PUBLICATIONS.md#papers) に載せています

## コーディングエージェント向け

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/shimo4228/zenn-content)

[llms.txt](llms.txt)（ナビゲータ）と [llms-full.txt](llms-full.txt)（自己完結の Q&A）から読んでください。正本はここにある Markdown で、各プラットフォームはその写しです。
