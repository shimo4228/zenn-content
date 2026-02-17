# ショート記事 修正プラン

作成日: 2026-02-18
元データ: セッション `cdd81ba8` の辛口editorレビュー結果

## サマリー

| # | slug | CRITICAL | MEDIUM | MINOR | 推定工数 |
|---|------|:--------:|:------:|:-----:|:--------:|
| B1 | `claudemd-hierarchy` | 3 | 4 | 3 | 中 |
| B2 | `zenn-lint-hooks` | 2 | 3 | 3 | 小 |
| A2 | `crosspost-cli` | 2 | 5 | 4 | 中 |
| B3 | `prh-nodejs20-regex` | 2 | 3 | 3 | 小 |
| A3 | `japanese-mcp` | 2 | 4 | 4 | 中 |
| C1 | `skill-cleanup` | 2 | 4 | 3 | 中 |
| C2 | `zed-setup` | 3 | 4 | 3 | 中（要検証） |
| C3 | `multi-llm` | 2 | 4 | 2 | 小 |
| D1 | `context-audit` | 3 | 4 | 5 | 中 |

### 全記事共通の修正パターン

1. **導入フック追加** — 全記事で冒頭に具体的な場面・失敗談を1〜2文追加
2. **まとめセクション追強化** — 箇条書き繰り返しではなく「何が変わったか」「次のステップ」を追加
3. **published: false → true** — 修正完了後に変更

---

## B1: `claude-code-claudemd-hierarchy`

### CRITICAL

**C1. `~/.claude/CLAUDE.md` のパスが不正確**
- 記事: `~/.claude/CLAUDE.md ← ユーザーレベル`
- 実態: このファイルは著者環境に存在しない。正しいユーザーレベルは `~/CLAUDE.md`
- 対応: Claude Code 公式ドキュメントで正確なパスを確認し修正

**C2. `~/.claude/` のダイアグラムから `skills/` が欠落**
- 記事のダイアグラム: `rules/`, `agents/`, `commands/`, `settings.json` のみ
- 実態: `~/.claude/skills/` が実在
- 対応: ダイアグラムに `skills/` を追加

**C3. additive vs override の説明が不正確**
- 記事: 「読み込み順序は下位が優先です。同名ファイルがあれば上書き」
- 実態: `settings.json` のキーは下位優先だが、`rules/`・`agents/` は全レベル合算（additive）
- 対応: 「設定値はマージされ同じキーは下位が優先。rules/agents は全レベルの内容が合算されて読み込まれます」に修正

### MEDIUM

- M1. 親ディレクトリの CLAUDE.md 走査動作が未記載 → 1文追加
- M2. zenn-content の `.claude/skills/` 実際の中身と記事の列挙が不一致 → 「主なものを抜粋」と注記
- M3. "Everything Claude Code (ECC)" の定義がない → 1文説明追加
- M4. 「ハマった話」の payoff が薄い → 結論で具体的な失敗→修正の体験を1段落追加

### MINOR

- 判断テーブルのカラム幅統一
- 「6プロジェクト」の内容を1文で補足
- `settings.local.json` と `settings.json` の混同を修正

---

## B2: `claude-code-zenn-lint-hooks`

### CRITICAL

**C1. `npm run lint:all` が未定義**
- 「動作確認」セクションで使用されるが `package.json` に定義なし
- 対応: `package.json` に `lint:all` スクリプトを追加するか、直接コマンドに書き換え

**C2. prh の「OK」サンプルが不適切**
- `Claude-Native` の表記ゆれとして `Claude based` / `claude native` は意味不成立
- 対応: `JavaScript` / `javascript` や `Github` / `github` の例に差し替え

### MEDIUM

- M1. MD060 の無効化理由が未説明 → Zenn の `:::message` との相性を1行追加
- M2. 結論セクションなし → 「この設定で変わったこと」「残課題」を追加
- M3. `no-dead-link` の pre-commit hook でのトレードオフ未記載 → オフライン時の対処を追加

### MINOR

- 冒頭の問題提起を強化（動機を先に）
- `filters.comments` の具体例追加
- husky v9 依存の注記

---

## A2: `claude-code-crosspost-cli`

### CRITICAL

**C1. コード例と実装の乖離**
- 記事のコードからエラーハンドリングが省略されているが明示なし
- 対応: 省略コメント `# ... error handling omitted` を追加、または実装に合わせて修正

**C2. `GITHUB_RAW_BASE` のユーザー名問題**
- スクリプト内に `shimo4228` がハードコード。記事のセットアップに変更手順の記載なし
- 対応: セットアップセクションに「自分のリポジトリ名に変更が必要」と明記

### MEDIUM

- M1. 導入フックなし → 具体的な「手動コピペで崩れた体験」から入る
- M2. セットアップ手順不完全 → `python-dotenv` 不使用の意図を説明
- M3. 英語記事ガードの挙動が「警告」と書いているが実際は「エラーで停止」 → 修正
- M4. Hashnode の `--update auto` 非対応を明記
- M5. `--canonical-url` の SEO 的意味を1行追加

### MINOR

- Dev.to の `--update auto` 対応を追記
- `per_page: 20` × 5ページ = 100件上限の注記
- `scripts/publish.py:行番号` の参照追加
- 結論セクション追加

---

## B3: `prh-nodejs20-regex-error`

### CRITICAL

**C1. `patterns` の説明が技術的に誤り**
- 記事: 「`patterns` は正規表現ではなく文字列の完全一致です。ハイフンを含むパターンの検出には使えません」
- 正確: `patterns` はリテラル文字列（内部で正規表現に変換）。ハイフン含む文字列もそのまま書ける
- 対応: 修正文「`patterns` はリテラル文字列として指定します（`\-` のような手動エスケープは不要）。`Claude-Native` のようにハイフンを含む文字列もそのまま書けます」

**C2. 方法2のサーバー例がハイフン問題と無関係**
- `サーバー` / `サーバ` は長音符の問題でありハイフンとは無関係
- 対応: ハイフン問題に直結した例（例: `/Claude.Native/`）に差し替え

### MEDIUM

- M1. 導入フックなし → 「Node.js 20 にアップグレードしたとき prh.yml が突然クラッシュ」の1文追加
- M2. 「まとめ」が再掲のみ → 「確認方法」「移行チェックリスト」形式に
- M3. `v` フラグの説明が不正確（「デフォルトで有効になった」は誤解を招く） → V8 バージョン関連の正確な説明に修正

### MINOR

- `patterns` 例に `Claude-Native` のリテラル検出を追加
- `articles/test.md` → プレースホルダーに変更
- prh のバージョン明記

---

## A3: `claude-code-japanese-mcp`

### CRITICAL

**C1. `~/.claude.json` の上書きリスク警告なし**
- 記事: 「`~/.claude.json` に以下を追加します」+ JSON スニペット
- 問題: `~/.claude.json` はシステム管理ファイル。上書きすると環境破壊
- 対応: 「`~/.claude.json` はClaude Codeが自動管理するファイルです。上書きせず、既存の `mcpServers` オブジェクトにキーを追加してください」と警告追加

**C2. 結論セクションなし**
- tips セクションで唐突に終了
- 対応: まとめ + 次のステップを追加

### MEDIUM

- M1. サンプル出力が架空であることを明示 → 「※ 出力例はイメージです」注記
- M2. ファイルパス系ツール vs インラインテキスト系ツールの区別が不明確 → API surface を整理
- M3. GitHub 直接インストールのセキュリティリスク未開示 → npm audit 不可、バージョン固定の注意
- M4. kuromoji 辞書の初回ロード時間の実態 → 「数秒かかります」は過小評価、実体験を共有

### MINOR

- 「やりたいこと」の書き出しを具体的な失敗から入る
- 「語彙多様性: 0.72」の指標を説明
- GitHub リポジトリへの直リンク追加
- 「できないこと」セクション追加検討

---

## C1: `claude-code-skill-cleanup`

### CRITICAL

**C1. `mv` コマンドに `.md` 拡張子がない**
- learned skills はフラットな `.md` ファイルだがディレクトリとして扱っている
- 対応: 全 `mv` コマンドに `.md` を追加

**C2. `disable-model-invocation: true` のコード例が曖昧**
- YAML frontmatter の `---` 内に配置する必要があるが、記事では裸で表示
- 対応: frontmatter 全体を含むコード例に修正

### MEDIUM

- M1. "ECC標準スキル" が未定義 → 「Claude Code 拡張スキルセット」に言い換え
- M2. 導入フックなし → 「learned skills が増え続ける問題」の背景を1〜2文追加
- M3. "Character Budget" が初出で未説明 → 括弧書きで説明追加
- M4. `~/.claude/skills-archive/` は存在しないパス → `mkdir -p` を追加

### MINOR

- 構成例ツリーの learned skills を `.md` ファイルに修正
- `/learn` の再生成は確率的（50-80%）→ 表現を調整
- 棚卸し後の実際の件数を追記

---

## C2: `claude-code-zed-setup`

### CRITICAL（要検証あり）

**C1. 導入パラグラフなし（H2 から始まる）**
- 対応: frontmatter 直後に2〜3行の導入文追加

**C2. `assistant.enabled: false` の設定キー要検証**
- Zed の設定スキーマは頻繁に変更される
- 対応: 現行バージョンで動作確認必須。Zed 公式ドキュメントと照合

**C3. `/learn` コマンドの存在確認**
- 対応: 実在確認済みなら残す。未確認なら削除して確実なコマンドのみ列挙

### MEDIUM

- M1. 「コンテキスト消費量表示」の位置・表示内容を正確に → スクショか詳細説明
- M2. 結論セクション欠落 → まとめ + 体験談 + 次のステップ追加
- M3. 「レイアウト」セクションへの導線不足 → 橋渡し1文追加
- M4. タイトルの「最適設定」が大言 → 「軽量化する設定」等に変更検討

### MINOR

- 「余計なバックグラウンド処理がありません」→ 具体的に
- Swift 言及が唐突 → 著者のユースケースと明示
- `inline_completion_provider: "none"` の説明追加

---

## C3: `claude-code-multi-llm`

### CRITICAL

**C1. 「Claude Code は教育的説明が苦手」の断言に根拠なし**
- 「こともあります」と留保→直後で断言。論理矛盾
- 対応: 「開発タスクのコンテキストで動作しているため、概念の丁寧な解説を求めると回答が簡潔すぎることがありました」（個人体験として表現）

**C2. 比較表の「得意なこと」が根拠不明**
- 対応: 「筆者の個人的な使い分け（2026年2月時点）」と明記、または列名を「私がこの目的で使う理由」に変更

### MEDIUM

- M1. 導入フックなし → 具体的な失敗場面から入る（ADR の例など）
- M2. 結論が繰り返し → 「この方法で何が変わったか」の体験追加
- M3. NotebookLM の「矛盾点を整理」の具体例なし → 実例追加
- M4. 第3段階の「Claude:」が何を指すか不明 → サービス名を明示

### MINOR

- 「4つの LLM を使い分ける4段階」→ 第3段階は「聞き方を変える段階」であり LLM の使い分けではない。整合性を修正
- グラップラー刃牙の TDD 例え → 技術的に曖昧。より正確な例えに

---

## D1: `claude-code-context-audit`

### CRITICAL

**C1. 実プロジェクト名の露出判断**
- `g-kentei-ios`, `gai-passport-ios`, `xmetrics-web` 等が記載
- 対応: 意図的な公開か判断。匿名化するなら `project-a`, `project-b` 等に

**C2. `~/.claude/projects/` のパス構造説明が不正確**
- 記事: `{hash}` と表現
- 実態: パスエンコーディング（`-Users-shimomoto-tatsuya-MyAI-Lab-...`）
- 対応: 説明を修正、`memory/` はセッション後に自動生成される旨を追記

**C3. common/ のファイル数が9ではなく10**
- `planning.md` と `documentation.md` が漏れ
- 対応: ファイル数・バイト数を再計測して修正

### MEDIUM

- M1. トークン変換レートの根拠未記載 → 「1 token ≈ 3–4 bytes」の注釈追加
- M2. 「約1.4%」のフレーミング → 短いセッションでは割合が高い点を補足
- M3. 「自動的に生成」は不正確 → 「リクエストすれば生成してくれます」に修正
- M4. CLAUDE.md + rules 併用は技術的には可能 → 「技術的には併用可能だが管理コスト増」と補足

### MINOR

- 導入フックを Section 5 の発見（起動場所で memory が変わる）から始める
- 「65〜89行程度」の根拠を追記
- MEMORY.md 存在テーブルに「なぜ有るか」のヒントを追加
- 「ゴッチャ」→「落とし穴」に統一
- bash コメントの memory 蓄積先パスを正確に

---

## 修正の進め方（推奨）

### Phase 1: 軽量修正（CRITICAL のみ）
全記事の CRITICAL を一括修正。事実誤認・セキュリティ問題を解消。

### Phase 2: 構造改善（共通パターン）
全記事に導入フック + まとめセクションを追加。

### Phase 3: 個別 MEDIUM 対応
記事ごとの MEDIUM を優先度順に対応。

### Phase 4: Lint + 最終確認
`npm run lint` → editor 再レビュー → `published: true`
