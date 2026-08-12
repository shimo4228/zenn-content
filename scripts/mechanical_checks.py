"""Deterministic prose checks for the article quality loop (evidence supplier).

Canonical checklist: .claude/refs/kaguura-craft-checklist.md §A.
Emits JSON findings for article-judge; never renders a verdict itself
(llm-as-judge: deterministic checks feed evidence, judgment stays holistic).

Usage:
    uv run python mechanical_checks.py path/to/article.md
    uv run python mechanical_checks.py draft.md --baseline first_draft.md
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

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
LONG_SENTENCE_CHARS = 100
PARAGRAPH_MAX_SENTENCES = 2  # >2 gets reported (exception judging is the judge's job)
SINGLE_SENTENCE_RUN = 6  # LinkedIn-robot warning threshold
TRIAD_RE = re.compile(r"[^、。\n]{1,18}、[^、。\n]{1,18}、[^、。\n]{1,18}[。．]")
VOICE_FIRST_PERSON = re.compile(r"私")
VOICE_DELTA_WARN = {"first_person_rate": 0.30, "mean_sentence_len": 0.20}


def _strip_noise(lines: list[str]) -> list[tuple[int, str]]:
    """Return (1-based line number, text) pairs with frontmatter, code fences,
    HTML comments and bare URLs removed. Headings are kept (title checks)."""
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


def _paragraphs(numbered: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Blank-line separated paragraphs as (start line, joined text).
    Headings, list items and quote lines are excluded from density checks."""
    paras: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    for n, text in numbered:
        stripped = text.strip()
        skip = stripped.startswith(("#", "-", "*", ">", "|")) or not stripped
        if skip:
            if buf:
                paras.append((start, "".join(buf)))
                buf = []
            continue
        if not buf:
            start = n
        buf.append(stripped)
    if buf:
        paras.append((start, "".join(buf)))
    return paras


def _sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_END.split(text) if s.strip()]


def _scan_words(numbered, words, check) -> list[dict]:
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


def voice_metrics(paras: list[tuple[int, str]]) -> dict:
    sents = [s for _, p in paras for s in _sentences(p)]
    if not sents:
        return {
            "sentences": 0,
            "first_person_rate": 0.0,
            "mean_sentence_len": 0.0,
            "sentence_len_stdev": 0.0,
        }
    lens = [len(s) for s in sents]
    fp = sum(1 for s in sents if VOICE_FIRST_PERSON.search(s))
    return {
        "sentences": len(sents),
        "first_person_rate": round(fp / len(sents), 4),
        "mean_sentence_len": round(statistics.mean(lens), 2),
        "sentence_len_stdev": round(statistics.pstdev(lens), 2),
    }


def analyze(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    numbered = _strip_noise(lines)
    paras = _paragraphs(numbered)
    findings: list[dict] = []

    findings += _scan_words(numbered, STADIUM_WORDS, "A1_stadium")
    findings += _scan_words(numbered, DEGREE_ADVERBS, "A2_degree_adverb")
    findings += _scan_words(numbered, list(FORMAL_WORDS), "A3_formal_word")
    findings += _scan_words(numbered, SLOP_WORDS, "A7_slop_word")
    findings += _scan_words(numbered, ["ではなく"], "A7_dewanaku")
    findings += _scan_words(numbered, ["—"], "A7_em_dash")

    # A4 paragraph density + LinkedIn-robot run
    single_run = 0
    for start, text in paras:
        sents = _sentences(text)
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

    # A5 long sentences / A7 triad heuristic
    for start, text in paras:
        for s in _sentences(text):
            if len(s) > LONG_SENTENCE_CHARS:
                findings.append(
                    {
                        "check": "A5_long_sentence",
                        "line": start,
                        "excerpt": s[:60],
                        "chars": len(s),
                    }
                )
        if TRIAD_RE.search(text):
            findings.append({"check": "A7_triad", "line": start, "excerpt": text[:60]})

    # A9 title
    title = next(
        (t.lstrip("# ").strip() for _, t in numbered if t.startswith("# ")), ""
    )
    body_chars = sum(len(p) for _, p in paras)

    counts: dict[str, int] = {}
    for f in findings:
        counts[f["check"]] = counts.get(f["check"], 0) + 1

    return {
        "file": str(path),
        "title": {
            "text": title,
            "has_number": bool(re.search(r"\d", title)),
            "chars": len(title),
        },
        "stats": {
            "paragraphs": len(paras),
            "body_chars": body_chars,
            "in_range_2000_5000": 2000 <= body_chars <= 5000,
        },
        "voice": voice_metrics(paras),
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
    args = ap.parse_args(argv)

    result = analyze(args.article)
    if args.baseline:
        result["voice_delta"] = voice_delta(result, analyze(args.baseline))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
