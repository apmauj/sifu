from datetime import date, datetime

from src.domain.excel_parsing_utils import parse_date_value, parse_decimal_value


def test_parse_date_value_with_datetime_and_date() -> None:
    assert parse_date_value(datetime(2026, 4, 19, 10, 30), ["%Y-%m-%d"]) == date(2026, 4, 19)
    assert parse_date_value(date(2026, 4, 19), ["%Y-%m-%d"]) == date(2026, 4, 19)


def test_parse_date_value_with_string_formats() -> None:
    formats = ["%d/%m/%Y", "%Y-%m-%d"]
    assert parse_date_value("19/04/2026", formats) == date(2026, 4, 19)
    assert parse_date_value("2026-04-19", formats) == date(2026, 4, 19)


def test_parse_date_value_returns_none_for_invalid_values() -> None:
    formats = ["%Y-%m-%d"]
    assert parse_date_value("", formats) is None
    assert parse_date_value("not-a-date", formats) is None
    assert parse_date_value(None, formats) is None


def test_parse_decimal_value_common_formats() -> None:
    assert parse_decimal_value("1234,56") == 1234.56
    assert parse_decimal_value("1.234,56") == 1234.56
    assert parse_decimal_value("1234.56") == 1234.56
    assert parse_decimal_value(1234.56) == 1234.56


def test_parse_decimal_value_returns_none_for_invalid_values() -> None:
    assert parse_decimal_value("") is None
    assert parse_decimal_value("abc") is None
    assert parse_decimal_value(None) is None
