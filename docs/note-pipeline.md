<!-- origin: shimo4228 -->
# note 日次配信

原文を保った無料転載を、著者が承認した順に 1 日 1 本、09:00 Asia/Tokyo に配信する。
実行体は `scripts/note_daily.sh`（launchd → `claude -p --chrome` → 実行 prompt
`scripts/note_daily_prompt.md`）。画面操作は
[.claude/skills/note-publishing/SKILL.md](../.claude/skills/note-publishing/SKILL.md)。
この文書は時刻・承認・キュー・再開・受入条件を所有し、投稿手順を複製しない。

## 素材と承認

候補は本文を読んで選ぶ。一般読者が自分の問題として読めること、原文で成立すること、
今も有効な内容であることを理由にし、note 既公開の記事を除外する。
最大 7 本のタイトル・順序・選定理由・tags・画像をまとめて提示し、承認を受ける。
表を含む記事は prepare が行ごとの箇条書きへ機械変換する（note は表を描画できない）。
変換結果は下書き段階の照合対象で、著者は candidates.md でその方針ごと承認する。

prepare の manifest は原文・HTML・タイトル・画像・tags・account の版を固定する。
素材の変更時は承認を取り直す。承認文字列は署名ではなく著者指示への参照であり、
実行エージェントが自分で承認を作ることを防ぐ境界はユーザー指示と実行環境の権限にある。

```sh
uv run --project scripts python scripts/note_publish.py approve .notes/note-publishing/SLUG/manifest.json --db .notes/note-publishing/queue.sqlite --evidence '実際に取得した著者承認への参照'
uv run --project scripts python scripts/note_publish.py status --db .notes/note-publishing/queue.sqlite
```

## 1 回の実行

`scripts/note_daily.sh run publish` が 1 回分。prompt は次を強制する。

1. ブラウザー preflight（shimo4228 でログイン済み）を台帳より先に確認。失敗なら claim しない。
2. status に claimed / publishing / uncertain があれば新規取得せず、その行の掲載状態を調べて
   `needs_human` で停止。
3. claim を 1 回。null なら `idle` で静かに終了。
4. 下書き → 読み戻し verify（body / links / headings / images 一致、structure 差は em / code のみ許容）。
5. publishing へ遷移してから公開。結果不明なら uncertain で停止し、公開ボタンを 2 度押さない。
6. API 照合後だけ published へ遷移。続けて note/ 転載 MD・corpus.yml・索引を同期（commit しない）。

結果は `.notes/note-publishing/runs/<timestamp>-<mode>/result.json`
（`outcome`: idle / blocked / needs_human / verify_failed / draft_ok / published）。
`run draft` は 4 まで実行して下書きを削除する rehearsal で、台帳を遷移させない。

取得は SQLite の transaction で排他し、取得日と公開日の双方で当日の次の記事を止める。
処理中の記事は日付が変わっても自動解放しない。未投稿日の埋め合わせ投稿は行わない。
自動再キュー機能はない。claimed で止まった記事は同じ記事の下書きから再開する。
ログイン切れ・素材変更・書式欠落・レート制限は停止して人間に残し、バースト再試行しない。

## 定期実行の配線と受入試験

```sh
scripts/note_daily.sh install     # ~/Library/LaunchAgents に 09:00 Asia/Tokyo の agent を生成・登録
scripts/note_daily.sh status      # launchd の状態と台帳
scripts/note_daily.sh uninstall
```

launchd は Mac がスリープ中の発火を次回 wake 時に 1 回だけ実行する。Chrome と
Claude in Chrome 拡張が接続できる状態（Chrome 起動済み、note ログイン済み）が前提で、
満たさない朝は preflight が `blocked` を返して終わる。1 回の実行は Claude の API 利用料が
かかる（2026-09-13 の read-only preflight 相当で約 2.4 USD、公開 1 本はその数倍の見込み）。

無人実行を有効化する前に次を満たす:

- Claude in Chrome の対話セッションで本物の記事 1 件を公開し、掲載結果を照合（2026-09-13 完了、
  domain-knowledge-travelers-vocabulary）。
- `scripts/note_daily.sh run draft` が `draft_ok` を返す（無人経路のツール・ブラウザー・
  ログイン・素材アクセスの実測。**未完了** — Claude Code セッション内からの起動は auto mode
  classifier が拒否するため、著者が端末から実行する）。
- 候補群の著者承認（2026-09-13 完了、4 本）と独立コード・セキュリティ・スキルレビュー。

テストは `uv run --project scripts pytest scripts/tests/test_note_publish.py`。
公開後の索引同期は note-publishing に従う。
