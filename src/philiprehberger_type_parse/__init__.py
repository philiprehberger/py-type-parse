"""Parse strings into Python types intelligently — booleans, numbers, dates, datetimes, UUIDs, filesizes, None, lists."""

from __future__ import annotations

import datetime
import re
import uuid as _uuid_mod

__all__ = [
    "parse",
    "parse_bool",
    "parse_bytes",
    "parse_date",
    "parse_datetime",
    "parse_list",
    "parse_number",
    "parse_time",
    "parse_uuid",
]

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

_DATETIME_FORMATS = (
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%B %d, %Y %I:%M %p",
    "%b %d, %Y %I:%M %p",
    "%B %d, %Y %I:%M:%S %p",
    "%b %d, %Y %I:%M:%S %p",
)

_DATETIME_FORMATS_DAYFIRST = (
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%B %d, %Y %I:%M %p",
    "%b %d, %Y %I:%M %p",
    "%B %d, %Y %I:%M:%S %p",
    "%b %d, %Y %I:%M:%S %p",
)

_TIME_FORMATS = (
    "%H:%M:%S.%f",
    "%H:%M:%S",
    "%H:%M",
    "%I:%M:%S %p",
    "%I:%M %p",
)

_CURRENCY_RE = re.compile(r"^[£$€¥₹]?\s*-?\s*[\d,]+\.?\d*$")
_PERCENT_RE = re.compile(r"^-?[\d,]+\.?\d*\s*%$")

# Timezone offset pattern: +HH:MM, -HH:MM, +HHMM, -HHMM, Z
_TZ_RE = re.compile(r"(Z|[+-]\d{2}:?\d{2})$")

# UUID pattern: 32 hex chars with optional hyphens and optional braces
_UUID_RE = re.compile(
    r"^\{?[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}\}?$",
    re.IGNORECASE,
)

# Bytes/filesize units (SI and IEC)
_BYTES_UNITS: dict[str, int] = {
    "b": 1,
    "kb": 1_000,
    "mb": 1_000_000,
    "gb": 1_000_000_000,
    "tb": 1_000_000_000_000,
    "pb": 1_000_000_000_000_000,
    "kib": 1_024,
    "mib": 1_048_576,
    "gib": 1_073_741_824,
    "tib": 1_099_511_627_776,
    "pib": 1_125_899_906_842_624,
}

_BYTES_RE = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*(b|kb|mb|gb|tb|pb|kib|mib|gib|tib|pib)?\s*$",
    re.IGNORECASE,
)


def parse(
    value: str,
) -> None | bool | int | float | _uuid_mod.UUID | datetime.datetime | datetime.date | str:
    """Auto-detect and parse a string into the most appropriate Python type.

    Detection order: None -> bool -> int -> float -> uuid -> datetime -> date -> str.
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
        return parse_uuid(stripped)
    except ValueError:
        pass

    try:
        return parse_datetime(stripped)
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


def parse_datetime(value: str, *, dayfirst: bool = False) -> datetime.datetime:
    """Parse a string into a datetime object.

    Supports ISO 8601 format, common date-time patterns, and timezone
    offsets (``Z``, ``+02:00``, ``-0500``).

    Raises:
        ValueError: If the string cannot be parsed as a datetime.
    """
    stripped = value.strip()

    # Try fromisoformat first (handles most ISO 8601 including tz)
    # Python 3.11+ fromisoformat handles "Z" suffix; for 3.10 compatibility
    # we replace trailing Z with +00:00.
    iso_candidate = stripped
    if iso_candidate.upper().endswith("Z"):
        iso_candidate = iso_candidate[:-1] + "+00:00"
    try:
        return datetime.datetime.fromisoformat(iso_candidate)
    except ValueError:
        pass

    # Strip timezone suffix for format-based parsing, then re-apply
    tz_info: datetime.timezone | None = None
    core = stripped
    tz_match = _TZ_RE.search(stripped)
    if tz_match:
        tz_str = tz_match.group(1)
        core = stripped[: tz_match.start()].rstrip()
        if tz_str.upper() == "Z":
            tz_info = datetime.timezone.utc
        else:
            sign = 1 if tz_str[0] == "+" else -1
            digits = tz_str[1:].replace(":", "")
            hours, minutes = int(digits[:2]), int(digits[2:4])
            tz_info = datetime.timezone(
                datetime.timedelta(hours=sign * hours, minutes=sign * minutes)
            )

    formats = _DATETIME_FORMATS_DAYFIRST if dayfirst else _DATETIME_FORMATS
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(core, fmt)
            if tz_info is not None:
                dt = dt.replace(tzinfo=tz_info)
            return dt
        except ValueError:
            continue

    raise ValueError(f"Cannot parse {value!r} as datetime")


def parse_time(value: str) -> datetime.time:
    """Parse a string into a time object.

    Supports 24-hour (``14:30``, ``14:30:00``), 12-hour (``2:30 PM``),
    and microsecond precision (``14:30:00.123456``).

    Raises:
        ValueError: If the string cannot be parsed as a time.
    """
    stripped = value.strip()

    for fmt in _TIME_FORMATS:
        try:
            return datetime.datetime.strptime(stripped, fmt).time()
        except ValueError:
            continue

    raise ValueError(f"Cannot parse {value!r} as time")


def parse_uuid(value: str) -> _uuid_mod.UUID:
    """Parse a string into a UUID object.

    Accepts standard UUID strings with or without hyphens, and optionally
    wrapped in braces (``{...}``).

    Raises:
        ValueError: If the string is not a valid UUID.
    """
    stripped = value.strip()
    if not _UUID_RE.match(stripped):
        raise ValueError(f"Cannot parse {value!r} as UUID")
    # Remove braces if present
    cleaned = stripped.strip("{}")
    return _uuid_mod.UUID(cleaned)


def parse_bytes(value: str) -> int:
    """Parse a filesize string into a number of bytes.

    Supports SI units (KB, MB, GB, TB, PB — base 1000) and IEC units
    (KiB, MiB, GiB, TiB, PiB — base 1024). Unit matching is
    case-insensitive.

    Examples:
        >>> parse_bytes("1.5 GB")
        1500000000
        >>> parse_bytes("1.5 GiB")
        1610612736
        >>> parse_bytes("500 MB")
        500000000

    Raises:
        ValueError: If the string cannot be parsed as a filesize.
    """
    stripped = value.strip()
    match = _BYTES_RE.match(stripped)
    if not match:
        raise ValueError(f"Cannot parse {value!r} as bytes")

    number_str, unit_str = match.group(1), match.group(2)
    number = float(number_str)

    if unit_str is None:
        # Bare number, treat as bytes
        multiplier = 1
    else:
        multiplier = _BYTES_UNITS.get(unit_str.lower(), 1)

    return int(number * multiplier)


def parse_list(
    value: str, *, separator: str = ",", coerce: bool = False
) -> list[str] | list[None | bool | int | float | _uuid_mod.UUID | datetime.datetime | datetime.date | str]:
    """Split a string into a list of stripped, non-empty strings.

    Args:
        value: The input string to split.
        separator: The delimiter to split on. Defaults to ``","``.
        coerce: When ``True``, run :func:`parse` on each element to
            auto-detect types. Defaults to ``False``.

    Returns:
        A list of trimmed strings (or parsed values when *coerce* is True)
        with empty entries removed.
    """
    parts = value.split(separator)
    items = [part.strip() for part in parts if part.strip()]
    if coerce:
        return [parse(item) for item in items]
    return items
