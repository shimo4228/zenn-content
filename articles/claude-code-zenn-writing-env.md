---
title: "Claude Codeで育てたZenn執筆環境 ── lint28件からエージェントレビューまで"
emoji: "🛠️"
type: "tech"
topics: ["claudecode", "zenn", "textlint", "python"]
published: true
---

Claude Code で Zenn の記事を書いています。自分の役割は方向性を決めて、書き上がった記事を全文読んでファクトチェックや指摘を入れることです。修正作業そのものは Claude Code がやります。

この体制で約2週間やってみて気づいたのは、問題が起きるたびに「二度と繰り返さないよう仕組み化する」サイクルが自然と回ることでした。口頭の指示はスキルへ、手動の作業はスクリプトへ、踏んだ地雷は learned スキルへ。すべてが再利用可能な形で環境に残ります。

この記事では、実際に遭遇した問題と、それぞれが何に仕組み化されたかを記録します。

## まずトーンをスキル化した

記事を書き始める前に、最初にやったのはトーンの定義でした。「技術的だけどくだけすぎない」「AI スロップ禁止」「失敗談も正直に書く」――こういった語調の指示を細かく出し、Claude Code の `zenn-writer` スキルとして保存しました。

スキル化する前は、セッションが変わるたびに「です・ます調で」「AI スロップ禁止」と繰り返す必要がありました。スキルにしておけば、次の記事から指示なしで同じトーンが維持されます。口頭の指示は忘れますが、スキルファイルは消えません。これが仕組み化の起点になりました。

## 28件の lint エラー → pre-commit hook

記事を3本書いたあと、まとめて lint を回したら28件のエラーが出ました。全角スペース混入、見出しレベルの飛び、表記ゆれ。1つずつ指摘するのは非効率なので、Claude Code に「コミット前に自動で止める仕組みがほしい」と伝えました。

husky + lint-staged で pre-commit hook を組んでくれました。

```text
package.json             ← lint-staged の設定
.husky/pre-commit        ← husky の hook（npx lint-staged を実行）
.textlintrc.json         ← textlint ルール
.markdownlint-cli2.jsonc ← markdownlint ルール
prh.yml                  ← 表記ゆれ辞書
```

textlint は `preset-ja-technical-writing` をベースに、`no-dead-link`（リンク切れ検出）と `prh`（表記ゆれ）を追加。markdownlint は Zenn 固有のルールを無効化しています。

```jsonc
// .markdownlint-cli2.jsonc — Zenn 向けの無効化
{
  "config": {
    "MD013": false,  // 日本語は1行が長くなる
    "MD025": false,  // Zenn はフロントマターが H1 相当
    "MD041": false,  // 先頭行はフロントマター
    "MD060": false   // :::message を誤検知する
  }
}
```

ここでハマりポイントがありました。最初 Claude Code が `.markdownlint-cli2.jsonc` に `"globs": ["articles/**/*.md"]` を入れました。しかし lint-staged 経由だと config 側の globs がファイル指定を上書きし、**全ファイルが lint されます**。この挙動を伝えたら、globs を削除して lint-staged 側で制御する形に直してくれました。

```json
// package.json — lint-staged でファイルを絞る
{
  "lint-staged": {
    "articles/**/*.md": ["textlint", "markdownlint-cli2"],
    "books/**/*.md": ["textlint", "markdownlint-cli2"]
  }
}
```

**仕組み化の結果**: 28件のエラーは pre-commit hook になりました。そしてこの globs の落とし穴は `learned/zenn-markdownlint-config` スキルとして自動抽出され、Claude Code が同じミスを繰り返さなくなりました。

## Node.js 20 のクラッシュ → learned スキル

コードを一切変えていないのに、textlint がクラッシュしました。

```text
SyntaxError: Invalid regular expression: /Claude\-first/gmu: Invalid escape
```

原因は Node.js 20 の Unicode mode（`u` flag）でした。prh は内部で正規表現に `gmu` フラグを自動付加します。`u` フラグ下ではキャラクタークラス外の `\-` が無効なエスケープとして扱われるため、`prh.yml` にハイフン入りパターンがあると即クラッシュします。

Claude Code にエラーログを見せたら、すぐに原因を特定してくれました。

```yaml
# NG: Node.js 20+ でクラッシュ
- expected: Claude-Native
  pattern: /Claude\-Native/

# OK: patterns（リテラル文字列）なら安全
- expected: Claude-Native
  patterns:
    - claude native
    - Claude based
```

Claude Code が prh.yml 全体をスキャンして、ハイフン含みの pattern をすべて patterns に書き換えてくれました。

**仕組み化の結果**: この回避策は `learned/prh-hyphen-regex-escape` スキルとして自動抽出されました。以降、Claude Code が prh.yml を編集するときは、ハイフンを含む pattern を自動で避けます。ランタイムのバージョン起因のクラッシュという再現条件が分かりにくい問題ほど、スキルとして残す価値があります。

## 嘘の文字数 → MCP サーバー

Zenn 記事は2,000〜4,000字あたりが読みやすいとされています。執筆中に Claude Code へ「この記事は何文字？」と聞いたら「約2,800文字です」と返ってきました。実際に数えたら3,200文字。400字もずれています。

LLM は日本語のトークン境界を正確に扱えません。英語なら空白で区切れますが、日本語はスペースで区切られないため、推測ベースの回答になります。

Claude Code に「正確に数える方法がほしい」と言ったら、MCP サーバーとして kuromoji.js ベースの日本語テキスト分析ツールを提案してきました。`~/.claude.json` に設定を追加するだけで接続できます。

```json
{
  "mcpServers": {
    "JapaneseTextAnalyzer": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "github:Mistizz/mcp-JapaneseTextAnalyzer"]
    }
  }
}
```

```text
me: この記事の文字数を確認して
Claude Code: [JapaneseTextAnalyzer.count_chars を実行]
→ 3,201文字（改行・スペース除外）
```

**仕組み化の結果**: `~/.claude.json`（グローバル設定）に置いたので、全プロジェクトで使えます。LLM の推測に頼らず、辞書ベースの正確な値が返ります。「LLM が苦手なことは外部ツールに任せる」という判断自体が、MCP サーバーという仕組みになりました。

## クロスポスト → Python スクリプト

記事が何本か溜まってきた頃、「Qiita にもクロスポストしたい」と Claude Code に伝えました。すると「Zenn の `:::message` や `:::details` は Qiita では表示されません。記法変換が必要です」と先に指摘してきました。

そのまま変換スクリプトを作ってもらい、`scripts/publish.py` ができあがりました。

変換ルールは3つです。

- `:::message` → blockquote（`>` 記法）
- `:::details タイトル` → HTML の `<details>` タグ
- `/images/` → GitHub raw URL

```bash
# Qiita に新規投稿
python scripts/publish.py articles/my-article.md --platform qiita

# 既存記事を更新（タイトルで自動検索）
python scripts/publish.py articles/my-article.md --platform qiita --update auto
```

`--update auto` はタイトルの完全一致で既存記事を検索して更新します。Zenn 側を直したら Qiita も追従、というワークフローが1コマンドで完結します。

その後、Dev.to と Hashnode にも対応を広げました。日本語記事を英語圏プラットフォームに誤投稿しないよう、英訳ファイルの有無をチェックする `--force` ガードも追加しています。

**仕組み化の結果**: 手動コピペの記法崩れリスクが `publish.py` というスクリプトに置き換わりました。クロスポストの手順全体は `learned/zenn-qiita-crosspost-workflow` として自動抽出され、Claude Code がクロスポストを提案する際の手順書になっています。

## 辛口エディターで公開前レビュー → エージェント

仕組みが揃ってくると、次に気になったのは記事そのものの品質でした。lint は表記ルールを機械的にチェックしてくれますが、「この説明は読者に伝わるか」「AI スロップが紛れていないか」「技術的に不正確な箇所はないか」は判定できません。

そこで Claude Code のエージェント機能を使い、`.claude/agents/editor.md` に辛口の編集者エージェントを定義しました。レビュー観点は6つです。

1. **技術的正確性** — コードスニペットが実行可能か、説明に嘘がないか
2. **コードの品質** — import 漏れ、構文エラー、不要な情報がないか
3. **ストーリーの流れ** — 冒頭のフック、動機づけ、論理展開、結論の整合性
4. **用語の一貫性** — プロジェクト固有の表記ルールに従っているか
5. **AI スロップ検出** — 「powerful tool」「seamless」のような空虚なフレーズがないか
6. **読者層の適切さ** — 説明の過不足、前提知識のレベル

評価は4段階（EXCELLENT / GOOD / NEEDS REVISION / MAJOR ISSUES）で、指摘は CRITICAL / MEDIUM / MINOR に分類されます。この記事自体もこのエディターのレビューを通しています。

**仕組み化の結果**: 「記事の品質が気になる」という漠然とした不安が、再現可能なレビュープロセスになりました。エージェント定義ファイルとして残るので、レビュー観点がセッションをまたいで維持されます。

## 仕組み化のサイクル

環境の全体像を整理します。

```text
記事を書く（zenn-writer スキルがトーンを維持）
  → git commit → pre-commit hook が lint を自動実行
  → 「何文字？」→ MCP サーバーが正確にカウント
  → editor エージェントが品質レビュー
  → publish.py → 記法変換して Qiita/Dev.to に投稿
```

各問題とその仕組み化先の一覧です。

| 問題 | 仕組み化先 | 種類 |
|------|-----------|------|
| トーンが毎回ぶれる | `zenn-writer` | スキル |
| lint エラー28件 | pre-commit hook | 設定 |
| markdownlint globs の罠 | `learned/zenn-markdownlint-config` | learned スキル |
| prh × Node.js 20 クラッシュ | `learned/prh-hyphen-regex-escape` | learned スキル |
| LLM の嘘文字数 | JapaneseTextAnalyzer MCP | 外部ツール接続 |
| 記事品質の属人的チェック | `editor` エージェント | エージェント |
| クロスポストの記法崩れ | `scripts/publish.py` | スクリプト |
| クロスポスト手順 | `learned/zenn-qiita-crosspost-workflow` | learned スキル |

どれも最初から計画して作ったわけではありません。記事を書く中で問題にぶつかり、Claude Code と一緒に解決し、その知見がスキルやスクリプトとして環境に残ります。問題が起きるたびに環境が少し賢くなる。これが Claude Code で執筆環境を「育てる」ということでした。
