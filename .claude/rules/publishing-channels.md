<!-- origin: shimo4228 -->
# Publishing Channel Contract

このファイルは zenn-content の媒体固有 overlay。執筆手順・中心命題・因果線・craft・AI slop・
タイトル判定は global `writing-ecosystem` / `title-eval` が持つ。ここには path、読者との約束、
register、review panel、機械検査、platform 形式、公開 handoff だけを置く。

## Channel routing

| Channel | Path matcher | Reader promise | Register | Channel editor | Deterministic checks | Title constraints | Publish handoff |
|---|---|---|---|---|---|---|---|
| Zenn | `articles/*.md` | 検索・feedから来たengineerが、数秒で用途を理解し再現または判断できる | 日本語ですます。直接指示・具体観察・判断則を優先し、修辞疑問で結論を弱めない | `editor` | `npm run validate`; Zenn frontmatter; `published: true`なら`published_at`必須 | 原則50字以内、正確さに必要なら60字まで | `zenn-format` → `publish-article` |
| Dev.to | `articles-en/*.md` | 英語圏のengineerが同じ成果を再現または判断できる | Natural English。direct、practical、outcome-first。essayistic hedgeへ寄せない | `editor` | `devto-translator` self-check; `devto_crosspost.py post <slug> --dry-run` | local上限なし。検索/フィードは原稿の性質で選ぶ | `devto-translator` → `publish-article` |
| note | `note/*.md` | AIを仕事や生活で使う一般読者が、一つの問いを自分の問題として考えられる | 日本語ですます、発見調。評価は問いへ開けるが事実は断定する | `essay-reviewer` | 新規稿はfrontmatterなし | platform上限なし。feedで問いと対象が分かる | `substack-publishing`のnote手順 |
| Substack | `substack/*.md` | 英語圏の一般読者がJA正本と同じ問いを追える | Natural English、discovery tone。JA正本の確度を保つ | `essay-reviewer` | 新規稿はfrontmatterなし; `prose-translation`後のレビュー完了 | title/subtitleを分ける | `substack-publishing` |

path がどの行にも一致しない、または複数行に一致する場合、`writing-ecosystem` と
`quality-gate` は推測せず BLOCKED を返す。

## Shared acceptance profile

全channelで、同じ最終タイトル + 本文に対する次の証跡を要求する。

- channel editor: unresolved CRITICAL 0、canonical coverageのpending / unverified 0
- `prose-clarity-reviewer`: PASS
- `fact-checker`: INACCURATE 0、未解決 PARTIALLY 0
- `codex-review`: 完了、または実行不能理由とfallback reviewを記録
- `title-eval`: 本文の最後の構造変更後に実行し、著者が選択済み
- AI-mediated writing: 適用可否を記録し、該当するならglobal canonの開示blockを収録済み
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

記事末尾の関連link節で著者自身のrepository / toolを一つでも紹介する場合は、著者hub
[github.com/shimo4228](https://github.com/shimo4228)を含める。本文中のself-linkは読者の実行導線
または直前の主張を支える一次資料に限定し、それ以外は末尾へ置く。

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
- global `quality-gate` / `title-eval` — 共通受け入れ・タイトル判定
- local `zenn-format` / `publish-article` / `substack-publishing` — platform操作
- local `devto-translator` — Dev.to固有のEN稿変換。投稿は`publish-article`
