"""Handler for parsing VNF NETWORKOPTIONS sections."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.network_options import NetworkOptionsMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class NetworkOptionsHandler(DeclarativeHandler[NetworkMV]):
    """Handler for VNF NETWORKOPTIONS sections."""

    COMPONENT_CLS = NetworkOptionsMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Network Options."""
        if kwarg_name == "general":
            return NetworkOptionsMV.General
        return None

    def handle(self, model: NetworkMV, raw: str) -> None:
        """Parse NETWORKOPTIONS and register a single merged NetworkOptionsMV.

        Vision emits one ``#General`` line per profile-item list, and the
        shared ``SECTION_REGEX`` treats each ``#General`` line as a separate
        section. The default ``handle`` would therefore build one
        ``NetworkOptionsMV`` per line and register each in turn, and since
        ``NetworkOptionsMV.register`` is a singleton replace, only the last
        line's properties would survive. Merge every ``#General`` line's
        properties into a single dict and deserialize once.
        """
        sections = list(self.parse_sections(raw))
        if not sections:
            return

        merged: dict = {}
        for section in sections:
            for line in section.get("#General ", []):
                if line:
                    merged.update(self._parse_gnf_line_to_dict(line))

        general = NetworkOptionsMV.General.deserialize(merged)
        NetworkOptionsMV(general=general).register(model)
