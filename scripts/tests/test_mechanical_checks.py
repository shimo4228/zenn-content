"""Tests for mechanical_checks.py — deterministic prose evidence supplier."""

from __future__ import annotations

import json

from mechanical_checks import analyze, main, voice_delta

SLOPPY = """---
title: dummy
---

# AI で 3 倍速くなった話

皆さん、こんにちは。この画期的なツールはとてもシームレスです。実装を活用することで、開発、運用、監視。

これは短い文です。次も短い文です。そして三文目まで続けてしまう段落です。

AI は道具ではなく、相棒だ — そう思いませんか。

```python
# 皆さん という語はコード内なので検出されないこと
print("画期的")
```

これは URL を含む行です <!-- 皆さん(コメント内) -->
"""

PLAIN = """# 静かな記事

私はこの記事を書いた。理由は一つある。

私は昨日、環境を作り直した。動いた。
"""

FLATTENED = """# 静かな記事

この記事が書かれた背景には、環境の再構築という、開発における反復的な作業プロセスの見直しと、その効果の検証という目的が存在している。

作業は問題なく完了しており、期待された効果が確認されている状況である。
"""


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_detects_each_category(tmp_path):
    result = analyze(_write(tmp_path, "sloppy.md", SLOPPY))
    checks = {f["check"] for f in result["findings"]}
    assert "A1_stadium" in checks
    assert "A2_degree_adverb" in checks
    assert "A3_formal_word" in checks
    assert "A7_slop_word" in checks
    assert "A7_dewanaku" in checks
    assert "A7_em_dash" in checks
    assert "A4_dense_paragraph" in checks
    assert "A7_triad" in checks


def test_code_frontmatter_comments_excluded(tmp_path):
    result = analyze(_write(tmp_path, "sloppy.md", SLOPPY))
    stadium_lines = [
        f["line"] for f in result["findings"] if f["check"] == "A1_stadium"
    ]
    # 皆さん appears in body (line 7), code block and HTML comment must not add hits
    assert stadium_lines == [7]
    slop_hits = [
        f
        for f in result["findings"]
        if f["check"] == "A7_slop_word" and f["match"] == "画期的"
    ]
    assert len(slop_hits) == 1


def test_title_number_detection(tmp_path):
    result = analyze(_write(tmp_path, "sloppy.md", SLOPPY))
    assert result["title"]["has_number"] is True
    plain = analyze(_write(tmp_path, "plain.md", PLAIN))
    assert plain["title"]["has_number"] is False


def test_dense_paragraph_reports_sentence_count(tmp_path):
    result = analyze(_write(tmp_path, "sloppy.md", SLOPPY))
    dense = [f for f in result["findings"] if f["check"] == "A4_dense_paragraph"]
    assert dense and dense[0]["sentences"] == 3


def test_clean_text_has_no_findings(tmp_path):
    result = analyze(_write(tmp_path, "plain.md", PLAIN))
    assert result["findings"] == []
    assert result["voice"]["sentences"] == 4


def test_voice_delta_warns_on_flattening(tmp_path):
    baseline = analyze(_write(tmp_path, "plain.md", PLAIN))
    current = analyze(_write(tmp_path, "flat.md", FLATTENED))
    delta = voice_delta(current, baseline)
    assert delta["first_person_rate"]["warn"] is True  # 私 disappeared
    assert delta["mean_sentence_len"]["warn"] is True  # sentences ballooned


def test_cli_emits_json(tmp_path, capsys):
    p = _write(tmp_path, "plain.md", PLAIN)
    assert main([str(p)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["file"] == str(p)
    assert "voice" in payload and "counts" in payload
