"""Mutual coupling between transmission lines.

Mutual elements represent electromagnetic coupling between two transmission lines,
used for modeling parallel line interactions in medium-voltage networks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyptp.elements.element_utils import Guid, decode_guid
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double_no_skip,
    write_guid_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass
class MutualMV:
    """Mutual coupling element for medium-voltage networks.

    Represents electromagnetic coupling between two transmission lines for
    accurate modeling of parallel line interactions in power system analysis.

    Attributes:
        line1: GUID reference to first transmission line.
        line2: GUID reference to second transmission line.
        R00: Zero-sequence mutual resistance in ohms.
        X00: Zero-sequence mutual reactance in ohms.

    """

    line1: Guid
    line2: Guid
    R00: float
    X00: float

    def register(self, network: NetworkMV) -> None:
        """Register mutual coupling in network.

        Args:
            network: Target network for registration.

        Warns:
            Logs critical warning if line pair already has mutual coupling defined.

        """
        key = f"{self.line1}_{self.line2}"
        if key in network.mutuals:
            logger.critical("Mutual %s already exists, overwriting", key)
        network.mutuals[key] = self

    def serialize(self) -> str:
        """Serialize mutual to VNF format.

        Returns:
            VNF-formatted string representation.

        """
        properties = serialize_properties(
            write_guid_no_skip("Line1", self.line1),
            write_guid_no_skip("Line2", self.line2),
            write_double_no_skip("R00", self.R00),
            write_double_no_skip("X00", self.X00),
        )
        return f"#General {properties}"

    @classmethod
    def deserialize(cls, data: dict) -> MutualMV:
        """Deserialize mutual from VNF format.

        Args:
            data: Dictionary containing parsed VNF section data with 'general' key.

        Returns:
            Initialized MutualMV instance.

        Raises:
            ValueError: If Line1 or Line2 are missing from the data.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}

        line1_raw = general_data.get("Line1")
        line2_raw = general_data.get("Line2")

        if not line1_raw or not line2_raw:
            msg = "Mutual requires both Line1 and Line2 GUIDs"
            raise ValueError(msg)

        return cls(
            line1=decode_guid(line1_raw),
            line2=decode_guid(line2_raw),
            R00=general_data.get("R00", 0.0),
            X00=general_data.get("X00", 0.0),
        )
