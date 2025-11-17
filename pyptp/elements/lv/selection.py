"""Selection object for LV networks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import Guid, config, decode_guid, encode_guid, string_field
from pyptp.elements.serialization_helpers import serialize_properties, write_guid_no_skip, write_quote_string

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass_json
@dataclass
class SelectionLV(DataClassJsonMixin):
    """Represents a selection (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a selection."""

        name: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_quote_string("Name", self.name),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SelectionLV.General:
            """Deserialize General properties."""
            return cls(
                name=data.get("Name", ""),
            )

    @dataclass_json
    @dataclass
    class Object(DataClassJsonMixin):
        """Object reference in a selection."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )

        def serialize(self) -> str:
            """Serialize Object properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SelectionLV.Object:
            """Deserialize Object properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
            )

    general: General
    objects: list[Object] = field(default_factory=list)

    def register(self, network: NetworkLV) -> None:
        """Register this selection in the given network."""
        network.selections.append(self)

    def serialize(self) -> str:
        """Serialize the selection to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Object {obj.serialize()}" for obj in self.objects)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SelectionLV:
        """Deserialize selection from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TSelectionLS: The deserialized selection

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        objects_data = data.get("objects", [])
        objects = [cls.Object.deserialize(obj_data) for obj_data in objects_data]

        return cls(
            general=general,
            objects=objects,
        )
