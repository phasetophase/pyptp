"""Medium-voltage selection element for grouping network objects.

Provides named collections of network element references for batch
operations, reporting, and analysis scoping in MV distribution networks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import Guid, config, decode_guid, encode_guid, string_field
from pyptp.elements.serialization_helpers import serialize_properties, write_guid_no_skip, write_quote_string

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class SelectionMV(DataClassJsonMixin):
    """Medium-voltage selection containing grouped element references.

    Supports organizing network elements into named groups for batch
    operations, filtered analysis, and reporting purposes.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core identification properties for MV selections.

        Contains the selection name for user identification.
        """

        name: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_quote_string("Name", self.name),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SelectionMV.General:
            """Deserialize General properties."""
            return cls(
                name=data.get("Name", ""),
            )

    @dataclass_json
    @dataclass
    class Object(DataClassJsonMixin):
        """GUID reference to a selected network element.

        Links to any network element by its unique identifier.
        """

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
        def deserialize(cls, data: dict) -> SelectionMV.Object:
            """Deserialize Object properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
            )

    general: General
    objects: list[Object] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Register this selection in the given network."""
        network.selections.append(self)

    def serialize(self) -> str:
        """Serialize the selection to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Object {obj.serialize()}" for obj in self.objects)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SelectionMV:
        """Deserialize selection from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TSelectionMS: The deserialized selection

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        objects_data = data.get("objects", [])
        objects = [cls.Object.deserialize(obj_data) for obj_data in objects_data]

        return cls(
            general=general,
            objects=objects,
        )
