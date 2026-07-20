"""Low-voltage measurement file reference.

Stores references to external measurement data files used by LV networks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.serialization_helpers import write_string_no_skip

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass
class MeasurementFileLV(DataClassJsonMixin):
    """Reference to an external measurement data file."""

    filename: str = field(default="")

    def serialize(self) -> str:
        """Serialize measurement file reference to GNF format."""
        return f"#File {write_string_no_skip('FileName', self.filename)}"

    @classmethod
    def deserialize(cls, data: dict) -> MeasurementFileLV:
        """Deserialize measurement file reference from GNF section data."""
        return cls(filename=data.get("FileName", ""))

    def register(self, network: NetworkLV) -> None:
        """Register measurement file in network."""
        network.measurement_files.append(self)
