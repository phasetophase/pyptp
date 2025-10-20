"""Rails (Other)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import Guid, decode_guid, encode_guid, string_field
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_guid_no_skip,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class RailSystemMV:
    """Represents a rail system (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a railsystem."""

        name: str = string_field()
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
            )

        @classmethod
        def deserialize(cls, data: dict) -> RailSystemMV.General:
            """Deserialize General properties."""
            return cls(
                name=data.get("Name", ""),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
            )

    @dataclass_json
    @dataclass
    class Node(DataClassJsonMixin):
        """Node."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )

        def serialize(self) -> str:
            """Serialize Node properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
            )

        @classmethod
        def deserialize(cls, data: dict) -> RailSystemMV.Node:
            """Deserialize Node properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
            )

    general: General
    nodes: list[Node]

    def register(self, network: NetworkMV) -> None:
        """Will add rail system to the network."""
        if self.general.guid in network.rail_systems:
            logger.critical("Rail System %s already exists, overwriting", self.general.guid)
        network.rail_systems[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the rails to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Node {node.serialize()}" for node in self.nodes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> RailSystemMV:
        """Deserialization of the rail system from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TRailsystemMS: The deserialized rail system

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        nodes_data = data.get("nodes", [])
        nodes = []
        for node_data in nodes_data:
            node = cls.Node.deserialize(node_data)
            nodes.append(node)

        return cls(
            general=general,
            nodes=nodes,
        )
