"""Medium-voltage network options.

Stores network-level configuration options such as winter profile items.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import decode_int_list, encode_int_list

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass
class NetworkOptionsMV(DataClassJsonMixin):
    """Network-level options for MV networks."""

    general: General

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General networkoptions."""

        winter_profile_items: list[int] = field(
            default_factory=list, metadata=config(encoder=encode_int_list, decoder=decode_int_list)
        )
        low_tactics_profile_items: list[int] = field(
            default_factory=list, metadata=config(encoder=encode_int_list, decoder=decode_int_list)
        )
        high_tactics_profile_items: list[int] = field(
            default_factory=list, metadata=config(encoder=encode_int_list, decoder=decode_int_list)
        )

        @classmethod
        def deserialize(cls, data: dict) -> NetworkOptionsMV.General:
            """Deserialize network options from VNF section data."""
            return cls(
                winter_profile_items=decode_int_list(data.get("WinterProfileItems", "")),
                low_tactics_profile_items=decode_int_list(data.get("LowTacticsProfileItems", "")),
                high_tactics_profile_items=decode_int_list(data.get("HighTacticsProfileItems", "")),
            )

    def is_empty(self) -> bool:
        """Return True if no profile items are set on any field."""
        return (
            not self.general.winter_profile_items
            and not self.general.low_tactics_profile_items
            and not self.general.high_tactics_profile_items
        )

    def serialize(self) -> str:
        """Serialize the network options to VNF format.

        Each populated profile-item list is emitted on its own ``#General``
        line, matching the form Vision accepts.
        """
        g = self.general
        lines: list[str] = []
        if g.winter_profile_items:
            lines.append(f"#General WinterProfileItems:{encode_int_list(g.winter_profile_items)}")
        if g.high_tactics_profile_items:
            lines.append(f"#General HighTacticsProfileItems:{encode_int_list(g.high_tactics_profile_items)}")
        if g.low_tactics_profile_items:
            lines.append(f"#General LowTacticsProfileItems:{encode_int_list(g.low_tactics_profile_items)}")
        return "\n".join(lines)

    def register(self, network: NetworkMV) -> None:
        """Register network options on the network (singleton; replaces any existing)."""
        network.network_options = self
