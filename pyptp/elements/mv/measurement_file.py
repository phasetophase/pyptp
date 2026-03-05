"""Medium-voltage measurement file reference.

Stores references to external measurement data files used by MV networks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.serialization_helpers import write_string_no_skip

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass
class MeasurementFileMV(DataClassJsonMixin):
    """Reference to an external measurement data file."""

    filename: str = field(default="")

    def serialize(self) -> str:
        """Serialize measurement file reference to VNF format."""
        return f"#File {write_string_no_skip('FileName', self.filename)}"

    @classmethod
    def deserialize(cls, data: dict) -> MeasurementFileMV:
        """Deserialize measurement file reference from VNF section data."""
        return cls(filename=data.get("FileName", ""))

    def register(self, network: NetworkMV) -> None:
        """Register measurement file in network."""
        network.measurement_files.append(self)
