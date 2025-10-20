from __future__ import annotations

"""Internal helpers for reading Excel-based type sheets."""


from typing import TYPE_CHECKING

import pandas as pd

from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from collections.abc import Iterable


def read_sheet(
    path: str,
    sheet_name: str,
    *,
    index_col: int | None = None,
    skiprows: Iterable[int] | None = (1,),
) -> pd.DataFrame:
    """Read a sheet, on failure returns an empty DataFrame."""
    try:
        return pd.read_excel(path, sheet_name=sheet_name, index_col=index_col, skiprows=list(skiprows or []))
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed reading sheet %s from %s: %s", sheet_name, path, exc)
        return pd.DataFrame()


def normalize_frame(frame: pd.DataFrame, rename: dict[str, str] | None = None) -> pd.DataFrame:
    """Drop-all-empty rows and apply a simple rename mapping."""
    if frame.empty:
        return frame
    if rename:
        frame = frame.rename(columns=rename)
    return frame.dropna(axis="index", how="all")


def read_frame_with_fallback(path: str, sheet_name: str, rename: dict[str, str]) -> pd.DataFrame:
    """Read sheet trying (1) unit-row skip, then (2) no-skip fallback."""
    frame = normalize_frame(read_sheet(path, sheet_name=sheet_name, index_col=None, skiprows=(1,)), rename=rename)
    if not frame.empty and ("Name" in frame.columns or "ShortName" in frame.columns):
        return frame
    # Fallback without skiprows
    return normalize_frame(read_sheet(path, sheet_name=sheet_name, index_col=None, skiprows=()), rename=rename)


def clean_row_dict(row: pd.Series) -> dict[str, object]:
    """Return a dict[str, object] from a Series, filtering out NaNs and coercing keys to str."""
    clean: dict[str, object] = {}
    for key, value in row.items():
        if pd.notna(value):
            clean[str(key)] = value
    return clean
