"""Internal alias loading for Name/ShortName resolution."""

from __future__ import annotations

from ._excel import normalize_rows, read_sheet
from .exceptions import MissingSheetError


def load_alias_map(path: str, sheet: str) -> dict[str, str]:
    """Return each alias on ``sheet`` with the type Name it stands for.

    A missing sheet gives an empty mapping.
    """
    try:
        rows = normalize_rows(read_sheet(path, sheet_name=sheet, skiprows=()))
    except MissingSheetError:
        return {}
    result: dict[str, str] = {}
    for row in rows:
        if not row:
            continue
        alias = row[next(iter(row))]
        name = str(row.get("Name", "")).strip()
        if alias and name:
            result[str(alias).strip()] = name
    return result
