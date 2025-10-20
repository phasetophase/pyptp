"""Profile containing timefactors for MV networks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import Guid, config, decode_guid, encode_guid, string_field
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
class ProfileMV:
    """Represents a load profile for MV networks.

    Profiles define time-varying load patterns with dynamic factor values
    based on the profile type and sort configuration.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a profile."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        name: str = string_field()
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
                write_quote_string("ProfileType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ProfileMV.General:
            """Parse General properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                type=data.get("ProfileType", ""),
            )

    @dataclass_json
    @dataclass
    class ProfileType(DataClassJsonMixin):
        """Profile type properties with dynamic factor values.

        Contains Sort value and dynamic f1, f2, f3... factor properties
        whose count depends on the Sort value according to Delphi logic:
        ABS(ReplaceInt(Sort,[-289,-865],[-288,-864]))
        """

        sort: int = 0
        f: list[float] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize ProfileType properties to VNF format.

            Dynamic properties are serialized as f1, f2, f3, ... based on the
            number of factors in the f list.

            Returns:
                Space-separated property string for VNF file section.

            """
            props = [write_integer_no_skip("Sort", self.sort)]
            props.extend([write_double_no_skip(f"f{i + 1}", factor) for i, factor in enumerate(self.f)])
            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> ProfileMV.ProfileType:
            """Parse ProfileType properties from VNF section data.

            Dynamically extracts f1, f2, f3, ... properties until no more are found.
            Handles European number format (comma decimal separator).

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized ProfileType instance with parsed properties.

            """
            f_values = []
            i = 1
            while f"f{i}" in data:
                value = data[f"f{i}"]
                value = float(value.replace(",", ".")) if isinstance(value, str) else float(value)
                f_values.append(value)
                i += 1

            return cls(
                sort=data.get("Sort", 0),
                f=f_values,
            )

    general: General
    type: ProfileType

    def register(self, network: NetworkMV) -> None:
        """Register profile in network with GUID-based indexing.

        Args:
            network: Target network for registration.

        Warns:
            Logs critical warning if GUID already exists in network.

        """
        if self.general.guid in network.profiles:
            logger.critical("Profile %s already exists, overwriting", self.general.guid)
        network.profiles[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete profile element to VNF format.

        Returns:
            Multi-line string with all element sections for VNF file.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.append(f"#ProfileType {self.type.serialize()}")
        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ProfileMV:
        """Parse complete profile element from VNF section data.

        Args:
            data: Dictionary containing parsed VNF section data with keys:
                - general: List of general property dictionaries
                - profileType: List of profile type property dictionaries

        Returns:
            Initialized TProfileMS instance with parsed properties.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        profile_type_data = data.get("profileType", [{}])[0] if data.get("profileType") else {}
        profile_type = cls.ProfileType.deserialize(profile_type_data)

        return cls(
            general=general,
            type=profile_type,
        )
