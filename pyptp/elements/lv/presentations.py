"""Presentation elements for LV network graphical representation.

Provides visual formatting and positioning classes for displaying
electrical network elements in graphical interfaces, supporting
schematic layout, symbol placement, and visual styling in GNF format.
"""

from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.color_utils import CL_BLACK, DelphiColor
from pyptp.elements.element_utils import (
    NIL_GUID,
    Guid,
    IntCoords,
    config,
    decode_guid,
    decode_int_coords,
    encode_guid,
    encode_int_coords,
    optional_field,
    string_field,
)
from pyptp.elements.enums import NodePresentationSymbol
from pyptp.elements.presentation_helpers import clamp_point_to_node, point_in_node_bounds
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
    write_string_no_skip,
)


@dataclass_json
@dataclass
class NodePresentation(DataClassJsonMixin):
    """Presentation properties for a node on a specific sheet."""

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    x: int = 0
    y: int = 0
    symbol: NodePresentationSymbol = NodePresentationSymbol.CLOSED_CIRCLE
    """Visual symbol shape for node representation on diagrams."""
    color: DelphiColor = field(default=CL_BLACK)
    size: int = optional_field(1)
    width: int = optional_field(1)
    """Thickness of the lines that draw the symbol."""
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
    text_rotation: int = optional_field(0)
    upstrings_x: int = optional_field(0)
    upstrings_y: int = optional_field(0)
    fault_strings_x: int = optional_field(0)
    fault_strings_y: int = optional_field(0)
    note_x: int = optional_field(0)
    """X offset relative to the object coordinates for the note text."""
    note_y: int = optional_field(0)
    """Y offset relative to the object coordinates for the note text."""

    def contains_point(self, point: tuple[int, int]) -> bool:
        """Check if a coordinate point falls within this node's visual bounds.

        Delegates to the shared point_in_node_bounds function which handles
        special node symbols (VERTICAL_LINE, HORIZONTAL_LINE) where the valid
        connection area extends beyond a single point.

        Args:
            point: (x, y) coordinate tuple to check.

        Returns:
            True if the point falls within the node's visual bounds.

        """
        return point_in_node_bounds(point, self.x, self.y, self.symbol, self.size)

    def clamp_point(self, point: tuple[int, int]) -> tuple[int, int]:
        """Clamp a point to the nearest valid connection position on this node.

        For line-type symbols (VERTICAL_LINE, HORIZONTAL_LINE), returns the
        closest point on the line segment. For other symbols, returns (x, y).

        This method requires the node presentation to be fully defined with
        valid coordinates, symbol, and size.

        Args:
            point: (x, y) coordinate tuple to clamp.

        Returns:
            The clamped (x, y) coordinate on this node's visual bounds.

        """
        return clamp_point_to_node(point, self.x, self.y, self.symbol, self.size)

    def serialize(self) -> str:
        """Serialize NodePresentation properties to a string."""
        return serialize_properties(
            write_string_no_skip("Sheet", encode_guid(self.sheet)),
            write_integer("X", self.x),
            write_integer("Y", self.y),
            write_integer_no_skip("Symbol", self.symbol),
            write_delphi_color("Color", self.color),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style),
            write_boolean("NoText", value=self.no_text),
            write_boolean("UpsideDownText", value=self.upside_down_text),
            write_integer("TextRotation", self.text_rotation),
            write_integer("UpstringsX", self.upstrings_x),
            write_integer("UpstringsY", self.upstrings_y),
            write_integer("FaultStringsX", self.fault_strings_x),
            write_integer("FaultStringsY", self.fault_strings_y),
            write_integer("NoteX", self.note_x),
            write_integer("NoteY", self.note_y),
        )

    @classmethod
    def deserialize(cls, data: dict) -> "NodePresentation":
        """Deserialize NodePresentation from a dictionary."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(NIL_GUID))),
            x=data.get("X", 0),
            y=data.get("Y", 0),
            symbol=NodePresentationSymbol(data.get("Symbol", NodePresentationSymbol.CLOSED_CIRCLE.value)),
            color=data.get("Color", CL_BLACK),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            text_color=data.get("TextColor", CL_BLACK),
            text_size=data.get("TextSize", 10),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 0),
            no_text=data.get("NoText", False),
            upside_down_text=data.get("UpsideDownText", False),
            text_rotation=data.get("TextRotation", 0),
            upstrings_x=data.get("UpstringsX", 0),
            upstrings_y=data.get("UpstringsY", 0),
            fault_strings_x=data.get("FaultStringsX", 0),
            fault_strings_y=data.get("FaultStringsY", 0),
            note_x=data.get("NoteX", 0),
            note_y=data.get("NoteY", 0),
        )


@dataclass_json
@dataclass
class BranchPresentation(DataClassJsonMixin):
    """Presentation properties for a branch on a specific sheet."""

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    color: DelphiColor = field(default=CL_BLACK)
    size: int = 1
    width: int = 1
    """Thickness of the lines that draw the symbol."""
    text_color: DelphiColor = field(default=CL_BLACK)
    """Color of the text."""
    text_size: int = 10
    """Size of the text."""
    font: str = string_field("Arial")
    text_style: int = optional_field(0)
    no_text: bool = False
    """Hides all text when True."""
    upside_down_text: bool = False
    """Makes text upside down when True."""
    strings1_x: int = optional_field(0)
    """X offset of the text relative to object."""
    strings1_y: int = optional_field(0)
    """Y offset of the text relative to object."""
    strings2_x: int = optional_field(0)
    strings2_y: int = optional_field(0)
    mid_strings_x: int = optional_field(0)
    mid_strings_y: int = optional_field(0)
    fault_strings_x: int = optional_field(0)
    fault_strings_y: int = optional_field(0)
    note_x: int = optional_field(0)
    """X offset relative to the object coordinates for the note text."""
    note_y: int = optional_field(0)
    """Y offset relative to the object coordinates for the note text."""
    flag_flipped1: bool = False
    flag_flipped2: bool = False
    first_corners: IntCoords = field(
        default_factory=list,
        metadata=config(encoder=encode_int_coords, decoder=decode_int_coords),
    )
    second_corners: IntCoords = field(
        default_factory=list,
        metadata=config(encoder=encode_int_coords, decoder=decode_int_coords),
    )

    def serialize(self) -> str:
        """Serialize BranchPresentation properties to a string."""
        props = [
            write_string_no_skip("Sheet", encode_guid(self.sheet)),
            write_delphi_color("Color", self.color),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style),
            write_boolean("NoText", value=self.no_text),
            write_boolean("UpsideDownText", value=self.upside_down_text),
            write_integer("Strings1X", self.strings1_x),
            write_integer("Strings1Y", self.strings1_y),
            write_integer("Strings2X", self.strings2_x),
            write_integer("Strings2Y", self.strings2_y),
            write_integer("MidStringsX", self.mid_strings_x),
            write_integer("MidStringsY", self.mid_strings_y),
            write_integer("FaultStringsX", self.fault_strings_x),
            write_integer("FaultStringsY", self.fault_strings_y),
            write_integer("NoteX", self.note_x),
            write_integer("NoteY", self.note_y),
            write_boolean("FlagFlipped1", value=self.flag_flipped1),
            write_boolean("FlagFlipped2", value=self.flag_flipped2),
        ]
        if self.first_corners:
            corners_str = (
                self.first_corners if isinstance(self.first_corners, str) else encode_int_coords(self.first_corners)
            )
            props.append(f"FirstCorners:{corners_str}")
        if self.second_corners:
            corners_str = (
                self.second_corners if isinstance(self.second_corners, str) else encode_int_coords(self.second_corners)
            )
            props.append(f"SecondCorners:{corners_str}")
        return serialize_properties(*props)

    @classmethod
    def deserialize(cls, data: dict) -> "BranchPresentation":
        """Deserialize BranchPresentation from a dictionary."""
        # Handle coordinate decoding
        first_corners = data.get("FirstCorners", [])
        if isinstance(first_corners, str):
            first_corners = decode_int_coords(first_corners)

        second_corners = data.get("SecondCorners", [])
        if isinstance(second_corners, str):
            second_corners = decode_int_coords(second_corners)

        return cls(
            sheet=decode_guid(data.get("Sheet", str(NIL_GUID))),
            color=data.get("Color", CL_BLACK),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            text_color=data.get("TextColor", CL_BLACK),
            text_size=data.get("TextSize", 10),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 0),
            no_text=data.get("NoText", False),
            upside_down_text=data.get("UpsideDownText", False),
            strings1_x=data.get("Strings1X", 0),
            strings1_y=data.get("Strings1Y", 0),
            strings2_x=data.get("Strings2X", 0),
            strings2_y=data.get("Strings2Y", 0),
            mid_strings_x=data.get("MidStringsX", 0),
            mid_strings_y=data.get("MidStringsY", 0),
            fault_strings_x=data.get("FaultStringsX", 0),
            fault_strings_y=data.get("FaultStringsY", 0),
            note_x=data.get("NoteX", 0),
            note_y=data.get("NoteY", 0),
            flag_flipped1=data.get("FlagFlipped1", False),
            flag_flipped2=data.get("FlagFlipped2", False),
            first_corners=first_corners,
            second_corners=second_corners,
        )


@dataclass_json
@dataclass
class ElementPresentation(DataClassJsonMixin):
    """Presentation properties for an element on a specific sheet."""

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    x: int = 0
    y: int = 0
    color: DelphiColor = field(default=CL_BLACK)
    size: int = optional_field(1)
    width: int = optional_field(1)
    """Thickness of the lines that draw the symbol."""
    text_color: DelphiColor = field(default=CL_BLACK)
    """Color of the text."""
    text_size: int = 10
    """Size of the text."""
    font: str = string_field("Arial")
    text_style: int = optional_field(0)
    no_text: bool = False
    """Hides all text when True."""
    upside_down_text: bool = False
    """Makes text upside down when True."""
    strings1_x: int = optional_field(0)
    """X offset of the text relative to object."""
    strings1_y: int = optional_field(0)
    """Y offset of the text relative to object."""
    symbol_strings_x: int = optional_field(0)
    symbol_strings_y: int = optional_field(0)
    note_x: int = optional_field(0)
    """X offset relative to the object coordinates for the note text."""
    note_y: int = optional_field(0)
    """Y offset relative to the object coordinates for the note text."""
    flag_flipped: bool = False

    def serialize(self) -> str:
        """Serialize ElementPresentation properties to a string."""
        return serialize_properties(
            write_string_no_skip("Sheet", encode_guid(self.sheet)),
            write_integer("X", self.x),
            write_integer("Y", self.y),
            write_delphi_color("Color", self.color),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style),
            write_boolean("NoText", value=self.no_text),
            write_boolean("UpsideDownText", value=self.upside_down_text),
            write_integer("Strings1X", self.strings1_x),
            write_integer("Strings1Y", self.strings1_y),
            write_integer("SymbolStringsX", self.symbol_strings_x),
            write_integer("SymbolStringsY", self.symbol_strings_y),
            write_integer("NoteX", self.note_x),
            write_integer("NoteY", self.note_y),
            write_boolean("FlagFlipped", value=self.flag_flipped),
        )

    @classmethod
    def deserialize(cls, data: dict) -> "ElementPresentation":
        """Deserialize ElementPresentation from a dictionary."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(NIL_GUID))),
            x=data.get("X", 0),
            y=data.get("Y", 0),
            color=data.get("Color", CL_BLACK),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            text_color=data.get("TextColor", CL_BLACK),
            text_size=data.get("TextSize", 10),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 0),
            no_text=data.get("NoText", False),
            upside_down_text=data.get("UpsideDownText", False),
            strings1_x=data.get("Strings1X", 0),
            strings1_y=data.get("Strings1Y", 0),
            symbol_strings_x=data.get("SymbolStringsX", 0),
            symbol_strings_y=data.get("SymbolStringsY", 0),
            note_x=data.get("NoteX", 0),
            note_y=data.get("NoteY", 0),
            flag_flipped=data.get("FlagFlipped", False),
        )


@dataclass_json
@dataclass
class SecundairPresentation(DataClassJsonMixin):
    """Presentation properties for a secondary on a specific sheet."""

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    distance: int = optional_field(0)
    otherside: bool = False
    color: DelphiColor = field(default=CL_BLACK)
    size: int = optional_field(1)
    width: int = optional_field(1)
    """Thickness of the lines that draw the symbol."""
    text_color: DelphiColor = field(default=CL_BLACK)
    """Color of the text."""
    text_size: int = 10
    """Size of the text."""
    font: str = string_field("Arial")
    text_style: int = optional_field(0)
    no_text: bool = False
    """Hides all text when True."""
    upside_down_text: bool = False
    """Makes text upside down when True."""
    strings_x: int = optional_field(0)
    """X offset of the text relative to object."""
    strings_y: int = optional_field(0)
    """Y offset of the text relative to object."""
    note_x: int = optional_field(0)
    """X offset relative to the object coordinates for the note text."""
    note_y: int = optional_field(0)
    """Y offset relative to the object coordinates for the note text."""

    def serialize(self) -> str:
        """Serialize SecundairPresentation properties to a string."""
        return serialize_properties(
            write_string_no_skip("Sheet", encode_guid(self.sheet)),
            write_integer("Distance", self.distance, skip=0),
            write_boolean("Otherside", value=self.otherside),
            write_delphi_color("Color", self.color),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.font, "Arial"),
            write_integer("TextStyle", self.text_style),
            write_boolean("NoText", value=self.no_text),
            write_boolean("UpsideDownText", value=self.upside_down_text),
            write_integer("StringsX", self.strings_x),
            write_integer("StringsY", self.strings_y),
            write_integer("NoteX", self.note_x),
            write_integer("NoteY", self.note_y),
        )

    @classmethod
    def deserialize(cls, data: dict) -> "SecundairPresentation":
        """Deserialize SecundairPresentation from a dictionary."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(NIL_GUID))),
            distance=data.get("Distance", 0),
            otherside=data.get("Otherside", False),
            color=data.get("Color", CL_BLACK),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            text_color=data.get("TextColor", CL_BLACK),
            text_size=data.get("TextSize", 10),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 0),
            no_text=data.get("NoText", False),
            upside_down_text=data.get("UpsideDownText", False),
            strings_x=data.get("StringsX", 0),
            strings_y=data.get("StringsY", 0),
            note_x=data.get("NoteX", 0),
            note_y=data.get("NoteY", 0),
        )
