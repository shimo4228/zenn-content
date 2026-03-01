---
title: "Claude Codeにシミュレータを渡したら自分でタップしてスクショで検証し始めた"
emoji: "📱"
type: "tech"
topics: ["claudecode", "ios", "xcode", "mcp"]
published: false
---

Claude Code がシミュレータ上のアプリをタップして、スクリーンショットで結果を確認して、バグがないか自分で検証する。SF ではない。XcodeBuildMCP という MCP サーバーを入れたら、実際にそうなった。

本記事では、既存の iOS アプリに新機能を追加し、Claude Code に **ビルド → テスト → アプリ起動 → UI操作 → スクリーンショット検証** までを一気通貫でやらせた実践記録を書く。

:::message
本記事の題材は便宜上「バキ検定アプリ」（刃牙シリーズの格闘技知識クイズ）としているが、実際の開発ドメインとは異なる。技術的な構造と数値はすべて実際の開発記録に基づいている。
<!-- textlint-disable -->
:::
<!-- textlint-enable -->

## XcodeBuildMCP とは

[XcodeBuildMCP](https://github.com/getsentry/XcodeBuildMCP) は、`xcodebuild` 等の CLI をラップして JSON 構造化レスポンスを返す MCP サーバーだ。元は Cameron Cooke 氏の個人プロジェクトだったが、**Sentry が買収**し、現在は getsentry 配下で開発されている。GitHub Stars は 4,000 を超えた。

特筆すべきは **59個のツール** を提供していること。Apple が Xcode 26.3 で公開したネイティブ MCP の 20 ツールと比べると、約 3 倍のカバー範囲だ。

そして最大の特徴は **Xcode プロセスが不要** なこと。`xcodebuild` コマンドを直接叩くため、ヘッドレスで動作する。Xcode を開かずにビルド・テスト・シミュレータ操作がすべて完結する。

### セットアップ

```bash
# Claude Code に MCP サーバーとして追加
claude mcp add XcodeBuildMCP -- npx -y xcodebuildmcp@latest mcp
```

または `~/.claude.json` に直接記述する。

```json
{
  "mcpServers": {
    "XcodeBuildMCP": {
      "command": "npx",
      "args": ["-y", "xcodebuildmcp@latest", "mcp"],
      "env": { "SENTRY_DISABLED": "true" }
    }
  }
}
```

UI 自動操作を有効化するには、プロジェクトルートに config を置く。

```yaml
# .xcodebuildmcp/config.yaml
schemaVersion: 1
enabledWorkflows:
  - simulator
  - ui-automation
sessionDefaults:
  scheme: "BakiQuiz"
  projectPath: "BakiQuiz.xcodeproj"
  simulatorName: "iPhone 16 Pro"
```

`sessionDefaults` を書いておくと、以降のツール呼び出しで毎回スキームやプロジェクトパスを渡す必要がなくなる。この 3 ステップで準備は終わる。

## Apple ネイティブ MCP vs XcodeBuildMCP

Xcode 26.3 で Apple 公式の MCP サーバーが使えるようになった。XcodeBuildMCP とどう違うのか。実際に両方使ってみた比較がこれだ。

| 領域 | Apple MCP（20ツール） | XcodeBuildMCP（59ツール） |
|-----|------|------|
| Xcode 依存 | **必要**（XPC 経由） | **不要**（スタンドアロン） |
| ビルド・テスト | 対応 | 対応 |
| シミュレータ管理 | 非対応 | **対応** |
| LLDB 統合 | 非対応 | **対応** |
| UI 自動操作（tap/swipe） | 非対応 | **対応** |
| ログキャプチャ | 非対応 | **対応** |
| ドキュメント検索 | **対応**（セマンティック） | 非対応 |
| Swift snippet 実行 | **対応** | 非対応 |
| SwiftUI Preview | **対応** | 非対応 |
| 実デバイスデプロイ | 非対応 | **対応** |

**補完関係**にある。Apple MCP は IDE 統合（ドキュメント検索、SwiftUI Preview）に強く、XcodeBuildMCP はヘッドレス操作（シミュレータ、UI 自動化、デバッグ）に強い。

Claude Code で使う場合、Apple MCP は以下のコマンドで接続できる。

```bash
claude mcp add --transport stdio xcode -s user -- xcrun mcpbridge
```

両方入れておいて、用途に応じて使い分けるのが現時点でのベストプラクティスだと感じた。

## 実践: 追い込みモードの自動検証

ここからが本題だ。バキ検定アプリに「追い込みモード（cram mode）」——忘れかけている問題を優先的に出題する機能——を Claude Code に実装させ、そのまま全自動で検証させた。自分はコードを 1 行も書いていない。

### Phase 1: セッション設定

まずプロジェクト情報を設定する。XcodeBuildMCP の `session_set_defaults` で、以降のツール呼び出しにプロジェクトパスやスキームを毎回渡す必要がなくなる。

```text
session_set_defaults(
  projectPath: "BakiQuiz.xcodeproj",
  scheme: "BakiQuiz",
  simulatorId: "2438BB91-...",
  bundleId: "dev.shimo4228.baki-quiz"
)
```

### Phase 2: ビルド + テスト

```text
build_sim → ✅ ビルド成功
test_sim  → ✅ 608件（605 passed, 3 skipped, 0 failed）
```

ビルドとテストは一撃で通った。追い込みモードの実装で追加した 418 行のテストコード（15 テストケース、3 スイート）も全パス。ここまでは通常の CI と変わらない。

### Phase 3: アプリ起動 + スクリーンショット

ここから XcodeBuildMCP の真価が出る。

```text
build_run_sim → アプリ起動
screenshot   → メイン画面キャプチャ
```

Claude Code がスクリーンショットを取得し、画面の内容を**自分で読み取って**検証する。「追い込み」セグメントが表示されていること、StatCard に 93 問と表示されていること、説明文が正しいことを、スクショの画像認識で確認した。

### Phase 4: UI 自動操作

これが最もインパクトのあるフェーズだった。ターミナルの向こうで Claude Code がアプリを操作し始めた瞬間、「これは CI ではない、もっと別の何かだ」と感じた。

```text
snapshot_ui                → UI 要素の accessibility ID と座標を取得
tap(label: "追い込み")      → セグメント切替
screenshot                 → 追い込みモード表示を確認
tap(label: "学習開始")      → セッション開始
screenshot                 → 問題画面（1/93）を確認
tap(id: "quiz_choice_D")   → 選択肢タップ
screenshot                 → 正解判定 + 解説表示を確認
tap(label: "次の問題へ")    → 次問題遷移
screenshot                 → 2/93 への遷移を確認
tap(id: "quiz_end_button") → セッション終了
screenshot                 → スタート画面復帰、復習対象カウント更新を確認
```

一連のフローを Claude Code が自律的に実行した。各ステップでスクリーンショットを撮り、期待通りの画面になっているかを**自分で判断**する。人間がシミュレータを手動で操作して目視確認する作業を、AI が代行している。

驚いたのは、Claude Code が `snapshot_ui` の結果を見て操作対象を自力で特定したことだ。このツールは画面上の全 UI 要素の accessibility ID、ラベル、座標を一覧で返す。Claude Code はその中から「追い込み」ラベルや `quiz_choice_D` という ID を見つけ、次にどこをタップすべきか自分で組み立てた。

`tap` は `label`（表示テキスト）でも `id`（accessibility ID）でも指定できる。最初は `label` で試していたが、途中から `id` に切り替えた方が安定することに気づいた。ラベルはローカライズで変わりうるが、ID は変わらない。

## 実機で修正点ゼロだった

追い込みモードは「追加の機能実装」であり、既存のコードベースとの整合性が求められる。XcodeBuildMCP での自動検証を通した後、実機にデプロイして手動で操作した。結果、**修正点は 1 つも見つからなかった。**

これがどれだけ大きいか、従来のワークフローと比較するとわかる。

このプロジェクトではこれまで、実装後の検証は自分が iPhone の実機で操作して確認するしかなかった。画面遷移のバグ、レイアウト崩れ、タップの反応——こうした問題を見つけるには、Xcode でビルドして実機に転送し、自分の目と指で確かめるしかない。この手動検証が、認知資源と時間をかなり食っていた。問題を見つけたら言語化して Claude Code に伝え、修正させて、また実機で確認する。このループが 2〜3 周回ることも珍しくなかった。

XcodeBuildMCP によって、**このループの大部分が自動化された。** Claude Code が操作し、自ら画面を確認するため、実機へ渡す前にほとんどの問題が潰される。今回「修正点ゼロ」だったのは、偶然ではなく仕組みの帰結だ。

### 従来の E2E テストとの違い

念のため補足すると、XcodeBuildMCP 以前にも E2E テストは存在していた。Claude Code が XCUITest ベースのテストコードを自作し、それを `xcodebuild test` で実行するという方式だ。

| 観点 | 従来の自作 E2E（XCUITest） | XcodeBuildMCP |
|------|---------------------------|---------------|
| テストシナリオ | **静的**（事前に書いたコード通り） | **動的**（AI が画面を見て判断） |
| 想定外の検出 | テストに書いていない問題は見逃す | スクショを見て異常に気づける |
| メンテナンスコスト | UI 変更のたびにテストコード修正 | accessibility ID があれば追従 |
| 検証の深さ | assert で合否判定 | 画像認識で視覚的な確認まで |
| 実行速度 | 速い（自動実行） | やや遅い（MCP 呼び出しのオーバーヘッド） |

従来の XCUITest は「書いたシナリオ通りに動くか」を検証する。XcodeBuildMCP は「画面が期待通りに見えるか」を AI が判断する。前者は回帰テストに強く、後者は探索的テストに強い。

実際のところ、両方使うのが正解だった。XCUITest で既知シナリオを高速に回帰テストし、XcodeBuildMCP で新機能を探索的に検証する。今回の追い込みモードでは、XCUITest の 15 ケースで基本動作を保証した上で、XcodeBuildMCP の UI 操作でユーザー体験全体を確認した。

## 追い込みモードの技術詳細

検証対象の「追い込みモード」自体の設計にも触れておく。540 行の実装を Claude Code が書き、418 行のテストも Claude Code が書いた。

### アーキテクチャ（MVVM + FSRS）

```text
StudyMode.cram
  → SessionManager.selectCramQuestions()
    → FSRSAlgorithm.cramPriority() で R 値算出
    → R 昇順ソート（忘れやすい順）
  → QuizViewModel.cramCount → UI 表示
```

FSRS（Free Spaced Repetition Scheduler）v5.0 の Retrievability 公式で、各問題の「忘れやすさ」を算出する。

```text
R = (1 + t/(9*S))^(-1)

t = 最終復習からの経過日数
S = Stability（記憶の安定度）
R = 0.0〜1.0（低いほど忘れている）
```

`R < 0.9` の問題を追い込み対象として抽出する。今回は 93 問がヒットした。

:::details cramPriority() と selectCramQuestions() の実装。

**cramPriority()**: 未学習の問題は `R = 0.0`（最優先）、学習済みは FSRS 公式で R 値を算出する。

```swift
public static func cramPriority(
    record: ProgressRecord,
    referenceDate: Date = Date()
) -> Double {
    guard let lastReviewed = record.lastReviewed else { return 0.0 }
    let elapsed = Calendar.current.dateComponents(
        [.day], from: lastReviewed, to: referenceDate
    )
    let t = max(0, Double(elapsed.day ?? 0))
    let stability = record.stability ?? max(1, Double(record.intervalDays))
    return retrievability(elapsedDays: t, stability: stability)
}
```

**selectCramQuestions()**: 学習済みの問題だけを R 昇順でソートする。「なんとなく古い順」ではなく、FSRS の数理的裏付けがある。

```swift
allQuestions
    .filter { progressMap[$0.questionId]?.lastReviewed != nil }
    .sorted { r1 < r2 }  // R 昇順（忘れやすい順）
```

<!-- textlint-disable -->
:::
<!-- textlint-enable -->

### 変更ファイル一覧

| ファイル | 追加行数 | 内容 |
|---------|---------|------|
| StudyMode.swift | +15 | `case cram` + displayName + validation |
| FSRSAlgorithm.swift | +24 | `cramPriority()` メソッド |
| SessionManager.swift | +30 | `selectCramQuestions()` + `cramCount()` |
| QuizViewModel.swift | +3 | `cramCount` プロパティ |
| QuizStartComponents.swift | +50 | UI（Picker、StatCard、説明文） |
| CramModeTests.swift | +418 | 15 テストケース（3 スイート） |
| **合計** | **+540** | — |

テストが全体の 77% を占めている。TDD で書いたため、実装よりテストの方が圧倒的に多い。

## Tips

### accessibility ID を先に設計する

XcodeBuildMCP の UI 操作は accessibility ID に依存する。`snapshot_ui` で取得できるが、ID が設定されていない要素はラベルや座標でタップするしかなく、不安定になる。

SwiftUI なら `.accessibilityIdentifier("quiz_choice_A")` を付けるだけだ。UI 実装と同時に ID を設計しておくと、XcodeBuildMCP による自動検証が格段に安定する。副産物として VoiceOver 等のアクセシビリティ対応も完了する。

### snapshot_ui を活用する

`snapshot_ui` は画面上の全 UI 要素を構造化データとして返す。Claude Code はこれを見て「追い込みセグメントの accessibility ID は `study_mode_picker` だ」と認識し、適切な操作を組み立てる。

手動で UI テストを書くときにも、まず `snapshot_ui` で画面構造を把握してから ID を特定する、という使い方ができる。

### ビルドエラー時の自動修正ループ

`build_sim` が失敗すると、Claude Code はエラーメッセージを読んでコードを修正し、再ビルドする。このループが XcodeBuildMCP のヘッドレス動作と相性が良い。Xcode を開いてエラーを確認して手動修正する、というサイクルが完全に不要になった。

## まとめ

今回の実践で、自分はコードを 1 行も書いていない。「追い込みモードを作ってくれ」と指示した。出来上がったものを Claude Code がシミュレータ上で操作し、検証するところまで見届けた。

XcodeBuildMCP を導入して実感したのは、**Claude Code の自律性が「ビルドが通る」から「UI が正しく動く」まで拡張された**ことだ。従来の AI コーディングは「コードを書いてビルドを通す」がゴールだった。59 のツール——特に `tap`、`screenshot`、`snapshot_ui`——によって、アプリを実際に操作して画面を見て正しく動いているか確認するところまで AI が担う。

Apple MCP（IDE 統合）と XcodeBuildMCP（ヘッドレス自動化）は補完関係にある。両方入れておけば、iOS 開発における AI エージェントの守備範囲はかなり広い。「Xcode を開かずに iOS アプリを検証する」という体験は、一度やると戻れなくなった。

## 参考

- [Apple Newsroom: Xcode 26.3 agentic coding](https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/)
- [Apple Developer: Giving external tools access to Xcode](https://developer.apple.com/documentation/xcode/giving-agentic-coding-tools-access-to-xcode)
- [Sentry Blog: Sentry acquires XcodeBuildMCP](https://blog.sentry.io/sentry-acquires-xcodebuildmcp/)
- [GitHub: getsentry/XcodeBuildMCP](https://github.com/getsentry/XcodeBuildMCP)
- [Blake Crosley: Two MCP Servers Turned Claude Code Into an iOS Build System](https://blakecrosley.com/blog/xcode-mcp-claude-code)
