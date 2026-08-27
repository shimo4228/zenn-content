---
name: publish-article
description: quality-gate PASS済みの対象稿1本について、Zennのfrontmatter・preview・予約またはDev.toのdry-run・予約、公開索引、push確認を扱うproject-local公開skill。Use when — 対象となるZenn稿またはEN稿自身のglobal quality-gate PASSと著者GOの後。NOT for — 翻訳生成、prose review、security/quality判定、note/Substack投稿。
user-invocable: true
origin: shimo4228
---

# Publish Article Skill

このskillは公開操作だけを持つ。文章品質とpublic-safetyはglobal `quality-gate`、Zenn形式は
`zenn-format`、channel値は `.claude/rules/publishing-channels.md` が正本。

## Usage

```text
/publish-article articles/<slug>.md
/publish-article articles-en/<slug>.md
```

引数なしなら `published: false` のZenn原稿を列挙する。

## Preconditions

- 引数で指定した対象稿自身のglobal `quality-gate`がPASS
- 著者が最終タイトルと本文を通読済み
- 著者が公開GOを出している

不足していれば公開操作を始めず、欠けた証跡を返す。

最初に対象pathをchannel contractの1行へ解決する。JP稿のPASSをEN稿へ流用しない。

## Zenn / Dev.to publish flow

### 1. Validate target

```bash
npm run evidence -- articles/<slug>.md --online   # 構造・書式・実在・一致 + 外部URLの生死
npm run validate
```

`deviations`が1件でもあれば公開操作を始めない。`grandfathered`は検査導入前の既公開分なので
blockしない。目視で数え直さず、scriptの出力をそのまま扱う。

Zenn稿のtitle、emoji、type、topics、slug、`published_at`は`zenn-format`とchannel contractに従う。
EN稿は`devto-translator` self-check済みであることを確認する。

### 2. Preview or dry-run

```bash
npm run preview
```

Zenn稿は`http://localhost:8000`でコードblock、画像、message/details、内部linkを確認する。

EN稿は実POSTせずdry-runする。

```bash
cd scripts && uv run python devto_crosspost.py post <slug> --dry-run
```

### 3. Schedule the resolved target

通常はfrontmatterを次の形にする。

```yaml
published: true
published_at: 2026-04-15 09:00
```

format、rate-limit、cadenceは`.claude/rules/publishing-channels.md`が正本。これはZenn channelだけに行う。

Dev.to channelではdry-runを著者へ提示して日時を確認してから予約する。

```bash
cd scripts && uv run python devto_crosspost.py schedule <slug> --at "2026-07-07 22:00 Asia/Tokyo"
```

即時投稿は著者が明示した場合だけ`post <slug>`を実行する。

### 4. Register production state

`.claude/refs/schedule-schema.md`に従って`scripts/schedule.json`へentryを追加する。

### 5. Cross-channel boundary

Zenn稿の公開実行からEN稿を生成・予約しない。crosspostする場合はこのrunを終了し、
`devto-translator`で`articles-en/<slug>.md`を生成する。そのEN稿でtitle選択・review panel・
`quality-gate`・著者通読GOを完了してから、別runとして
`/publish-article articles-en/<slug>.md`を実行する。

Dev.to schedule成功時、実URLは`schedule.json`へ自動書き戻しされ、one-shot jobは自己削除される。

### 6. Regenerate the publication index

```bash
npm run generate:index
npm run check:index
```

note/Substack essayは`scripts/corpus.yml`へentryを追加してから生成する。READMEのreading pathは
`scripts/reading_paths.yml`の著者判断であり、新記事を自動追加しない。

### 7. Commit and push boundary

commit / pushはユーザーの明示依頼がある場合だけ行う。記事・schedule・索引をcommitした場合は、
未pushだとZenn予約とDev.to jobが反映されないため、必ずpush状態を確認してユーザーへ伝える。

## Failure behavior

| Failure | Action |
|---|---|
| quality-gate receipt missing | 公開を開始せずgateへ戻す |
| frontmatter/index failure | fieldを修正し`npm run validate`から再実行 |
| preview issue | 原稿またはassetを修正しpreviewを再確認 |
| Dev.to API failure | dry-runとAPI responseを確認。Zenn公開とは分離して記録 |
| Zenn registration rejected | rate-limit解除後のpushでdeployを再trigger |

## Related

- global `writing-ecosystem` / `quality-gate`
- local `zenn-format`
- `.claude/rules/publishing-channels.md`
- `.claude/refs/schedule-schema.md`
