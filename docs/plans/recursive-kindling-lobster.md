# Zenn レビューの lint 化（review-to-lint 適用）

## Context

zenn-content の Zenn チャンネルには、reviewer（`editor` / `prose-clarity-reviewer` / `fact-checker`）と
受け入れゲート（`quality-gate`）が見るチェック項目が 20 以上ある。そのうち構造・書式・実在・一致は
LLM が数えるより script が数える方が正確で安い。この作業はその境界を引き、機械側を evidence script
へ降ろし、reviewer の注意を意味的チェックへ戻す。

直接の契機は 2026-08-27 の正本リンク追加で、そこで 2 つの実態が見えた。

- **今日の変更が既存規約と衝突した**。`## Related links` の著者 hub 規約は「関連リンク節で自 repo を
  紹介するなら hub を含める」。正本リンク（zenn-content = 著者の repo）で全 68 本に発火し、46 本が
  規約違反状態になった。人間もレビューも気づかなかった — 存在の一致は script の仕事だという実例。
- **`npm run validate` はほぼ何も検査していない**。実体は `zenn list:articles`（一覧表示）。
  zenn-cli 0.4.5 に validation ロジックは同梱されているが、到達口は `zenn preview` のブラウザ UI
  だけで CLI サブコマンドが無い。

## 実測した現状（記事 70 本 / published 68 本 全件）

免除境界を決めるための全数計測。**違反 0 件**の項目（= 初日から緑）:

frontmatter 必須 field / `published_at` の存在と書式 / `topics` 1〜5 件・lowercase / `type` enum /
相対内部リンク `](/articles/` / `:::` ブロックの開閉均衡 / 画像ファイルの実在 / 用語表の
Do-not-rewrite 語 / 正本リンクの存在と slug 一致（今朝の commit 後）

**違反あり**の項目:

| 項目 | 件数 | 扱い |
|---|---|---|
| 著者 hub 併記なし | 46 | 今回追加して 0 にする（著者決定 2026-08-27） |
| 本文が H1 で始まる | 5 | 既公開・据え置き（evidence には出す） |
| code fence の language 無し | 6（2 記事） | 既公開・据え置き |
| title 60 字超 | 3（66/62/64 字） | 既公開・据え置き。検索流入と既存被リンクに影響するため触らない |

**偽陽性として除外が必要な項目**: 個人 path。素朴な `/Users/` 検出は 3 件ヒットするが全部
`/Users/you/` `/Users/hanma/` の説明用プレースホルダで**偽陽性 100%**。実ユーザー名の混入は 0 件。
→ 検出は実ユーザー名ベースに限定する。

見出し検出は fenced code block を除外しないと bash コメント `# foo` を H1 と誤検出する（実測 2 件）。

## 3 分類の棚卸し（review-to-lint §1）

対象: `.claude/rules/publishing-channels.md`（channel 表・Shared acceptance profile・Zenn frontmatter・
Zenn-specific syntax・Related links・Project terminology）、`.claude/skills/zenn-format/SKILL.md`、
global `editor` agent の 7 criteria。

**deterministic → script**（存在・書式・実在・一致）

1. frontmatter 必須 field の存在（title / emoji / type / topics / published）
2. `published: true` → `published_at` 必須 + `YYYY-MM-DD HH:MM` 書式（slash・秒付きは不可）
3. `topics` 1〜5 件・lowercase / `emoji` 単一 / `type` ∈ {tech, idea}
4. title 文字数（50 字 = info、60 字 = deviation の 2 段）
5. Zenn 内部記事リンクが相対 `](/articles/` になっていないか
6. code fence の language 指定と fence の均衡（code block 除外パーサを共用）
7. `:::message` / `:::details` の開閉均衡
8. 本文の最初の見出しが H2 か
9. 画像参照 `/images/...` の実ファイル存在
10. 個人 path・credential（実ユーザー名ベース。プレースホルダは免除）
11. 関連リンク節の存在 + 正本リンク行の存在・slug 一致
12. 関連リンク節の著者 hub 行の存在
13. Project terminology の Do-not-rewrite 語の混入
14. `--online`: 本文中の外部 URL の生死

**hybrid → script が数え reviewer が解釈**

- 表記ゆれの分布（用語表に無い変種の共存。実例: `LLMエージェント`/`AIエージェント` を統一した
  `8d06622`、`記憶`/`メモリー` の `a150b71`）
- 文体（ですます / だ・である）の混在カウント
- self-link の本数と位置（本文中 vs 末尾）— Related links 規約の「本文中の self-link は実行導線か
  一次資料に限定」の材料
- 段落密度・節あたり文数

**semantic → reviewer に残す**

中心命題が一つか / 因果線 / 証拠が網羅でなく役割で選ばれているか / AI slop / 技術的正確性と
trade-off の誠実さ / 読者問題ファースト / 第一画面 / タイトルの軸一致（`title-reviewer`）

## search-first 照合（review-to-lint §2）

- **`zenn-validator`**（公式 `zenn-dev/zenn-editor`）— 単独 package の最終公開が 2023-04-12。
  ロジックは zenn-cli 0.4.5 に同梱されているが CLI 到達口が無い。カバー範囲は上記 1〜3 と 9 の
  4 項目で、いずれも本 corpus では**実測 0 件**。載せ替えコストに見合わない。
- **textlint / markdownlint** — 2026-07-05 の `c0e98f0` で撤去済み（「Remove prose/markdown lint」）。
  prose/style 層の判断で、これは覆さない。
- **harness 内の既存 evidence script** — `readme_evidence.py` / `adr_lint.py` は対象 corpus が違う。
  ただし出力形（JSON・verdict 無し・exit 0）と uv sub-project の作りは踏襲する。
- **`lint:links` の位置づけ** — 同じ `c0e98f0` で撤去されたが、これは textlint プラグイン実装
  だったための巻き添え。実害を捕まえた実績が 2 件ある（`56bf025` broken external links、
  `62c3110` private repo で読者に 404）。**offline 既定 + `--online` flag に隔離して復活させる**
  （RFC-0005 row 2 で方針として固定済みの形と同じ）。

## 実装

### 1. evidence script

`scripts/zenn_evidence.py` + `scripts/tests/test_zenn_evidence.py`。既存の uv sub-project
（`scripts/pyproject.toml`、pytest、coverage 床 80%、`test_generate_article_index.py` と同居）を
再利用する。

- **evidence モード既定**: JSON 出力・判定しない・exit 0。「evidence, not a verdict」。
  blocking が要る場合だけ `--gate` を足す（今回は足さない）
- **免除境界を実装に埋める**: 個人 path はプレースホルダ除外、既公開記事の grandfathered 項目は
  `grandfathered: true` を立てて deviation と分離。検出パターンには実測根拠
  （どの記事の何件か）をコメントで残す
- `--online` は外部 URL の HTTP 確認のみを追加。既定では一切ネットを触らない
- 置き場は review-to-lint §3 の既定（`skills/<owner>/scripts/`）から外す。検査対象がこの repo の
  channel contract で cross-repo 性が無く、global `writing-ecosystem` は RFC-0005 row 3 で
  「設計安定後」に保留されているため。ADR に理由を残す

**review-to-lint §3 の手順どおり、既存 corpus 70 本全件に当ててから免除境界を確定する**
（上の実測は候補検査の下見であって、実装後にもう一度全数で確認する）。

### 2. reviewer 薄化（review-to-lint §4）

`editor` は**global agent で他 project と共有**しているので、Zenn 固有の Step 0 を書き込まない。
配線先は project 側に置く。

- `.claude/rules/publishing-channels.md` の channel 表 Zenn 行「Deterministic checks」列へ
  script の実行コマンドを追加 → `quality-gate` が Procedure 3 で自動的に拾う
- `.claude/skills/zenn-format/SKILL.md` の Validation and handoff 節に Step 0 を配線:
  「script を実行 → JSON の逸脱を findings に転記 → 目視で数え直さない」
- `.claude/skills/publish-article/SKILL.md` の公開前手順にも同じ実行座標を置く
- **commit hook / verify.sh へは配線しない**（review-to-lint §5。記事を触らない commit にも
  課税する）。過去に husky + lint-staged で常時配線して撤去した経緯とも整合する

### 3. 規約の確定

`.claude/rules/publishing-channels.md` の Related links 節:

- 著者 hub の併記を全 Zenn / Dev.to 記事の要件として明記（著者決定 2026-08-27。理由: 正本リンクは
  「書いたもの」のコーパス、hub は「作ったもの」の DOI 付き repo 群で行き先が違う）
- 記事ページのプロフィールカードは GitHub リンクを `<a href>` として持たない
  （`githubUsername` は `__NEXT_DATA__` の JSON 値のみ）ことを根拠として 1 行残す

### 4. hub 行の遡及（46 本、別 commit）

正本リンクと同じ機械編集で、関連リンク節へ 1 行追加する。

```
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧
```

既に hub を持つ 19 本（curated 16 + 定型 3）は冪等 skip。

### 5. ADR

`docs/adr/0012-zenn-review-deterministic-layer.md` に残す: code / LLM の境界線（どの項目を
どちらへ）、`npm run validate` の実効カバレッジと drift しない根拠、免除境界の実測値、
search-first の却下理由（zenn-validator / textlint）、`lint:links` を `--online` として
戻す判断と 2026-07 撤去との関係。

`~/.claude/rfcs/0005-review-to-lint-rollout-ledger.md` の row 3 に注記を 1 行:
project-local な Zenn 層は 2026-08-27 に先行実施済み、row 3 の保留は global
`writing-ecosystem` 側にのみ掛かる。

## 未決（この plan の承認で確定させたい 2 点）

- **`--online` を同梱する** — 実害 2 件を捕まえた唯一のクラス。既定 offline で隔離するので
  常時コストは無い。反対なら offline 検査のみに落とす
- **既公開の既存違反（H1 5 / fence 6 / title 3）は据え置く** — evidence には出すが今回は直さない。
  lint を初日から赤くしない（review-to-lint の免除境界規律）。title は検索流入と既存被リンクへの
  影響があるため特に触らない

## 検証

```bash
cd scripts && uv run pytest --cov=. --cov-report=term-missing   # coverage 床 80%
uv run python zenn_evidence.py ../articles/ai-review-task-loop.md          # 単体
uv run python zenn_evidence.py ../articles/ --text                          # 全数、免除境界の確認
uv run python zenn_evidence.py ../articles/ --online                        # URL 生死（公開直前想定）
```

- **全数で緑になること**: 上の「違反 0 件」14 項目が実装後も 0 で出ること。1 件でも出たら
  免除境界の設計ミスとして検出条件を直す（実装をゲートに合わせるのではなく、実測に合わせる）
- **grandfathered が分離されていること**: H1 5 / fence 6 / title 3 が deviation ではなく
  grandfathered として出ること
- **偽陽性の回帰テスト**: `/Users/you/` のプレースホルダ 3 件、bash コメント `# foo` の
  H1 誤検出 2 件を fixture 化してテストに固定する
- hub 遡及後: `npm run validate` / `npm run check:index` / diff が追加行のみ / 46 本の
  slug 一致と hub URL の HTTP 200

## 停止点

1. script + テスト + reviewer 配線 + 規約 + ADR で 1 commit
2. hub 行の遡及 46 本で 1 commit
3. **push は著者確認まで止める**（記事本文を触るため、Zenn 公開版へ即反映される）
