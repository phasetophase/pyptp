from __future__ import annotations

"""Internal MV loaders: build MV dataclass instances from Excel rows."""

from typing import Any

from pyptp.ptp_log import logger

from ._excel import clean_row_dict, read_frame_with_fallback


def load_cables(path: str) -> dict[str, Any]:
    """Return by_name dict of MV CableType objects (Name-only)."""
    from pyptp.elements.mv.shared import CableType as MVCableType

    cable_frame = read_frame_with_fallback(path, sheet_name="Cable", rename={"Shortname": "ShortName"})
    by_name: dict[str, Any] = {}
    for _, row in cable_frame.iterrows():
        row_dict = clean_row_dict(row)
        name = str(row_dict.get("Name", "")).strip()
        row_dict.setdefault("Info", name)
        try:
            obj = MVCableType.deserialize(row_dict)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Skipping MV cable '%s': %s", name, exc)
            continue
        if name:
            by_name[name] = obj
    return by_name


def load_fuses(path: str) -> dict[str, Any]:
    """Return by_name dict of MV FuseType objects (Name-only)."""
    from pyptp.elements.mv.shared import FuseType as MVFuseType

    fuse_frame = read_frame_with_fallback(path, sheet_name="Fuse", rename={"Shortname": "ShortName"})
    by_name: dict[str, Any] = {}
    for _, row in fuse_frame.iterrows():
        row_dict = clean_row_dict(row)
        name = str(row_dict.get("Name", "")).strip()
        try:
            obj = MVFuseType.deserialize(row_dict)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Skipping MV fuse '%s': %s", name, exc)
            continue
        if name:
            by_name[name] = obj
    return by_name
