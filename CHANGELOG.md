# Changelog

## 0.2.0 (2026-03-16)

- Add `parse_datetime()` with timezone support
- Add `parse_time()` for time-only strings
- Add `parse_uuid()` for UUID/GUID strings
- Add `parse_bytes()` for filesize strings (KB, MB, GB, KiB, MiB, etc.)
- Add `coerce` parameter to `parse_list()` for automatic type conversion
- Include UUID and datetime in `parse()` auto-detection chain

## 0.1.5

- Add basic import test

## 0.1.4

- Add Development section to README

## 0.1.1

- Re-release for PyPI publishing

## 0.1.0 (2026-03-15)

- Initial release
- `parse()` auto-detects None, bool, int, float, date, or str
- `parse_bool()` handles true/yes/1/on/y and false/no/0/off/n
- `parse_number()` supports commas, currency symbols, and percentages
- `parse_date()` parses common date formats with optional dayfirst mode
- `parse_list()` splits strings into trimmed, non-empty lists
