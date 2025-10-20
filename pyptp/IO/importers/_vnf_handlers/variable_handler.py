"""Handler for parsing VNF Variable sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.variable import VariableMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class VariableHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Variable components using a declarative recipe."""

    COMPONENT_CLS = VariableMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("value", "#Variable ", required=True),
    ]

    def post_process_element(self, element: VariableMV, network: TNetworkMSType) -> None:
        """Post-process the variable element after parsing.

        Variables are stored in the network variables list rather than a GUID-indexed dict.

        Args:
            element: The parsed variable element.
            network: The target network to register the element with.

        """
        network.variables.append(element)
