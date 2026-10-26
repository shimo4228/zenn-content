kind: external
# devto-translator に brief と著者の指摘の記録を渡す版を replay で採否する plan の前提事実（内部 5 点・外部 2 点）

調査時点: 2026-10-26。plan の決定（何回・どの順で・どこに置くか）は書かない。末尾の「plan が決めるべき論点」で止める。

## Scope searched

内部（working tree の読み取りと reflog。この調査は Bash を持たないため `git show` / `git log` / diff は取れていない）:

- 読んだ: `.claude/agents/devto-translator.md`、`.claude/agents/editor.md`、`.claude/skills/writing-ecosystem/SKILL.md` と `references/{author-corrections,publication-procedures,persona-read,review-output-format}.md`、`.claude/rules/{publishing-channels,writing-principles}.md`、`.claude/settings.json`、`.claude/output-styles/zenn-writing.md`、`docs/plans/{harness-scope-writing-harness,readme-human-llm-fold,skill-description-pointer}.md`（brief）、`drafts/` の処分記録 3 本と corrections 3 本、`~/.claude/skills/prose-translation/SKILL.md`、`~/.claude/skills/persona-read-loop/scripts/read.sh`、`~/.claude/settings.json`、`.git/logs/HEAD`（commit の順序と時刻の根拠）。
- Grep で該当行だけ読んだ: JP 3 本（`articles/`）と EN 3 本（`articles-en/`）。全文は読んでいない。
- 読んでいない: 翻訳時点の JP と brief（`git show` 不可）、`scripts/devto_crosspost.py`、`~/.claude/hooks/` の大半（`docs-prewrite.sh` と `review-model-notice.sh` の冒頭だけ読んだ）、`scripts/zenn_evidence.py` の全体。

外部（2026-10-26 に取得）:

- 一次: code.claude.com の docs 5 ページ（cli-reference / sub-agents / headless / output-styles / permission-modes）を WebFetch で本文まで。ページに版の表示は無い。
- 二次: GitHub issue の mirror（claudeissues.com）2 件。
- 翻訳の先行研究: WebSearch 3 回（用語集・スタイルガイドを渡す効果 / 確度（hedge）の保存 / 翻訳 brief）。arXiv 3 本と ACL Anthology 1 本を取得したが、読めたのは abstract だけ。ベンダー研究 1 件は fetch が 404 で、検索 snippet だけ。
- context7 は Claude Code の library ID を解決したが、docs 本体を取れる code.claude.com を直接読んだので query していない。

## Found

### 内部 1. translator が読むもの・書くもの（`.claude/agents/devto-translator.md`）

frontmatter は `model: opus`（:4）。`tools` の指定は無い（:1-6）ので全 tool を継承する（sub-agents docs の frontmatter 表: "Inherits every tool available to subagents if omitted"）。入力は JP 記事の path 1 つだけ（:13-15）。

| Phase | 行 | 読むもの | 副作用（書くもの） |
|---|---|---|---|
| 1 翻訳 | :19-42 | `~/.claude/skills/prose-translation/SKILL.md`（:25）、JP 記事（:26）、`docs/translation-glossary.json`（:27）、`scripts/schedule.json` の `articles-en/` エントリの `devto`（:33-36、著者の Zenn 記事へのリンクを Dev.to 版 URL に置換するため）、`writing-ecosystem/references/publication-procedures.md` の「AI 開示」（:40-41）。常駐の CLAUDE.md と rules も context に入る | `articles-en/{slug}.md`（:42） |
| 1.5 図 | :44-52 | EN 稿の `![](/images/*.png)`、`figures/<name>.html`、skill `mono-figure` | `figures/<name>-en.html`、`images/<name>-en.png`、撮影用の server の起動と停止（:49）、EN 稿の画像参照と alt の置換（:51） |
| 2 タグ | :54-64 | `scripts/devto_crosspost.py` の `resolve_devto_tags()`（:56）、`https://dev.to/t/<tag>`（:61、外部 web） | EN 稿 frontmatter の `tags:`（:63） |
| 3 cover | :66-70 | `images/covers/{slug}.png` の有無 | 無し（手動生成を促すだけ） |
| 4 セルフチェック | :72-80 | `writing-ecosystem` の原則と style-diagnostics（:79） | EN 稿をその場で直す（:74） |
| 5 schedule | :82-89 | `.claude/refs/schedule-schema.md`（:84） | `scripts/schedule.json` に EN エントリを追加（:86-89、追跡ファイル） |
| 6 / 7 | :91-107 | — | 投稿はしない（:96）。完了報告のみ |

replay で訳文の段だけを比べるときの事実:

- 訳文を作る段は Phase 1 の手順 1〜4（:25-41）。手順 5（:42）の保存先だけが production の path に固定されている。
- Phase 1.5 / 2 / 3 / 5 は訳文の外（PNG、tags、cover、schedule.json）。ただし EN 稿の中に痕跡が残る: 画像参照と alt（:51）、frontmatter の `tags:`（:63）。editor はこれらも読む。
- Phase 4 は EN 稿を書き換える（:74）。production では Phase 4 の後の稿が editor に渡った。Phase 1 だけで止めると、editor が見る稿は production の入力と違う。Phase 4 の 2 項目目（:77）は「図は `-en.png` を指しているか」を確かめるので、Phase 1.5 を止めると自己検査が成り立たない。
- 副作用を止める手段は、定義文の外にしか無い。agent は `tools` を絞っていないので、定義文を replay 用に書き換えると「今の版」と別物を比べる。起動側（prompt の指示 / 権限 / 作業コピー）で止めることになる。
- 訳文は時間で変わる外部状態を読む: `schedule.json` の `devto` URL（:33-36）と dev.to のタグ確認（:61）。replay は翻訳時点でなく現在の状態を読む。
- 現行の定義は、3 本の翻訳より後に足された規則を含む（reflog の commit subject からの推測。agent ファイルの履歴は取れていない）:
  - AI 開示の訳出（:40-41）は、開示を全媒体の既定にした c053e7b と Zenn 84 稿に開示を足した 04afbcd（`.git/logs/HEAD:170-171`、10/8 19:48 JST）より後。harness-scope（10/3）の翻訳はこれより前。
  - `{% details %}` の規則（:37-39）は、`fix(devto): ...liquid tag に変換する` の 7e30e02（`.git/logs/HEAD:177`、10/8 21:10 JST）に対応するはず。readme の EN commit（21:09 JST）はその 72 秒前。
  - Phase 1.5（`feat(agents): devto-translator に図の英訳の Phase を足す`、7f41790、`.git/logs/HEAD:143`、10/3 16:33 JST）は 3 本とも前。

関連する既存の設計根拠: `~/.claude/skills/prose-translation/SKILL.md:12-13` は、voice 非収束な prose の翻訳をサブエージェントへ handoff すると「会話文脈と voice 制約を落とす」と書く。定型 pipeline の venue 翻訳は例外とし（:15-17）、隔離モードでは起動時に voice sample・term-lock 表・localization policy を「明示的に手渡す」と定める（:127-132）。今回の版は、この手渡しの対象を brief と corrections に広げる形になる。

### 内部 2. EN editor の採用指摘の分類

材料: `drafts/harness-scope-writing-harness.disposition.md:53-60`、`drafts/review-disposition_readme-human-llm-fold.md:56-62`、`drafts/review-disposition_skill-description-pointer.md:47-52`。いずれも 1 指摘 1 行の要約で、EN 初稿の該当箇所は残っていない（EN の最初の commit は反映後）。反映後の文は最終 EN に残る。以下の分類は要約 1 行からの私の読みで、EN 初稿は見ていない。

記号: K = 確度・帰属のずれ / E = 英語の言い回し / S = 構造・その他 / ? = 要約から決まらない。

| 記事 | 採用 | K | E | S | ? |
|---|---|---|---|---|---|
| harness-scope（MEDIUM 4 + MINOR 7） | 11 | 1 | 4 | 6 | 0 |
| readme-human-llm-fold（MEDIUM 4 + MINOR 12） | 16 | 1 | 14 | 1 | 0 |
| skill-description-pointer（MEDIUM 3 + MINOR 9） | 12 | 1 | 8 | 1 | 2 |
| 計 | 39 | 3 | 26 | 8 | 2 |

（readme の M1 は E に数えたが、中心命題の含意に触れる境界例。下の表で扱う。skill の「?」2 件は、「〜ほど」の勾配と "did not measure that"。）

内訳の要点:

- harness-scope: K は M1。E は M2（"I stopped that conclusion"）、m2（翻訳調）、m6（導入の文構造）、m7（3 つの言い回し）。S は M3、M4（Output Style の表記ゆれ）、m1（見出しの主語）、m3（帰属行の反復）、m4（引用符の入れ子）、m5（表見出し）。M3 は、JP の「コード以外のタスクにも」（JP:157）を忠実に訳したため直後の文と矛盾した、原文由来の曖昧さ。EN は JP から離れて "other tasks besides writing" に直した（EN:165）。
- readme: K は M2。E は M1・M3・M4 と MINOR 11 件。S は "this English version" の注記 1 件。
- skill-description: K は M3。E は M1（係り）、M2（"the pairs" の指示対象）、MINOR 6 件。S は "stayed resident" の初出 1 件。

確度・帰属のずれ（K）と境界例を 1 件ずつ、brief の Author's words と corrections で避けられた種類かを判定した。「あり」はすべて推測で、replay が検証する対象。corrections は翻訳時点にあった項目だけを見た（内部 3 参照）。

| 指摘 | 起きたこと | JP の該当 | brief | corrections | 判定 |
|---|---|---|---|---|---|
| harness-scope M1 | "I found that" が著者の「分かってきた」より強い。反映後 "it started to become clear that"（EN:15） | JP:14「分かってきました」 | `docs/plans/harness-scope-writing-harness.md:18`（原文「わかってきた」）、:24（「確度は「分かってきた」のまま」） | 確度を扱う項目は C1〜C8 に無い | あり得る（弱い）。JP:14 は既に「分かってきました」で、背骨 1（`writing-principles.md:12`）も常駐していたのに起きた。brief が足すのは「ここは確度保持の対象」と名指す点だけ。register 行（`publishing-channels.md:13`「essayistic hedge へ寄せない」）と prose-translation の stance 規則（`SKILL.md:55`「実用の直接指示なら hedge へ弱めない」）が背骨と逆向きに引いた、という構図は推測 |
| readme M2 | "should keep getting more mixed" が規範に読める。反映後 "I expect the line … to keep blurring"、要旨は "will likely"（EN:150） | JP:136「混ざっていくはずです」 | `docs/plans/readme-human-llm-fold.md:26`（原文「はずだから」）、:33（確度は「はず」「理想」「重要」のまま） | 「はず」を扱う項目は無い | あり得る。brief:33 が「はず」を名指ししている |
| readme M1（境界） | "Still," が譲歩に読め、「まだ分ける側」の含意が出ない。反映後 "But this is still a way of separating"（EN:25） | JP:24「ただ、これはまだ、人間とLLMを分けるやり方です」 | brief:28（「まだ分ける側だ。これからも続く試行錯誤のひとつだ。」）、:30-32 | C2（`drafts/readme-human-llm-fold.corrections.md:12-19`）。JP を直した指摘で、修正後の文が JP:24 に実在する。C2 の Trigger は、orchestrator が「まだ分ける側」を 1 句に縮めて不自然にした経緯 | あり得る。立場の意味は brief と C2 にあるが、"Still," は接続語の選び方なので、意味を知っていても出る余地が残る |
| skill-description M3 | 締めの命令形が、著者の「決めたこと」を読者向けの手順に変えた。反映後 "I decided three things: …"（EN:137） | JP:136「呼ばせるかを先に決め、呼ばせるものは短く書き、幅はlintで数える。ここまでが決めたことです。」 | `docs/plans/skill-description-pointer.md:9`（「といのまま読者に渡していいよ」）、:14（Central thesis の末尾「問いのまま渡す」）、:21（「締めは問いのまま」） | C1（`drafts/skill-description-pointer.corrections.md:3-10`）。対象は締め、Expect は「締めが答えを言い切っている・教訓に見えると止まる」。commit 0630f10 は EN より前 | あり得る（4 件で最も強い）。JP:136 の「〜、〜、〜で数える」は te 形の連なりで、英語では命令形にも列挙にも読める。brief と C1 が同じ誤読を名指しで予防している |
| skill-description MINOR「〜ほど」の勾配（?） | 要約は 4 字だけ。EN:25 に "the longer I had written a description, the more likely …" が残る | JP:24 | brief:15・:18 は対象を「自前の 4 本」と書く | — | 不明。JP 段で fact-checker が同じ一般化を ❌ にして限定させている（`drafts/review-disposition_skill-description-pointer.md:6`）ので、確度の項目だった可能性がある（推測） |

この表から言えること / 言えないこと:

- 確実な K は 3 件（採用 39 件の約 8%）、境界・不明を足しても 6 件。26 件（境界の 1 件を含む）は英語の言い回しで、brief や corrections が効く種類とは考えにくい。
- K の 4 件とも、必要な情報は JP 本文に既にあり、背骨 1 も常駐していた。brief と corrections が足すのは、情報でなく「この箇所を保て」という名指しと意図。
- corrections が効きうるのは skill の C1 と readme の C2 の 2 つに限られる。corrections の 17 件の大半は JP の起草の誤りへの指摘で、修正後の文は最終 JP に入っている（C2 の修正後は JP:24 と JP:138、harness-scope C7 の修正後は JP:14、skill C2 の題は JP の title、と抜き取りで確認）。つまり corrections が translator に足す情報の中心は、最終 JP から読み取れない「消した内容」と Expect。この点は内部 4 の混入経路と同じ場所にある。
- 同じ箇所への指摘が JP 段の panel（fact-checker・Codex）にもあったのは、skill の「ほど」だけ。EN 段で走らせた reviewer は editor だけ（内部 5 参照）。

### 内部 3. 翻訳時点の版と corrections の時刻

JST。reflog（`.git/logs/HEAD`）の timestamp から換算した。

| 記事 | brief | JP | EN | JP→EN | その間の作業 |
|---|---|---|---|---|---|
| harness-scope | acf9b93 `docs(plan)` 10/3 15:23（:139）。図 3 枚を入れた 0be7292 は 17:05（:144） | b62de14 17:31（:151） | fd73501 17:42（:153） | 10 分 39 秒 | 3403a1e 図の EN 版 17:37（:152）を挟む |
| readme-human-llm-fold | ebf0cc0 10/8 20:58（:172） | c989a61 20:59（:173） | fce97b6 21:09（:174） | 10 分 16 秒 | — |
| skill-description-pointer | 0630f10 10/9 20:38（:181） | 87c27dc 20:39（:182） | b3fd863 21:17（:183） | 37 分 47 秒 | — |

JP→EN の時間には、translator・EN editor・指摘の反映が全部入っている。

corrections.md の各項目に日時は無い。項目の欄は 原文 / 対象 / 修正前 / 修正後 / Trigger / Expect / commit（任意）で（`references/author-corrections.md:8-17`）、並びは追記順（C 番号）だけ。時間に置く手段は次の 3 つで、いずれも間接的:

1. `commit:` 行の SHA を reflog に当てる。
2. Trigger の記述（「headline-craft の候補を提示した」→ 題の確定段、「公開後に記事を見直した」→ 公開後）。
3. 項目の中身と commit subject の一致。

結果:

| 記事 | 項目数 | 翻訳時点にあった | 見分けの根拠 | 翻訳後に足された |
|---|---|---|---|---|
| harness-scope | 8 | C1〜C7 | C1〜C4: brief 段階の項目（対象が brief、Trigger が「再確認」）で commit 行は無い。C5: `commit: dd7ab04`（17:18、:146）。C6・C7: commit 行は無いが、題を決めた cdc3c38（17:27、:147）の subject と中身が一致（推測） | C8（推測）: commit 行は無いが、修正後が「見出し 44〜48px・1 行に戻す」で 0bec3cb の subject「図の見出しを 1 行の大きさに戻す」（17:48、:158、EN の 6 分後）と一致し、Trigger が「公開後に記事を見直した」。図の PNG だけを変える項目で、EN の散文には影響しない |
| readme-human-llm-fold | 7 | C1〜C7 | 7 件とも `commit: c989a61`（JP の commit、EN の 10 分前）。見分けは確実 | 無し |
| skill-description-pointer | 2 | C1・C2 | 2 件とも `commit: 0630f10`（EN の 38 分前）。見分けは確実 | 無し |

見分けられない限界: harness-scope の C1〜C4・C6・C7 は commit 行が無く、時間への配置は内容と subject からの推測。corrections は `drafts/`（gitignore、`.gitignore:26`）にあり git 履歴が無いので、翻訳時点の版の復元もできない。今のファイルが唯一の版。17 件中 16 件が翻訳時点にあったと言えるのは、この推測を含めた数。

brief も同じで、この調査は working tree の版を読んでいる。lead が確かめた翻訳時点の brief（0be7292 / ebf0cc0 / 0630f10）と同一かは diff が取れておらず未確認。harness-scope の brief は、C2・C3 の Trigger（書く前の「再確認」）を反映した形（brief:34-39）になっている。plan commit（acf9b93）より後の編集と読めるので、plan commit 時点の版とは違うはず（推測）。

### 内部 4. corrections が EN 訳に紛れる経路

前提となる事実:

- corrections は非公開（`drafts/` は gitignore）。EN 稿・EN の commit・`schedule.json` は公開される。translator が書くのは公開側。
- 運用規則は、公開側へ出すものを絞っている。commit 本文へ写すときは公開安全規約を原文に当てて `[略]` にし、「修正前後の抜粋は `drafts/` にだけ置く」（`writing-ecosystem/SKILL.md:168-172`）。translator に渡すこと自体は repo への書き込みではないが、出力に混ざれば公開側に出る。
- brief は追跡される公開ファイル（`docs/plans/`。`public-records.md` の対象）。corrections と違い、混ざっても非公開情報の漏れにはならないが、内部ラベルが混ざる品質の問題はある。3 本の brief には、台帳の C 番号の参照を含む行が 34 行ある（Grep で数えた。セッション ID の行を含む）。現在の EN 3 本には C 番号・「台帳」・`drafts/` が 0 件（Grep で確認）なので、基準線はきれい。
- 3 本の corrections に個人 path と credential は無い（Grep で確認）。

経路（corrections の欄ごと）:

1. 修正前の抜粋を、正しい原文だと読んで復活させる。著者が意図して消した内容が戻る。例: readme C5・C6 は、取得に失敗した 3 回分の行と説明を記事から消させた項目（`drafts/readme-human-llm-fold.corrections.md:40-55`、修正前に当たる文が載る）。C1 は旧い「この形はこの 1 本」の記述（:6）。harness-scope C1 は本文から外させた「これまでの手」の列挙（`drafts/harness-scope-writing-harness.corrections.md:4`）。
2. 本文に載せないと著者が決めた数値が、Expect に載っている。readme C4 の Expect（:36）は、クローン数と閲覧数の集計値を挙げて「本文には載せない著者選択」と明記する。translator が根拠として本文に足せば、著者の選択が覆る。
3. 著者の発言の原文（口語・内輪）が引用として訳され、本文に入る。または Trigger / Expect の内容が注や hedge として足される。
4. AI 開示の枠への過剰記載。開示は「著者が決めたこと」「著者が確かめたこと」を記事の具体で埋める（`publication-procedures.md:25-31`）。corrections を渡すと、translator が著者の判断を根拠に「確かめた」を書き足せる。skill-description の処分記録に、orchestrator と researcher の作業を著者が確かめたことのように書いた開示を文ごと削った前例がある（`drafts/review-disposition_skill-description-pointer.md:41-42`）。
5. Phase 7 の完了報告（:98-107）と commit message。非公開の報告に留まるが、commit に写る。

検出手段の現状: EN 稿の機械検査は、Dev.to 行で `devto-translator` の self-check と `devto_crosspost.py post --dry-run` だけ（`publishing-channels.md:13`）。`scripts/zenn_evidence.py` は `articles/*.md` を対象とする（:2）。個人 path・secret の検査（:75-82, :289-295）が `articles-en/` に当たるかは確かめていない。受け入れの「public-safety scan」は全 channel の要件（`publishing-channels.md:43`）だが、EN に自動で走るかは未確認。つまり混入を拾うのは editor と著者の通読が主。

渡し方の注意（事実から導ける条件。採否は plan）:

- translator が EN 稿に載せてよいのは JP 稿の内容だけ、という線を渡す文面で保てるか。修正後は最終 JP に既にある。corrections が足すのは「消した内容」と Expect なので、そこを渡さずに済む形（修正後と Trigger の要旨だけ、など）があるかが論点。
- 混入は機械で拾える部分がある: EN 稿にあって JP 稿に無い数値・URL・C 番号・`drafts/` を grep する（現在の EN 3 本は C 番号などが 0 件で、検査の基準線になる）。
- replay の出力は公開稿でなく草稿として扱い、`drafts/` 配下（gitignore）に置く。この report は公開リポジトリに入るため、corrections の原文・数値は書き写していない。

### 内部 5. EN editor の dispatch に要る入力

editor の仕様（`.claude/agents/editor.md`）:

- tools は Read / Grep / Glob だけ（:5）、model は `fable`（:6）。Write を持たないので、report は最終メッセージで返り、保存は呼び出し側がする。
- 「`writing-ecosystem` が構造凍結した稿に 1 回だけ dispatch される」（:3）。
- チャンネル表の該当行を引き、担当外ならその旨を返して所見を出さない（:19-20）。EN の行は path matcher が `articles-en/*.md`、channel editor が `editor`（`publishing-channels.md:13`）。matcher に一致しない path を渡すと、editor が行を引けない恐れがある（推測。contract は一致しない場合 `writing-ecosystem` と `quality-gate` が BLOCKED を返すと定める、:17-18）。replay の稿を `articles-en/` を path に含む場所（例: `drafts/<slug>/replay/<run>/articles-en/<slug>.md`、`drafts/` は cwd 内で gitignore）に置けば matcher に当たる。dispatch でチャンネルを明示する手もある。
- §7（:111-131）が要求する dispatch 内容は 2 つ: 承認済み brief の path（:113-114）と、AI が本文を生成したかどうか（:116-117。無ければ開示の検査は unverified）。`writing-ecosystem/SKILL.md:134-135` も同じ 2 点を書く。
- 開示の検査（:121-125）: ブロックが最末尾にあり、リンクが無く、この記事の具体で埋まっているか。EN の型は `**How this was written:**`、JP の開示を訳して翻訳を (1) に足す（`publication-procedures.md:21-23, :47`）。translator の版によってこのブロックの出来が変わると、brief や corrections と無関係な反転として一覧に出る。
- report の骨格は `references/review-output-format.md`（Review Summary / CRITICAL / MEDIUM / MINOR / Suggestions / Canonical coverage）。指摘は自由文で、ID は付かない。

production の EN 段の事実:

- EN 訳に走らせた reviewer は editor だけ。contract が、JP 正本が profile を通った後の EN 訳には「ペルソナ読み・初見の読み・`fact-checker`・`title-reviewer` は回さない」と定める（`publishing-channels.md:24-26`）。
- production で editor が brief を持っていた証拠: harness-scope M1 の処分が「brief の「分かってきた」」を根拠に挙げる（`drafts/harness-scope-writing-harness.disposition.md:54`）。
- 当時の dispatch の文面は、処分記録 3 本にも `drafts/` にも残っていない。editor に JP 稿の path が渡っていたかも不明。

両版に同じ dispatch を使うための文面の要件（要件であって、中身の決定ではない）:

- 稿の path（Read できる絶対 path）、brief の path、AI が本文を書いたこと、チャンネル（Dev.to）の 4 点を含む。
- 文面は 1 つのテンプレートに固定する。production では orchestrator が毎回書いていたので、replay では文面の揺れが混ざる。
- どちらの版の出力か、replay であること、過去の指摘を、editor に伝えない。
- editor の model を記録する。内部の環境変数が絡む（外部 6 参照）。

### 外部 6. headless で名前付きの agent を走らせる方法（as-of 2026-10-26）

`claude -p --agent <name>` は現行 docs で仕様として書かれている:

- CLI reference: `--agent` は「現在の session に agent を指定する（`agent` 設定を上書きする）」。`-p` は print mode（cli-reference）。
- sub-agents docs（"Run the whole session as a subagent"）: `--agent <name>` で main thread が subagent の tool 制限と model を引き受ける。system prompt は default を丸ごと置換する（`--system-prompt` と同じ。prompt が空のときだけ維持）。CLAUDE.md は読み込まれる。`-p` で prompt を持つ custom agent を走らせると git status の snapshot も付かない、と明記。
- agent の探索（同名なら上位が勝つ）: managed settings → `--agents` CLI flag → `.claude/agents/` → `~/.claude/agents/` → plugin。`--agents` は JSON で agent を定義でき、print mode ではファイル path も受ける（v2.1.281 以降）。使える項目は `prompt` と frontmatter 項目。`name` は frontmatter で自由に付けられ、`reviewer-v2` のような名前が例示されている。つまり新旧 2 版を別名で並べる / `--agents` で差し替える、のどちらも docs 上は可能。
- headless docs: `-p` は `--bare` を付けない限り、hooks・skills・subagents・MCP・auto memory・CLAUDE.md を interactive と同じく探索して読み込む。出力は `--output-format text|json|stream-json`。json は `result`、session ID、`total_cost_usd` などを返す。stream-json の `system/init` は model・tools・plugins などを返す。
- `--bare` は subagent の自動探索を飛ばし、subscription の login を使わない（`ANTHROPIC_API_KEY` が要る）。ローカルの rule は harness の agent の runner を `claude -p`（サブスク）で呼ぶと定める（`~/.claude/rules/common/evals.md:18`）。bare とは両立しない。

Agent tool で subagent として呼ぶ場合との違い（docs の記述と、ローカルの設定から読めること）:

| 観点 | Agent tool 経由（production の経路） | `claude -p --agent` |
|---|---|---|
| context | 新しい隔離 context。親の会話履歴は見えない。CLAUDE.md の階層（project rules を含む）は継承する。結果は要約として親に戻る | 新しい session。入力は `-p` の prompt。CLAUDE.md は同じく読み込まれる |
| system prompt | agent の本文 | 同じ（default を置換） |
| output style | 適用されない（output-styles docs: 「他の subagent は自分の system prompt を走らせるので、style は応答を変えない」） | main conversation として扱われるため、project の `outputStyle: zenn-writing`（`.claude/settings.json:2`）が効く可能性がある。agent が system prompt を置換する場合に style が残るかは docs に無い。style の規約には「稿や規約のファイルは、著者が変えてと言ってから触る」（`.claude/output-styles/zenn-writing.md:9`）があり、translator のファイル書き込みを妨げうる。`--settings` は同じ key の値を上書きする（cli-reference）ので、`{"outputStyle":"default"}` で外せる |
| auto memory | 主会話の auto memory は読み込まれない（sub-agents docs） | 読み込まれる。`read.sh:17-22` は、空の `--setting-sources` だけでは作業ディレクトリの project の auto memory が残ると 2.1.302（2026-10-18）で実測し、`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` を併用している。この repo の MEMORY.md には 3 本の記事の pipeline メモが載っている |
| permission | 親の mode を継承（sub-agents docs の permissionMode 節） | `permissions.defaultMode` が設定にあれば優先される（permission-modes docs の順序: flag → settings → 既定）。この環境は `~/.claude/settings.json:125` が `auto`。docs の既定は v2.1.302 以降 Manual（許可の無い書き込みは拒否）。`acceptEdits` の自動承認は working directory と `additionalDirectories` の中だけ（permission-modes docs）。scratch が cwd の外だと書き込めない恐れがある |
| model | frontmatter が優先（v2.1.251 以降の順序: 呼び出しの引数 → frontmatter → `CLAUDE_CODE_SUBAGENT_MODEL` → 親）。この環境は `~/.claude/settings.json:3-5` で `CLAUDE_CODE_SUBAGENT_MODEL=opus` | main thread が frontmatter の model を引き受ける（sub-agents docs）。`--model` との優先順位は docs に無い。env var が main thread に効くかも書かれていない |
| 並列 | 同時 20 まで（既定）。結果は親の context に戻るので、6〜18 本の report は親の context を消費する | 別 process を並べて起動できる。結果は stdout / ファイル。`--no-session-persistence` で session を残さない |
| hooks | SubagentStart など | non-bare の `-p` は user と project の hooks を走らせる。`~/.claude/settings.json:135-309` の hooks が走る。Edit/Write の PreToolUse は `docs-prewrite.sh`（別の docs ディレクトリ専用）、`skill-create-notice.sh`、`research-gate.sh`。後者は plan の依頼に反応する hook で、本体は読んでいない |

既知の不具合と、確認の方法:

- `--agent` が `-p` で黙って無視される報告（v2.0.76、2025-12-30 起票）は、2026-03-12 に "not planned" で閉じられ、修正版は示されていない（mirror のページ）。現行 docs は `-p` でも使える前提で書かれている。矛盾の扱いは Contradictions 参照。smoke check として、stream-json の `system/init` の `tools` が agent の frontmatter の tools と一致するか（editor なら Read / Grep / Glob だけか）を見る手がある。`read.sh:76-82` は同じ init event の `tools` を検査に使っている。
- `CLAUDE_CODE_SUBAGENT_MODEL` が frontmatter の `model` を上書きする報告（2.1.236、2026-09-01 起票、mirror の snapshot 時点で open）。同じ報告に、`model: fable` の alias が黙って既定 model に落ちる、という記述もある。docs は 2.1.251 以降 frontmatter が優先と書いているので、報告は旧順序の挙動と読める。この環境で editor（`fable`）が実際に何で走るかは、記録して確かめる。subagent の transcript から実 model を読む手が local にある: `review-model-notice.sh:14-19` は subagent 自身の transcript を `<親 transcript の dir>/subagents/agent-<agent_id>.jsonl` で読む（docs 未記載の実装詳細と、同ファイルが書く）。
- 版: `read.sh` の実測は 2.1.302（2026-10-18）。docs のページに版の表示は無い。replay で使う版は `claude --version` で記録する必要がある。

形の例（documented な flag の組み合わせで、未実行。plan の決定ではない）:

```
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --agent devto-translator \
  --settings '{"outputStyle":"default"}' --output-format json --no-session-persistence "<dispatch>"
```

### 外部 7. 翻訳に著者の意図・用語の決定を渡すと drift（確度の強まり・帰属のずれ）が減るかの一次資料

確度・帰属の drift を、翻訳で、意図や brief を渡す条件と渡さない条件で直接比べた一次資料は見つからなかった。近いものは次の 4 本。いずれも abstract または snippet だけを読んだ。

- Belem ほか, "From 'May' to 'Is': Certainty Distortion in Language Model Rewriting"（arXiv 2606.07951、2026-06-06 投稿、2026-09-15 に v2、EMNLP 2026 Main 採択; abstract のみ）。科学・ニュース・医療文の書き換えで、意味を保つはずの変換が表明された確度を変える現象を測った。出力の最大 75% に歪みがあり、確度を上げる側が下げる側の 1.5〜2 倍多い。claude-haiku-4.5 は医療文で、1 回の書き換えで 20%、5 回で 40% の例が確度を上げた。「prompt による介入は全体の歪みを減らすが、無くしはしない」。翻訳でなく書き換えの研究。確度が強まる方向への偏りの大きさと、prompt での緩和が部分的であることの根拠になる。
- Lai & Li, "The Role of Prompt Language and Translation-Theory-Driven Prompts in LLMs: A Case Study on Spanish-Chinese Journalistic Translation"（arXiv 2607.03160、2026-07-03; abstract のみ）。GPT-5.2 でスペイン語→中国語の社説 4 本、48 条件。人手の MQM では brief 志向の prompt が最高（8.66 対 7.84）、BLEU と BERTScore は baseline を好んだ。翻訳理論に基づく prompt は "Awkward style" の誤りを選択的に減らし、"Unidiomatic style" は全条件で残った。abstract には、brief の中身（著者の意図を含むか）が書かれていない。日本語でも、確度でもない。prompt の効果が誤りの種類で偏ることと、自動指標と人手評価が割れることの根拠。
- Karpinska & Iyyer (2023), "Large language models effectively leverage document-level context for literary translation, but critical errors persist"（arXiv 2304.03245、2023-04-06 投稿; abstract のみ）。段落単位で訳す方が文単位より誤訳・文法誤り・文体の不整合が少ない。日本語を含む 18 言語対、GPT-3.5。重大な誤りは残り、著者の声を保つには人間の翻訳者が要ると結論。年代が古く、モデルも古い。
- 用語集・locale 規則を prompt に入れる効果: Lingo.dev の研究（ベンダー、peer review 無し。fetch は 404、WebSearch の snippet のみ）が、用語の誤りが 16.6〜44.6% 減り、全体の品質スコア（GEMBA-DA）では差が検出できなかった、と報告する。EAMT 2026 の Graça ほか "Automated Information Extraction and Template Filling from Client Style Guides"（abstract のみ）は、クライアントのスタイルガイドを system prompt に入れて訳す枠組みを人手の選好で評価し、modest な差を報告する。どちらも用語・スタイル規約の遵守が対象で、確度や帰属ではない。

この領域の主張は 1 週間で古くなる分野なので、上は 2026-10-26 時点。期限条件: 確度を対象にした翻訳の ablation が出たら置き換える。

## Contradictions

- `--agent` と `-p`: 2025-12 の issue（v2.0.76）は「黙って無視される、閉じた理由は not planned」、現行 docs は `-p` で custom agent を走らせる前提で書かれている。docs は first-party で新しい（2026-10-26 取得）ので docs を採る。ただし issue の経緯があるため、init event の `tools` による smoke check を入れる価値がある。
- model の優先順位: docs は 2.1.251 以降、frontmatter が `CLAUDE_CODE_SUBAGENT_MODEL` に勝つと書き、issue（2.1.236）は逆の挙動を報告する。docs の本文が「2.1.251 より前は env var が先だった」と書いているので、両者は版の違いとして整合する。この環境の版では未確認。
- 推奨の mode と環境: docs は scripted call に `--bare` を勧め、将来 `-p` の既定にするとも書く。ローカルの rule は harness の agent に `claude -p`（サブスク）を使うと定める。bare は subscription の login を使わないので両立しない。
- 記述と実物の食い違い（rule `knowledge-staleness.md` に従い列挙）:
  - `articles-en/harness-scope-writing-harness.md:167` の開示は `**AI-mediated writing disclosure:**` で、関連リンク節の前にある。現行規則（`publication-procedures.md:21-23`）は最末尾・`**How this was written:**`。翻訳当時の規則の名残。
  - `writing-ecosystem/SKILL.md:121-122` は「凍結稿と処分記録の組は replay の材料になる」と書くが、`drafts/**/frozen*.md` は 1 件も無い（Glob で確認）。この規則は新しく（最新の commit 456ff2e）、3 本はそれ以前。
  - `prose-translation/SKILL.md:12-13` は voice を伴う翻訳をサブエージェントに渡すと文脈を落とすと書き、devto-translator は subagent。例外条項（:15-17）で整合するが、今回の plan はその例外の中身を検証する。
  - `editor.md:6` は `model: fable`、`~/.claude/settings.json:3-5` は `CLAUDE_CODE_SUBAGENT_MODEL=opus`。docs の順序では frontmatter が勝つ。この環境で実際にどうなるかは未確認。

## Local evidence

- lead が git で確かめた版（prompt に記載）: EN の commit / JP の commit / brief の commit、corrections の項目数 8 / 7 / 2、drafts は gitignore で corrections は今の版だけ、EN の最初の commit は反映後。reflog（`.git/logs/HEAD`）の commit 順と時刻はこれと整合した（内部 3 の表）。
- 処分記録 3 本の EN 節（`drafts/harness-scope-writing-harness.disposition.md:53-60`、`drafts/review-disposition_readme-human-llm-fold.md:56-62`、`drafts/review-disposition_skill-description-pointer.md:47-52`）。採用 39 件の分類は内部 2。
- reflog の時刻（JST、10 月）: 7f41790 3 日 16:33 / acf9b93 3 日 15:23 / 0be7292 3 日 17:05 / dd7ab04 3 日 17:18 / cdc3c38 3 日 17:27 / b62de14 3 日 17:31 / fd73501 3 日 17:42 / 0bec3cb 3 日 17:48 / c053e7b・04afbcd 8 日 19:48 / ebf0cc0 8 日 20:58 / c989a61 8 日 20:59 / fce97b6 8 日 21:09 / 7e30e02 8 日 21:10 / 0630f10 9 日 20:38 / 87c27dc 9 日 20:39 / b3fd863 9 日 21:17。
- 1 回の EN 生産（translator + editor + 反映）の実時間は 10〜38 分（内部 3）。replay の 1 run あたりの規模の目安になる。
- `~/.claude/skills/persona-read-loop/scripts/read.sh` は、`claude -p` で隔離した reader を走らせる既存の実装。隔離フラグ・auto memory 無効化・init event での検査（:17-33, :76-93）を持つ。ただし reader は project の agent や CLAUDE.md を意図して外す設計で、今回の translator / editor は逆にそれらを読む必要がある。
- `~/.claude/rules/common/evals.md:18` は、harness の agent の runner / judge は `claude -p`（サブスク）と定める。

## plan が決めるべき論点（決定は書かない）

1. 起動経路。Agent tool（production と同じ経路）か `claude -p --agent` か。違いは output style・permission・auto memory・model（外部 6 の表）。両版と editor を同じ経路にするか。
2. 訳文の段を止める範囲。Phase 1 のみか、Phase 4 を含めるか（production の editor 入力は Phase 4 後）。EN 稿内の画像参照・alt・`tags:`・AI 開示の扱い。止める手段（prompt の指示 / 権限 / 作業コピー）。「今の版」の定義文は変えない前提でよいか。
3. 入力の時点。JP と brief は翻訳時点の版（`git show`）か現在か。harness-scope は JP:b62de14 の時点に AI 開示ブロックが無い可能性が高く（04afbcd が 10/8 に足した）、現行の translator と editor の開示規則と噛み合わない。corrections は全件か、翻訳時点の項目だけか（harness-scope の C8）。時点を揃える材料が無い項目の扱い。
4. corrections の渡し方。全文 / 修正後と Trigger / 要旨のみ。修正前の抜粋と著者の原文を含めるか。混入の機械検査を置くか（JP に無い数値・URL・C 番号・`drafts/` を EN から grep する案は、現在の EN 3 本が 0 件で基準線を持つ）。
5. 新版の置き方。別名の agent ファイル / `--agents` の JSON / branch。同名の旧版と並べたときの探索優先順位。
6. editor の dispatch 文面。固定テンプレートの中身（内部 5 の 4 点）と、JP 稿を渡すか。
7. 反転の数え方。自由文の指摘の同一性をどう判定するか。baseline の 3 回に出なかった過去の採用指摘（39 件）をどう扱うか（39 件は現行 translator の出力に対する指摘ではないので、baseline で再現する保証が無い）。editor のノイズをどう測るか（同一稿への複数回の dispatch は、3 回 × 2 版の設計に含まれない）。
8. 対象の指摘の範囲。全指摘の反転を一覧にするか、確度・帰属の類に絞るか（採用 39 件のうち、確実な K は 3、境界・不明が 3（1 件は E に数えた）、E が 26、S が 8）。全件を並べると、brief や corrections と無関係な言い回しの揺れが一覧の大半になりうる。
9. 「他の reviewer も出していたか」の列の情報源。EN 段で走らせる reviewer は editor だけなので、列を埋めるには replay で別の reviewer（`prose-clarity-reviewer` / Codex / `fact-checker` の類）を EN 稿に足すか、JP 段の panel の記録（JP 稿への指摘）で代えるか。
10. 規模と置き場。3 本 × 2 版 × 3 回 = translator 18 run + editor 18 run。記事を絞るか。出力は草稿として `drafts/`（gitignore）に置き、この種の公開 report に corrections の原文を写さない。

## Still unknown

- 翻訳時点の JP / brief の内容（`git show` / diff が取れていない）。特に harness-scope の b62de14 に AI 開示ブロックがあるか、brief が plan commit 後にどこまで変わったか。
- EN editor の原指摘の本文と箇所（処分記録は 1 行の要約）。translator の生の出力は残っていない。分類の「?」2 件（skill の「〜ほど」と "did not measure that"）は要約から決まらない。
- 当時の EN editor の dispatch 文面と、JP 稿の path が渡っていたか。
- `devto-translator.md` のどの行がどの commit で足されたか（reflog の subject からの推測に留まる）。
- `--agent` の main thread で、project の output style が system prompt の置換後も残るか。`--model` / `--tools` と frontmatter の優先順位。`--setting-sources` が `.claude/agents/` の探索に影響するか。`CLAUDE_CODE_SUBAGENT_MODEL` が main thread に効くか。いずれも docs に記述が無く、probe が要る。
- この環境の `claude --version`。
- `research-gate.sh` ほか user hooks が、translator / editor の `-p` 実行で書き込みや prompt に干渉するか。
- 同一の EN 稿に editor を複数回かけたときの指摘の一致率。
- `scripts/zenn_evidence.py` の個人 path・secret 検査を `articles-en/` に向けられるか。
- Lingo.dev の数値の一次確認（fetch 404）。確度・帰属の drift を対象にした翻訳の ablation の有無（見つからなかったことは、無いことの証明ではない）。
