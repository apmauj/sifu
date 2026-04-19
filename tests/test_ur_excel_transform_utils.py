from src.domain.ur_excel_transform_utils import (
    is_ine_ur_list_format,
    map_ur_month_columns,
)


def test_is_ine_ur_list_format_detects_date_like_values():
    values = ["2026-01-01 00:00:00", "2026-02-01", "foo"]

    assert is_ine_ur_list_format(values) is True


def test_is_ine_ur_list_format_rejects_non_date_values():
    values = ["ENERO", "FEBRERO", "TOTAL"]

    assert is_ine_ur_list_format(values) is False


def test_map_ur_month_columns_maps_full_and_abbrev_month_names():
    columns = ["AÑO", "ENERO", "FEB", "SETIEMBRE", "DICIEMBRE", None, ""]

    mapped = map_ur_month_columns(columns)

    assert mapped[1] == "ENERO"
    assert mapped[2] == "FEB"
    assert mapped[9] == "SETIEMBRE"
    assert mapped[12] == "DICIEMBRE"


def test_map_ur_month_columns_ignores_unmapped_columns():
    columns = ["AÑO", "PROMEDIO", "OBSERVACIONES"]

    mapped = map_ur_month_columns(columns)

    assert mapped == {}
