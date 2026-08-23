#!/usr/bin/env bash
# render_note_assets.sh — note/substack 原稿の貼り付け用資産を一括再生成する。
#
# Usage:
#   scripts/render_note_assets.sh note/ai-desire-exhaustion.md
#   scripts/render_note_assets.sh substack/ai-desire-exhaustion-en.md
#
# やること:
#   1. 先頭 h1 をタイトルとして抽出（note/Substack ではタイトル欄に別入力するため
#      本文からは除外する — repo 規約）
#   2. <slug>.html を併置生成（ブラウザで開いて全選択コピー → エディタへペースト）
#
# 生成物はコミット対象（既存の .html 併置慣例に従う）。
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <path/to/article.md>" >&2
  exit 64
fi

md="$1"
if [[ ! -f "$md" ]]; then
  echo "error: not found: $md" >&2
  exit 66
fi
if ! command -v pandoc >/dev/null 2>&1; then
  echo "error: pandoc not installed" >&2
  exit 69
fi

first_line=$(head -n 1 "$md")
if [[ "$first_line" != '# '* ]]; then
  echo "error: first line of $md is not an h1 title" >&2
  exit 65
fi
title=${first_line#\# }

html="${md%.md}.html"
# -f gfm 必須: 既定方言 (-f markdown) は「blank line なしで段落直後に始まるリスト」を
# 段落に潰し、GitHub 上のレンダリングと乖離する（substack-publishing に実証あり）。
tail -n +2 "$md" | pandoc -f gfm -t html -s --metadata pagetitle="$title" -o "$html"
echo "title: $title"
echo "wrote: $html"
