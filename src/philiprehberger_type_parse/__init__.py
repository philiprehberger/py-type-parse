"""Parse strings into Python types intelligently — booleans, numbers, dates, None, lists."""

from __future__ import annotations

import datetime
import re

__all__ = ["parse", "parse_bool", "parse_date", "parse_list", "parse_number"]

_TRUE_VALUES = frozenset({"true", "yes", "1", "on", "y"})
_FALSE_VALUES = frozenset({"false", "no", "0", "off", "n"})

_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%d.%m.%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%Y%m%d",
)

_DATE_FORMATS_DAYFIRST = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%Y%m%d",
)

_CURRENCY_RE = re.compile(r"^[£$€¥₹]?\s*-?\s*[\d,]+\.?\d*$")
_PERCENT_RE = re.compile(r"^-?[\d,]+\.?\d*\s*%$")


def parse(value: str) -> None | bool | int | float | datetime.date | str:
    """Auto-detect and parse a string into the most appropriate Python type.

    Detection order: None -> bool -> int -> float -> date (YYYY-MM-DD) -> str.
    """
    stripped = value.strip()

    if stripped.lower() in ("none", "null", "nil", ""):
        return None

    try:
        return parse_bool(stripped)
    except ValueError:
        pass

    try:
        return parse_number(stripped)
    except ValueError:
        pass

    try:
        return parse_date(stripped)
    except ValueError:
        pass

    return stripped


def parse_bool(value: str) -> bool:
    """Parse a string into a boolean.

    Recognized true values: true, yes, 1, on, y (case-insensitive).
    Recognized false values: false, no, 0, off, n (case-insensitive).

    Raises:
        ValueError: If the string is not a recognized boolean value.
    """
    lower = value.strip().lower()
    if lower in _TRUE_VALUES:
        return True
    if lower in _FALSE_VALUES:
        return False
    raise ValueError(f"Cannot parse {value!r} as bool")


def parse_number(value: str) -> int | float:
    """Parse a string into an int or float.

    Handles comma-separated numbers, currency symbols ($, EUR, etc.),
    and percentage strings.

    Raises:
        ValueError: If the string cannot be parsed as a number.
    """
    stripped = value.strip()

    is_percent = False
    if _PERCENT_RE.match(stripped):
        is_percent = True
        stripped = stripped.rstrip().rstrip("%").strip()

    cleaned = re.sub(r"^[£$€¥₹]\s*", "", stripped)
    cleaned = cleaned.replace(",", "")

    if not cleaned:
        raise ValueError(f"Cannot parse {value!r} as number")

    try:
        num = int(cleaned)
    except ValueError:
        try:
            num = float(cleaned)
        except ValueError:
            raise ValueError(f"Cannot parse {value!r} as number") from None

    if is_percent:
        return num / 100 if isinstance(num, float) or num % 100 != 0 else num // 100

    return num


def parse_date(value: str, *, dayfirst: bool = False) -> datetime.date:
    """Parse a string into a date object.

    Supports common formats including YYYY-MM-DD, MM/DD/YYYY, DD.MM.YYYY,
    and more. Use ``dayfirst=True`` to prefer DD/MM/YYYY over MM/DD/YYYY
    for ambiguous formats.

    Raises:
        ValueError: If the string cannot be parsed as a date.
    """
    stripped = value.strip()
    formats = _DATE_FORMATS_DAYFIRST if dayfirst else _DATE_FORMATS

    for fmt in formats:
        try:
            return datetime.datetime.strptime(stripped, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Cannot parse {value!r} as date")


def parse_list(value: str, *, separator: str = ",") -> list[str]:
    """Split a string into a list of stripped, non-empty strings.

    Args:
        value: The input string to split.
        separator: The delimiter to split on. Defaults to ``","``.

    Returns:
        A list of trimmed strings with empty entries removed.
    """
    parts = value.split(separator)
    return [part.strip() for part in parts if part.strip()]
