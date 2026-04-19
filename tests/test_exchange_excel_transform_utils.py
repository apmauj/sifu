from src.domain.exchange_excel_transform_utils import (
    EXCHANGE_RATE_CURRENCY_MAPPINGS,
    parse_exchange_rate_value,
)


def test_currency_mappings_include_supported_core_currencies():
    codes = {code for code, _, _ in EXCHANGE_RATE_CURRENCY_MAPPINGS}

    assert {"USD", "EUR", "ARS", "BRL"}.issubset(codes)


def test_parse_exchange_rate_value_parses_decimal_comma_format():
    assert parse_exchange_rate_value("41,75") == 41.75


def test_parse_exchange_rate_value_parses_thousand_comma_format():
    assert parse_exchange_rate_value("1,234.56") == 1234.56


def test_parse_exchange_rate_value_rejects_invalid_and_out_of_range_values():
    assert parse_exchange_rate_value("..") is None
    assert parse_exchange_rate_value("") is None
    assert parse_exchange_rate_value(None) is None
    assert parse_exchange_rate_value("not-a-number") is None
    assert parse_exchange_rate_value(-1) is None
    assert parse_exchange_rate_value(20000) is None
