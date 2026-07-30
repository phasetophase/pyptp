from __future__ import annotations

"""Internal LV loaders: build LV dataclass instances from Excel rows (Name-only)."""

from typing import Any

from pyptp.ptp_log import logger

from ._excel import clean_row_dict, read_type_sheet

# Vision's type reader accepts both a _T and a _O suffix for these columns
# (leestypen.pas). The GNF property name uses _o, so only _T needs a rename.
DEFAULT_CABLE_RENAME = {
    "R_CC_T": "R_cc_o",
    "X_CC_T": "X_cc_o",
    "R_CH_T": "R_ch_o",
    "X_CH_T": "X_ch_o",
    "R_HH_T": "R_hh_o",
    "X_HH_T": "X_hh_o",
}


def load_cables(path: str, rename: dict[str, str] | None = None) -> dict[str, Any]:
    """Return by_name dict of LV CableType objects (Name-only).

    ``rename`` maps source Excel headers to expected headers, for headers that
    are genuinely named something else; entries extend (and override)
    :data:`DEFAULT_CABLE_RENAME`. Headers that differ only in case need no
    rename.
    """
    from pyptp.elements.lv.shared import CableType as LVCableType

    cable_rows = read_type_sheet(path, sheet_name="Cable", rename={**DEFAULT_CABLE_RENAME, **(rename or {})})
    by_name: dict[str, Any] = {}
    for row in cable_rows:
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


def load_fuses(path: str, rename: dict[str, str] | None = None) -> dict[str, Any]:
    """Return by_name dict of LV FuseType objects (Name-only).

    ``rename`` maps source Excel headers to expected headers, for headers that
    are genuinely named something else. Headers that differ only in case need
    no rename.
    """
    from pyptp.elements.lv.shared import FuseType as LVFuseType

    fuse_rows = read_type_sheet(path, sheet_name="Fuse", rename=rename)
    by_name: dict[str, Any] = {}
    for row in fuse_rows:
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
