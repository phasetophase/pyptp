"""Handler for parsing VNF Frame sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.frame import FrameMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class FrameHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Frame components using a declarative recipe."""

    COMPONENT_CLS = FrameMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("lines", "#Line Text:", required=False),
        SectionConfig("geo_series", "#Geo ", required=False),
        SectionConfig("presentations", "#Presentation ", required=False),
        SectionConfig("extras", "#Extra Text:", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for Frame-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "general":
            return FrameMV.General
        if kwarg_name == "presentations":
            return FrameMV.FramePresentation

        return None

    def register_element(self, element: FrameMV, network: TNetworkMSType) -> None:
        """Register the frame element in the network.

        Args:
            element: The parsed frame element.
            network: The target network to register the element with.

        """
        element.register(network)
