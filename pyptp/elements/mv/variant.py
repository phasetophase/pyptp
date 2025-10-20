"""Variant (Other)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import NIL_GUID, decode_guid, encode_guid, string_field
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean_no_skip,
    write_guid,
    write_integer_no_skip,
    write_quote_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.element_utils import Guid
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class VariantMV:
    """Represents a variant object (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a variant."""

        name: str = string_field()
        description: str = string_field()
        message: str = string_field()
        related_scenarios: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_quote_string_no_skip("Name", self.name),
                write_quote_string_no_skip("Description", self.description),
                write_quote_string_no_skip("Message", self.message),
                write_quote_string_no_skip("RelatedScenarios", self.related_scenarios),
            )

        @classmethod
        def deserialize(cls, data: dict) -> VariantMV.General:
            """Deserialize General properties."""
            return cls(
                name=data.get("Name", ""),
                description=data.get("Description", ""),
                message=data.get("Message", ""),
                related_scenarios=data.get("RelatedScenarios", ""),
            )

    @dataclass_json
    @dataclass
    class VariantItem(DataClassJsonMixin):
        """Variant item."""

        date: int = 0
        vision_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        present: bool = False
        comment: str = string_field()

        def serialize(self) -> str:
            """Serialize VariantItem properties."""
            return serialize_properties(
                write_integer_no_skip("Date", self.date),
                write_guid("VisionObject", self.vision_object) if self.vision_object != NIL_GUID else "",
                write_boolean_no_skip("Present", value=self.present),
                write_quote_string_no_skip("Comment", self.comment),
            )

        @classmethod
        def deserialize(cls, data: dict) -> VariantMV.VariantItem:
            """Deserialize VariantItem properties."""
            return cls(
                date=data.get("Date", 0),
                vision_object=decode_guid(data.get("VisionObject", str(NIL_GUID))),
                present=data.get("Present", False),
                comment=data.get("Comment", ""),
            )

    general: General
    variant_items: list[VariantItem] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Will add variant to the network."""
        key = self.general.name
        if key in network.variants:
            logger.critical("Variant %s already exists, overwriting", key)
        network.variants[key] = self

    def serialize(self) -> str:
        """Serialize the variant to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#VariantItem {item.serialize()}" for item in self.variant_items)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> VariantMV:
        """Deserialization of the variant from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TVariantMS: The deserialized variant

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        variant_items_data = data.get("variant_items", [])
        variant_items = []
        for item_data in variant_items_data:
            item = cls.VariantItem.deserialize(item_data)
            variant_items.append(item)

        return cls(
            general=general,
            variant_items=variant_items,
        )
