"""Handler for parsing GNF Sheet sections using a declarative recipe."""

from typing import ClassVar

from pyptp.elements.lv.sheet import SheetLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV as TNetworkLSType


class SheetHandler(DeclarativeHandler[TNetworkLSType]):
    """Parses GNF Sheet components using a declarative recipe."""

    COMPONENT_CLS = SheetLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("comment", "#Comment"),
    ]
