---
title: "Claude Code スキルが膨れ続けた 15 日間 — 3 回の棚卸しで学んだこと"
emoji: "🗃️"
type: "tech"
topics: ["claude", "ai", "claudecode", "開発環境"]
published: true
---

## はじめに

[Part 1](https://qiita.com/shimo4228/items/06d48f19bde5e6401a85) では ECC 環境で初めて本格開発を始めた 10 日間を、[Part 2](https://qiita.com/shimo4228/items/743f2b43f63b2bbe2dba) では pdf2anki の開発で踏んだ 6 つの落とし穴を書きました。

今回は、その裏で膨れ続けていた**スキル**の話をします。

ECC を導入して 15 日間で、スキルは 16 件から 48 件に増えました。learned スキル（Claude Code が開発セッションから自動抽出したパターン）だけで 40 件。6 プロジェクトを並行開発する中で、それらが全部グローバルの同じフォルダに混在していました。

Swift の DI パターン、Python の不変データクラス、Zenn の textlint 回避策。全部同じ `~/.claude/skills/learned/` へ。

棚卸しは 1 回では終わりませんでした。15 日間で 3 回やりました。そして 3 回目で、ようやく「スキル管理には終わりがない」と気づきました。

この記事では、スキルが増えすぎた経緯、3 回の棚卸しで何をしたか、そして continuous-learning-v2 の衝撃的な実態を書きます。

---

## スキルの仕組みを 3 分で

Claude Code のスキルは 3 段階で読み込まれます。

| 段階 | 読み込み内容 | コスト |
|------|------------|-------|
| Discovery | name + description のみ | 30〜50 tokens/件 |
| Activation | タスクに関連した SKILL.md 全文 | 数百〜数千 tokens |
| Deep refs | 参照ファイルを必要時に読み込み | 可変 |

重要なのは Discovery 段階の**Character Budget 制約**です。スキル一覧の表示に使える容量はコンテキストウィンドウの約 2%（約 16,000 文字）に制限されています。63 件のスキルのうち 42 件しか表示されなかった事例も報告されています（[GitHub #13099](https://github.com/anthropics/claude-code/issues/13099)）。

つまり、**スキルが多すぎると警告なしで切り捨てられます。** 増やせばいいというものではないのです。

配置場所は 3 つあります。

| 場所 | 用途 | 共有 |
|------|------|------|
| `~/.claude/skills/` | 全プロジェクト共通 | 不可 |
| `<project>/.claude/skills/` | プロジェクト固有 | git で共有可 |
| `~/.claude/skills/learned/` | セッションから自動抽出 | 不可 |

この「どこに置くか」が、後で大きな問題になります。

---

## ECC を入れた日（1/31）— 誤配置からすべてが始まった

2026 年 1 月 31 日、Everything Claude Code (ECC) を GitHub から ZIP でダウンロードし、手動で配置しました。

ここで重大なミスを犯しました。Part 1 でも書きましたが、`~/.claude/`（個人設定）に置くべきファイルを `MyAI_Lab/.claude/`（ワークスペース）に配置してしまったのです。

```text
MyAI_Lab/.claude/
├── rules/     ← 本来 ~/.claude/ に置くもの
├── skills/    ← 16 スキル + 23 レガシーコマンド
├── agents/    ← 本来 ~/.claude/ に置くもの
├── README.md  ← GitHub のファイルがそのまま
└── LICENSE    ← 同上
```

この誤配置のまま 8 日間、6 プロジェクトを並行開発しました。

| プロジェクト | スタック | コミット数 |
|-------------|---------|-----------|
| baki-quiz-app | Python/Streamlit | 4 |
| baki-quiz-ios | Swift/SwiftUI | 50+ |
| xmetrics-web | Next.js/Supabase | 15 |
| hanma-db-ios | Swift/SwiftUI | 2 |
| XMetricsTracker | Swift/SPM | 1 |
| pdf2anki | Python | 20 |

8 日間で 90 以上のコミット。その間、最初の learned スキルが生まれ始めました。

- `protocol-di-testing` — Swift の Protocol ベース DI パターン
- `immutable-model-updates` — Swift の不変モデル更新
- `swift-actor-persistence` — Actor ベースの状態管理

すべて `MyAI_Lab/.claude/skills/learned/` に混在。Swift のスキルも Python のスキルも同じ場所です。

---

## 再インストールとスキルの爆発（2/8〜2/9）

2 月 8 日、ようやく `~/.claude/` へ移行しました。

**移行でやったこと:**

1. `~/.claude/skills/` に ECC スキル 10 件を配置
2. `MyAI_Lab/.claude/` から rules/skills/agents を削除
3. 不要な GitHub 関連ファイル（README、LICENSE）を削除
4. 使わないコマンド 5 件を `~/.claude/commands-archive/` に退避

移行と同時に、pdf2anki の開発が加速しました。そして learned スキルが急増しました。

| 日付 | スキル | 起源 |
|------|--------|------|
| 2/8 | cost-aware-llm-pipeline | pdf2anki |
| 2/9 | long-document-llm-pipeline | pdf2anki |
| 2/9 | backward-compatible-frozen-extension | pdf2anki |
| 2/9 | ai-era-architecture-principles | 汎用 |
| 2/9 | root-cause-challenge-pattern | 汎用 |
| 2/9 | python-immutable-accumulator | 汎用 |
| 2/9 | skill-stocktaking-process | メタ（棚卸し手順そのもの） |

2 月 9 日時点で、learned ディレクトリには **14 ファイル**が存在していました。pdf2anki 固有のパイプラインパターンも、baki-quiz-ios の Swift パターンも、全部グローバルの `~/.claude/skills/learned/` に混在しています。

Swift プロジェクトを開くたびに pdf2anki の LLM パイプラインスキルが Discovery に表示される。Python プロジェクトでは Swift の Actor パターンが表示される。Character Budget を無駄に消費している状態です。

---

## 第 1 回棚卸し（2/10）— 3 層構造の誕生

**トリガー:** learned が 14 件に達し、「これはまずい」と感じた。

棚卸しのルールを決めました。

1. **そのスキルは 1 つのプロジェクトでしか使わないか？** → プロジェクトに移動
2. **複数プロジェクトで使うか？** → グローバルに残留
3. **ワンライナーで再導出できるか？** → 退役（削除）

結果、3 層構造が初めて確立されました。

| 層 | 件数 | 内容 |
|----|------|------|
| Global (`~/.claude/skills/learned/`) | 7 件 | 全プロジェクト共通パターン |
| pdf2anki (`.claude/skills/learned/`) | 10 件 | LLM パイプライン固有 |
| baki-quiz-ios (`.claude/skills/learned/`) | 5 件 | Swift/iOS 固有 |

**グローバルに残した 7 件:**

| スキル | なぜグローバルか |
|--------|----------------|
| ai-era-architecture-principles | 全プロジェクトに適用する設計原則 |
| root-cause-challenge-pattern | 機能追加の ROI 評価フレームワーク |
| python-immutable-accumulator | Python 全般で使う frozen dataclass パターン |
| python-module-to-package-refactor | リファクタリング時の patch target 更新 |
| skill-stocktaking-process | 棚卸し手順そのもの（メタスキル） |
| claude-code-tool-patterns | Write/Edit ツールの gotcha |
| tech-writing-patterns | Zenn/Qiita 投稿のトーン調整 |

### ECC 標準スキルの大規模無効化

ECC には Django、Spring Boot、Go、ClickHouse など多くの標準スキルが含まれています。使わないスキルも Discovery で Character Budget を消費します。

19 件の未使用スキルの SKILL.md 冒頭に `disable-model-invocation: true` を追記し、モデルからの呼び出しを無効化しました。

```yaml
# SKILL.md 冒頭に追加
disable-model-invocation: true
```

Django や Spring Boot を使わないのに、毎回 Discovery に表示されていた無駄がなくなりました。

---

## また増えた（2/11〜2/13）

棚卸しから 1 日後、もう増えていました。

2 月 11 日に小さな第 2 回棚卸しを実施しました。

| 操作 | スキル | 理由 |
|------|--------|------|
| 退役 | `pbpaste-secret-to-env` | ワンライナー trick、再導出容易 |
| 昇格 | `python-optional-dependencies` → global | pdf2anki 固有でない汎用パターン |
| 新規 | `mock-friendly-api-layering` | 公開 API からの内部パラメータ漏洩防止 |

結果: Global 7 → 9 件 / pdf2anki 10 → 9 件。

しかし同日だけで新規 learned スキルが **7 件**生成されました。翌日以降もスキルは増え続けます。

ECC の Wave 2 アップデート（2/12）で標準スキル 5 件が追加されました。zenn-content では `prh-hyphen-regex-escape` や `zenn-markdownlint-config` が learned として蓄積されていきました。

棚卸しても棚卸しても、開発を続ける限りスキルは増え続けます。

---

## continuous-learning-v2 の衝撃（2/14）

第 3 回棚卸しの前に、ECC の学習システムの実態を調べました。

ECC には 2 つの学習システムがあります。

**v1（continuous-learning）:** セッション終了時に Stop hook でパターンを抽出し、`learned/` にスキルファイルを生成する。`/learn` コマンドで明示的に実行もできます。

**v2（continuous-learning-v2）:** PreToolUse/PostToolUse hooks で全ツール呼び出しを記録する。observer が observations から instincts（本能）を抽出し、`/evolve` で instincts をスキルに昇華させる設計です。

v2 のほうが高度に見えます。調べてみました。

```bash
$ wc -l ~/.claude/homunculus/observations.jsonl
10557 observations.jsonl    # 6.5 MB の生ログ

$ ls ~/.claude/homunculus/instincts/personal/
（空）

$ ls ~/.claude/homunculus/instincts/inherited/
（空）

$ ls ~/.claude/homunculus/evolved/
（空）
```

**10,557 行のログが蓄積されているのに、instincts は 0 件。**

アーキテクチャを追いかけました。

```text
observe.sh (hooks)          ← 実装済み、動作中
    ↓ writes
observations.jsonl          ← 10,557 行蓄積
    ↓ ??? observer が読む
instincts/personal/         ← 空 ← ここが未実装
    ↓ /evolve がクラスタリング
evolved/                    ← 空
```

`observer.md` は「仕様書」であって「実行コード」ではありませんでした。observations から instincts へ変換する実行可能なコード（デーモン、cron、スクリプト）が**存在しません**。

`observe.sh` は `.observer.pid` に SIGUSR1 を送ろうとしますが、その pid を作るプロセスもない。`config.json` の `"observer": { "enabled": true }` を読んで何かを起動するコードもない。

**v2 は「記録だけして何も学んでいない」状態でした。**

設計図は優秀です。observations → instincts → evolved skills というパイプラインのアイデアは素晴らしい。しかし、中間の実装が抜けている。

一方、v1 の `/learn` は正常に動作しており、私の手元の learned スキル 40 件はすべて v1 が生成したものです。

**現時点での結論:** v2 が動く日まで、v1 でこまめに `/learn` を使うのが最も実用的な選択肢です。

---

## 第 3 回棚卸し（2/14）— 移動 9 件、統合 2 件

### 外部ツールを探した

棚卸しを手動でやるのは面倒です。自動化ツールがあるのではないかと調べました。

| ツール | 用途 | 結果 |
|--------|------|------|
| skill-audit (npm) | 品質・セキュリティ監査 | CLI 未登録で動作せず。未成熟 |
| CCPI | スキルマーケットプレイス | 整理後に検討 |
| OpenSkills | マルチエージェント対応 | 個人利用ではオーバーキル |
| CraftDesk | パッケージマネージャー | レジストリ開発中。時期尚早 |

**外部ツールはまだ成熟しておらず、手動棚卸しが最も確実。** これが 2026 年 2 月時点の現実です。

### ECC Wave 3 の即時無効化

同日、ECC Wave 3 で 14 件のスキルが追加されました。Django 4 件、Spring Boot 4 件、Java 2 件、Go 2 件、ClickHouse 1 件、project-guidelines-example 1 件。

**即座に全 14 件を無効化しました。** 使わないスキルは追加した瞬間に無効化する。これが第 1 回棚卸しからの学びです。

### 仕分けの実行

グローバルの learned は 17 件まで再膨張していました。仕分けルールは第 1 回と同じです。

**プロジェクトへの移動（9 件）:**

| スキル | 移動先 | 理由 |
|--------|--------|------|
| baki-ocr-text-normalization | baki-quiz-ios | 格闘技名鑑 OCR の正規化 regex |
| xcode-pbxproj-file-registration | baki-quiz-ios | Xcode 固有操作 |
| swift-codable-decode-diagnosis | baki-quiz-ios | Swift Codable 診断 |
| tech-writing-patterns | zenn-content | Zenn/Qiita トーン調整 |
| zenn-qiita-crosspost-workflow | zenn-content | クロスポスト手順 |
| zenn-markdownlint-config | zenn-content | Zenn 向け lint 設定 |
| zenn-context-driven-writing | zenn-content | 記事執筆プロセス |
| zenn-textlint-workarounds | zenn-content | textlint 誤検出回避 |
| prh-hyphen-regex-escape | zenn-content | prh のハイフン問題 |

**統合（親スキルに吸収、2 件）:**

| 吸収元 | 吸収先 | 理由 |
|--------|--------|------|
| mock-patch-target-migration | python-module-to-package-refactor | patch ターゲット更新はリファクタの一部 |
| llm-batch-json-key-normalization | parallel-subagent-batch-merge | キー正規化はバッチマージの品質検証ステップ |

「このスキルは独立した知識か、それとも別のスキルの一部か？」を問うことで、粒度を適正化しました。

---

## 15 日間の数値変遷

### learned スキルの推移

| 時点 | Global | pdf2anki | baki-quiz-ios | zenn-content | 合計 |
|------|--------|----------|-------------|-------------|------|
| 2/9（未整理） | 14 | — | — | — | 14 |
| 2/10 棚卸し後 | 7 | 10 | 5 | — | 22 |
| 2/11 棚卸し後 | 9 | 9 | 5 | — | 23 |
| 2/14 棚卸し前 | 17+ | 9 | 5 | — | 31+ |
| 2/14 棚卸し後 | 17 | 9 | 8 | 6 | 40 |

### ECC 標準スキルの推移

| 時点 | 有効 | 無効化 | イベント |
|------|------|--------|---------|
| 1/31 | 16 | 0 | 初期インストール |
| 2/8 | 10 | 0 | `~/.claude/` へ移行 |
| 2/10 | 10 | 19 | 第 1 回棚卸しで大規模無効化 |
| 2/12 | 15 | 19 | Wave 2 で 5 件追加 |
| 2/14 | 15 | 33 | Wave 3 で 14 件追加 → 即無効化 |

---

## 学んだこと

### 1. 棚卸しは「一度きり」ではなく「繰り返すもの」

15 日間で 3 回棚卸ししました。第 1 回で「これでスッキリした」と思った翌日には、もう新しいスキルが溜まり始めていました。

開発を続ける限りスキルは増えます。だから棚卸しも繰り返すものです。

**私のトリガー: 1 つの層で 10 件を超えたら棚卸し。** この閾値はプロジェクト規模で調整しますが、「何件になったらやる」と決めておくことが大事です。

### 2. スキルは「作る」より「置く場所」が大事

スキルの書き方やテンプレートの記事は多く見かけます。しかし、書いた後の配置場所で価値が変わります。

- Swift の Protocol パターンが Python プロジェクトの Discovery に表示されても邪魔なだけ
- Zenn の textlint 回避策がグローバルにあっても、他プロジェクトでは使わない
- 逆に、frozen dataclass パターンはどの Python プロジェクトでも使うからグローバルが正解

仕分けの判断基準はシンプルです。「このスキルは 1 つのプロジェクトでしか使わないか？」

Yes ならプロジェクトへ。No ならグローバルへ。迷ったらグローバルに置いて、次の棚卸しで見直す。

### 3. Character Budget の制約を意識する

スキルが増えすぎると、Discovery で切り捨てが発生します。せっかく作ったスキルが Claude から見えなくなる。

対策は 2 つ。使わないスキルを `disable-model-invocation: true` で無効化すること。そして、プロジェクト固有のスキルをグローバルに置かないこと。

どちらも「減らす」方向の施策です。スキルを増やすことよりも、不要なスキルが表示されないようにすることのほうが重要です。

### 4. 統合と退役を恐れない

2 件の統合（親スキルへの吸収）と 1 件の退役（`pbpaste-secret-to-env`）を実行しました。

退役の判断基準: **「ワンライナーで再導出できるか？」** Yes なら削除して問題ありません。必要になったらまた `/learn` で生成すればいい。

統合の判断基準: **「独立した知識か、それとも別のスキルの一部か？」** patch target の更新手順は、module-to-package リファクタリングの一ステップでしかありません。独立スキルにする必要はなかった。

### 5. v2 が動く日まで v1 でこまめに /learn

continuous-learning-v2 の instinct system は、設計としては素晴らしい。observations から自動的にパターンを抽出し、confidence scoring で精錬し、スキルに昇華させる。

しかし 2026 年 2 月時点では、中間の実装が存在しません。10,557 行のログを貯めても instincts は 0 件です。

v1 の `/learn` は確実に動きます。セッションの終わりに手動で実行するだけで、有用なパターンが learned スキルとして保存されます。私の 40 件の learned スキルはすべてこの方法で生まれました。

---

## おわりに

スキルを増やすのは簡単です。Claude Code と開発していれば、自然に溜まっていきます。

難しいのは管理です。どこに置くか。いつ整理するか。何を捨てるか。

15 日間で 3 回の棚卸しを経て到達した現在地を整理します。

| 場所 | learned | カスタム | ECC 標準 | 合計 |
|------|---------|---------|---------|------|
| Global | 17 | 3 | 15（有効）| 35 |
| pdf2anki | 9 | — | — | 9 |
| baki-quiz-ios | 8 | — | — | 8 |
| zenn-content | 6 | 5 | — | 11 |
| ECC（無効化済み） | — | — | 33 | — |

有効スキル合計: **約 63 件（うち 33 件無効化）。実質 48 件が稼働中。**

スキルの「数」に価値はありません。**適切な場所に、適切な粒度で、必要なスキルだけがある** ことに価値があります。

そしてこの状態は永続しません。次のプロジェクトを始めれば、また learned が増え、また棚卸しが必要になります。

棚卸しは終わらない。でも、それでいい。開発が続く限り、学びも続いているということだから。

---

## 参考リンク

### 公式ドキュメント

- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### ECC / continuous-learning

- [everything-claude-code (GitHub)](https://github.com/affaan-m/everything-claude-code)
- [humanplane/homunculus (GitHub)](https://github.com/humanplane/homunculus)

### 関連記事

- [everything-claude-code を読み解く](https://zenn.dev/ttks/articles/a54c7520f827be)
- [everything-claude-code の設計思想解説](https://zenn.dev/tmasuyama1114/articles/everything-claude-code-concepts)
- [Claude Code スキル機能完全ガイド](https://zenn.dev/ino_h/articles/2025-10-23-claude-code-skills-guide)
- [2026 年初頭の Claude Code Skills についてまとめる](https://zenn.dev/nanahiryu/articles/claude-code-skills-202601)
- [濫立する Claude Code の機能の使い分け](https://zenn.dev/notahotel/articles/a175aa95629d0b)

### シリーズ

- Part 1: [Everything Claude Code で初めて本格的な開発を始めた初心者の 10 日間](https://qiita.com/shimo4228/items/06d48f19bde5e6401a85)
- Part 2: [LLM の出力は信用するな — Claude API で PDF→Anki 自動生成 CLI を作って学んだ 6 つの防御策](https://qiita.com/shimo4228/items/743f2b43f63b2bbe2dba)
