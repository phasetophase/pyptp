"""Shared Presentation Properties."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.color_utils import CL_BLACK, CL_GRAY, DelphiColor
from pyptp.elements.element_utils import (
    NIL_GUID,
    Guid,
    IntCoords,
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
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
)


@dataclass_json
@dataclass
class NodePresentation(DataClassJsonMixin):
    """Presentation properties for a node (MV)."""

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    x: int = optional_field(0)
    y: int = optional_field(0)
    symbol: NodePresentationSymbol = NodePresentationSymbol.CLOSED_CIRCLE
    """Visual symbol shape for node representation on diagrams."""
    color: DelphiColor = field(default=CL_BLACK)
    size: int = optional_field(1)
    width: int = optional_field(1)
    style: str = "Solid"  # Line style: Solid, Dash, Dot, DashDot, DashDotDot
    text_color: DelphiColor = field(default=CL_BLACK)
    text_size: int = optional_field(10)
    font: str = string_field("Arial")
    text_style: int = optional_field(0)
    is_text_hidden: bool = False
    is_text_upside_down: bool = False
    text_rotation: int = optional_field(0)
    upstrings_x: int = optional_field(0)
    upstrings_y: int = optional_field(0)
    fault_strings_x: int = optional_field(0)
    fault_strings_y: int = optional_field(0)
    note_x: int = optional_field(0)
    note_y: int = optional_field(0)
    icon_x: int = optional_field(0)
    icon_y: int = optional_field(0)

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
        """Serialize NodePresentation properties."""
        return serialize_properties(
            write_guid_no_skip("Sheet", self.sheet),
            write_integer("X", self.x),
            write_integer("Y", self.y),
            write_integer_no_skip("Symbol", int(self.symbol)),
            write_delphi_color("Color", self.color),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_quote_string("Style", self.style, skip="Solid"),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style, skip=0),
            write_boolean("NoText", value=self.is_text_hidden),
            write_boolean("UpsideDownText", value=self.is_text_upside_down),
            write_integer("TextRotation", self.text_rotation),
            write_integer("UpstringsX", self.upstrings_x),
            write_integer("UpstringsY", self.upstrings_y),
            write_integer("FaultStringsX", self.fault_strings_x),
            write_integer("FaultStringsY", self.fault_strings_y),
            write_integer("NoteX", self.note_x),
            write_integer("NoteY", self.note_y),
            write_integer("IconX", self.icon_x),
            write_integer("IconY", self.icon_y),
        )

    @classmethod
    def deserialize(cls, data: dict) -> NodePresentation:
        """Deserialize NodePresentation properties."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(uuid4()))),
            x=data.get("X", 0),
            y=data.get("Y", 0),
            symbol=NodePresentationSymbol(data.get("Symbol", NodePresentationSymbol.CLOSED_CIRCLE.value)),
            color=DelphiColor(data.get("Color", str(CL_BLACK))),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            style=data.get("Style", "Solid"),
            text_color=DelphiColor(data.get("TextColor", str(CL_BLACK))),
            text_size=data.get("TextSize", 10),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 0),
            is_text_hidden=data.get("NoText", False),
            is_text_upside_down=data.get("UpsideDownText", False),
            text_rotation=data.get("TextRotation", 0),
            upstrings_x=data.get("UpstringsX", 0),
            upstrings_y=data.get("UpstringsY", 0),
            fault_strings_x=data.get("FaultStringsX", 0),
            fault_strings_y=data.get("FaultStringsY", 0),
            note_x=data.get("NoteX", 0),
            note_y=data.get("NoteY", 0),
            icon_x=data.get("IconX", 0),
            icon_y=data.get("IconY", 0),
        )


@dataclass_json
@dataclass
class BranchPresentation(DataClassJsonMixin):
    """Presentation properties for a branch (object between two nodes) (MV)."""

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    color: DelphiColor = field(default=CL_BLACK)
    size: int = 1
    width: int = 1
    """Thickness of the lines that draw the symbol."""

    style: str = "Solid"  # Line style: Solid, Dash, Dot, DashDot, DashDotDot
    text_color: DelphiColor = field(default=CL_BLACK)
    """Color of the text."""

    text_size: int = 7
    """Size of the text."""
    font: str = string_field("Arial")
    text_style: int = 1
    no_text: bool = False
    """Hides all text when True."""

    upside_down_text: bool = False
    """Makes text upside down when True."""

    strings1_x: int = 0
    """X offset of the text relative to object."""

    strings1_y: int = 0
    """Y offset of the text relative to object."""
    strings2_x: int = 0
    """X offset of the text relative to object."""

    strings2_y: int = 0
    """Y offset of the text relative to object."""
    mid_strings_x: int = 0
    mid_strings_y: int = 0
    fault_strings_x: int = 0
    fault_strings_y: int = 0
    note_x: int = 0
    """X offset relative to the object coordinates for the note text."""

    note_y: int = 0
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
        """Serialize BranchPresentation properties."""
        props = [
            write_guid_no_skip("Sheet", self.sheet),
            write_delphi_color("Color", self.color),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_quote_string("Style", self.style, skip="Solid"),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=7),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style, skip=1),
            write_boolean("NoText", value=self.no_text, skip=False),
            write_boolean("UpsideDownText", value=self.upside_down_text, skip=False),
            write_integer("Strings1X", self.strings1_x, skip=0),
            write_integer("Strings1Y", self.strings1_y, skip=0),
            write_integer("Strings2X", self.strings2_x, skip=0),
            write_integer("Strings2Y", self.strings2_y, skip=0),
            write_integer("MidStringsX", self.mid_strings_x, skip=0),
            write_integer("MidStringsY", self.mid_strings_y, skip=0),
            write_integer("FaultStringsX", self.fault_strings_x, skip=0),
            write_integer("FaultStringsY", self.fault_strings_y, skip=0),
            write_integer("NoteX", self.note_x, skip=0),
            write_integer("NoteY", self.note_y, skip=0),
            write_boolean("FlagFlipped1", value=self.flag_flipped1, skip=False),
            write_boolean("FlagFlipped2", value=self.flag_flipped2, skip=False),
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
    def deserialize(cls, data: dict) -> BranchPresentation:
        """Deserialize BranchPresentation properties."""
        first_corners = data.get("FirstCorners", [])
        if isinstance(first_corners, str):
            first_corners = decode_int_coords(first_corners)

        second_corners = data.get("SecondCorners", [])
        if isinstance(second_corners, str):
            second_corners = decode_int_coords(second_corners)

        return cls(
            sheet=decode_guid(data.get("Sheet", str(uuid4()))),
            color=DelphiColor(data.get("Color", str(CL_BLACK))),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            style=data.get("Style", "Solid"),
            text_color=DelphiColor(data.get("TextColor", str(CL_BLACK))),
            text_size=data.get("TextSize", 7),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 1),
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
class DWPresentation(BranchPresentation):
    """Presentation properties for a three winding transformer (MV)."""

    x: int = 0
    y: int = 0
    strings3_x: int = 0
    strings3_y: int = 0
    third_corners: IntCoords = field(
        default_factory=list,
        metadata=config(encoder=encode_int_coords, decoder=decode_int_coords),
    )

    def serialize(self) -> str:
        """Serialize DWPresentation properties."""
        props = [
            write_guid_no_skip("Sheet", self.sheet),
            write_integer("X", self.x),
            write_integer("Y", self.y),
            write_delphi_color("Color", self.color),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_quote_string("Style", self.style, skip="Solid"),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=7),
            write_integer("TextStyle", self.text_style, skip=1),
            write_boolean("NoText", value=self.no_text),
            write_boolean("UpsideDownText", value=self.upside_down_text),
            write_integer("Strings1X", self.strings1_x, skip=0),
            write_integer("Strings1Y", self.strings1_y, skip=0),
            write_integer("Strings2X", self.strings2_x, skip=0),
            write_integer("Strings2Y", self.strings2_y, skip=0),
            write_integer("Strings3X", self.strings3_x, skip=0),
            write_integer("Strings3Y", self.strings3_y, skip=0),
            write_integer("MidStringsX", self.mid_strings_x, skip=0),
            write_integer("MidStringsY", self.mid_strings_y, skip=0),
            write_integer("FaultStringsX", self.fault_strings_x, skip=0),
            write_integer("FaultStringsY", self.fault_strings_y, skip=0),
            write_integer("NoteX", self.note_x, skip=0),
            write_integer("NoteY", self.note_y, skip=0),
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
        if self.third_corners:
            corners_str = (
                self.third_corners if isinstance(self.third_corners, str) else encode_int_coords(self.third_corners)
            )
            props.append(f"ThirdCorners:{corners_str}")

        return serialize_properties(*props)

    @classmethod
    def deserialize(cls, data: dict) -> DWPresentation:
        """Deserialize DWPresentation properties."""
        first_corners = data.get("FirstCorners", [])
        if isinstance(first_corners, str):
            first_corners = decode_int_coords(first_corners)

        second_corners = data.get("SecondCorners", [])
        if isinstance(second_corners, str):
            second_corners = decode_int_coords(second_corners)

        third_corners = data.get("ThirdCorners", [])
        if isinstance(third_corners, str):
            third_corners = decode_int_coords(third_corners)

        return cls(
            sheet=decode_guid(data.get("Sheet", str(uuid4()))),
            x=data.get("X", 0),
            y=data.get("Y", 0),
            color=DelphiColor(data.get("Color", str(CL_BLACK))),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            style=data.get("Style", "Solid"),
            text_color=DelphiColor(data.get("TextColor", str(CL_BLACK))),
            text_size=data.get("TextSize", 7),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 1),
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
            strings3_x=data.get("Strings3X", 0),
            strings3_y=data.get("Strings3Y", 0),
            third_corners=third_corners,
        )


@dataclass_json
@dataclass
class ElementPresentation(DataClassJsonMixin):
    """Presentation properties for an element (object attached to a singular node) (MV).

    Controls the visual appearance and positioning of MV network elements on the diagram,
    including colors, sizes, text formatting, and coordinate positioning on sheets.
    """

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    """The sheet where the element is visible."""
    x: int = 0
    """X coordinate on the sheet."""
    y: int = 0
    """Y coordinate on the sheet."""
    color: DelphiColor = field(default=CL_BLACK)
    """Color of the object."""
    size: int = 1
    """Size of the object, scales it bigger."""
    width: int = 1
    """Thickness of the lines that draw the symbol."""
    text_color: DelphiColor = field(default=CL_BLACK)
    """Color of the text."""
    text_size: int = 7
    """Size of the text."""
    font: str = string_field("Arial")
    """Font for the text by the object."""
    text_style: int = 1
    """Text style (cursive, bold, etc.)."""
    no_text: bool = False
    """Hides all text when True."""
    upside_down_text: bool = False
    """Makes text upside down when True."""
    strings1_x: int = 0
    """X offset of the text relative to object."""
    strings1_y: int = 0
    """Y offset of the text relative to object."""
    symbol_strings_x: int = 0
    symbol_strings_y: int = 0
    note_x: int = 0
    """X offset relative to the object coordinates for the note text."""
    note_y: int = 0
    """Y offset relative to the object coordinates for the note text."""
    flag_flipped: bool = False
    """Flips the flag upside down if the switch is opened."""

    def serialize(self) -> str:
        """Serialize ElementPresentation properties."""
        return serialize_properties(
            write_guid_no_skip("Sheet", self.sheet),
            write_integer_no_skip("X", self.x),
            write_integer_no_skip("Y", self.y),
            write_delphi_color("Color", self.color, skip=CL_BLACK),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_delphi_color("TextColor", self.text_color, skip=CL_BLACK),
            write_integer("TextSize", self.text_size, skip=7),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style, skip=1),
            write_boolean("NoText", value=self.no_text, skip=False),
            write_boolean("UpsideDownText", value=self.upside_down_text, skip=False),
            write_integer("Strings1X", self.strings1_x, skip=0),
            write_integer("Strings1Y", self.strings1_y, skip=0),
            write_integer("SymbolStringsX", self.symbol_strings_x, skip=0),
            write_integer("SymbolStringsY", self.symbol_strings_y, skip=0),
            write_integer("NoteX", self.note_x, skip=0),
            write_integer("NoteY", self.note_y, skip=0),
            write_boolean("FlagFlipped", value=self.flag_flipped, skip=False),
        )

    @classmethod
    def deserialize(cls, data: dict) -> ElementPresentation:
        """Deserialize ElementPresentation properties."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(uuid4()))),
            x=data.get("X", 0),
            y=data.get("Y", 0),
            color=DelphiColor(data.get("Color", str(CL_BLACK))),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            text_color=DelphiColor(data.get("TextColor", str(CL_BLACK))),
            text_size=data.get("TextSize", 7),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 1),
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
class SecondaryPresentation(DataClassJsonMixin):
    """Presentation properties for a secundairy (modelled on top of a branch or element) (MV)."""

    sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
    distance: int = 0
    otherside: bool = False
    color: DelphiColor = field(default=CL_GRAY)
    size: int = 1
    width: int = 1
    style: str = string_field()
    text_color: DelphiColor = field(default=CL_BLACK)
    text_size: int = 10
    font: str = string_field(default="Arial")
    text_style: int = 1
    no_text: bool = False
    upside_down_text: bool = False
    strings_x: int = 0
    strings_y: int = 0
    note_x: int = 0
    note_y: int = 0

    def serialize(self) -> str:
        """Serialize SecondaryPresentation properties."""
        return serialize_properties(
            write_guid_no_skip("Sheet", self.sheet),
            write_integer("Distance", self.distance),
            write_boolean("Otherside", value=self.otherside),
            write_delphi_color("Color", self.color, skip=CL_BLACK),
            write_integer("Size", self.size, skip=1),
            write_integer("Width", self.width, skip=1),
            write_quote_string("Style", self.style),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.font, skip="Arial"),
            write_integer("TextStyle", self.text_style, skip=1),
            write_boolean("NoText", value=self.no_text),
            write_boolean("UpsideDownText", value=self.upside_down_text),
            write_integer("StringsX", self.strings_x),
            write_integer("StringsY", self.strings_y),
            write_integer("NoteX", self.note_x),
            write_integer("NoteY", self.note_y),
        )

    @classmethod
    def deserialize(cls, data: dict) -> SecondaryPresentation:
        """Deserialize SecondaryPresentation properties."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(uuid4()))),
            distance=data.get("Distance", 0),
            otherside=data.get("Otherside", False),
            color=DelphiColor(data.get("Color", str(CL_BLACK))),
            size=data.get("Size", 1),
            width=data.get("Width", 1),
            style=data.get("Style", ""),
            text_color=DelphiColor(data.get("TextColor", str(CL_BLACK))),
            text_size=data.get("TextSize", 10),
            font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 1),
            no_text=data.get("NoText", False),
            upside_down_text=data.get("UpsideDownText", False),
            strings_x=data.get("StringsX", 0),
            strings_y=data.get("StringsY", 0),
            note_x=data.get("NoteX", 0),
            note_y=data.get("NoteY", 0),
        )
