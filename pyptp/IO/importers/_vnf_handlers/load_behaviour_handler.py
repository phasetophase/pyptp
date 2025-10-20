"""Handler for parsing VNF Load Behaviour sections using a declarative recipe."""

from typing import ClassVar

from pyptp.elements.mv.load_behaviour import LoadBehaviourMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class LoadBehaviourHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Load Behaviour components using a declarative recipe."""

    COMPONENT_CLS = LoadBehaviourMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
    ]
