# Zenn/Dev.to 執筆ハーネスの実用軸への再構成

## Context（なぜやるか）

ユーザーは久しぶりに Zenn/Dev.to 記事を書くにあたり、まずハーネスを最適化したい。調査で 2 つの問題が確定した：

1. **声のミスマッチ**：global `writing-ecosystem` skill の Voice 規約（発見調・結論の問い化＝初期経典の語り口・断定→弱化）は **essay の声**。Zenn の技術記事もこの essay 声を正本にしていたため、**技術記事チャンネルの声が未定義**だった。
2. **冗長の堆積**：project 11 skills が frontmatter 仕様を 6 箇所、security check を 4 箇所、投稿時刻を 3 箇所（かつ**日と時刻の両方が矛盾**：火〜水7:00 / 火〜木8:00 / 火・木）で重複。`content-research-writer` ≈ `zenn-writer` の research flow はほぼ逐語重複。`chatlog-to-article` は frontmatter 無しで既に inert な orphan。

**ユーザーの方針（確定）**：今は channel ごとに文体が確立している（essay→writing-ecosystem/Substack、paper→paper-ecosystem）。だから **Zenn/Dev.to は独自軸を持つべき——「読者が即座に何かわかり、すぐ手に取って使える」**。低情報密度・実コード/図・即実用・低認知負荷・用途が瞬時にわかる。これを **今後の Zenn/Dev.to の既定**にし（既存 33 tech + 16 idea は遡及変更しない）、ハーネスを**フル整理**する。

**判断ログ（grill 結果）**：Q1=全記事の既定（tech レーン限定でなく channel 軸）／Q2=フル整理／FORK A=essay 声は「退役」でなく「本来の住所（essay corpus）へ再配置」。

---

## External Research Findings（Phase 0）

新スキルの style spec は独自発明でなく確立フレームに接地する。`geo-writer` は global/project とも**存在しない**（MEMORY.md の記載は stale）。

| フレーム | 使う部分 | 出典性 |
|---|---|---|
| **Diátaxis** | how-to（task 志向）+ reference（lookup 志向）象限。essay は explanation 象限→writing-ecosystem 側 | 業界標準の doc 分類 |
| **BLUF / Minto** | 冒頭に成果物・結論（bottom line up front） | 確立した technical writing 原則 |
| **GEO / answer-first** | 自己完結チャンク＝LLM 被引用性。人間 skim と machine extract の両立 | 本 repo の corpus 戦略と整合 |

**Verdict: Extend** — 既存フレーム（Diátaxis how-to/reference + BLUF + GEO）を採用し、薄い Zenn 固有ラッパー（新スキル）として包む。ゼロから style を発明しない。

---

## Target Topology（各ファイルの帰結）

| ファイル | 帰結 |
|---|---|
| **`zenn-practical-writing`（新規）** | 実用 style spec の正本。genre 中立 canon（AI-slop / title 誠実さ / topic 3軸）は writing-ecosystem に defer。Voice は**明示的に override**（essay 声を持ち込まない）。**強い description + `user-invocable: true` + `origin: shimo4228` の実 frontmatter 必須**（無いと「既定」として発火しない） |
| **`zenn-writer`（in-place 改修）** | **薄い router/stub に転換**。既定→`zenn-practical-writing`、essay/opinion の明示 opt-in→writing-ecosystem 声＋personality 資産。**path が生存するので inbound pointer が一切 dangle しない**（writing-team L38 / zenn-drafter L72 / CLAUDE.md / seo-optimizer / zenn-writing.md）。title-dup・essay-voice-dup・research-dup を除去 |
| **毒humor/刃牙**（zenn-writer 内） | **実用スキルに入れない**（personality かつ idea 資産）。標準 author-voice 資産として抽出（`zenn-idea-voice` 小スキル or idea レーン節）。**削除でなく soft 退避**（reversibility gate：author 資産を消さない） |
| **`content-research-writer`** | **soft-delete**（外部 origin / disable-model-invocation / 冗長）。`drafts/article-context` research flow は `zenn-drafter` の pre-Phase-1 step に 1 本化（drafter が唯一の consumer） |
| **`chatlog-to-article`** | **soft-delete**（既に inert）。固有の `articles/_context/{slug}-{source}-log.md` raw-log 規約（Zenn sync 除外）だけ `zenn-writing.md` に 3 行で保存。inline AI-slop リストは overlay 違反なので破棄 |
| **`zenn-format`** | JP-Zenn format/frontmatter の**単一正本**として維持。JP 4 コピーを pointer 化 |
| **`refs/translation-rules.md`** | **触らない**。Dev.to/EN は別スキーマ（`description`/`tags` CSV）。JP frontmatter に統合しない |
| **`writing-team`** | router 方式なら Mission A step2 は**無編集で OK**（zenn-writer router が type 分岐）。念のため step2 に「genuine essay は essay corpus へ」注記 |
| pipeline skills（quality-gate / publish-article / schedule-publish / seo-optimizer / ideation / series-checker / zenn-drafter / devto-translator） | 再掲を pointer 化。**seo-optimizer L36-42 の title 再掲本文を削除**（pointer は既にある）。投稿時刻を**live ファイルで 1 値に canonicalize**。frontmatter 欠落スキルに実 frontmatter 追加（slash 登録のため） |
| **`zenn-writing.md`（rule）** | dangling MEMORY.md 参照 2 件を修正（値を inline 化）。「Zenn **tech** 基盤＝新スキル、idea→writing-ecosystem」注記。`_context/` 規約 3 行を追加 |
| **`.claude/docs/adr/0003-*.md`（新規）** | channel 軸 + genre-split を記録。**ADR-0001 L58（zenn-writer voice「存続」行）と ADR-0002 §2（存在しない `writing-standards.md` 参照）を明示的に supersede**（しないと内部矛盾を出荷） |

---

## Migration Sequence（dangle 不能な依存順・各段は独立 commit/revert 可）

**鉄則：inbound link を repoint してから rename する。**

1. **Create** `zenn-practical-writing/SKILL.md`（実 frontmatter 付き）。純加算、何も壊れない
2. **Create** idea author-voice 資産（毒humor/刃牙 のコピーを移設。原本はまだ zenn-writer に残る）
3. **Fold** `drafts/article-context` research flow を `zenn-drafter` に追加（加算）
4. **Repoint** `zenn-drafter` L119 + L124 を content-research-writer→新 in-agent step へ
5. **Soft-delete** `content-research-writer`（inbound 無し→安全）
6. `zenn-writing.md`：`_context/` 規約保存＋MEMORY.md 参照修正＋投稿ペース inline（always-loaded なので下流編集前に）
7. **Soft-delete** `chatlog-to-article`（inbound 無し→安全）
8. **Rewrite** `zenn-writer` を router/stub に（path 不変→全 inbound 生存）。title/voice/research dup 除去
9. `writing-team` Mission A step2：router が分岐するなら no-op、注記のみ
10. JP frontmatter 4 コピーを `zenn-format` に repoint／seo-optimizer L36-42 削除／投稿時刻 canonicalize（独立・順不同）
11. **Write ADR-0003**（adr-writer agent 使用）。最後＝出荷後の end-state を記述。ADR-0001 L58 + ADR-0002 §2 を supersede

---

## 新スキル `zenn-practical-writing` の中身（style spec の核）

ユーザーの 5 マーカー → 検証可能な具体ルール：

| マーカー | ルール |
|---|---|
| 情報密度を抑えめ | 1 節 1 論点。前置き除去。短段落。密な散文より箇条書き/表。再読を要求しない |
| 図や実コード | 1 記事に ≥1 図/表。コードは**コピペで動く自己完結**（file path + 言語タグ + input→output） |
| すぐ使える | task 志向（Diátaxis how-to）。再現可能な成果物を渡す。前提を冒頭列挙。手順は順序付き・完全 |
| 低認知負荷 | BLUF：成果物を第一画面で宣言。見出しは outcome を述べる。前方参照禁止。詳細は `:::details` に progressive disclosure |
| 用途が瞬時にわかる | title + 冒頭が「これは何/読後に何ができるか」に答える。冒頭に「この記事で作れるもの/わかること」1 行 |

**inherit（writing-ecosystem に defer）**：AI-slop 禁止・title 誠実さ・topic 3軸。
**override（essay からの反転）**：essay は宣言調（「〜すべきだ」）を避け問い化するが、**実用 how-to は直接指示（「まず X する」）を推奨**——essay の tone-softening を明示的に反転する。これが最大の差別化点。
**接地**：Diátaxis（how-to/reference 象限。tutorial は副次、explanation=essay は対象外）＋ GEO（自己完結チャンク＝被引用性）。

---

## Risks & Guardrails

- **[HIGH] catchify 亡霊 / ADR-0001 違反**：「低認知負荷・用途明快・scannable」は ADR-0001 が葬った catchify と同語。**Bright-line（ADR-0003 に明記）**：実用スタイルは**著者が選ぶ draft 時の生成既定**（Content・著者所有・許可）。**完成稿へのエンゲージメント目的の事後リライトには絶対にしない**（＝catchify、禁止）。seo-optimizer/quality-gate に「もっと punchy に」権限を与えない。ADR-0001 の判定式「誰のために変えるか」が safe-harbor
- **[HIGH] idea レーン writer/reviewer ミスマッチ**：解決済み——router で既定=practical、genuine essay は essay corpus/opt-in。Zenn の主レビュアーは `editor`＋type-gated 実用チェックリスト。`essay-reviewer` は essay corpus 用に global 維持（Zenn practical 稿に essay 声採点を課さない）
- **[MED] series-checker vs 声境界**：新 practical 稿が**既存シリーズ先行記事（遡及変更しない 33 本）とトーン不整合**と flag されうる。ADR-0003 でルール明記：継続シリーズ内では channel 既定より先行声を優先（or 明示転換を許可）
- **[MED] ADR 内部矛盾**：ADR-0003 が ADR-0001 L58・ADR-0002 §2 を supersede しないと矛盾出荷
- **[LOW] Dev.to/EN 継承**：`devto-translator` の忠実翻訳で JP practical を自動継承。EN 専用スキルを作らない。ADR-0003 に継承を明記
- **[LOW] slash 未登録**：publish-article/schedule-publish/seo-optimizer は frontmatter 無しで `/slash` 未登録の可能性。編集ついでに `user-invocable` 追加
- **[LOW] AGENTS.md symlink→CLAUDE.md**：CLAUDE.md 編集は非 Claude ツールの読む内容も変える（意図通り）

---

## Reviewer stance（新エージェント不要）

`editor`（global）は runnable code / ≥1 図 / 冒頭 utility 宣言 / 前提列挙 / scannable を**検証しない**ため実用軸は under-covered。だが **(a) 新レビュアーを作らない**（ADR-0002 §1）**(b) global editor を編集しない**（essay/paper channel と共有・漏洩）。**正解＝5 マーカーを project-scoped `quality-gate` に `type:"tech"` gate で客観チェックリスト化**（runnable code ブロック有？図/表 ≥1？成果物を冒頭 N 行で宣言？前提列挙？見出し >30% 無し？）。判断でなく客観 gate なので quality-gate が正しい住所。任意で invocation 時に editor へ context 手渡し（global 改変せず）

---

## Verification（chore/refactor 系・build/test 非該当）

1. **リンク整合**：soft-delete 済みスキルへの参照が repo に残らない（`grep -rn "content-research-writer\|chatlog-to-article"` が pointer を返さない）
2. **invocation graph 解決**：writing-team Missions A-E の全 `[skill:]`/`[agent:]` 参照が実在ファイルに解決
3. **frontmatter 正本一意**：JP frontmatter が zenn-format 1 箇所（translation-rules の Dev.to スキーマは別途保持）
4. **投稿時刻一意**：live ファイル（schema + schedule-publish + publish-article + zenn-writing）で 1 値。ADR-0001 の歴史記述は**凍結**（書き換えない）
5. **ADR supersession**：ADR-0003 が 0001 L58 + 0002 §2 を明示 supersede
6. **dangling 解消**：zenn-writing.md の MEMORY.md 参照 2 件が消滅
7. **git status** 確認 → 意図しないファイル無し

---

## Out of Scope / Follow-ups

- 既存 33 tech + 16 idea 記事は**遡及変更しない**（legacy 資産）
- reorg 着地後、project auto-memory の MEMORY.md skill inventory を更新（現状 stale：9 skills 記載・名前も旧）
- **本タスク完了後に本来の目的（Zenn/Dev.to 記事執筆）へ**——新 `zenn-practical-writing` を初適用する記事テーマは reorg 後に選定

---

## Chain（実行時）

- 種別：harness reorg（skills/rules/agents/ADR＝markdown）。TDD 非該当
- Review：skills.md（origin/portability）自己レビュー＋リンク整合パス＋ADR は adr-writer agent
- 人間 gate：**Plan 承認（今）** ＋ **Verify 結果確認（commit 直前）**
- **Git push リマインダー**（CLAUDE.md CRITICAL）：commit 後にユーザーへ push 促す
