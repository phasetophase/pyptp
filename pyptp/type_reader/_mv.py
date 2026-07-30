from __future__ import annotations

"""Internal MV loaders: build MV dataclass instances from Excel rows."""

from typing import Any

from pyptp.ptp_log import logger

from ._excel import clean_row_dict, read_type_sheet

DEFAULT_CABLE_RENAME = {
    # Workbook headers that differ from the VNF property name by more than
    # case. Vision's own type reader accepts these same spellings.
    "Tan_delta": "TanDelta",
    "VoP": "PulseVelocity",
}


def load_cables(path: str, rename: dict[str, str] | None = None) -> dict[str, Any]:
    """Return by_name dict of MV CableType objects (Name-only).

    ``rename`` maps source Excel headers to expected headers, for headers that
    are genuinely named something else; entries extend (and override)
    :data:`DEFAULT_CABLE_RENAME`. Headers that differ only in case need no
    rename.
    """
    from pyptp.elements.mv.shared import CableType as MVCableType

    cable_rows = read_type_sheet(path, sheet_name="Cable", rename={**DEFAULT_CABLE_RENAME, **(rename or {})})
    by_name: dict[str, Any] = {}
    for row in cable_rows:
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


def load_fuses(path: str, rename: dict[str, str] | None = None) -> dict[str, Any]:
    """Return by_name dict of MV FuseType objects (Name-only).

    ``rename`` maps source Excel headers to expected headers, for headers that
    are genuinely named something else. Headers that differ only in case need
    no rename.
    """
    from pyptp.elements.mv.shared import FuseType as MVFuseType

    fuse_rows = read_type_sheet(path, sheet_name="Fuse", rename=rename)
    by_name: dict[str, Any] = {}
    for row in fuse_rows:
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
