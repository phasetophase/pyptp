from __future__ import annotations

"""Internal LV loaders: build LV dataclass instances from Excel rows (Name-only)."""

from typing import Any

from pyptp.ptp_log import logger

from ._excel import clean_row_dict, read_frame_with_fallback


def load_cables(path: str) -> dict[str, Any]:
    """Return by_name dict of LV CableType objects (Name-only)."""
    from pyptp.elements.lv.shared import CableType as LVCableType

    cable_frame = read_frame_with_fallback(
        path,
        sheet_name="Cable",
        rename={"Shortname": "ShortName", "Tan_delta": "TanDelta"},
    )
    by_name: dict[str, Any] = {}
    for _, row in cable_frame.iterrows():
        row_dict = clean_row_dict(row)
        name = str(row_dict.get("Name", "")).strip()
        try:
            obj = LVCableType.deserialize(row_dict)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Skipping LV cable '%s': %s", name, exc)
            continue
        if name:
            by_name[name] = obj
    return by_name


def load_fuses(path: str) -> dict[str, Any]:
    """Return by_name dict of LV FuseType objects (Name-only)."""
    from pyptp.elements.lv.shared import FuseType as LVFuseType

    fuse_frame = read_frame_with_fallback(path, sheet_name="Fuse", rename={"Shortname": "ShortName"})
    by_name: dict[str, Any] = {}
    for _, row in fuse_frame.iterrows():
        row_dict = clean_row_dict(row)
        name = str(row_dict.get("Name", "")).strip()
        try:
            obj = LVFuseType.deserialize(row_dict)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Skipping LV fuse '%s': %s", name, exc)
            continue
        if name:
            by_name[name] = obj
    return by_name
