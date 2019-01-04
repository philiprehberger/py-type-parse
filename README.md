# philiprehberger-type-parse

Parse strings into Python types intelligently — booleans, numbers, dates, None, lists.

## Install

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

### List Parsing

```python
from philiprehberger_type_parse import parse_list

parse_list("a, b, c")           # ["a", "b", "c"]
parse_list("x|y|z", separator="|")  # ["x", "y", "z"]
```

## API

| Function | Description |
|----------|-------------|
| `parse(value)` | Auto-detect type: None, bool, int, float, date, or str |
| `parse_bool(value)` | Parse true/yes/1/on/y or false/no/0/off/n |
| `parse_number(value)` | Parse int or float with commas, currency, percentages |
| `parse_date(value, *, dayfirst=False)` | Parse common date formats into `datetime.date` |
| `parse_list(value, *, separator=",")` | Split into trimmed, non-empty strings |

## License

MIT
