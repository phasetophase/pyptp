"""Legend element for medium-voltage networks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.color_utils import CL_BLACK, DelphiColor
from pyptp.elements.element_utils import (
    Guid,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
)

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class LegendCell(DataClassJsonMixin):
    """Legend cell with text content."""

    row: int = 1
    column: int = 1
    text_size: int = 20
    text_lines: list[str] = field(default_factory=list)

    def serialize_cell(self) -> list[str]:
        """Serialize cell and its text lines."""
        lines = []
        cell_properties = serialize_properties(
            write_integer_no_skip("Row", self.row),
            write_integer_no_skip("Column", self.column),
            write_integer_no_skip("TextSize", self.text_size),
        )
        lines.append(f"#Cell {cell_properties}")

        # Add text lines
        lines.extend(f"#Text {text_line}" for text_line in self.text_lines)

        return lines

    @classmethod
    def deserialize(cls, data: dict) -> LegendCell:
        """Deserialize legend cell."""
        return cls(
            row=data.get("Row", 1),
            column=data.get("Column", 1),
            text_size=data.get("TextSize", 20),
            text_lines=data.get("text_lines", []),
        )


@dataclass_json
@dataclass
class LegendPresentation(DataClassJsonMixin):
    """Presentation properties for a legend."""

    sheet: Guid = field(
        default_factory=lambda: Guid(uuid4()),
        metadata=config(encoder=encode_guid, decoder=decode_guid),
    )
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0
    color: DelphiColor = field(default=CL_BLACK)
    width: int = optional_field(1)
    """Thickness of the lines that draw the symbol."""

    style: str = field(default="Solid")
    text_color: DelphiColor = field(default=CL_BLACK)
    """Color of the text."""

    text_size: int = optional_field(10)
    """Size of the text."""
    font: str = string_field("Arial")
    text_style: int = optional_field(0)
    no_text: bool = False
    """Hides all text when True."""

    upside_down_text: bool = False
    """Makes text upside down when True."""

    def serialize(self) -> str:
        """Serialize legend presentation properties."""
        return serialize_properties(
            write_guid_no_skip("Sheet", self.sheet),
            write_integer_no_skip("X1", self.x1),
            write_integer_no_skip("Y1", self.y1),
            write_integer_no_skip("X2", self.x2),
            write_integer_no_skip("Y2", self.y2),
            write_delphi_color("Color", self.color),
            write_integer("Width", self.width, skip=1),
            write_quote_string("Style", self.style, skip="Solid"),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style, skip=0),
            write_boolean("NoText", value=self.no_text),
            write_boolean("UpsideDownText", value=self.upside_down_text),
        )

    @classmethod
    def deserialize(cls, data: dict) -> LegendPresentation:
        """Deserialize legend presentation."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(uuid4()))),
            x1=data.get("X1", 0),
            y1=data.get("Y1", 0),
            x2=data.get("X2", 0),
            y2=data.get("Y2", 0),
            color=data.get("Color", CL_BLACK),
            width=data.get("Width", 1),
            style=data.get("Style", "Solid"),
            text_color=data.get("TextColor", CL_BLACK),
            text_size=data.get("TextSize", 10),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 0),
            no_text=data.get("NoText", False),
            upside_down_text=data.get("UpsideDownText", False),
        )


@dataclass_json
@dataclass
class LegendMV(DataClassJsonMixin):
    """Legend element for MV networks."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for legend."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        rows: int = 1
        columns: int = 1

        def serialize(self) -> str:
            """Serialize general properties to VNF format."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date) if self.mutation_date != 0 else "",
                write_integer("RevisionDate", self.revision_date) if self.revision_date != 0 else "",
                write_boolean("Variant", value=self.variant),
                write_integer_no_skip("Rows", self.rows),
                write_integer_no_skip("Columns", self.columns),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LegendMV.General:
            """Parse general properties from VNF section data."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                rows=data.get("Rows", 1),
                columns=data.get("Columns", 1),
            )

    general: General = field(default_factory=General)
    merges: list[str] = field(default_factory=list)  # Merge specifications like "C1:E2"
    cells: list[LegendCell] = field(default_factory=list)
    presentations: list[LegendPresentation] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Register legend in network with GUID-based indexing."""
        from pyptp.ptp_log import logger

        if self.general.guid in network.legends:
            logger.critical("Legend %s already exists, overwriting", self.general.guid)
        network.legends[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete legend to VNF format."""
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Merge {merge}" for merge in self.merges)

        # Add cell sections
        for cell in self.cells:
            lines.extend(cell.serialize_cell())

        # Add presentation sections
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> LegendMV:
        """Deserialize legend from VNF section data."""
        return cls(
            general=cls.General.deserialize(data.get("general", {})),
            merges=data.get("merges", []),
            cells=[LegendCell.deserialize(c) for c in data.get("cells", [])],
            presentations=[LegendPresentation.deserialize(p) for p in data.get("presentations", [])],
        )
