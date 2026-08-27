"""Tests for zenn_evidence.py — the deterministic Zenn article evidence extractor.

The false-positive regressions at the bottom are the point of the file: every
one of them fired against the real corpus on 2026-08-27 and had to be excluded
by measurement, not by guessing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import zenn_evidence as ze

CANONICAL = "https://github.com/shimo4228/zenn-content/blob/main/articles"


def article(
    slug: str = "sample",
    *,
    title: str = "短いタイトル",
    emoji: str = "🤖",
    type_: str = "tech",
    topics: str = '["claude", "ai"]',
    published: bool = True,
    published_at: str | None = "2026-08-01 09:00",
    body: str = "\n## 見出し\n\n本文です。\n",
    related: str | None = None,
) -> str:
    fm = [
        f'title: "{title}"',
        f'emoji: "{emoji}"',
        f'type: "{type_}"',
        f"topics: {topics}",
        f"published: {'true' if published else 'false'}",
    ]
    if published_at is not None:
        fm.append(f"published_at: {published_at}")
    if related is None:
        related = (
            "\n## 関連リンク\n\n"
            f"- [この記事のMarkdown正本（GitHub）]({CANONICAL}/{slug}.md) — 索引も同じリポジトリ\n"
            "- [著者のGitHub](https://github.com/shimo4228) — DOI 付きの研究リポジトリ一覧\n"
        )
    return "---\n" + "\n".join(fm) + "\n---\n" + body + related


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "articles").mkdir()
    (tmp_path / "images").mkdir()
    return tmp_path


def write(repo: Path, slug: str, text: str) -> Path:
    p = repo / "articles" / f"{slug}.md"
    p.write_text(text)
    return p


def rules(result: dict, key: str = "deviations") -> list[str]:
    return [d["rule"] for d in result[key]]


# --- clean baseline -------------------------------------------------------


def test_clean_article_has_no_deviations(repo: Path) -> None:
    p = write(repo, "sample", article())
    result = ze.evaluate(p, repo)
    assert result["deviations"] == []
    assert result["grandfathered"] == []
    assert result["published"] is True
    assert result["slug"] == "sample"


def test_file_path_is_relative_to_root(repo: Path) -> None:
    p = write(repo, "sample", article())
    assert ze.evaluate(p, repo)["file"] == "articles/sample.md"


# --- frontmatter ----------------------------------------------------------


def test_missing_published_at_when_published(repo: Path) -> None:
    p = write(repo, "sample", article(published_at=None))
    assert "published-at-missing" in rules(ze.evaluate(p, repo))


def test_draft_without_published_at_is_fine(repo: Path) -> None:
    p = write(repo, "sample", article(published=False, published_at=None))
    assert "published-at-missing" not in rules(ze.evaluate(p, repo))


@pytest.mark.parametrize("value", ["2026/08/01 09:00", "2026-08-01 09:00:00", "2026-08-01"])
def test_published_at_format_rejected(repo: Path, value: str) -> None:
    p = write(repo, "sample", article(published_at=value))
    assert "published-at-format" in rules(ze.evaluate(p, repo))


def test_topics_count_and_case(repo: Path) -> None:
    p = write(repo, "sample", article(topics='["A", "b", "c", "d", "e", "f"]'))
    found = rules(ze.evaluate(p, repo))
    assert "topics-count" in found
    assert "topics-not-lowercase" in found


def test_type_must_be_tech_or_idea(repo: Path) -> None:
    p = write(repo, "sample", article(type_="essay"))
    assert "type-invalid" in rules(ze.evaluate(p, repo))


def test_emoji_must_be_single(repo: Path) -> None:
    p = write(repo, "sample", article(emoji="🤖🧠"))
    assert "emoji-not-single" in rules(ze.evaluate(p, repo))


def test_zwj_emoji_counts_as_one(repo: Path) -> None:
    """A ZWJ sequence renders as one glyph and must not read as several."""
    p = write(repo, "sample", article(emoji="👨‍💻"))
    assert "emoji-not-single" not in rules(ze.evaluate(p, repo))


def test_missing_frontmatter_field(repo: Path) -> None:
    text = article().replace('emoji: "🤖"\n', "")
    p = write(repo, "sample", text)
    result = ze.evaluate(p, repo)
    assert any(d.get("field") == "emoji" for d in result["deviations"])


def test_title_over_hard_limit_is_grandfathered_when_published(repo: Path) -> None:
    p = write(repo, "sample", article(title="あ" * 61))
    result = ze.evaluate(p, repo)
    assert "title-over-hard-limit" in rules(result, "grandfathered")
    assert "title-over-hard-limit" not in rules(result)


def test_title_over_hard_limit_is_a_deviation_for_a_draft(repo: Path) -> None:
    p = write(repo, "sample", article(title="あ" * 61, published=False, published_at=None))
    assert "title-over-hard-limit" in rules(ze.evaluate(p, repo))


def test_title_over_soft_limit_is_info_only(repo: Path) -> None:
    p = write(repo, "sample", article(title="あ" * 55))
    result = ze.evaluate(p, repo)
    assert result["info"]["title_over_soft_limit"] is True
    assert result["deviations"] == []


# --- structure ------------------------------------------------------------


def test_code_fence_without_language(repo: Path) -> None:
    body = "\n## 見出し\n\n```\nplain text\n```\n"
    p = write(repo, "sample", article(published=False, published_at=None, body=body))
    assert "code-fence-without-language" in rules(ze.evaluate(p, repo))


def test_unbalanced_code_fence(repo: Path) -> None:
    body = "\n## 見出し\n\n```python\nx = 1\n"
    p = write(repo, "sample", article(body=body))
    assert "code-fence-unbalanced" in rules(ze.evaluate(p, repo))


def test_unbalanced_message_block(repo: Path) -> None:
    body = "\n## 見出し\n\n:::message\n補足\n"
    p = write(repo, "sample", article(body=body))
    assert "message-block-unbalanced" in rules(ze.evaluate(p, repo))


def test_body_heading_must_start_at_h2(repo: Path) -> None:
    body = "\n# 大見出し\n\n本文です。\n"
    p = write(repo, "sample", article(published=False, published_at=None, body=body))
    assert "body-heading-not-h2" in rules(ze.evaluate(p, repo))


# --- links ----------------------------------------------------------------


def test_relative_internal_link_rejected(repo: Path) -> None:
    body = "\n## 見出し\n\n[前回](/articles/other-slug) を参照。\n"
    p = write(repo, "sample", article(body=body))
    assert "internal-link-relative" in rules(ze.evaluate(p, repo))


def test_missing_image_file(repo: Path) -> None:
    body = "\n## 見出し\n\n![図](/images/missing.png)\n"
    p = write(repo, "sample", article(body=body))
    assert "image-missing" in rules(ze.evaluate(p, repo))


def test_present_image_file(repo: Path) -> None:
    (repo / "images" / "there.png").write_bytes(b"x")
    body = "\n## 見出し\n\n![図](/images/there.png)\n"
    p = write(repo, "sample", article(body=body))
    assert "image-missing" not in rules(ze.evaluate(p, repo))


def test_related_links_section_missing(repo: Path) -> None:
    p = write(repo, "sample", article(related=""))
    assert "related-links-section-missing" in rules(ze.evaluate(p, repo))


def test_canonical_link_must_match_own_slug(repo: Path) -> None:
    related = (
        "\n## 関連リンク\n\n"
        f"- [正本]({CANONICAL}/other-article.md)\n"
        "- [著者のGitHub](https://github.com/shimo4228)\n"
    )
    p = write(repo, "sample", article(related=related))
    result = ze.evaluate(p, repo)
    assert "canonical-link-missing" in rules(result)
    found = next(d for d in result["deviations"] if d["rule"] == "canonical-link-missing")
    assert found["found_slugs"] == ["other-article"]


def test_author_hub_missing(repo: Path) -> None:
    related = f"\n## 関連リンク\n\n- [正本]({CANONICAL}/sample.md)\n"
    p = write(repo, "sample", article(related=related))
    assert "author-hub-missing" in rules(ze.evaluate(p, repo))


def test_canonical_link_alone_does_not_satisfy_the_hub_rule(repo: Path) -> None:
    """The canonical URL starts with the hub URL; a prefix match would hide the gap."""
    related = f"\n## 関連リンク\n\n- [正本]({CANONICAL}/sample.md)\n"
    p = write(repo, "sample", article(related=related))
    assert "author-hub-missing" in rules(ze.evaluate(p, repo))


def test_related_links_section_stops_at_disclosure_separator(repo: Path) -> None:
    related = (
        "\n## 関連リンク\n\n"
        f"- [正本]({CANONICAL}/sample.md)\n"
        "- [著者のGitHub](https://github.com/shimo4228)\n"
        "\n---\n\n**AIメディエイト執筆について**: 本文。\n"
    )
    p = write(repo, "sample", article(related=related))
    assert ze.evaluate(p, repo)["deviations"] == []


def test_related_links_with_subheadings(repo: Path) -> None:
    related = (
        "\n## 関連リンク\n\n### リポジトリ\n\n"
        f"- [正本]({CANONICAL}/sample.md)\n"
        "- [著者のGitHub](https://github.com/shimo4228)\n"
    )
    p = write(repo, "sample", article(related=related))
    assert ze.evaluate(p, repo)["deviations"] == []


# --- safety ---------------------------------------------------------------


def test_real_personal_path_is_a_deviation(repo: Path) -> None:
    body = "\n## 見出し\n\n設定は /Users/shimomoto_tatsuya/.claude/ にあります。\n"
    p = write(repo, "sample", article(body=body))
    result = ze.evaluate(p, repo)
    assert "personal-path" in rules(result)


def test_secret_pattern_detected(repo: Path) -> None:
    body = "\n## 見出し\n\n`AKIAIOSFODNN7EXAMPLE` を使います。\n"
    p = write(repo, "sample", article(body=body))
    assert "secret-pattern" in rules(ze.evaluate(p, repo))


# --- signals --------------------------------------------------------------


def test_signals_separate_body_and_related_self_links(repo: Path) -> None:
    body = "\n## 見出し\n\n[実装](https://github.com/shimo4228/contemplative-agent) を参照。\n"
    p = write(repo, "sample", article(body=body))
    signals = ze.evaluate(p, repo)["signals"]
    assert signals["self_links"]["in_body"] == 1
    assert signals["self_links"]["in_related_links"] == 2


def test_related_links_count_sees_every_bullet(repo: Path) -> None:
    """Counted 1 for a 5-link section until the pattern got re.M."""
    related = (
        "\n## 関連リンク\n\n"
        f"- [正本]({CANONICAL}/sample.md)\n"
        "- [著者のGitHub](https://github.com/shimo4228)\n"
        "- [前作](https://zenn.dev/shimo4228/articles/other)\n"
    )
    p = write(repo, "sample", article(related=related))
    assert ze.evaluate(p, repo)["info"]["related_links_count"] == 3


def test_signals_count_register_endings(repo: Path) -> None:
    body = "\n## 見出し\n\n本文です。これも書きました。\n\nこれは断定である。\n"
    p = write(repo, "sample", article(body=body))
    signals = ze.evaluate(p, repo)["signals"]
    assert signals["register"]["polite_endings"] == 2
    assert signals["register"]["plain_endings"] == 1


# --- false-positive regressions (measured against the real corpus) --------


def test_placeholder_personal_path_is_not_a_deviation(repo: Path) -> None:
    """All 3 corpus hits on 2026-08-27 were documented placeholders, not leaks."""
    body = (
        "\n## 見出し\n\n"
        "`/Users/you/.claude/**` は説明用です。\n\n"
        "`/Users/hanma/` も便宜上の置換例です。\n"
    )
    p = write(repo, "sample", article(body=body))
    result = ze.evaluate(p, repo)
    assert "personal-path" not in rules(result)
    assert result["info"]["path_placeholders"] == ["hanma", "you"]


def test_shell_comment_in_code_block_is_not_an_h1(repo: Path) -> None:
    """`# comment` inside a fence read as a body H1 in 2 articles before the fix."""
    body = "\n```bash\n# これはコメント\nls -la\n```\n\n## 見出し\n\n本文です。\n"
    p = write(repo, "sample", article(body=body))
    assert "body-heading-not-h2" not in rules(ze.evaluate(p, repo), "grandfathered")
    assert "body-heading-not-h2" not in rules(ze.evaluate(p, repo))


def test_wrong_terminology_inside_a_code_block_is_not_a_deviation(repo: Path) -> None:
    """The single corpus hit was a prh.yml example that lists wrong forms on purpose."""
    body = "\n## 見出し\n\n```yaml\nexpected: Claude-Native\npatterns:\n  - Claude based\n```\n"
    p = write(repo, "sample", article(body=body))
    assert "terminology" not in rules(ze.evaluate(p, repo))


def test_wrong_terminology_in_prose_is_a_deviation(repo: Path) -> None:
    body = "\n## 見出し\n\nこれは Claude based な設計です。\n"
    p = write(repo, "sample", article(body=body))
    assert "terminology" in rules(ze.evaluate(p, repo))


# --- CLI ------------------------------------------------------------------


def test_cli_json_over_a_directory(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(repo, "a", article("a"))
    write(repo, "b", article("b"))
    assert ze.main([str(repo / "articles"), "--root", str(repo)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert [r["slug"] for r in payload] == ["a", "b"]


def test_cli_text_mode_reports_clean_corpus(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(repo, "a", article("a"))
    assert ze.main([str(repo / "articles"), "--root", str(repo), "--text"]) == 0
    assert "no deviations" in capsys.readouterr().out


def test_cli_exits_zero_even_with_deviations(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Evidence, not a verdict — a deviation never fails the process."""
    write(repo, "a", article("a", related=""))
    assert ze.main([str(repo / "articles"), "--root", str(repo), "--text"]) == 0
    assert "related-links-section-missing" in capsys.readouterr().out


def test_cli_missing_path_returns_2(repo: Path) -> None:
    assert ze.main([str(repo / "articles" / "nope.md"), "--root", str(repo)]) == 2


def test_cli_text_mode_labels_grandfathered_separately(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(repo, "a", article("a", title="あ" * 61))
    assert ze.main([str(repo / "articles"), "--root", str(repo), "--text"]) == 0
    out = capsys.readouterr().out
    assert "grandfathered title-over-hard-limit" in out
    assert "deviations: 0" in out


# --- online (network isolated behind --online) ----------------------------


class _Resp:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> _Resp:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def test_online_flags_dead_url(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body = "\n## 見出し\n\n[外部](https://example.com/gone) を参照。\n"
    p = write(repo, "sample", article(body=body))
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: _Resp(404))
    result = ze.evaluate(p, repo, online=True)
    dead = [d for d in result["deviations"] if d["rule"] == "url-dead"]
    assert dead and dead[0]["status"] == 404


def test_online_flags_unreachable_url(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body = "\n## 見出し\n\n[外部](https://example.invalid/x) を参照。\n"
    p = write(repo, "sample", article(body=body))

    def boom(*a: object, **k: object) -> None:
        raise OSError("dns")

    monkeypatch.setattr("urllib.request.urlopen", boom)
    assert "url-unreachable" in rules(ze.evaluate(p, repo, online=True))


def test_online_accepts_live_url(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body = "\n## 見出し\n\n[外部](https://example.com/ok) を参照。\n"
    p = write(repo, "sample", article(body=body))
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: _Resp(200))
    assert ze.evaluate(p, repo, online=True)["deviations"] == []


def test_offline_is_the_default(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No network call may happen unless --online is passed."""
    body = "\n## 見出し\n\n[外部](https://example.com/anything) を参照。\n"
    p = write(repo, "sample", article(body=body))

    def forbidden(*a: object, **k: object) -> None:
        raise AssertionError("network touched without --online")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    assert ze.evaluate(p, repo)["deviations"] == []


def test_cli_single_file(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    p = write(repo, "a", article("a"))
    assert ze.main([str(p), "--root", str(repo)]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 1
