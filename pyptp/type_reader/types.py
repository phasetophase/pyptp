"""Excel-backed type provider for LV and MV component types."""

from __future__ import annotations

import difflib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, Self, TypeAlias, TypeVar, get_args

from pyptp.ptp_log import logger

from ._aliases import load_alias_map
from ._excel import clean_row_dict, read_type_sheet
from ._gm import gm_row_to_sections
from ._lv import DEFAULT_CABLE_RENAME as LV_CABLE_RENAME
from ._mv import DEFAULT_CABLE_RENAME as MV_CABLE_RENAME
from .exceptions import UnknownTypeError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from pyptp.elements.lv import shared as lv_shared
    from pyptp.elements.lv.gm_type import GMTypeLV
    from pyptp.elements.lv.transformer import TransformerLV
    from pyptp.elements.mv import shared as mv_shared
    from pyptp.elements.mv.fuse import FuseMV
    from pyptp.elements.mv.transformer import TransformerMV

    from ._excel import TypeRow

TypeKey: TypeAlias = Literal[
    "lv_cable",
    "mv_cable",
    "lv_fuse",
    "mv_fuse",
    "lv_transformer",
    "mv_transformer",
    "lv_gm_type",
]
"""Kind of type in the workbook, as passed to :meth:`Types.type_name` and ``column_renames``."""

RENAME_KEYS: tuple[TypeKey, ...] = get_args(TypeKey)
"""Valid keys for the ``column_renames`` argument of :class:`Types`."""

_TRAFO_RENAME = {
    # Workbook headers that differ from the GNF/VNF property name by more than
    # case.
    "Pnul": "Po",
    "Inul": "Io",
    "s1": "WindingConnection1",
    "s2": "WindingConnection2",
    "Clock": "ClockNumber",
    "Side Z0": "Side_Z0",
}


@dataclass(frozen=True)
class _Sheet:
    """Sheet, alias sheet and header renames for one kind of type."""

    sheet: str
    label: str
    alias_sheet: str | None
    rename: Mapping[str, str]


_SHEETS: dict[TypeKey, _Sheet] = {
    "lv_cable": _Sheet("Cable", "LV cable", "Cable alias", LV_CABLE_RENAME),
    "mv_cable": _Sheet("Cable", "MV cable", "Cable alias", MV_CABLE_RENAME),
    "lv_fuse": _Sheet("Fuse", "LV fuse", "Fuse alias", {}),
    "mv_fuse": _Sheet("Fuse", "MV fuse", "Fuse alias", {}),
    "lv_transformer": _Sheet("Trafo", "LV transformer", "Trafo alias", _TRAFO_RENAME),
    "mv_transformer": _Sheet("Trafo", "MV transformer", "Trafo alias", _TRAFO_RENAME),
    "lv_gm_type": _Sheet("GM", "GM", None, {}),
}


def _workbook_path(path: str | None) -> str:
    if path is not None:
        return path
    env_path = os.environ.get("PYPTP_TYPES_EXCEL")
    if env_path:
        return env_path
    return str(Path(__file__).with_name("types.xlsx"))


def _info_from_name(row: dict[str, object]) -> dict[str, object]:
    """Set ``Info`` to the Name when the row has none.

    MV cable types have a description, and the sheet has no column for it.
    """
    if "Info" not in row:
        row["Info"] = str(row.get("Name", "")).strip()
    return row


class _FromRow(Protocol):
    """A type dataclass that can be built from a header -> value row."""

    @classmethod
    def deserialize(cls, data: dict) -> Self: ...


_TypeT = TypeVar("_TypeT", bound=_FromRow)


class Types:
    """Excel-backed type library for component types.

    Sheets are read on first use and cached.
    """

    def __init__(
        self,
        path: str | None = None,
        *,
        column_renames: Mapping[str, Mapping[str, str]] | None = None,
    ) -> None:
        """Set up the type library for ``path``.

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
            FileNotFoundError: If ``path`` names no file.
            ValueError: If ``column_renames`` contains a key not in :data:`RENAME_KEYS`.

        """
        self._path = _workbook_path(path)
        if not Path(self._path).is_file():
            msg = f"Type workbook not found: {self._path}"
            raise FileNotFoundError(msg)

        self._column_renames: dict[str, dict[str, str]] = {}
        for key, mapping in (column_renames or {}).items():
            if key not in RENAME_KEYS:
                msg = f"Unknown column_renames key {key!r}; expected one of {', '.join(RENAME_KEYS)}"
                raise ValueError(msg)
            self._column_renames[key] = dict(mapping)

        self._rows_by_key: dict[str, dict[str, TypeRow]] = {}
        self._alias_by_sheet: dict[str, dict[str, str]] = {}

    def type_name(self, key: TypeKey, name: str) -> str:
        """Return the type Name for ``name``, which may be a Name or an alias.

        ``key`` says which kind of type to look in, for example ``"lv_cable"``.

        Raises:
            UnknownTypeError: If no type has that Name or alias.

        """
        rows = self._rows(key)
        wanted = name.strip()
        if wanted in rows:
            return wanted

        actual = self._alias_target(key, wanted)
        if actual is not None:
            return actual

        label = _SHEETS[key].label
        raise UnknownTypeError(self._unknown_name_message(label, wanted, rows))

    def _alias_target(self, key: TypeKey, wanted: str) -> str | None:
        """Return the Name that ``wanted`` is an alias of, when that Name is on the sheet."""
        alias_sheet = _SHEETS[key].alias_sheet
        if alias_sheet is None:
            return None
        actual = self._aliases(alias_sheet).get(wanted)
        if actual is None or actual not in self._rows(key):
            return None
        return actual

    def get_lv_cable(self, name: str) -> lv_shared.CableType:
        """Return the LV cable type for ``name``, a Name or an alias."""
        from pyptp.elements.lv.shared import CableType

        return self._get("lv_cable", CableType, name)

    def get_mv_cable(self, name: str) -> mv_shared.CableType:
        """Return the MV cable type for ``name``, a Name or an alias."""
        from pyptp.elements.mv.shared import CableType

        return self._get("mv_cable", CableType, name, adapt=_info_from_name)

    def get_lv_fuse(self, name: str) -> lv_shared.FuseType:
        """Return the LV fuse type for ``name``, a Name or an alias."""
        from pyptp.elements.lv.shared import FuseType

        return self._get("lv_fuse", FuseType, name)

    def get_mv_fuse(self, name: str) -> FuseMV.FuseType:
        """Return the MV fuse type for ``name``, a Name or an alias."""
        from pyptp.elements.mv.fuse import FuseMV

        return self._get("mv_fuse", FuseMV.FuseType, name)

    def get_lv_transformer(self, name: str) -> TransformerLV.TransformerType:
        """Return the LV transformer type for ``name``, a Name or an alias."""
        from pyptp.elements.lv.transformer import TransformerLV

        return self._get("lv_transformer", TransformerLV.TransformerType, name)

    def get_mv_transformer(self, name: str) -> TransformerMV.TransformerType:
        """Return the MV transformer type for ``name``, a Name or an alias."""
        from pyptp.elements.mv.transformer import TransformerMV

        return self._get("mv_transformer", TransformerMV.TransformerType, name)

    def get_lv_gm_type(self, name: str) -> GMTypeLV:
        """Return the GM type for ``name``.

        Adding it to a network gives it the next free number.
        """
        from pyptp.elements.lv.gm_type import GMTypeLV

        return self._get("lv_gm_type", GMTypeLV, name, adapt=gm_row_to_sections)

    def _get(
        self,
        key: TypeKey,
        cls: type[_TypeT],
        name: str,
        adapt: Callable[[dict[str, object]], dict] | None = None,
    ) -> _TypeT:
        """Return a new type object for ``name``.

        Raises:
            UnknownTypeError: If no type has that Name or alias.
            ValueError: If the row cannot be turned into a type object.

        """
        type_name = self.type_name(key, name)
        row = self._rows(key)[type_name].copy()
        try:
            data = adapt(row) if adapt else row
            return cls.deserialize(data)
        except (KeyError, TypeError, ValueError) as exc:
            msg = f"{_SHEETS[key].label} type {type_name!r} in {self._path} could not be read: {exc}"
            raise ValueError(msg) from exc

    def _rows(self, key: TypeKey) -> dict[str, TypeRow]:
        """Return the rows of one sheet by Name, reading the sheet on first use."""
        cached = self._rows_by_key.get(key)
        if cached is not None:
            return cached

        spec = _SHEETS[key]
        rename = {**spec.rename, **self._column_renames.get(key, {})}
        sheet_rows = read_type_sheet(self._path, sheet_name=spec.sheet, rename=rename)
        rows: dict[str, TypeRow] = {}
        for raw in sheet_rows:
            row = clean_row_dict(raw)
            name = str(row.get("Name", "")).strip()
            if not name:
                continue
            if name in rows:
                logger.warning(
                    "%s type %r appears more than once in %s. Using the last row", spec.label, name, self._path
                )
            rows[name] = row
        self._rows_by_key[key] = rows
        return rows

    def _aliases(self, sheet: str) -> dict[str, str]:
        alias = self._alias_by_sheet.get(sheet)
        if alias is None:
            alias = load_alias_map(self._path, sheet)
            self._alias_by_sheet[sheet] = alias
        return alias

    def _unknown_name_message(self, label: str, name: str, names: Iterable[str]) -> str:
        message = f"No {label} type named {name!r} in {self._path}"
        close = difflib.get_close_matches(name, names)
        if close:
            suggestions = ", ".join(repr(match) for match in close)
            return f"{message}. Did you mean {suggestions}?"
        return message
