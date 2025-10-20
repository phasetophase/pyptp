"""Handler for parsing VNF Mutual sections using a declarative recipe.

Mutual elements represent electromagnetic coupling between transmission lines.
"""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.mutual import MutualMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class MutualHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Mutual components using a declarative recipe.

    Mutual elements only contain Line1, Line2, R00, and X00 properties
    with no presentation, extras, notes, or other sections.
    """

    COMPONENT_CLS = MutualMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
    ]
