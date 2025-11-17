"""Calculation case element for medium-voltage networks."""

from __future__ import annotations

from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double_no_skip,
    write_quote_string_no_skip,
    write_string_no_skip,
)


@dataclass
class CalculationCaseMV(DataClassJsonMixin):
    """Calculation case element for MV networks."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for calculation case."""

        calculation: str = field(default="")
        name: str = field(default="")
        date: float = field(default=0.0)

        def serialize(self) -> str:
            """Serialize general properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_quote_string_no_skip("Calculation", self.calculation),
                write_quote_string_no_skip("Name", self.name),
                write_double_no_skip("Date", self.date),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CalculationCaseMV.General:
            """Parse general properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            return cls(
                calculation=data.get("Calculation", ""),
                name=data.get("Name", ""),
                date=data.get("Date", 0.0),
            )

    general: General = field(default_factory=General)
    content_strings: list[str] = field(default_factory=list)

    def serialize(self) -> str:
        """Serialize complete calculation case to VNF format.

        Returns:
            Multi-line string with all calculation case sections for VNF file.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.extend(f"#Content {write_string_no_skip('Text', content)}" for content in self.content_strings)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> CalculationCaseMV:
        """Deserialize calculation case from VNF section data.

        Args:
            data: Dictionary containing parsed calculation case data.

        Returns:
            Initialized TCalcCaseMS instance.

        """
        return cls(
            general=cls.General.deserialize(data.get("general", {})),
            content_strings=data.get("content_strings", []),
        )
