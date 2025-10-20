"""Growth (Profile)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import Guid, decode_guid, encode_guid, string_field
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double,
    write_guid_no_skip,
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
        scale: list[float] | None = field(default_factory=lambda: [0] * 31)  # Scale0-Scale30 = 31 values
        growth: list[float] | None = field(default_factory=lambda: [1] * 30)  # Growth1-Growth30 = 30 values
        growth_sort: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            arr_props = []
            if self.scale:
                for i, scale_val in enumerate(self.scale, start=0):  # Start from Scale0
                    arr_props.append(write_double(f"Scale{i}", scale_val))
            if self.growth:
                for i, growth_val in enumerate(self.growth, start=1):  # Start from Growth1
                    arr_props.append(write_double(f"Growth{i}", growth_val))
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
                *arr_props,
                write_quote_string("GrowthSort", self.growth_sort),
            )

        @classmethod
        def deserialize(cls, data: dict) -> GrowthMV.General:
            """Deserialize General properties."""
            scale_values = []
            i = 0  # Start from Scale0
            while f"Scale{i}" in data:
                scale_values.append(float(data[f"Scale{i}"]))
                i += 1

            growth_values = []
            i = 1  # Start from Growth1
            while f"Growth{i}" in data:
                growth_values.append(float(data[f"Growth{i}"]))
                i += 1

            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                scale=scale_values if scale_values else [0.0] * 31,  # Scale0-Scale30 = 31 values
                growth=growth_values if growth_values else [1.0] * 30,  # Growth1-Growth30 = 30 values
                growth_sort=data.get("GrowthSort", ""),
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
