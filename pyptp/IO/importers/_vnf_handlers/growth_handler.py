"""Handler for parsing VNF Growth sections using a declarative recipe."""

from typing import ClassVar

from pyptp.elements.mv.growth import GrowthMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class GrowthHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Growth components using a declarative recipe."""

    COMPONENT_CLS = GrowthMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
    ]
