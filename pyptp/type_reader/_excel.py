from __future__ import annotations

"""Internal helpers for reading Excel-based type sheets."""


from typing import TYPE_CHECKING

from openpyxl import load_workbook

from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from collections.abc import Iterable


def read_sheet(
    path: str,
    sheet_name: str,
    *,
    skiprows: Iterable[int] | None = (1,),
) -> list[dict[str, object]]:
    """Read a sheet into a list of header->value row dicts; on failure returns an empty list."""
    skip = set(skiprows or ())
    wb = None
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
        if sheet_name not in wb.sheetnames:
            return []
        ws = wb[sheet_name]
        header: list[object] | None = None
        rows: list[dict[str, object]] = []
        for index, values in enumerate(ws.iter_rows(values_only=True)):
            if index in skip:
                continue
            if header is None:
                header = list(values)
                continue
            rows.append({str(col): val for col, val in zip(header, values, strict=False) if col is not None})
        return rows
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed reading sheet %s from %s: %s", sheet_name, path, exc)
        return []
    finally:
        if wb is not None:
            wb.close()


def normalize_rows(
    rows: list[dict[str, object]],
    rename: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    """Drop all-empty rows and apply a simple key rename mapping."""
    normalized: list[dict[str, object]] = []
    for row in rows:
        if all(value is None for value in row.values()):
            continue
        if rename:
            normalized.append({rename.get(key, key): value for key, value in row.items()})
        else:
            normalized.append(row)
    return normalized


def read_frame_with_fallback(
    path: str,
    sheet_name: str,
    rename: dict[str, str],
) -> list[dict[str, object]]:
    """Read sheet trying (1) unit-row skip, then (2) no-skip fallback."""
    rows = normalize_rows(read_sheet(path, sheet_name=sheet_name, skiprows=(1,)), rename=rename)
    if rows and ("Name" in rows[0] or "ShortName" in rows[0]):
        return rows
    # Fallback without skiprows
    return normalize_rows(read_sheet(path, sheet_name=sheet_name, skiprows=()), rename=rename)


def clean_row_dict(row: dict[str, object]) -> dict[str, object]:
    """Return a dict[str, object] from a row dict, filtering out None values and coercing keys to str."""
    clean: dict[str, object] = {}
    for key, value in row.items():
        if value is not None:
            clean[str(key)] = value
    return clean
