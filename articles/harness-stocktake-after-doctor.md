---
title: "Claude Code の harness 棚卸し、192項目を1枚の report と2回の判断に"
emoji: "🧹"
type: "tech"
topics: ["claudecode", "claude", "agentskills", "harness"]
published: true
published_at: 2026-11-02 17:00
---

前に書いた skill が、もう無いスクリプトを呼んでいる。rule と skill が同じことを違う言い方で言っている。CLAUDE.md が、消した command の名前を挙げている。Claude Code の harness（skills、rules、agents、hooks、CLAUDE.md）は、放っておくとこうして衛生状態が悪くなります。どれも書いたときは正しかったものです。

私は harness を、持ち主の考えがエージェントを通して出てくる場所だと見ています。だからここが整理されていないのは、頭が整理されていないのに近いと思っています。

この記事は、その掃除をまとめて回す道具 harness-stocktake を公開した記録です。新しく考えた道具ではありません。この半年あまり、一つずつ磨いてきた棚卸しのパーツを、統合できると気づいた、という話です。

## パーツは一つずつ磨いてきた

最初のパーツは skill の棚卸し `skill-stocktake` でした。2026年2月に作って[記事にし](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey)、コミュニティの skill 集 [ECC（Everything Claude Code）](https://github.com/affaan-m/everything-claude-code)に PR を出してマージされました。その後、skills から rule を蒸留する `rules-distill` も ECC にマージされました。手元ではさらに足していき、パーツは7本になりました。skills を見る `skill-stocktake`、rules を見る `rules-stocktake`、rule の候補を探す `rules-distill`、agents を見る `agent-stocktake`、hooks を見る `hook-stocktake`、CLAUDE.md や README などの記述を実物に合わせる `context-sync`、repo の設定やスクリプトを見る `repo-asset-stocktake` です。

一つずつは良くなっていきました。けれど harness 全体は綺麗になりませんでした。パーツは別々に回り、それぞれが1件ずつ私に判断を聞いてきたからです。2026年10月31日、私はこう書いています。

> skill-stocktake が 1 個 1 個私に判断を聞く形だから、一括承認しづらい

1件ずつ聞くのは、中身を見ないまま一括で承認させないための設計でした。その設計を7本それぞれに写していたので、判断の回数はパーツの数と項目の数だけ増えていきました。

## 判定はパーツに、承認と適用は1か所に

統合のやり方は、仕事の分け方を変えることでした。7本のパーツは判定までを受け持ちます。判定は Keep（残す）、Improve（中身を良くする）、Update（古くなった参照を実物に合わせる）、Merge（まとめる）、Retire（退役させる）のどれかです。承認と適用は、harness-stocktake の1つの手順に渡します。

1. 7本が並列に判定し、結果を1枚の report にまとめる。項目ごとに、判定・対象のファイル・理由・具体的な変更を1行で書く
2. 私は report を読み、直したい行だけ書き換えて、1回で承認する
3. 承認した変更を作業用の branch に適用し、完了 report を出す
4. 私は完了 report を見て、main に取り込む

1件ずつ聞いていたのは、中身を見ない一括承認を防ぐためでした。1回の承認でそれを防ぐのは、回数ではなく report の書き方です。各行に、ファイルを開かずに判断できるだけの理由を書き、影響の大きい行（退役）から並べます。report の1行は、たとえばこうです。plugin の repo に置いたサンプルの harness（誰でも開いて確かめられます）から出た行を訳しました。

| 判定 | 対象 | 理由 |
|---|---|---|
| Retire（代案: Improve） | `.claude/hooks/check-secrets.sh` | `settings.json` の PostToolUse が Bash のたびにこのスクリプトを呼んでいるが、ファイルが repo に無い。毎回 hook のエラーになり、秘密の検査は行われていない |

1枚にまとめると、パーツをまたぐ衝突も見えるようになりました。ある skill を退役させると、別の rule からの参照が切れる、といった衝突です。

同じ日に、私自身の harness で初回を回しました。7本のパーツから192項目が出て、Keep 以外は74項目でした。私が判断したのは2回です。report の承認と、完了 report を見たあとの取り込みです。この記事で「片付いた」と言うのは、承認した変更が適用されて main に入ったところまでです。まだこの1回しか回していません。

## 公開されている harness 20本で回した

自分の harness だけでは、私の散らかし方の癖を見ているだけかもしれません。そこで、公開されている harness 20本を手元に clone して、読むだけのモード（`--dry-run`）で回しました。選び方は、GitHub の code search 1つ（`filename:SKILL.md path:.claude/skills`）で出た662 repo を乱数で並べ替え（seed は固定）、fork でなく、90日以内に更新があり、skill が5本以上あるものを先頭から20本です。持ち主には連絡していません。repo の名前も出しません。

docs（CLAUDE.md、README、設計判断の記録である ADR）、skills、repo の設定やスクリプトのそれぞれで、20本中19本に Keep 以外の判定が1件以上出ました。rules で出たのは20本中2本でした。

Keep 以外には退役や統合だけでなく、改善や更新の提案も入ります。判定したのも Claude で、持ち主の判断ではありません。だからこれは直す候補が出たという数で、直すべき汚れがあったと確かめた数ではありません。この20本は1つの検索から選んだもので、Claude Code の harness 全体を代表してもいません。回したのも公開前の版です。

## `/doctor` の後に回す

Claude Code には、使っていない plugin や skill と遅い hook を挙げる `/doctor`、古い指示や矛盾する指示を挙げる `/doctor prompt-audit`、skill ごとの常駐コストを測る `/skill-doctor` が入っています。harness-stocktake が見るのは、ファイルをまたいだ中身です。skill と矛盾する rule、スクリプトが消えた hook、コードと合わなくなった ADR、同じ仕事をする2つの agent です。

私の harness で両方を回して突き合わせると、どちらも相手が拾わないものを拾っていました。答えが割れた例もあります。10日間使っていない skill を、`/doctor` は off にするよう勧め、harness-stocktake は中身を見て残すと判定しました。使った頻度を見るか、中身を見るかで、答えが変わります。だから `/doctor` の代わりではなく、`/doctor` の後に回す道具として出しました。

## 試す

```bash
claude plugin install harness-stocktake --marketplace shimo4228/harness-stocktake
```

Claude Code を開いて `/harness-stocktake:harness-stocktake --dry-run` と打つと、`~/.claude` を読んで Markdown の report を1枚書きます。ファイルは何も変えません。repo の `.claude/` を見るときは `--project <repo のパス>` を足します。repo で月1回回すなら、[GitHub Action](https://github.com/marketplace/actions/harness-stocktake) もあります。

## 決めたこと、決めなかったこと

7本のパーツは1本の plugin にまとめ、repo で回し続けるための GitHub Action も出しました。公開 harness は手元で回し、持ち主には連絡せず、集計だけを出しました。使い方のデータを送る仕組み（telemetry）は入れていません。

私はエージェントの知識を育てる手順を6つの phase に分けて AKC（Agent Knowledge Cycle）と呼んでいて、harness-stocktake はそのうちの Curate（重複・古い項目・発火しない項目を見つける段）を回す形です。

決めていないこともあります。`/doctor` と比べたのは私の harness 1本だけで、公開20本では比べていません。判定が repo の実物と合っているかの照合も Claude 系のモデルが行っていて、持ち主の判断ではありません。plugin の形で配られている harness は、20本に入っていません。直したあとにエージェントの振る舞いが良くなったかも、まだ測っていません。

harness を綺麗に保つのは、自分の考えを整理し続けることに近いと思っています。私が変えたのは、その整理を1件ずつの判断から、1枚の report と2回の判断にしたことです。

## 関連リンク

- [harness-stocktake（GitHub）](https://github.com/shimo4228/harness-stocktake) — plugin の本体。サンプルの harness と、そこから出た report があります
- [harness-stocktake-action（GitHub Marketplace）](https://github.com/marketplace/actions/harness-stocktake) — repo で月1回回すための GitHub Action
- [AI の苦手な仕事をスクリプトに逃がす — スキル棚卸しコマンドの設計・実装・公開の全記録](https://zenn.dev/shimo4228/articles/skill-stocktake-design-journey) — 最初のパーツ skill-stocktake の記録
- [個人スキルを5万人に届ける最短経路が見つかった](https://zenn.dev/shimo4228/articles/ecc-marketplace-contribution) — ECC に PR を出したときの記録
- [Agent Knowledge Cycle（DOI）](https://doi.org/10.5281/zenodo.19200726) — Curate を含む6つの phase
- [この記事のMarkdown正本（GitHub）](https://github.com/shimo4228/zenn-content/blob/main/articles/harness-stocktake-after-doctor.md) — 全記事のMarkdownと索引（docs/PUBLICATIONS.md）は同じリポジトリにあります
- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧

---

**この記事の書き方**: 本文は Claude（Claude Code）が書きました。素材は、私の harness の棚卸しの記録、公開 harness 20本を手元で回した集計、過去の記事、私との対話です。harness を考えの出口と見ること、磨いたパーツを統合したという筋、本文に載せる数字を192項目と2回の判断に絞ることは、私が決めました。公開前に私が全文を読み、内容の責任は私が負います。
