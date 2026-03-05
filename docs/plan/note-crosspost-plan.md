# note.com クロスポスト実装計画

## Context

Zenn 記事を Qiita/Dev.to/Hashnode にクロスポストする仕組み（`scripts/publish.py`）を運用中。
コンテンツの性格が「技術 HowTo」より「AI 実験エッセイ」に近いと認識し、note.com への展開を決定。
note.com は公式 API がないため、**Playwright ブラウザ自動化** + **ドラフト保存のみ（手動公開）** で実装する。

**Why Playwright**: note.com のエディタは ProseMirror ベースで、本文が独自ブロック JSON 形式。
既存ツール（NoteClient, notion2note_article）もすべてブラウザ自動化を採用。
クリップボード経由で Markdown をペーストすると note.com 側が自動変換してくれるため、
ブロック JSON のリバースエンジニアリングが不要。

## ファイル構成

```
scripts/
├── publish.py           # 変更: "note" プラットフォーム追加
├── note_client.py       # 新規: Playwright ベースの note.com クライアント
├── note_login.py        # 新規: セッション保存用ログインスクリプト
├── .note-state.json     # 生成: ブラウザセッション状態（gitignore 対象）
├── pyproject.toml       # 変更: playwright 依存追加
└── tests/
    ├── test_publish.py  # 変更: note プラットフォームのテスト追加
    └── test_note_client.py  # 新規: note_client のテスト
.gitignore               # 変更: .note-state.json 追加
```

## Phase 1: note_login.py — セッション保存

**What**: note.com に Playwright headed ブラウザでログインし、セッション cookies を `.note-state.json` に保存するスクリプト。

**Why**: note.com は Cookie ベース認証のみ。API キーや OAuth がないため、一度ブラウザでログインしてセッション状態を保存する必要がある。notion2note_article も同じ方式。

```python
# 使い方:
# uv run python scripts/note_login.py
# → ブラウザが開く → 手動でログイン → Enter で保存
```

**仕様**:
- Playwright の Chromium を headed モードで起動
- `https://note.com/login` に遷移
- ユーザーが手動でログイン（email/password + 2FA 等）
- ユーザーが Enter を押したらセッション状態を `scripts/.note-state.json` に保存
- `browser_context.storage_state(path=...)` で保存

## Phase 2: note_client.py — Playwright ドラフト作成

**What**: note.com にドラフト記事を作成するモジュール。

**Why**: publish.py から呼び出される。Playwright 固有のロジックを分離して保守性を確保。

**公開関数**:
```python
@dataclass(frozen=True)
class NoteDraftResult:
    success: bool
    url: str | None
    error: str | None

async def create_note_draft(
    title: str,
    markdown_body: str,
    tags: tuple[str, ...] = (),
    state_path: Path = Path(__file__).parent / ".note-state.json",
    headless: bool = True,
) -> NoteDraftResult:
    """note.com にドラフト記事を作成する。"""
```

**処理フロー** (notion2note_article のパターンを踏襲):
1. セッション状態ファイルの存在チェック
2. Playwright Chromium を headless で起動（session state をロード）
3. `https://note.com/notes/new` に遷移
4. タイトル入力: `[placeholder*="タイトル"]` または `.o-noteEditorTextarea__title` セレクタ
5. 本文入力: クリップボード経由で Markdown をペースト（`navigator.clipboard.writeText()` → `Cmd+V`）
   - note.com の ProseMirror エディタが Markdown を自動変換
6. タグ追加（あれば）: ハッシュタグ入力フィールドを操作
7. 「下書き保存」ボタンをクリック: `text=下書き保存` または `Cmd+S`
8. 結果を返す

**セレクタ戦略** (カスケード、notion2note_article と同じ):
```python
TITLE_SELECTORS = [
    '[placeholder*="タイトル"]',
    '.o-noteEditorTextarea__title',
    '[data-testid="article-title"]',
    'textarea',
]
BODY_SELECTORS = [
    '[data-testid="article-body"]',
    '.o-noteEditorTextarea__body',
    '[contenteditable="true"]',
    '.ProseMirror',
    '[role="textbox"]',
]
```

**エラーハンドリング**:
- セッション切れ → 明確なエラーメッセージ（`note_login.py を再実行してください`）
- セレクタ不一致 → タイムアウト後にスクリーンショット保存して失敗

## Phase 3: publish.py 変更

**What**: `--platform note` を追加。

**変更点**:
1. `build_parser()`: `choices` に `"note"` 追加
2. `convert_to_note(article)`: `_strip_zenn_syntax()` を再利用して clean markdown を返す
3. `_run_note(article, args)`:
   - dry-run: 変換結果を表示
   - 通常: `note_client.create_note_draft()` を呼び出し
   - `asyncio.run()` で async 関数を実行
4. `_RUNNERS` に `"note": _run_note` 追加
5. note は日本語記事のみ → `_check_english_translation` のガードは不要（devto/hashnode のみ）

**再利用する既存関数**:
- `_strip_zenn_syntax()` (`publish.py:97-108`) — Zenn 構文の除去
- `parse_zenn_article()` (`publish.py:66-73`) — Zenn 記事の解析
- `_load_env()` (`publish.py:28-38`) — 環境変数読み込み
- `Article` / `PublishResult` データクラス

## Phase 4: テスト

**test_note_client.py** (新規):
- `create_note_draft()` は Playwright を使うため、実際のブラウザテストは統合テストとして分離
- ユニットテストでは関数のバリデーション（セッションファイル不在時のエラー等）をテスト

**test_publish.py** (変更):
- `TestConvertToNote`: `convert_to_note()` の変換テスト（`_strip_zenn_syntax` と同じ変換が適用されることを確認）
- `TestRunNote`:
  - `test_dry_run`: dry-run 出力の確認
  - `test_missing_session`: `.note-state.json` 不在時のエラー
  - `test_create_success`: `note_client.create_note_draft` をモックして成功パス
  - `test_create_failure`: モックして失敗パス

## Phase 5: 設定変更

**.gitignore** に追加:
```
scripts/.note-state.json
```

**pyproject.toml** に追加:
```toml
dependencies = [
    "httpx>=0.28.1",
    "python-frontmatter>=1.1.0",
    "playwright>=1.49",
]
```

**schedule.json**: 既存エントリに `"note"` フィールドは不要（note は日本語記事の選択的クロスポスト先なので、使うときだけ手動で追加する運用）

## 検証手順

1. `uv sync` で playwright 依存をインストール
2. `uv run playwright install chromium` でブラウザをインストール
3. `uv run python scripts/note_login.py` でログイン → セッション保存
4. `uv run python scripts/publish.py articles/xxx.md --platform note --dry-run` で変換確認
5. `uv run python scripts/publish.py articles/xxx.md --platform note` でドラフト作成
6. note.com のダッシュボードでドラフトが作成されていることを確認
7. `cd scripts && uv run pytest tests/ -v` で全テスト通過
8. `uv run pytest --cov=publish --cov-report=term-missing` でカバレッジ 80% 以上

## リスクと対策

| リスク | 対策 |
|--------|------|
| note.com の UI/セレクタ変更 | カスケードセレクタ + エラー時スクリーンショット |
| セッション切れ | 明確なエラーメッセージで再ログインを促す |
| Playwright 依存の重さ | playwright は dev ではなく main 依存（実行時に必要） |
| クリップボード操作の macOS 権限 | Playwright は自前ブラウザなので OS 権限不要 |
