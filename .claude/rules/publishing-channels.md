<!-- origin: shimo4228 -->
# Publishing Channel Contract

このファイルは zenn-content の媒体固有 overlay。執筆手順・中心命題・因果線・craft・AI slop・
タイトル点検は global `writing-ecosystem` / `title-reviewer` が持つ。ここには path、読者との約束、
register、review panel、機械検査、platform 形式、公開 handoff だけを置く。

## Channel routing

| Channel | Path matcher | Reader promise | Register | Channel editor | Deterministic checks | Title constraints | Publish handoff |
|---|---|---|---|---|---|---|---|
| Zenn | `articles/*.md` | 検索・feedから来たengineerが、数秒で用途を理解し再現または判断できる | 日本語ですます。直接指示・具体観察・判断則を優先し、修辞疑問で結論を弱めない | `editor` | `npm run validate`; `npm run evidence -- articles/<slug>.md`（deviations 0。公開直前は`--online`も） | 原則50字以内、正確さに必要なら60字まで | `zenn-format` → `publish-article` |
| Dev.to | `articles-en/*.md` | 英語圏のengineerが同じ成果を再現または判断できる | Natural English。direct、practical、outcome-first。essayistic hedgeへ寄せない | `editor` | `devto-translator` self-check; `devto_crosspost.py post <slug> --dry-run` | local上限なし。検索/フィードは原稿の性質で選ぶ | `devto-translator` → `publish-article` |
| note | `note/*.md` | AIを仕事や生活で使う一般読者が、一つの問いを自分の問題として考えられる | 日本語ですます、発見調。評価は問いへ開けるが事実は断定する | `essay-reviewer` | 新規稿はfrontmatterなし | platform上限なし。feedで問いと対象が分かる | `substack-publishing`のnote手順 |
| Substack | `substack/*.md` | 英語圏の一般読者がJA正本と同じ問いを追える | Natural English、discovery tone。JA正本の確度を保つ | `essay-reviewer` | 新規稿はfrontmatterなし; `prose-translation`後のレビュー完了 | title/subtitleを分ける | `substack-publishing` |

path がどの行にも一致しない、または複数行に一致する場合、`writing-ecosystem` と
`quality-gate` は推測せず BLOCKED を返す。

## Shared acceptance profile

全channelで、内容GO済みの本文 + 最終タイトルに対する次の証跡を要求する。reviewer panel は
タイトル確定前の凍結本文に対して実行してよい（タイトル作業は著者の内容GO後）。

- channel editor: unresolved CRITICAL 0、canonical coverageのpending / unverified 0
- `prose-clarity-reviewer`: PASS
- `fact-checker`: INACCURATE 0、未解決 PARTIALLY 0
- `codex-review`: 完了、または実行不能理由とfallback reviewを記録
- `title-reviewer`: 著者の内容GO後（= 本文の最後の構造変更後）に実行し、findings を見て著者がタイトルを選択済み
- AI-mediated writing: Zenn (`articles/*.md`) は開示block適用外（媒体読者にとってAI利用は
  前提で、開示は情報量を持たない。毎回問い直さない）。
  Dev.to / note / Substackは適用可否を記録し、該当するならglobal canonの開示blockを収録済み
- source embedding: Zenn/Dev.toは検証済み主張をinline linkまたはReferencesへ、note/Substackは
  検証済みsourceを末尾へ編入し、channel editorのfocused recheck完了
- public-safety scan: 秘密、個人path、未sanitized screenshot / raw log 0

`quality-gate` はこのprofileと上表の機械検査を集約する。reviewerを起動したり、文章を再判定
したりしない。

## Zenn frontmatter

基本field（title / emoji / type / topics / published）は `zenn-format` が正本。公開記事では次も必須。

```yaml
published_at: 2026-04-15 07:00
```

- format: `YYYY-MM-DD HH:MM`、JST固定。slash区切り・秒付きは不可
- 省略はdraftまたは即時公開だけ。通常は予約投稿を使う
- 予約登録自体が投稿上限に計上される。公開予定日の3日以上前にpushし、Zennのデプロイ履歴を確認する
- 登録拒否後は上限解除後のpushでdeployを再triggerする

## Zenn-specific syntax

- 内部記事linkは `/articles/slug` でなく `https://zenn.dev/shimo4228/articles/slug`
- `:::message` / `:::message alert` / `:::details` の構文は `zenn-format` が正本
- 画像は `images/` に置き、個人path・credentialを含むscreenshotを置かない

## Practical-channel evidence

Zenn / Dev.toの技術記事では、意思決定のwhyとtrade-offを説明する。中心命題を進めるcode / terminal
evidenceだけを使い、snippetは実行・検証済みにする。code blockはlanguageを指定し、読者の理解に
必要ならsource pathを示す。著者環境のpath、skill名、設定は本文内で説明し、内部文脈の代わりにしない。

## Material locations

- raw AI logs: `articles/_context/{slug}-{source}-log.md`
- structured evidence dossier: `drafts/article-context_<topic>-<date>.md`

## Related links

Zenn / Dev.toの全稿は、末尾の関連link節に次の2行を含める。節が無い稿には`## 関連リンク`
（EN: `## Related links`）を末尾に新設する。Dev.to既公開分はplatformにupdate手段が無いため
遡及しない。

```
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/<slug>.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
```

2行は行き先が違うので併記する。正本リンクは**書いたもの**のコーパスへ、
著者hubは**作ったもの**——DOI付きの研究repo群へ届く。Zennの記事ページは著者hubへのリンクを
`<a href>`として持たない（`githubUsername`は`__NEXT_DATA__`のJSON値のみで、profile cardの
リンク先はZenn内`/shimo4228`）。本文末のリンクはprofile cardと違い本文DOMの一部なので、
本文抽出後も残る。

本文中のself-linkは読者の実行導線または直前の主張を支える一次資料に限定し、それ以外は末尾へ置く。

## Project terminology

| Use | Do not rewrite as |
|---|---|
| pdf2anki | PDF2Anki, pdf-to-anki, Pdf2Anki |
| Claude-Native | Claude-first, Claude based |
| CLI-First | CLI first, command-line first |
| 半自動 (Semi-automated) | semi-automatic, partially automated |
| Anki card | flashcard, card alone |
| LLM critique | AI critique, model critique |
| TDD (Test-Driven Development) | test driven, test-first |

## Cadence and scheduling

- Zenn: 週2〜3本。火〜水 7:00〜9:00 JSTを優先し、burstしない
- note: 週1〜2本。手動投稿
- JP/EN pair: Zenn 09:00 JST、Dev.toは前日22:00 JSTを既定とする
- `scripts/schedule.json` schemaは `.claude/refs/schedule-schema.md`

## Dev.to contract

- `description:`をfrontmatterに含める
- parserは`topics:` YAML listと`tags:` comma-separated stringを読む
- cover: `images/covers/{slug}.png`をGitHub raw URLで参照
- JAとENは別言語なのでZennの`canonical_url`を設定しない
- scheduling: `devto_crosspost.py schedule <slug> --at "<timestamp> Asia/Tokyo"`

## note / Substack contract

- JA正本・初出は`note/<slug>.md`。ENは`prose-translation`で`substack/<slug>-en.md`へ訳す
- 新規稿はfrontmatterなし。既存の旧mirrorは変更しない
- note/SubstackへMarkdownを直貼りせず、`substack-publishing`のHTML paste手順を使う
- 公開後は`scripts/corpus.yml`を更新し、`npm run generate:index`

## Related

- global `writing-ecosystem` — 共通執筆フローとcanon
- global `quality-gate` / `title-reviewer` — 共通受け入れ・タイトル点検
- local `zenn-format` / `publish-article` / `substack-publishing` — platform操作
- local `devto-translator` — Dev.to固有のEN稿変換。投稿は`publish-article`
