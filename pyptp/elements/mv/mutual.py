"""Mutual coupling between transmission lines.

Mutual elements represent electromagnetic coupling between two transmission lines,
used for modeling parallel line interactions in medium-voltage networks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import NIL_GUID, Guid, decode_guid, encode_guid
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double_no_skip,
    write_guid,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass
class MutualMV:
    """Mutual coupling element for medium-voltage networks.

    Represents electromagnetic coupling between two transmission lines for
    accurate modeling of parallel line interactions in power system analysis.

    """

    general: General

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core mutual coupling parameters."""

        line1: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        line2: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        R00: float = 0
        X00: float = 0

        def serialize(self) -> str:
            """Serialize general properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid("Line1", self.line1),
                write_guid("Line2", self.line2),
                write_double_no_skip("R00", self.R00),
                write_double_no_skip("X00", self.X00),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MutualMV.General:
            """Deserialize general properties from VNF format.

            Args:
                data: Dictionary with parsed #General section properties.

            Returns:
                Initialized General instance;

            """
            return cls(
                line1=decode_guid(data.get("Line1", str(NIL_GUID))),
                line2=decode_guid(data.get("Line2", str(NIL_GUID))),
                R00=data.get("R00", 0.0),
                X00=data.get("X00", 0.0),
            )

    def register(self, network: NetworkMV) -> None:
        """Register mutual coupling in network.

        Args:
            network: Target network for registration.

        Warns:
            Logs critical warning if line pair already has mutual coupling defined.

        """
        key = f"{self.general.line1!s}_{self.general.line2!s}"
        if key in network.mutuals:
            logger.critical("Mutual %s already exists, overwriting", key)
        network.mutuals[key] = self

    def serialize(self) -> str:
        """Serialize the mutual coupling to the VNF format.

        Returns:
            str: The serialized representation.

        """
        return f"#General {self.general.serialize()}"

    @classmethod
    def deserialize(cls, data: dict) -> MutualMV:
        """Deserialization of the mutual coupling from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            MutualMV: The deserialized mutual coupling

        Raises:
            ValueError: If Line1 or Line2 are missing from the data.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        if not general.line1 or not general.line2:
            msg = "Mutual requires both Line1 and Line2 GUIDs"
            raise ValueError(msg)

        return cls(general=general)
