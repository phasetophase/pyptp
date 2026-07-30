"""Excel-backed type provider for LV and MV cables and fuses."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ._aliases import load_alias_map
from ._lv import load_cables as load_lv_cables
from ._lv import load_fuses as load_lv_fuses
from ._mv import load_cables as load_mv_cables
from ._mv import load_fuses as load_mv_fuses

if TYPE_CHECKING:
    from collections.abc import Mapping

RENAME_KEYS = ("lv_cable", "mv_cable", "lv_fuse", "mv_fuse")
"""Valid keys for the ``column_renames`` argument of :class:`Types`."""


class Types:
    """Excel-backed type library for component types."""

    def __init__(
        self,
        path: str | None = None,
        *,
        column_renames: Mapping[str, Mapping[str, str]] | None = None,
    ) -> None:
        """Load the Excel workbook and build lookup indices.

        If ``path`` is None, uses environment variable ``PYPTP_TYPES_EXCEL`` when set,
        otherwise falls back to a package-relative default: ``types.xlsx`` located
        alongside this module.

        Headers are matched ignoring case, so a ``Shortname`` or ``R_C`` column
        needs no configuration.

        ``column_renames`` covers headers that are genuinely named something
        else. It maps a loader key (see :data:`RENAME_KEYS`) to a per-loader
        rename of source Excel header -> expected header, e.g.
        ``{"lv_cable": {"Weerstand": "R_c"}}``.

        Raises:
            ValueError: If ``column_renames`` contains a key not in :data:`RENAME_KEYS`.

        """
        if path is None:
            env_path = os.environ.get("PYPTP_TYPES_EXCEL")
            if env_path:
                self._path = env_path
            else:
                self._path = str(Path(__file__).with_name("types.xlsx"))
        else:
            self._path = path

        self._column_renames: dict[str, dict[str, str]] = {}
        for key, mapping in (column_renames or {}).items():
            if key not in RENAME_KEYS:
                msg = f"Unknown column_renames key {key!r}; expected one of {', '.join(RENAME_KEYS)}"
                raise ValueError(msg)
            self._column_renames[key] = dict(mapping)

        self._lv_cable_by_name: dict[str, Any] = {}
        self._lv_fuse_by_name: dict[str, Any] = {}

        self._mv_cable_by_name: dict[str, Any] = {}
        self._mv_fuse_by_name: dict[str, Any] = {}

        self._cable_alias: dict[str, str] = {}
        self._fuse_alias: dict[str, str] = {}

        self._load_aliases()
        self._load_cables()
        self._load_fuses()

    def get_lv_cable(self, name: str) -> object | None:
        """Return an LV CableType by Name or alias (Name-only resolution)."""
        from pyptp.elements.lv.shared import CableType as LVCableType

        obj = self._resolve(name, self._lv_cable_by_name, self._cable_alias)
        if obj is None:
            return None
        if isinstance(obj, LVCableType):
            return obj
        return None

    def get_mv_cable(self, name: str) -> object | None:
        """Return an MV CableType by Name or alias (Name-only resolution)."""
        from pyptp.elements.mv.shared import CableType as MVCableType

        obj = self._resolve(name, self._mv_cable_by_name, self._cable_alias)
        if obj is None:
            return None
        if isinstance(obj, MVCableType):
            return obj
        return None

    def get_lv_fuse(self, name: str) -> object | None:
        """Return an LV FuseType by Name or alias (Name-only resolution)."""
        from pyptp.elements.lv.shared import FuseType as LVFuseType

        obj = self._resolve(name, self._lv_fuse_by_name, self._fuse_alias)
        if obj is None:
            return None
        if isinstance(obj, LVFuseType):
            return obj
        return None

    def get_mv_fuse(self, name: str) -> object | None:
        """Return an MV FuseType by Name or alias (Name-only resolution)."""
        from pyptp.elements.mv.shared import FuseType as MVFuseType

        obj = self._resolve(name, self._mv_fuse_by_name, self._fuse_alias)
        if obj is None:
            return None
        if isinstance(obj, MVFuseType):
            return obj
        return None

    def _load_aliases(self) -> None:
        self._cable_alias = load_alias_map(self._path, "Cable alias")
        self._fuse_alias = load_alias_map(self._path, "Fuse alias")

    def _load_cables(self) -> None:
        lv_by_name = load_lv_cables(self._path, rename=self._column_renames.get("lv_cable"))
        mv_by_name = load_mv_cables(self._path, rename=self._column_renames.get("mv_cable"))
        self._lv_cable_by_name.update(lv_by_name)
        self._mv_cable_by_name.update(mv_by_name)

    def _load_fuses(self) -> None:
        lv_by_name = load_lv_fuses(self._path, rename=self._column_renames.get("lv_fuse"))
        mv_by_name = load_mv_fuses(self._path, rename=self._column_renames.get("mv_fuse"))
        self._lv_fuse_by_name.update(lv_by_name)
        self._mv_fuse_by_name.update(mv_by_name)

    @staticmethod
    def _resolve(
        name: str,
        by_name: dict[str, object],
        alias: dict[str, str],
    ) -> object | None:
        key = str(name).strip()
        if not key:
            return None

        if key in by_name:
            return by_name[key]

        if key in alias:
            actual_name = alias[key]
            obj = by_name.get(actual_name)
            if obj is not None:
                return obj

        return None
