from collections.abc import Iterable
from typing import Any


def is_ine_ur_list_format(sample_values: Iterable[str]) -> bool:
    """Detect INE list format based on date-like values in first column."""
    return any(
        "-" in str(value) and any(char.isdigit() for char in str(value))
        for value in sample_values
    )


def map_ur_month_columns(columns: Iterable[Any]) -> dict[int, Any]:
    """Map UR month number to source dataframe column names."""
    mapping: dict[int, Any] = {}

    for col in columns:
        if col is None:
            continue

        col_str = str(col).upper().strip()
        if col_str in {"", "NAN"}:
            continue

        if "ENERO" in col_str or col_str == "ENE":
            mapping[1] = col
        elif "FEBRERO" in col_str or col_str == "FEB":
            mapping[2] = col
        elif "MARZO" in col_str or col_str == "MAR":
            mapping[3] = col
        elif "ABRIL" in col_str or col_str == "ABR":
            mapping[4] = col
        elif "MAYO" in col_str or col_str == "MAY":
            mapping[5] = col
        elif "JUNIO" in col_str or col_str == "JUN":
            mapping[6] = col
        elif "JULIO" in col_str or col_str == "JUL":
            mapping[7] = col
        elif "AGOSTO" in col_str or col_str == "AGO":
            mapping[8] = col
        elif (
            "SEPTIEMBRE" in col_str
            or "SETIEMBRE" in col_str
            or col_str == "SEP"
            or col_str == "SET"
        ):
            mapping[9] = col
        elif "OCTUBRE" in col_str or col_str == "OCT":
            mapping[10] = col
        elif "NOVIEMBRE" in col_str or col_str == "NOV":
            mapping[11] = col
        elif "DICIEMBRE" in col_str or col_str == "DIC":
            mapping[12] = col

    return mapping