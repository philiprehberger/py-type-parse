# Changelog

## 0.1.1

- Re-release for PyPI publishing

## 0.1.0 (2026-03-15)

- Initial release
- `parse()` auto-detects None, bool, int, float, date, or str
- `parse_bool()` handles true/yes/1/on/y and false/no/0/off/n
- `parse_number()` supports commas, currency symbols, and percentages
- `parse_date()` parses common date formats with optional dayfirst mode
- `parse_list()` splits strings into trimmed, non-empty lists
