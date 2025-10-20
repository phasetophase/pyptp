"""Load Behaviour (Profile)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import Guid, decode_guid, encode_guid, string_field
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class LoadBehaviourMV:
    """Represents a load behaviour profile (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a load behaviour profile."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        name: str = string_field()
        constant_p: int = 0
        constant_q: int = 0

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
                write_integer("ConstantP", self.constant_p),
                write_integer("ConstantQ", self.constant_q),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LoadBehaviourMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                constant_p=data.get("ConstantP", 0),
                constant_q=data.get("ConstantQ", 0),
            )

    general: General

    def register(self, network: NetworkMV) -> None:
        """Will add load behaviour to the network."""
        if self.general.guid in network.load_behaviours:
            logger.critical("Load Behaviour %s already exists, overwriting", self.general.guid)
        network.load_behaviours[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the load behaviour to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> LoadBehaviourMV:
        """Deserialization of the load behaviour from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TLoadBehaviourMS: The deserialized load behaviour

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        return cls(
            general=general,
        )
