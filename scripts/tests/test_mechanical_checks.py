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

この手法には 3 つの利点があります。

**速度**: とにかく速い

**品質**: 壊れない

**再現性**: 何度でも動く

あの装置のことを、覚えているでしょうか。

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
    assert "A7_triad_preannounce" in checks
    assert "A7_triad_bold_list" in checks
    assert "A10_deictic" in checks


def test_comma_enumeration_is_not_a_triad(tmp_path):
    # 2026-08-13 redesign: ordinary comma lists (「開発、運用、監視。」) must not
    # be flagged — the old heuristic hit ~100% false positives on normal prose.
    text = "# 静か\n\n開発、運用、監視の三領域を見た。問題はなかった。\n"
    result = analyze(_write(tmp_path, "commas.md", text))
    checks = {f["check"] for f in result["findings"]}
    assert "A7_triad_preannounce" not in checks
    assert "A7_triad_bold_list" not in checks


def test_triad_preannounce_edges(tmp_path):
    # 「23 点の」 is a quantity, not a preannounced triad; 「3 つあります」 is one.
    neg = analyze(_write(tmp_path, "neg.md", "# t\n\n23 点の資料を集めた。\n"))
    assert "A7_triad_preannounce" not in {f["check"] for f in neg["findings"]}
    pos = analyze(_write(tmp_path, "pos.md", "# t\n\n理由は 3 つあります。\n"))
    assert "A7_triad_preannounce" in {f["check"] for f in pos["findings"]}


def test_bold_run_of_five_is_a_list_not_a_triad(tmp_path):
    body = "\n\n".join(f"**項目{i}**: 説明です。" for i in range(5))
    result = analyze(_write(tmp_path, "five.md", f"# t\n\n{body}\n"))
    assert "A7_triad_bold_list" not in {f["check"] for f in result["findings"]}


def test_bold_bullets_are_not_a_triad(tmp_path):
    body = "\n".join(f"- **項目{i}**: 説明" for i in range(3))
    result = analyze(_write(tmp_path, "bullets.md", f"# t\n\n{body}\n"))
    assert "A7_triad_bold_list" not in {f["check"] for f in result["findings"]}


def test_bold_triad_reports_first_line_and_span(tmp_path):
    result = analyze(_write(tmp_path, "sloppy.md", SLOPPY))
    hit = next(f for f in result["findings"] if f["check"] == "A7_triad_bold_list")
    assert hit["excerpt"].startswith("**速度**")
    assert hit["end_line"] > hit["line"]


def test_lang_mismatch_guard(tmp_path):
    result = analyze(_write(tmp_path, "en-as-ja.md", EN_PLAIN))  # ja default
    assert "lang_mismatch" in {f["check"] for f in result["findings"]}


def test_long_sentence_thresholds(tmp_path):
    ja = "# t\n\n" + "この文はとにかく長い、" * 12 + "終わりです。\n"
    result = analyze(_write(tmp_path, "long-ja.md", ja))
    assert "A5_long_sentence" in {f["check"] for f in result["findings"]}
    en = "# t\n\n" + "this sentence keeps going and going, " * 8 + "the end.\n"
    result_en = analyze(_write(tmp_path, "long-en.md", en), lang="en")
    assert "A5_long_sentence" in {f["check"] for f in result_en["findings"]}


def test_deictic_reports_line(tmp_path):
    result = analyze(_write(tmp_path, "sloppy.md", SLOPPY))
    deictic = [f for f in result["findings"] if f["check"] == "A10_deictic"]
    assert deictic and deictic[0]["match"] == "あの"


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


def test_reader_address_is_stats_only(tmp_path):
    # A11: SLOPPY carries 「ませんか」「でしょうか」 → counted in stats;
    # PLAIN has zero markers but that must NOT become a finding (発見調 essays
    # legitimately score 0 — absence is judge evidence, not a violation).
    sloppy = analyze(_write(tmp_path, "sloppy.md", SLOPPY))
    assert sloppy["stats"]["reader_address_total"] >= 2
    assert "ませんか" in sloppy["stats"]["reader_address_markers"]
    plain = analyze(_write(tmp_path, "plain.md", PLAIN))
    assert plain["stats"]["reader_address_total"] == 0
    assert plain["stats"]["reader_address_markers"] == {}
    assert all(f["check"] != "A11_no_reader_address" for f in plain["findings"])


def test_reader_address_en_counts_you(tmp_path):
    result = analyze(_write(tmp_path, "sloppy-en.md", EN_SLOPPY), lang="en")
    # "your workflow" + "you should know"
    assert result["stats"]["reader_address_total"] >= 2
    plain = analyze(_write(tmp_path, "plain-en.md", EN_PLAIN), lang="en")
    assert plain["stats"]["reader_address_total"] == 0


def test_voice_delta_warns_on_flattening(tmp_path):
    baseline = analyze(_write(tmp_path, "plain.md", PLAIN))
    current = analyze(_write(tmp_path, "flat.md", FLATTENED))
    delta = voice_delta(current, baseline)
    assert delta["first_person_rate"]["warn"] is True  # 私 disappeared
    assert delta["mean_sentence_len"]["warn"] is True  # sentences ballooned


EN_SLOPPY = """# How AI Changed Everything

Moreover, this powerful tool will seamlessly leverage your workflow.

It's not just automation, it's a paradigm.

There are three things you should know.
"""

EN_PLAIN = """# A Quiet Note

I rebuilt my environment yesterday. It worked.

I had one reason to do it.
"""


def test_en_mode_detects_english_slop(tmp_path):
    result = analyze(_write(tmp_path, "sloppy-en.md", EN_SLOPPY), lang="en")
    checks = {f["check"] for f in result["findings"]}
    assert "A7_slop_word" in checks  # moreover / powerful tool / seamless / paradigm
    assert "A3_formal_word" in checks  # leverage
    assert "A7_not_x_but_y" in checks
    assert "A7_triad_preannounce" in checks
    assert result["lang"] == "en"
    assert "density_range_advisory_800_2000w" in result["stats"]


def test_en_mode_clean_text_and_voice(tmp_path):
    result = analyze(_write(tmp_path, "plain-en.md", EN_PLAIN), lang="en")
    assert result["findings"] == []
    assert result["voice"]["sentences"] == 3
    assert result["voice"]["first_person_rate"] > 0.5


def test_en_negatives_survive(tmp_path):
    # Corpus-verified false positives from the first review round:
    # "Every" must not match "very"; honest concessives are not the not-X-but-Y
    # tell; excerpts must keep original casing.
    text = (
        "# Quiet\n\n"
        "Every morning I open my task list.\n\n"
        "It's not perfect, but it works.\n\n"
        "That's not ideal, but I shipped it anyway.\n"
    )
    result = analyze(_write(tmp_path, "neg-en.md", text), lang="en")
    checks = {f["check"] for f in result["findings"]}
    assert "A2_degree_adverb" not in checks
    assert "A7_not_x_but_y" not in checks


def test_en_excerpt_keeps_original_casing(tmp_path):
    result = analyze(_write(tmp_path, "sloppy-en.md", EN_SLOPPY), lang="en")
    slop = [f for f in result["findings"] if f["check"] == "A7_slop_word"]
    assert any(f["excerpt"].startswith("Moreover") for f in slop)


def test_cli_accepts_lang_flag(tmp_path, capsys):
    p = _write(tmp_path, "plain-en.md", EN_PLAIN)
    assert main([str(p), "--lang", "en"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["lang"] == "en"


def test_cli_baseline_respects_lang(tmp_path, capsys):
    p = _write(tmp_path, "plain-en.md", EN_PLAIN)
    b = _write(tmp_path, "base-en.md", EN_PLAIN)
    assert main([str(p), "--baseline", str(b), "--lang", "en"]) == 0
    payload = json.loads(capsys.readouterr().out)
    # identical drafts → zero drift; the baseline was parsed as EN, not JA
    assert payload["voice_delta"]["first_person_rate"]["relative_change"] == 0.0
    assert payload["voice_delta"]["first_person_rate"]["baseline"] > 0


def test_cli_emits_json(tmp_path, capsys):
    p = _write(tmp_path, "plain.md", PLAIN)
    assert main([str(p)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["file"] == str(p)
    assert "voice" in payload and "counts" in payload
    # A6 is report-only; the key name must carry "advisory" (2026-08-13)
    assert "density_range_advisory_2000_5000" in payload["stats"]
    assert "in_range_2000_5000" not in payload["stats"]
