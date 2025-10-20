"""Variable element for medium-voltage networks."""

from __future__ import annotations

from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.serialization_helpers import write_string_no_skip


@dataclass
class VariableMV(DataClassJsonMixin):
    """Variable element for MV networks - stores a single variable string."""

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
