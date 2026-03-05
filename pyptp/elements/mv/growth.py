"""Growth profile element for load forecasting in distribution networks.

Defines load growth factors and temporal scaling parameters for
long-term network planning and capacity analysis scenarios.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import Guid, decode_guid, encode_guid, string_field
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer_no_skip,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class GrowthMV:
    """Represents a growth profile (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a growth profile."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        name: str = string_field()
        dates: list[int] = field(default_factory=list)
        scale: list[float] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize General properties."""
            arr_props = []
            for i, date_val in enumerate(self.dates):
                arr_props.append(write_integer_no_skip(f"Date{i}", date_val))
            for i, scale_val in enumerate(self.scale):
                arr_props.append(write_double_no_skip(f"Scale{i}", scale_val))
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
                *arr_props,
            )

        @classmethod
        def deserialize(cls, data: dict) -> GrowthMV.General:
            """Deserialize General properties."""
            date_values = []
            i = 0
            while f"Date{i}" in data:
                date_values.append(int(data[f"Date{i}"]))
                i += 1

            scale_values = []
            i = 0
            while f"Scale{i}" in data:
                scale_values.append(float(data[f"Scale{i}"]))
                i += 1

            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                dates=date_values,
                scale=scale_values,
            )

    general: General

    def register(self, network: NetworkMV) -> None:
        """Will add growth to the network."""
        if self.general.guid in network.growths:
            logger.critical("Growth %s already exists, overwriting", self.general.guid)
        network.growths[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the growth to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> GrowthMV:
        """Deserialization of the growth from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            GrowthMV: The deserialized growth

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        return cls(
            general=general,
        )
