"""Tests for parse_many batch parsing."""

from __future__ import annotations

import datetime
import uuid

import pytest

from philiprehberger_type_parse import parse_many


def test_auto_detect_each_element() -> None:
    result = parse_many(["1", "true", "hello"])
    assert result == [1, True, "hello"]


def test_target_type_int() -> None:
    assert parse_many(["1", "2", "3"], target_type=int) == [1, 2, 3]


def test_target_type_float() -> None:
    assert parse_many(["1.5", "2", "3.25"], target_type=float) == [1.5, 2.0, 3.25]


def test_target_type_bool() -> None:
    assert parse_many(["yes", "no", "on", "off"], target_type=bool) == [True, False, True, False]


def test_target_type_str_strips_whitespace() -> None:
    assert parse_many(["  hi  ", "there"], target_type=str) == ["hi", "there"]


def test_target_type_uuid() -> None:
    u = "12345678-1234-5678-1234-567812345678"
    result = parse_many([u], target_type=uuid.UUID)
    assert result == [uuid.UUID(u)]


def test_target_type_date() -> None:
    result = parse_many(["2026-03-15", "2026-04-01"], target_type=datetime.date)
    assert result == [datetime.date(2026, 3, 15), datetime.date(2026, 4, 1)]


def test_target_type_datetime() -> None:
    result = parse_many(["2026-03-15 10:30:00"], target_type=datetime.datetime)
    assert result == [datetime.datetime(2026, 3, 15, 10, 30, 0)]


def test_unsupported_target_type_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported target_type"):
        parse_many(["1"], target_type=list)


def test_empty_list_returns_empty() -> None:
    assert parse_many([]) == []
    assert parse_many([], target_type=int) == []
