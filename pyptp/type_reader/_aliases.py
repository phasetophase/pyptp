from __future__ import annotations

"""Internal alias loading for Name/ShortName resolution."""

from ._excel import normalize_rows, read_sheet


def load_alias_map(path: str, sheet: str) -> dict[str, str]:
    """Return mapping of alias into a canonical Name for a sheet.

    Expects two columns where the first column is the alias, and a column 'Name'.
    Unknown/missing sheets yield an empty mapping.
    """
    rows = normalize_rows(read_sheet(path, sheet_name=sheet, skiprows=()))
    result: dict[str, str] = {}
    for row in rows:
        if not row:
            continue
        alias = row[next(iter(row))]
        name = str(row.get("Name", "")).strip()
        if alias and name:
            result[str(alias).strip()] = name
    return result
