"""Handler for parsing VNF Variant sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.variant import VariantMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class VariantHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Variant components using a declarative recipe."""

    COMPONENT_CLS = VariantMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("variant_items", "#VariantItem "),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Variant-specific fields."""
        if kwarg_name == "variant_items":
            return VariantMV.VariantItem
        return None
