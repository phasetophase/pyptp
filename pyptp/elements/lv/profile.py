"""Profile containing timefactors."""

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
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass_json
@dataclass
class ProfileLV:
    """Represents a load profile (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a profile."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        name: str = string_field()
        profile_type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
                write_quote_string("ProfileType", self.profile_type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ProfileLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                profile_type=data.get("ProfileType", ""),
            )

    @dataclass_json
    @dataclass
    class ProfileType(DataClassJsonMixin):
        """Time factors for a profile."""

        sort: int = -3456
        f: list[float] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize ProfileType properties."""
            props = [write_integer("Sort", self.sort)]
            props.extend([write_double_no_skip(f"f{i + 1}", factor) for i, factor in enumerate(self.f)])
            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> ProfileLV.ProfileType:
            """Deserialize ProfileType properties."""
            # Extract f values from data
            f_values = []
            i = 1
            while f"f{i}" in data:
                value = data[f"f{i}"]
                value = float(value.replace(",", ".")) if isinstance(value, str) else float(value)
                f_values.append(value)
                i += 1

            return cls(
                sort=data.get("Sort", -3456),
                f=f_values,
            )

    general: General
    type: ProfileType

    def register(self, network: NetworkLV) -> None:
        """Will add profile to the network."""
        if self.general.guid in network.profiles:
            logger.critical("Profile %s already exists, overwriting", self.general.guid)
        network.profiles[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the profile to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.append(f"#ProfileType {self.type.serialize()}")
        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ProfileLV:
        """Deserialization of the profile from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TProfileLS: The deserialized profile

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        profile_type_data = data.get("profileType", [{}])[0] if data.get("profileType") else {}
        profile_type = cls.ProfileType.deserialize(profile_type_data)

        return cls(
            general=general,
            type=profile_type,
        )
