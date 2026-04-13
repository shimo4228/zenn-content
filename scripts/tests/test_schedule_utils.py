"""Tests for _schedule_utils.py — shared publishing utilities."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pytest

from _schedule_utils import (
    JST,
    load_schedule,
    now_jst,
    save_schedule,
    setup_logging,
    validate_article_path,
)


class TestLoadSchedule:
    def test_loads_valid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "schedule.json"
        path.write_text('{"articles": []}')
        result = load_schedule(path)
        assert result == {"articles": []}

    def test_missing_file_exits(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit):
            load_schedule(tmp_path / "nonexistent.json")

    def test_invalid_json_exits(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("{invalid json")
        with pytest.raises(SystemExit):
            load_schedule(path)


class TestSaveSchedule:
    def test_writes_json(self, tmp_path: Path) -> None:
        path = tmp_path / "schedule.json"
        data = {"articles": [{"file": "test.md"}]}
        save_schedule(data, path)
        written = json.loads(path.read_text())
        assert written == data

    def test_preserves_unicode(self, tmp_path: Path) -> None:
        path = tmp_path / "schedule.json"
        data = {"articles": [{"title": "日本語テスト"}]}
        save_schedule(data, path)
        text = path.read_text()
        assert "日本語テスト" in text  # ensure_ascii=False


class TestValidateArticlePath:
    def test_valid_path(self, tmp_path: Path) -> None:
        article = tmp_path / "articles" / "test.md"
        article.parent.mkdir(parents=True)
        article.write_text("test")
        result = validate_article_path("articles/test.md", tmp_path)
        assert result == article.resolve()

    def test_path_traversal_detected(self, tmp_path: Path) -> None:
        result = validate_article_path("../../etc/passwd", tmp_path)
        assert result is None

    def test_missing_file(self, tmp_path: Path) -> None:
        result = validate_article_path("articles/missing.md", tmp_path)
        assert result is None


class TestNowJst:
    def test_returns_timezone_aware(self) -> None:
        result = now_jst()
        assert result.tzinfo is not None
        assert result.tzinfo == JST

    def test_reasonable_time(self) -> None:
        result = now_jst()
        assert result.year >= 2026


class TestSetupLogging:
    def test_adds_handlers(self, tmp_path: Path) -> None:
        test_logger = logging.getLogger("test_setup_logging")
        test_logger.handlers.clear()
        log_file = tmp_path / "test.log"
        setup_logging(test_logger, log_file)
        assert len(test_logger.handlers) == 2
        assert test_logger.level == logging.INFO

    def test_idempotent(self, tmp_path: Path) -> None:
        test_logger = logging.getLogger("test_setup_idempotent")
        test_logger.handlers.clear()
        log_file = tmp_path / "test.log"
        setup_logging(test_logger, log_file)
        setup_logging(test_logger, log_file)  # Second call should be no-op
        assert len(test_logger.handlers) == 2
