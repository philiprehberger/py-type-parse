# philiprehberger-type-parse

[![Tests](https://github.com/philiprehberger/py-type-parse/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-type-parse/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-type-parse.svg)](https://pypi.org/project/philiprehberger-type-parse/)
[![License](https://img.shields.io/github/license/philiprehberger/py-type-parse)](LICENSE)

Parse strings into Python types intelligently — booleans, numbers, dates, datetimes, UUIDs, filesizes, None, lists.

## Installation

```bash
pip install philiprehberger-type-parse
```

## Usage

```python
from philiprehberger_type_parse import parse

parse("true")        # True
parse("42")          # 42
parse("3.14")        # 3.14
parse("2026-03-15")  # datetime.date(2026, 3, 15)
parse("none")        # None
parse("hello")       # "hello"
```

### Boolean Parsing

```python
from philiprehberger_type_parse import parse_bool

parse_bool("yes")    # True
parse_bool("off")    # False
parse_bool("1")      # True
```

### Number Parsing

```python
from philiprehberger_type_parse import parse_number

parse_number("1,234")     # 1234
parse_number("$19.99")    # 19.99
parse_number("50%")       # 50
```

### Date Parsing

```python
from philiprehberger_type_parse import parse_date

parse_date("2026-03-15")              # datetime.date(2026, 3, 15)
parse_date("15.03.2026", dayfirst=True)  # datetime.date(2026, 3, 15)
parse_date("March 15, 2026")          # datetime.date(2026, 3, 15)
```

### Datetime Parsing

```python
from philiprehberger_type_parse import parse_datetime

parse_datetime("2026-03-16 14:30:00")          # datetime(2026, 3, 16, 14, 30)
parse_datetime("2026-03-16T14:30:00Z")         # datetime(2026, 3, 16, 14, 30, tzinfo=UTC)
parse_datetime("2026-03-16T14:30:00+02:00")    # datetime with +02:00 offset
parse_datetime("Mar 16, 2026 2:30 PM")         # datetime(2026, 3, 16, 14, 30)
```

### Time Parsing

```python
from philiprehberger_type_parse import parse_time

parse_time("14:30")             # time(14, 30)
parse_time("2:30 PM")           # time(14, 30)
parse_time("14:30:00")          # time(14, 30)
parse_time("14:30:00.123456")   # time(14, 30, 0, 123456)
```

### UUID Parsing

```python
from philiprehberger_type_parse import parse_uuid

parse_uuid("550e8400-e29b-41d4-a716-446655440000")    # UUID('550e8400-...')
parse_uuid("550e8400e29b41d4a716446655440000")         # UUID without hyphens
parse_uuid("{550e8400-e29b-41d4-a716-446655440000}")   # UUID with braces
```

### Bytes / Filesize Parsing

```python
from philiprehberger_type_parse import parse_bytes

parse_bytes("1.5 GB")     # 1500000000 (SI, base 1000)
parse_bytes("1.5 GiB")    # 1610612736 (IEC, base 1024)
parse_bytes("500 MB")     # 500000000
parse_bytes("1024 KB")    # 1024000
```

### List Parsing

```python
from philiprehberger_type_parse import parse_list

parse_list("a, b, c")                        # ["a", "b", "c"]
parse_list("x|y|z", separator="|")           # ["x", "y", "z"]
parse_list("1, true, hello", coerce=True)    # [1, True, "hello"]
parse_list("42, 3.14, none", coerce=True)    # [42, 3.14, None]
```

## API

| Function | Description |
|----------|-------------|
| `parse(value)` | Auto-detect type: None, bool, int, float, UUID, datetime, date, or str |
| `parse_bool(value)` | Parse true/yes/1/on/y or false/no/0/off/n |
| `parse_number(value)` | Parse int or float with commas, currency, percentages |
| `parse_date(value, *, dayfirst=False)` | Parse common date formats into `datetime.date` |
| `parse_datetime(value, *, dayfirst=False)` | Parse date-time strings with optional timezone into `datetime.datetime` |
| `parse_time(value)` | Parse time strings (24h, 12h AM/PM) into `datetime.time` |
| `parse_uuid(value)` | Parse UUID strings (with/without hyphens/braces) into `uuid.UUID` |
| `parse_bytes(value)` | Parse filesize strings (KB, MB, GB, KiB, MiB, GiB, etc.) to bytes |
| `parse_list(value, *, separator=",", coerce=False)` | Split into trimmed, non-empty strings; optionally auto-detect types |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
