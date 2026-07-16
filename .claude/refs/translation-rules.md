# Translation Rules（翻訳ルール 正本）

> このファイルは JP→EN 翻訳の **唯一の正本**。
> `devto-translator` エージェントはここを参照する。
> 根拠: [ADR-0002](../../docs/adr/0002-writing-team-orchestration.md)

---

## 翻訳の必須ルール

- コードブロック（``` で囲まれた部分）は**絶対に翻訳しない**
- インラインコード（`backtick`）内も翻訳しない
- Markdown 構文（#, -, |, [], ![] 等）をそのまま保持
- frontmatter: title のみ翻訳、他はそのまま
- 画像リンク（`/images/xxx`）はそのまま保持
- 用語集（`docs/translation-glossary.json`）の `never_translate` 用語はそのまま保持

## 文体ルール

- 技術的で明快な英語（対象読者: ソフトウェアエンジニア）
- 直訳ではなく、英語として自然な表現にする
- 著者の個性と洞察を保持する
- 日本特有の文化的文脈は、英語圏の読者向けに簡潔に補足する
- AI slop 禁止（詳細は `~/.claude/skills/writing-ecosystem/SKILL.md` の English セクション）
- 謙遜表現は英語の技術文書の慣習に合わせて調整する
- EN 記事には `canonical_url` を設定しない（言語が異なるため Zenn canonical は無意味）

## frontmatter の翻訳

```yaml
---
title: "英語タイトル（原文の意味を保持、60文字以内）"
emoji: "📚"           # そのまま
type: "tech"           # そのまま
topics: ["claude", "ai", "automation"]  # 英語タグに変換
published: true        # そのまま
---
```

topics の変換例:
- "開発ツール" → "devtools"
- "チートシート" → "cheatsheet"
- "自動化" → "automation"

## Dev.to 内リンクの置換（必須）

- **著者自身の Zenn 記事へのリンクは、本文・関連リンク節とも、必ず Dev.to 版記事の URL に置き換える**（Dev.to 読者を日本語の Zenn へ送らない）
- 対応 URL の解決: `scripts/schedule.json` の該当 `articles-en/` エントリの `devto` フィールドを参照する
- Dev.to 版が存在しない場合（エントリなし / `devto: null`）のみ、Zenn URL をそのまま残す
- GitHub リポジトリ・ADR・公式ドキュメント等、記事以外のリンクはそのまま保持

## Dev.to タグ付け

1. `scripts/devto_crosspost.py` の `resolve_devto_tags()` フォールバック規則を参照
2. JP 記事の `topics` を Dev.to タグに変換（最大4つ）
3. マッピングにない topics: 英語としてそのまま通じるか → 上位カテゴリ → 汎用タグ（ai, programming, discuss）
4. `type: "idea"` の記事は先頭に "discuss" を付与

## 品質チェックリスト

翻訳完了後、以下を自己検証する:

1. **コードブロック完全性**: 原文と翻訳文のコードブロック数が一致するか
2. **リンク完全性**: すべての URL、画像パスが保持されているか
3. **用語一貫性**: 用語集の用語が正しく使われているか
4. **AI slop 検出**: 汎用的な AI 表現が混入していないか grep で確認
5. **技術的正確性**: 技術用語が正しく翻訳されているか

問題が見つかった場合はその場で修正する。

## エラーリカバリ

| 問題 | 対応 |
|------|------|
| コードブロックが翻訳された | 原文からコードブロックを抽出して差し替え |
| 用語が不統一 | 用語集を参照して一括置換 |
| frontmatter が壊れた | 原文から frontmatter をコピーして title のみ翻訳 |
| 文体が硬すぎる | 「技術ブログ」のトーンで書き直し |
| カバー画像なし | 手動生成を提案。無い場合はカバーなしで投稿続行 |
| Dev.to API エラー | エラー内容を報告。30秒間隔のレートリミットに注意 |
| schedule.json パースエラー | バックアップを取ってから修正 |
