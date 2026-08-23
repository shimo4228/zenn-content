"""Deterministic prose checks for the article quality loop (evidence supplier).

Canonical checklist: .claude/refs/kaguura-craft-checklist.md §A.
Emits JSON findings for article-judge; never renders a verdict itself
(llm-as-judge: deterministic checks feed evidence, judgment stays holistic).

Usage:
    uv run python mechanical_checks.py path/to/article.md
    uv run python mechanical_checks.py draft.md --baseline first_draft.md
    uv run python mechanical_checks.py substack/article-en.md --lang en
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Literal

Lang = Literal["ja", "en"]

# A1 stadium address
STADIUM_WORDS = ["皆さん", "みなさん", "皆様", "みなさま", "読者の皆"]
# A2 degree adverbs (weak-verb crutches)
DEGREE_ADVERBS = [
    "とても",
    "非常に",
    "かなり",
    "しっかり",
    "すごく",
    "本当に",
    "極めて",
    "めちゃくちゃ",
]
# A3 formal words → plain alternatives
FORMAL_WORDS = {
    "活用す": "使う",
    "活用し": "使い",
    "実施す": "やる",
    "実施し": "やり",
    "レバレッジ": "生かす",
}
# A7 AI slop vocabulary (JP; canonical list lives in writing-ecosystem)
SLOP_WORDS = [
    "画期的",
    "革命的",
    "革新的",
    "素晴らしい",
    "驚くべき",
    "感動的",
    "シームレス",
    "パワフル",
    "ロバスト",
    "パラダイムシフト",
    "深い洞察",
    "示唆に富む",
    "重要な示唆",
    "最先端",
    "深掘り",
    "と言えるでしょう",
]

SENTENCE_END = re.compile(r"(?<=[。！？])")
JA_SENTENCE_MARK = re.compile(r"[。！？]")
LONG_SENTENCE_CHARS = 100
PARAGRAPH_MAX_SENTENCES = 2  # >2 gets reported (exception judging is the judge's job)
SINGLE_SENTENCE_RUN = 6  # LinkedIn-robot warning threshold
# A7 triad: structural tells only (2026-08-13 redesign — the old comma-count
# heuristic flagged ordinary sentences at ~100% false-positive rate).
# Digit lookbehind avoids 「23 点の」; the lookahead set covers 「3 つの利点」
# 「3 つあります」「三つ。」 while leaving 「一つ」 untouched.
TRIAD_PREANNOUNCE_RE = re.compile(
    r"(?<![0-9０-９])[3３三]\s*(?:つ|点|要素)(?=[のあ。、がでにはを])"
)
# Bold-paragraph runs only. Bullet lists (`- **…`) are excluded — bold-lead
# bullets are the default shape of technical lists in this corpus (51% of
# articles hit when they were included). Matched against stripped text.
BOLD_LINE_RE = re.compile(r"^\*\*")
BOLD_LIST_RUN = 3  # a run of exactly 3 is the triad tell; longer runs are lists
# A10 deictic references — evidence for article-judge K4 (指示語の回収).
# Report-only: whether the referent resolves nearby is the judge's call.
# 「例の」 is excluded (substring-matches 事例の/実例の/具体例の).
DEICTIC_MARKERS = ["あの", "さっきの", "先ほどの"]
# A11 reader address — evidence for judge B6 (単数の読者の積極形, 2026-08-20).
# Stats-only, never a finding: 発見調 essays legitimately score 0 (their
# 「〜ではないか」 questions carry the address), so absence is judge evidence.
# JA relies on sentence-final forms because Japanese drops the subject.
READER_ADDRESS_MARKERS = ["ください", "ませんか", "でしょうか", "ましょう", "あなた"]
VOICE_FIRST_PERSON = re.compile(r"私")
VOICE_DELTA_WARN = {"first_person_rate": 0.30, "mean_sentence_len": 0.20}

# ---- English mode (--lang en; for substack/*-en.md etc., 2026-08-13) ----
# Canonical EN slop list lives in writing-ecosystem; this is the greppable core.
EN_SLOP_WORDS = [
    "powerful tool",
    "revolutioniz",
    "cutting-edge",
    "game-changer",
    "seamless",
    "effortlessly",
    "delve",
    "multifaceted",
    "holistic",
    "transformative",
    "testament to",
    "deep dive",
    "pivotal",
    "tapestry",
    "unlock",
    "unleash",
    "empower",
    "paradigm",
    "moreover,",
    "furthermore,",
    "it's worth noting",
    "it is worth noting",
    "hope this helps",
    "in today's rapidly evolving",
]
EN_STADIUM_WORDS = ["dear reader", "folks,", "you guys", "everyone reading"]
# Word-boundary regex — substring matching flagged "Every"/"delivery" (contains
# "very") on the first real corpus run.
EN_DEGREE_ADVERB_RE = re.compile(
    r"(?i)\b(?:very|really|extremely|incredibly|absolutely)\b"
)
EN_FORMAL_WORDS = ["utilize", "leverage"]
# Echo forms only ("it's not X, it's Y"). A bare trailing "but" is NOT a tell —
# it matches honest concessives ("It's not perfect, but it works.").
EN_NOT_X_BUT_Y_RE = re.compile(
    r"(?i)\b(?:it'?s|it is|this is|that'?s|that is) not (?:just |merely |only )?"
    r"[^.;]{1,40}?[,;—]?\s*(?:it'?s|it is|this is|that'?s|that is)\b"
)
EN_TRIAD_PREANNOUNCE_RE = re.compile(
    r"(?i)\bthree (?:things|reasons|ways|points|lessons|steps|takeaways)\b"
)
# Abbreviation-aware split: don't break after e.g./i.e./Dr./etc., and require
# the next sentence to open with a capital or a quote.
EN_SENTENCE_END = re.compile(
    r"(?<=[.!?])(?<!e\.g\.)(?<!i\.e\.)(?<!Dr\.)(?<!Mr\.)(?<!Ms\.)"
    r"(?<!Fig\.)(?<!vs\.)(?<!etc\.)\s+(?=[A-Z\"'“])"
)
EN_LONG_SENTENCE_CHARS = 220
EN_VOICE_FIRST_PERSON = re.compile(r"\bI\b(?!/)")  # (?!/) keeps "I/O" out
EN_READER_ADDRESS_RE = re.compile(r"(?i)\b(?:you|your|yours)\b")


def _strip_noise(lines: list[str]) -> list[tuple[int, str]]:
    """Return (1-based line number, text) pairs with frontmatter, code fences,
    HTML comments and bare URLs removed. Headings are kept (title checks).
    Note: fenced code is dropped entirely, so a bold-paragraph run separated
    only by a code fence is seen as contiguous (documented bias)."""
    out: list[tuple[int, str]] = []
    in_code = False
    in_front = False
    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if i == 1 and line.strip() == "---":
            in_front = True
            continue
        if in_front:
            if line.strip() == "---":
                in_front = False
            continue
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        line = re.sub(r"<!--.*?-->", "", line)
        line = re.sub(r"https?://\S+", "", line)
        out.append((i, line))
    return out


def _paragraphs(
    numbered: list[tuple[int, str]], lang: Lang = "ja"
) -> list[tuple[int, str]]:
    """Blank-line separated paragraphs as (start line, joined text).
    Headings, list items and quote lines are excluded from density checks."""
    joiner = " " if lang == "en" else ""
    paras: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    for n, text in numbered:
        stripped = text.strip()
        skip = stripped.startswith(("#", "-", "*", ">", "|")) or not stripped
        if skip:
            if buf:
                paras.append((start, joiner.join(buf)))
                buf = []
            continue
        if not buf:
            start = n
        buf.append(stripped)
    if buf:
        paras.append((start, joiner.join(buf)))
    return paras


def _sentences(text: str, lang: Lang = "ja") -> list[str]:
    splitter = EN_SENTENCE_END if lang == "en" else SENTENCE_END
    return [s for s in splitter.split(text) if s.strip()]


def _scan_words(
    numbered: list[tuple[int, str]], words: list[str], check: str
) -> list[dict]:
    findings = []
    for n, text in numbered:
        for w in words:
            if w in text:
                findings.append(
                    {
                        "check": check,
                        "line": n,
                        "excerpt": text.strip()[:60],
                        "match": w,
                    }
                )
    return findings


def _scan_words_ci(
    numbered: list[tuple[int, str]], words: list[str], check: str
) -> list[dict]:
    """Case-insensitive match; the excerpt keeps the original casing so it
    greps back to the source (lowercased excerpts broke judge citations)."""
    findings = []
    for n, text in numbered:
        low = text.lower()
        for w in words:
            if w in low:
                findings.append(
                    {
                        "check": check,
                        "line": n,
                        "excerpt": text.strip()[:60],
                        "match": w,
                    }
                )
    return findings


def voice_metrics(paras: list[tuple[int, str]], lang: Lang = "ja") -> dict:
    sents = [s for _, p in paras for s in _sentences(p, lang)]
    if not sents:
        return {
            "sentences": 0,
            "first_person_rate": 0.0,
            "mean_sentence_len": 0.0,
            "sentence_len_stdev": 0.0,
        }
    fp_re = EN_VOICE_FIRST_PERSON if lang == "en" else VOICE_FIRST_PERSON
    lens = [len(s) for s in sents]
    fp = sum(1 for s in sents if fp_re.search(s))
    return {
        "sentences": len(sents),
        "first_person_rate": round(fp / len(sents), 4),
        "mean_sentence_len": round(statistics.mean(lens), 2),
        "sentence_len_stdev": round(statistics.pstdev(lens), 2),
    }


def analyze(path: Path, lang: Lang = "ja") -> dict:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    numbered = _strip_noise(lines)
    paras = _paragraphs(numbered, lang)
    findings: list[dict] = []

    if lang == "en":
        findings += _scan_words_ci(numbered, EN_STADIUM_WORDS, "A1_stadium")
        findings += _scan_words_ci(numbered, EN_SLOP_WORDS, "A7_slop_word")
        findings += _scan_words_ci(numbered, EN_FORMAL_WORDS, "A3_formal_word")
        findings += _scan_words(numbered, ["—"], "A7_em_dash")
        for n, text in numbered:
            m = EN_DEGREE_ADVERB_RE.search(text)
            if m:
                findings.append(
                    {
                        "check": "A2_degree_adverb",
                        "line": n,
                        "excerpt": text.strip()[:60],
                        "match": m.group(0),
                    }
                )
            if EN_NOT_X_BUT_Y_RE.search(text):
                findings.append(
                    {
                        "check": "A7_not_x_but_y",
                        "line": n,
                        "excerpt": text.strip()[:60],
                    }
                )
    else:
        findings += _scan_words(numbered, STADIUM_WORDS, "A1_stadium")
        findings += _scan_words(numbered, DEGREE_ADVERBS, "A2_degree_adverb")
        findings += _scan_words(numbered, list(FORMAL_WORDS), "A3_formal_word")
        findings += _scan_words(numbered, SLOP_WORDS, "A7_slop_word")
        findings += _scan_words(numbered, ["ではなく"], "A7_dewanaku")
        findings += _scan_words(numbered, ["—"], "A7_em_dash")
        # Guard: an English article run through the ja default produces phantom
        # findings (no 。 → every paragraph is one "long sentence"). Report
        # loudly instead of proceeding silently.
        if paras and not any(JA_SENTENCE_MARK.search(p) for _, p in paras):
            findings.append(
                {
                    "check": "lang_mismatch",
                    "line": paras[0][0],
                    "excerpt": "no 。！？ in body — English article? rerun with --lang en",
                }
            )

    # A4 paragraph density + LinkedIn-robot run
    single_run = 0
    for start, text in paras:
        sents = _sentences(text, lang)
        if len(sents) > PARAGRAPH_MAX_SENTENCES:
            findings.append(
                {
                    "check": "A4_dense_paragraph",
                    "line": start,
                    "excerpt": sents[0][:60],
                    "sentences": len(sents),
                }
            )
        if len(sents) == 1:
            single_run += 1
            if single_run == SINGLE_SENTENCE_RUN:
                findings.append(
                    {
                        "check": "A4_single_sentence_run",
                        "line": start,
                        "excerpt": text[:60],
                    }
                )
        else:
            single_run = 0

    # A5 long sentences
    long_at = EN_LONG_SENTENCE_CHARS if lang == "en" else LONG_SENTENCE_CHARS
    for start, text in paras:
        for s in _sentences(text, lang):
            if len(s) > long_at:
                findings.append(
                    {
                        "check": "A5_long_sentence",
                        "line": start,
                        "excerpt": s[:60],
                        "chars": len(s),
                    }
                )

    # A7 triad — structural tells only
    triad_re = EN_TRIAD_PREANNOUNCE_RE if lang == "en" else TRIAD_PREANNOUNCE_RE
    for n, text in numbered:
        if triad_re.search(text):
            findings.append(
                {
                    "check": "A7_triad_preannounce",
                    "line": n,
                    "excerpt": text.strip()[:60],
                }
            )
    # Bold-paragraph runs: collect runs first, report only exact-3 runs
    # (a 5-item bold list is a list, not a triad).
    runs: list[tuple[int, int, str, int]] = []  # start, end, first line, length
    run_len = 0
    run_start = 0
    run_end = 0
    run_first = ""
    for n, text in numbered:
        stripped = text.strip()
        if not stripped:
            continue  # blank lines separate bold paragraphs but keep the run
        if BOLD_LINE_RE.match(stripped):
            if run_len == 0:
                run_start, run_first = n, stripped
            run_len += 1
            run_end = n
        elif run_len:
            runs.append((run_start, run_end, run_first, run_len))
            run_len = 0
    if run_len:
        runs.append((run_start, run_end, run_first, run_len))
    for start, end, first, length in runs:
        if length == BOLD_LIST_RUN:
            findings.append(
                {
                    "check": "A7_triad_bold_list",
                    "line": start,
                    "end_line": end,
                    "excerpt": first[:60],
                }
            )

    # A10 deictic references (evidence for judge K4; JA only)
    if lang != "en":
        findings += _scan_words(numbered, DEICTIC_MARKERS, "A10_deictic")

    # A11 reader address (evidence for judge B6; stats-only like A6 —
    # a zero count is legitimate in 発見調 essays, so it is never a finding)
    if lang == "en":
        addr_counts = {
            "you/your": sum(len(EN_READER_ADDRESS_RE.findall(t)) for _, t in numbered)
        }
    else:
        addr_counts = {
            m: sum(t.count(m) for _, t in numbered) for m in READER_ADDRESS_MARKERS
        }

    # A9 title
    title = next(
        (t.lstrip("# ").strip() for _, t in numbered if t.startswith("# ")), ""
    )
    body_chars = sum(len(p) for _, p in paras)

    counts: dict[str, int] = {}
    for f in findings:
        counts[f["check"]] = counts.get(f["check"], 0) + 1

    # Checklist A6 is report-only ("判定しない — 密度が本体"). The key names say
    # "advisory" so downstream never treats them as a hard gate
    # (2026-08-13: the old name `in_range_2000_5000` induced exactly that).
    stats: dict[str, object] = {"paragraphs": len(paras), "body_chars": body_chars}
    stats["reader_address_total"] = sum(addr_counts.values())
    stats["reader_address_markers"] = {k: v for k, v in addr_counts.items() if v}
    if lang == "en":
        body_words = sum(len(p.split()) for _, p in paras)
        stats["body_words"] = body_words
        stats["density_range_advisory_800_2000w"] = 800 <= body_words <= 2000
        checks_applied = [
            "A1_stadium",
            "A2_degree_adverb",
            "A3_formal_word",
            "A4",
            "A5",
            "A7_slop_word",
            "A7_em_dash",
            "A7_not_x_but_y",
            "A7_triad",
            "A9",
            "A11_reader_address",
        ]
    else:
        stats["density_range_advisory_2000_5000"] = 2000 <= body_chars <= 5000
        checks_applied = [
            "A1_stadium",
            "A2_degree_adverb",
            "A3_formal_word",
            "A4",
            "A5",
            "A7_slop_word",
            "A7_dewanaku",
            "A7_em_dash",
            "A7_triad",
            "A9",
            "A10_deictic",
            "A11_reader_address",
            "lang_guard",
        ]

    return {
        "file": str(path),
        "lang": lang,
        "checks_applied": checks_applied,
        "title": {
            "text": title,
            "has_number": bool(re.search(r"\d", title)),
            "chars": len(title),
        },
        "stats": stats,
        "voice": voice_metrics(paras, lang),
        "counts": counts,
        "findings": findings,
    }


def voice_delta(current: dict, baseline: dict) -> dict:
    """A8: relative drift of voice metrics vs the first draft (over-editing signal)."""
    delta: dict[str, dict] = {}
    for key, warn_at in VOICE_DELTA_WARN.items():
        base, cur = baseline["voice"][key], current["voice"][key]
        rel = 0.0 if base == 0 else (cur - base) / base
        delta[key] = {
            "baseline": base,
            "current": cur,
            "relative_change": round(rel, 4),
            "warn": abs(rel) > warn_at,
        }
    return delta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("article", type=Path)
    ap.add_argument("--baseline", type=Path, help="first draft for A8 voice regression")
    ap.add_argument(
        "--lang",
        choices=["ja", "en"],
        default="ja",
        help="prose language (en switches slop lists, sentence splitting, density)",
    )
    args = ap.parse_args(argv)

    result = analyze(args.article, lang=args.lang)
    if args.baseline:
        result["voice_delta"] = voice_delta(
            result, analyze(args.baseline, lang=args.lang)
        )
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
