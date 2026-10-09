"""List what a persona-read revision added or dropped that the author did not decide.

A revision round may change how the thinking is shown, never what is claimed (writing backbone 1:
the author's words cap the certainty). This compares two full rounds of a draft and returns:
numbers absent from the evidence dossier, added superlatives, added and removed hedges, and Latin
names absent from the dossier. Any of these goes to the author before the next round. New katakana
words are listed for reading only, because ordinary loanwords would fire every round.

Usage:
    uv run --project scripts python scripts/drift_count.py <prev.md> <curr.md> [--dossier <path>]

Prints JSON. Exit 1 when anything other than new_katakana is non-empty, 0 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SUPERLATIVES = ("最も", "唯一", "初めて", "誰よりも", "第一人者", "圧倒的", "並ぶ者", "随一", "最高", "最大")
HEDGES = ("かもしれ", "と思われ", "可能性があ", "おそらく", "とは限らな", "と考えられ", "ように見え")

# A digit run that is not part of a date, time, version or identifier (2026-10-09, 09:00, v2.1, C17).
_NUMBER = re.compile(r"(?<![A-Za-z0-9\-/:.])\d[\d,]*(?:\.\d+)?(?![\d\-/:]|\.\d)%?")
_LATIN = re.compile(r"[A-Za-z][A-Za-z0-9_\-]*")
_KATAKANA = re.compile(r"[ァ-ヴー]{2,}")
INFORMATIONAL = ("new_katakana",)


def _canonical_number(raw: str) -> str:
    percent = raw.endswith("%")
    value = raw.rstrip("%").replace(",", "")
    if "." in value:
        value = value.rstrip("0").rstrip(".")
    value = value.lstrip("0") or "0"
    return value + ("%" if percent else "")


def numbers(text: str) -> set[str]:
    """Canonical numbers: full-width folded, separators and redundant zeros dropped, % kept."""
    return {_canonical_number(m.group()) for m in _NUMBER.finditer(unicodedata.normalize("NFKC", text))}


def latin_names(text: str) -> set[str]:
    return set(_LATIN.findall(unicodedata.normalize("NFKC", text)))


def katakana(text: str) -> set[str]:
    return set(_KATAKANA.findall(text))


def added(prev: str, curr: str, terms: tuple[str, ...]) -> list[str]:
    return sorted(t for t in terms if curr.count(t) > prev.count(t))


def removed(prev: str, curr: str, terms: tuple[str, ...]) -> list[str]:
    return sorted(t for t in terms if curr.count(t) < prev.count(t))


def drift(prev: str, curr: str, dossier: str) -> dict[str, list[str]]:
    said_numbers = numbers(prev) | numbers(dossier)
    said_names = latin_names(prev) | latin_names(dossier)
    return {
        "new_numbers": sorted(numbers(curr) - said_numbers),
        "new_superlatives": added(prev, curr, SUPERLATIVES),
        "new_hedges": added(prev, curr, HEDGES),
        "removed_hedges": removed(prev, curr, HEDGES),
        "new_names": sorted(latin_names(curr) - said_names),
        "new_katakana": sorted(katakana(curr) - katakana(prev) - katakana(dossier)),
    }


def has_drift(result: dict[str, list[str]]) -> bool:
    return any(v for k, v in result.items() if k not in INFORMATIONAL)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List what a persona-read revision added or dropped.")
    parser.add_argument("prev", type=Path)
    parser.add_argument("curr", type=Path)
    parser.add_argument("--dossier", type=Path, help="evidence dossier; its numbers and names count as said")
    args = parser.parse_args(argv)

    dossier = args.dossier.read_text(encoding="utf-8") if args.dossier else ""
    result = drift(args.prev.read_text(encoding="utf-8"), args.curr.read_text(encoding="utf-8"), dossier)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 1 if has_drift(result) else 0


if __name__ == "__main__":
    raise SystemExit(main())
