from __future__ import annotations

"""Internal alias loading for Name/ShortName resolution."""

from ._excel import normalize_frame, read_sheet


def load_alias_map(path: str, sheet: str) -> dict[str, str]:
    """Return mapping of alias into a canonical Name for a sheet.

    Expects two columns where index is the alias, and a column 'Name'.
    Unknown/missing sheets yield an empty mapping.
    """
    frame = read_sheet(path, sheet_name=sheet, index_col=0, skiprows=())
    frame = normalize_frame(frame)
    result: dict[str, str] = {}
    for alias, row in frame.iterrows():
        name = str(row.get("Name", "")).strip()
        if alias and name:
            result[str(alias).strip()] = name
    return result
