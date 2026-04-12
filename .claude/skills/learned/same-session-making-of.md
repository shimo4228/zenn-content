---
name: same-session-making-of
description: "記事を書いた直後に同セッションで制作過程のメタ記事を書くパターン"
user-invocable: false
origin: auto-extracted
---

# Same-Session Making-Of Article

**Extracted:** 2026-03-20
**Context:** 記事の校正プロセスが面白かった・教育的価値があるとき

## Problem
記事の制作過程には、完成記事には載らない判断・対話・転換がある。
セッションが終わるとコンテキストが失われ、後から再現できない。

## Solution
1. 記事を公開した直後に `/collect-context` でセッションのコンテキストを収集
2. Before/After（タイトル、核心、トーンの変遷）を構造化
3. 著者の対話ログから転換点を抽出
4. 同一セッション内でメタ記事を執筆（記憶が鮮明なうちに）

## When to Use
- 校正プロセスで記事の核心が変わったとき
- 著者が「この過程自体が面白い」と言ったとき
- AI との協業プロセスを可視化する価値があるとき

## Key Structure
- 何を書いたか（対象記事のリンク+概要）
- なぜ書くのか（動機）
- 制作フロー全体像
- Before/After の具体例（タイトル、核心、トーン）
- AI が間違えたこと
- 校正対話の記録（テーブル）
