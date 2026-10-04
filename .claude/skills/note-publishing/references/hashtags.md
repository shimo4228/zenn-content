# note ハッシュタグの現況

`note-publishing` の「ハッシュタグ」節が使う実測値。数値は日付が経つと古くなる。

- as-of: 2026-10-04 10:54〜10:58 JST（日曜の午前。時間帯による偏りは測っていない）
- valid-until: 2026-11-04。それより前でも、表のコンテストが締め切られた行（#AIとできたこと は 2026-10-18、#自動化したいこと は 2026-11-01）と、SKILL.md「ハッシュタグ」節末尾の失効条件に当たったときは無効にする
- 失効した「タグの現況」表は使わず、下の取得方法で記事ごとに語を測り直す。「自記事のタグ」表は失効せず、note を公開するたびに取得方法 4 で取り直して行を足す

## 取得方法

認証は要らない。間隔は 1.5 秒以上空ける。429 が返ったら、それ以上取らずに止めて著者へ報告する（rate limit は policy signal として扱う）。

```sh
TAG=ClaudeCode   # 日本語のタグは URL エンコードする（例: python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" 自動化したいこと）
D=.notes/note-publishing/hashtags; mkdir -p $D   # 応答はファイルに落としてから読む（curl を interpreter へ pipe すると PreToolUse hook が止める）

# 1. 転送先を見る。/tag/ ならキーワードページ、/contest/ ならコンテスト、404 ならまだ無いタグ
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' "https://note.com/hashtag/$TAG"

# 2. 記事数・関連タグ・開催中のコンテスト
sleep 2; curl -s "https://note.com/api/v2/hashtags/$TAG" -o $D/v2.json
python3 -c "import json;d=json.load(open('$D/v2.json'))['data'];print(d['count'],[h['name'] for h in d['relatedHashtags']],[(c.get('name'),c.get('openAt'),c.get('closeAt')) for c in d['relatedContests']])"

# 3. 新着 50 件の時間幅（新着欄に記事が残る時間の目安）
sleep 2; curl -s "https://note.com/api/v3/hashtags/$TAG/notes?order=new&page=1" -o $D/new.json
python3 -c "import json;from datetime import datetime as T;n=json.load(open('$D/new.json'))['data']['notes'];t=[T.fromisoformat(x['publish_at']) for x in n];print(len(n),'件',round((max(t)-min(t)).total_seconds()/60),'分')"

# 4. 自記事に付いたタグ（NOTE_ID は公開 URL の n で始まる id）
sleep 2; curl -s "https://note.com/api/v3/notes/$NOTE_ID" -o $D/note.json
python3 -c "import json;d=json.load(open('$D/note.json'))['data'];print(d['publish_at'][:10],' '.join(h['hashtag']['name'] for h in d['hashtag_notes']))"
```

`/hashtag/<tag>` が 307 を返すと、レスポンス本文にも転送先が埋め込まれる。キーの位置は、v2 が `data.count`・`data.relatedHashtags`・`data.relatedContests`、v3 が `data.notes[].publish_at`・`like_count` と `data.count`。

## タグの現況（2026-10-04）

記事数は `count`。取得方法 2 の v2 と v3 は #自動化したいこと 以外で一致し、表は v3 の値（食い違いは同じ行に併記）。新着の時間幅は、新着 50 件の最新から最古までの時間。

| タグ | 転送先 | 記事数 | 新着 50 件の時間幅 | 開催中のコンテスト |
|---|---|---|---|---|
| エッセイ | /tag/ | 2,786,781 | 15〜18 分 | - |
| AI | /tag/ | 981,324 | 24 分 | - |
| 生成AI | 未測定 | 581,182 | 26 分 | - |
| ChatGPT | 未測定 | 555,844 | 34〜38 分 | - |
| 哲学 | 未測定 | 288,519 | 2.7 時間 | - |
| AIとやってみた | 未測定 | 221,423 | 2.2 時間 | - |
| 思考 | 未測定 | 214,304 | 4.6 時間 | - |
| Claude | 未測定 | 142,311 | 74 分（49 件） | - |
| 業務効率化 | 未測定 | 124,165 | 84 分 | - |
| エンジニア | 未測定 | 117,757 | 9.9 時間 | - |
| プログラミング | 未測定 | 108,932 | 10.3 時間 | - |
| AIエージェント | 未測定 | 76,356 | 105 分 | - |
| ClaudeCode | /tag/ | 70,477 | 108 分 | - |
| 自動化 | 未測定 | 66,381 | 2.6 時間 | - |
| 書くこと | 未測定 | 56,469 | 17.4 時間 | - |
| LLM | 未測定 | 40,988 | 13.2 時間 | - |
| 文章術 | 未測定 | 34,223 | 11.6 時間 | - |
| AIとできたこと | 未測定 | 14,330 | 51 分 | Google Gemini×note、2026-09-18〜10-18 |
| 自動化したいこと | /contest/ | 912（v2 は 813） | 2.7 時間 | Manus×note、2026-10-02〜11-01（API の message 文には「5月22日まで」とあり、closeAt と食い違う） |

`/hashtag/AI` は 307 で `/tag/AI` へ転送された。まだ存在しない語（例: `観測計器の退役`）は 404 になる。

人気順は、取得元によって並びが違う。v3 の `order=popular` で取った #AI の 50 件は直近 1 日分だけだった（スキ中央値 49）。一方、`/tag/AI` の HTML に埋め込まれた 20 件は 7 月〜10 月の記事だった（中央値 801）。どちらの並びも定義は公開されていないので、人気欄に載るかどうかの見積もりには使わない。

## 自記事のタグ（2026-10-04、note API v3 `hashtag_notes`）

| slug | 公開 | tags |
|---|---|---|
| harness-scope-writing-harness | 2026-10-04 | #Claude #スキル #AIライティング #MOD #ハーネス #自動化したいこと #ClaudeMods |
| agi-judgment-trail | 2026-10-01 | #ClaudeCode #情熱 #AGI #不条理 #無意味 #ハーネスエンジニアリング |
| lost-referents-in-generated-prose | 2026-09-28 | #AI #ClaudeCode #AIライティング #ハーネス #AIスロップ #共通基盤 |
| agent-blackbox-capitalism-timescale | 2026-09-18 | #エージェント #AI倫理 #ブラックボックス #Scaffolding |
| agent-causal-traceability-org-adoption | 2026-09-17 | #AI #エージェント #事故 #自律エージェント #AIアカウンタビリティ |
| ai-agent-accountability-wall | 2026-09-15 | #責任 #エージェント #AIガバナンス #看板 #AIアカウンタビリティ |
| domain-knowledge-travelers-vocabulary | 2026-09-13 | #AI #キャリア #働き方 #AIエージェント #ドメイン知識 |
| ai-externalized-accountability-pollution | 2026-08-06 | （なし） |

2 本以上で使ったタグ: #AI（3 本）、#エージェント（3）、#AIアカウンタビリティ（2）、#ClaudeCode（2）、#AIライティング（2）、#ハーネス（2）。

似た語が別のタグとして並んでいる。#ハーネス と #ハーネスエンジニアリング、#エージェント と #AIエージェント。表記をそろえるかは著者が決める。

この表は、タグとインプレッションの関係を示さない。記事ごとの観測期間（公開から 0〜59 日）がそろっていないうえ、API はインプレッションの流入元を返さない。

## 公式と食い違う観測

ヘルプの上限は 10 個だが、他人の公開記事に 12 個（n6193cc3277b9）と 16 個（nfd66b7efdc42）のタグが付いていた。上限より前に付けたタグか、アプリ経由かなど、理由は確かめていない。提案は 10 個以内に収める。

## 二次資料（報告、未確認）

- 推奨個数は、実践者によって 3 個から 10 個まで割れている。2025〜2026 年の実践者記事に、個数やタグの有無を変えて PV を比べた定量検証は見つからなかった（2026-10-04 調査）
- 2026-09-08 の新しいダッシュボードのインプレッションには、ハッシュタグページでの表示も数えられているという報告がある（design-works.jp、2026-09-19）。ダッシュボードで流入元の内訳が見られるかは未確認
