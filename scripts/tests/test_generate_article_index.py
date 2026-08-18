"""Tests for generate_article_index.py — the article index / reading-path generator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import generate_article_index as gai

README_EN = "# zenn-content\n\nintro\n\n<!-- reading-paths:start -->\nold\n<!-- reading-paths:end -->\n\ntail\n"
README_JA = "# zenn-content\n\n導入\n\n<!-- reading-paths:start -->\n古い\n<!-- reading-paths:end -->\n\n末尾\n"


def _article(title: str, published: bool = True, published_at: str | None = "2026-08-01 09:00", topics=("ai",)) -> str:
    fm = [f'title: "{title}"', "emoji: \"x\"", "type: \"tech\"", f"topics: {json.dumps(list(topics))}", f"published: {'true' if published else 'false'}"]
    if published_at is not None:
        fm.append(f"published_at: {published_at}")
    return "---\n" + "\n".join(fm) + "\n---\n\nbody\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "articles").mkdir()
    (tmp_path / "articles-en").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs").mkdir()
    a = tmp_path / "articles"
    a.joinpath("newer.md").write_text(_article("新しい記事", published_at="2026-08-10 09:00", topics=("ai", "agent")))
    a.joinpath("older.md").write_text(_article("古い記事", published_at="2026-07-01"))
    a.joinpath("legacy.md").write_text(_article("旧命名の記事", published_at="2026-07-15 07:00", topics=()))
    a.joinpath("draft.md").write_text(_article("下書き", published=False, published_at=None))
    e = tmp_path / "articles-en"
    e.joinpath("newer.md").write_text('---\ntitle: "Newer Article"\npublished: true\n---\n\nbody\n')
    e.joinpath("legacy-en.md").write_text('---\ntitle: "Legacy Article"\npublished: true\n---\n\nbody\n')
    (tmp_path / "scripts" / "schedule.json").write_text(json.dumps({"articles": [
        {"file": "articles/newer.md", "date": "2026-08-10"},
        {"file": "articles-en/newer.md", "devto": "https://dev.to/x/newer-1"},
        {"file": "articles-en/legacy-en.md", "devto": None},
        {"file": "articles-en/renamed.md", "devto": "https://dev.to/x/renamed-9"},  # file is now renamed-en.md
    ]}))
    a.joinpath("renamed.md").write_text(_article("改名された記事", published_at="2026-06-20 09:00"))
    e.joinpath("renamed-en.md").write_text('---\ntitle: "Renamed Article"\npublished: true\n---\n\nbody\n')
    (tmp_path / "scripts" / "reading_paths.yml").write_text(
        "routes:\n"
        "  - id: r1\n    label: {en: Route One, ja: 経路一}\n    reason: {en: Why one., ja: 理由一。}\n"
        "    articles: [newer, older]\n"
        "  - id: r2\n    label: {en: Route Two, ja: 経路二}\n    articles: [legacy]\n"
        "    title_en: {legacy: Fallback Title}\n"
    )
    (tmp_path / "note").mkdir()
    (tmp_path / "substack").mkdir()
    (tmp_path / "note" / "essay-a.md").write_text("# エッセイA\n\n本文\n")
    (tmp_path / "substack" / "essay-a-en.md").write_text("# Essay A\n\nbody\n")
    (tmp_path / "substack" / "essay-b-en.md").write_text("# Essay B\n\nbody\n")
    (tmp_path / "scripts" / "corpus.yml").write_text(
        "essays:\n"
        "  - slug: essay-b\n    date: 2026-06-01\n"
        "    en: {title: Essay B, url: https://x.substack.com/p/b, file: substack/essay-b-en.md}\n"
        "  - slug: essay-a\n    date: 2026-08-01\n"
        "    ja: {title: エッセイA, url: https://note.com/u/n/a, file: note/essay-a.md}\n"
        "    en: {title: Essay A, url: https://x.substack.com/p/a, file: substack/essay-a-en.md}\n"
        "papers:\n"
        "  - title: Paper One\n    date: 2026-05-01\n    line: Line X\n"
        "    zenodo: 10.5281/zenodo.1\n    ssrn: 10.2139/ssrn.1\n    from: [older]\n"
        "  - title: Paper Two\n    date: 2026-06-01\n    line: Line Y\n    zenodo: 10.5281/zenodo.2\n"
        "research_lines:\n"
        "  - {name: Line X, repo: https://github.com/u/x, doi: 10.5281/zenodo.10}\n"
    )
    (tmp_path / "README.md").write_text(README_EN)
    (tmp_path / "README.ja.md").write_text(README_JA)
    return tmp_path


def _corpus(repo: Path) -> gai.Corpus:
    return gai.load_corpus(repo, {a.slug for a in gai.load_articles(repo)})


# ---------------------------------------------------------------------------
# load_articles
# ---------------------------------------------------------------------------


def test_load_articles_membership_order_and_enrichment(repo: Path):
    arts = gai.load_articles(repo)
    assert [a.slug for a in arts] == ["newer", "legacy", "older", "renamed"]  # newest first, draft excluded
    newer, legacy, older, renamed = arts
    assert renamed.en_file == "articles-en/renamed-en.md" and renamed.devto == "https://dev.to/x/renamed-9"  # URL keyed by slug
    assert newer.title_en == "Newer Article" and newer.devto == "https://dev.to/x/newer-1"
    assert newer.en_file == "articles-en/newer.md"
    assert legacy.en_file == "articles-en/legacy-en.md" and legacy.title_en == "Legacy Article"
    assert legacy.devto is None  # null in schedule.json → not posted
    assert older.en_file is None and older.title_en is None
    assert older.published_at == "2026-07-01 00:00"  # date-only normalized
    assert newer.date == "2026-08-10"
    assert newer.zenn_url == "https://zenn.dev/shimo4228/articles/newer"


def test_published_article_without_published_at_is_an_error(repo: Path):
    (repo / "articles" / "nodate.md").write_text(_article("日付なし", published_at=None))
    with pytest.raises(ValueError, match="nodate: published article without published_at"):
        gai.load_articles(repo)


def test_unparseable_published_at_is_an_error(repo: Path):
    (repo / "articles" / "bad.md").write_text(_article("変な日付", published_at='"2026/08/01"'))
    with pytest.raises(ValueError, match="unparseable published_at"):
        gai.load_articles(repo)


def test_en_slug():
    assert gai._en_slug("articles-en/foo-en.md") == "foo"
    assert gai._en_slug("articles-en/foo.md") == "foo"
    assert gai._en_slug("articles-en/agent-essence-is-memory.md") == "agent-essence-is-memory"


def test_norm_date_accepts_yaml_parsed_datetime():
    from datetime import date, datetime

    assert gai._norm_date(datetime(2026, 8, 1, 9, 5), "s") == "2026-08-01 09:05"
    assert gai._norm_date(date(2026, 8, 1), "s") == "2026-08-01 00:00"
    assert gai._norm_date("2026-08-01T22:00", "s") == "2026-08-01 22:00"


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------


def test_render_index_groups_by_month_and_links(repo: Path):
    text = gai.render_index(gai.load_articles(repo), _corpus(repo))
    assert text.startswith(gai.GENERATED_NOTE)
    assert "[4 articles](#articles-zenn--devto)" in text
    assert "[2 idea essays](#idea-essays-note--substack)" in text and "[2 papers](#papers)" in text
    assert text.index("### 2026-08") < text.index("### 2026-07")
    assert "- **2026-08-10** [新しい記事](https://zenn.dev/shimo4228/articles/newer)" in text
    assert "EN: [Newer Article](https://dev.to/x/newer-1) · `ai` `agent`" in text
    assert "EN: [Legacy Article](../articles-en/legacy-en.md) (source)" in text
    assert "EN: — · `ai` · grew into the paper *Paper One*" in text  # older: no EN, but a paper grew from it
    assert text.endswith("\n")


def test_render_index_essays_papers_lines(repo: Path):
    text = gai.render_index(gai.load_articles(repo), _corpus(repo))
    essays = text[text.index("## Idea essays") : text.index("## Papers")]
    assert essays.index("**2026-08-01**") < essays.index("**2026-06-01**")  # newest first
    assert "JA: [エッセイA](https://note.com/u/n/a) (note)\n  EN: [Essay A](https://x.substack.com/p/a) (Substack)" in essays
    assert "JA: —\n  EN: [Essay B](https://x.substack.com/p/b) (Substack)" in essays
    papers = text[text.index("## Papers") : text.index("## Research lines")]
    assert papers.index("Paper Two") < papers.index("Paper One")
    assert "*Paper One* — Line X\n  [Zenodo](https://doi.org/10.5281/zenodo.1) · [SSRN](https://doi.org/10.2139/ssrn.1) · grew from: [older](https://zenn.dev/shimo4228/articles/older)" in papers
    assert "*Paper Two* — Line Y\n  [Zenodo](https://doi.org/10.5281/zenodo.2)\n" in papers  # no SSRN, no from
    assert "- [Line X](https://github.com/u/x) — [DOI 10.5281/zenodo.10](https://doi.org/10.5281/zenodo.10)" in text


def test_load_corpus_validates_files_and_slugs(repo: Path):
    slugs = {a.slug for a in gai.load_articles(repo)}
    (repo / "substack" / "essay-b-en.md").unlink()
    with pytest.raises(ValueError, match="essay 'essay-b' en file missing"):
        gai.load_corpus(repo, slugs)
    (repo / "scripts" / "corpus.yml").write_text("papers:\n  - {title: P, date: 2026-01-01, line: L, zenodo: x, from: [ghost]}\n")
    with pytest.raises(ValueError, match="references unknown slug 'ghost'"):
        gai.load_corpus(repo, slugs)
    (repo / "scripts" / "corpus.yml").write_text("essays:\n  - {slug: e, date: 2026-01-01}\n")
    with pytest.raises(ValueError, match="neither ja nor en"):
        gai.load_corpus(repo, slugs)


def test_render_routes_en_and_ja(repo: Path):
    arts = gai.load_articles(repo)
    routes = gai.load_routes(repo)
    en = gai.render_routes(routes, arts, "en")
    ja = gai.render_routes(routes, arts, "ja")
    assert en.startswith(gai.START) and en.endswith(gai.END)
    assert "### Route One\n\nWhy one.\n\n- [Newer Article](https://dev.to/x/newer-1)\n" in en
    assert "- [古い記事](https://zenn.dev/shimo4228/articles/older) (JP)" in en  # no EN → JP title + Zenn
    assert "- [Legacy Article](articles-en/legacy-en.md) (English source in this repo — not yet on Dev.to)" in en  # translated, not cross-posted
    assert "### 経路一\n\n理由一。\n\n- [新しい記事](https://zenn.dev/shimo4228/articles/newer)" in ja
    assert "### 経路二\n\n- [旧命名の記事]" in ja  # no reason line when absent


def test_render_routes_uses_manifest_title_fallback(repo: Path):
    (repo / "articles-en" / "legacy-en.md").unlink()
    en = gai.render_routes(gai.load_routes(repo), gai.load_articles(repo), "en")
    assert "- [Fallback Title](https://zenn.dev/shimo4228/articles/legacy) (JP)" in en


def test_render_routes_rejects_unknown_slug(repo: Path):
    (repo / "scripts" / "reading_paths.yml").write_text("routes:\n  - id: r\n    label: {en: R, ja: R}\n    articles: [ghost]\n")
    with pytest.raises(ValueError, match="unknown or unpublished slug 'ghost'"):
        gai.render_routes(gai.load_routes(repo), gai.load_articles(repo), "en")


def test_splice_replaces_only_marker_block():
    out = gai.splice(README_EN, f"{gai.START}\nnew\n{gai.END}")
    assert out == "# zenn-content\n\nintro\n\n<!-- reading-paths:start -->\nnew\n<!-- reading-paths:end -->\n\ntail\n"


def test_splice_requires_exactly_one_marker_pair():
    with pytest.raises(ValueError, match="found 0/0"):
        gai.splice("no markers", "x")
    with pytest.raises(ValueError, match="found 2/1"):
        gai.splice(f"{gai.START}{gai.START}{gai.END}", "x")


# ---------------------------------------------------------------------------
# main / --check
# ---------------------------------------------------------------------------


def test_main_writes_then_check_passes(repo: Path, capsys):
    assert gai.main(["--root", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "updated:" in out and "docs/PUBLICATIONS.md" in out and "README.md" in out
    assert (repo / "docs" / "PUBLICATIONS.md").read_text().startswith(gai.GENERATED_NOTE)
    assert "### Route One" in (repo / "README.md").read_text()
    assert "### 経路一" in (repo / "README.ja.md").read_text()
    assert "\nold\n" not in (repo / "README.md").read_text()

    assert gai.main(["--root", str(repo), "--check"]) == 0
    assert "up to date" in capsys.readouterr().out
    assert gai.main(["--root", str(repo)]) == 0
    assert "no changes" in capsys.readouterr().out


def test_check_fails_when_stale(repo: Path, capsys):
    assert gai.main(["--root", str(repo)]) == 0
    capsys.readouterr()
    (repo / "articles" / "extra.md").write_text(_article("追加", published_at="2026-08-11 09:00"))
    assert gai.main(["--root", str(repo), "--check"]) == 1
    out = capsys.readouterr().out
    assert "stale generated files" in out and "docs/PUBLICATIONS.md" in out
    assert "README.md" not in out.replace("README.ja.md", "")  # READMEs unaffected by a non-route article


def test_main_reports_source_errors_as_exit_2(repo: Path, capsys):
    (repo / "articles" / "nodate.md").write_text(_article("日付なし", published_at=None))
    assert gai.main(["--root", str(repo), "--check"]) == 2
    assert "published article without published_at" in capsys.readouterr().err
