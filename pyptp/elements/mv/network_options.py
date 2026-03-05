"""Medium-voltage network options.

Stores network-level configuration options such as winter profile items.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.serialization_helpers import write_string_no_skip

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass
class NetworkOptionsMV(DataClassJsonMixin):
    """Network-level options for MV networks."""

    winter_profile_items: str = field(default="")

    def serialize(self) -> str:
        """Serialize network options to VNF format."""
        return f"#General {write_string_no_skip('WinterProfileItems', self.winter_profile_items)}"

    @classmethod
    def deserialize(cls, data: dict) -> NetworkOptionsMV:
        """Deserialize network options from VNF section data."""
        return cls(winter_profile_items=data.get("WinterProfileItems", ""))

    def register(self, network: NetworkMV) -> None:
        """Register network options in network."""
        network.network_options = self
