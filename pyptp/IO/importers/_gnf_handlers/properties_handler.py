"""Handler for parsing GNF Properties sections using a declarative recipe."""

from typing import ClassVar

from pyptp.elements.lv.properties import PropertiesLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class PropertiesHandler(DeclarativeHandler[NetworkLV]):
    COMPONENT_CLS = PropertiesLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("system", "#System ", required=False),
        SectionConfig("network", "#Network ", required=False),
        SectionConfig("general", "#General ", required=False),
        SectionConfig("invisible", "#Invisible ", required=False),
        SectionConfig("history", "#History ", required=False),
        SectionConfig("history_items", "#HistoryItems ", required=False),
        SectionConfig("users", "#Users ", required=False),
    ]
