"""Handler for parsing VNF Node sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.node import NodeMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class NodeHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Node components using a declarative recipe."""

    COMPONENT_CLS = NodeMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("railtype", "#Railtype "),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("fields", "#Field "),
        SectionConfig("customer", "#Customer "),
        SectionConfig("installation", "#Installation "),
        SectionConfig("icon", "#Icon "),
        SectionConfig("differential_protection", "#DifferentialProtection "),
        SectionConfig("differential_protection_switches", "#DifferentialProtectionSwitch "),
        SectionConfig("differential_protection_transfer_trip_switch", "#DifferentialProtectionTransferTripSwitch "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Node-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import NodePresentation

            return NodePresentation
        if kwarg_name == "railtype":
            return NodeMV.Railtype
        if kwarg_name == "fields":
            return NodeMV.Field
        if kwarg_name == "customer":
            return NodeMV.Customer
        if kwarg_name == "installation":
            return NodeMV.Installation
        if kwarg_name == "icon":
            return NodeMV.Icon
        if kwarg_name == "differential_protection":
            return NodeMV.DifferentialProtection
        if kwarg_name == "differential_protection_switches":
            return NodeMV.DifferentialProtectionSwitch
        if kwarg_name == "differential_protection_transfer_trip_switch":
            return NodeMV.DifferentialProtectionTransferTripSwitch
        return None
