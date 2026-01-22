"""Medium-voltage variable element for network configuration.

Provides simple text variable storage for configuration values
and metadata in MV distribution network files.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.serialization_helpers import write_string_no_skip


@dataclass
class VariableMV(DataClassJsonMixin):
    """Medium-voltage variable storing configuration text values.

    Supports simple string storage for network-level configuration
    and metadata in VNF format files.
    """

    value: str = field(default="")

    def serialize(self) -> str:
        """Serialize variable to VNF format.

        Returns:
            VNF format string for variable section.

        """
        return f"#Variable {write_string_no_skip('Text', self.value)}"

    @classmethod
    def deserialize(cls, data: dict) -> VariableMV:
        """Deserialize variable from VNF section data.

        Args:
            data: Dictionary containing parsed variable data.

        Returns:
            Initialized TVariableMS instance.

        """
        return cls(value=data.get("Text", ""))
