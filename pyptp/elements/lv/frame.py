"""Frame (Other)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config

from pyptp.elements.color_utils import CL_BLACK, CL_BLUE, DelphiColor
from pyptp.elements.element_utils import (
    NIL_GUID,
    FrameShape,
    Guid,
    IntCoords,
    LineStyle,
    decode_guid,
    decode_int_coords,
    encode_guid,
    encode_int_coords,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import Extra, Geography, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass
class FrameLV:
    """Frame element for grouping and organizing components in low-voltage networks.

    A frame is a visual container (rectangle, polygon, or ellipse) in the one-line diagram
    that indicates components belong together, such as components of a substation.
    When the container property is enabled, nodes and texts placed entirely within
    the frame are kept together when dragging the frame.

    The frame has no influence on electrical calculations - it is purely organizational.
    Frames can contain nodes, texts, legends, and even other frames. Components must
    fit entirely within the frame boundaries to be considered contained.

    Supports three shapes:
    - Rectangle (default)
    - Polygon (with bendable corners)
    - Ellipse
    - Image-based frame (size determined by image)
    """

    @dataclass
    class General(DataClassJsonMixin, HasPresentationsMixin):
        """Core properties defining the frame element.

        Contains identification, naming, and behavioral properties that
        determine how the frame interacts with contained components.
        """

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)

        name: str = string_field()
        """User-defined name for the frame element."""

        revision_date: float | int = optional_field(0.0)

        image: str = string_field()
        """Path or URL to an image file used as the frame background."""

        container: bool = False
        """Whether contained objects move together with the frame when dragged."""

        def serialize(self) -> str:
            """Serialize General properties to GNF format.

            Returns:
                Space-separated property string for the #General section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_quote_string("Name", self.name),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_quote_string("Image", self.image),
                write_boolean("Container", value=self.container),
            )

        @classmethod
        def deserialize(cls, data: dict) -> FrameLV.General:
            """Parse General properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                name=data.get("Name", ""),
                revision_date=data.get("RevisionDate", 0.0),
                image=data.get("Image", ""),
                container=data.get("Container", False),
            )

    @dataclass
    class FramePresentation(DataClassJsonMixin):
        """Visual presentation properties for displaying the frame on a sheet.

        Controls the graphical appearance including shape, colors, line style,
        text formatting, and positioning on the network diagram.
        """

        sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """Sheet GUID where this presentation is displayed."""

        sort: FrameShape = FrameShape.RECTANGLE
        """Frame shape type."""

        name_x: int = optional_field(0)
        """X offset of the text relative to the weighted centre of the frame."""

        name_y: int = optional_field(0)
        """Y offset of the text relative to the weighted centre of the frame."""

        filled: bool = False
        """Whether the frame interior is filled with a background color."""

        fill_color: DelphiColor = field(default=CL_BLUE)
        """Background fill color when filled is True."""

        image_size: int = 100
        """Scaling factor for the background image (100 = original size)."""

        color: DelphiColor = field(default=CL_BLUE)
        """Border/outline color of the frame."""

        width: int = 1
        """Line width of the frame border."""

        style: LineStyle = LineStyle.SOLID
        """Line style for the frame border."""

        text_color: DelphiColor = field(default=CL_BLACK)
        """Color of the frame's text label."""

        text_size: int = 10
        """Font size for the frame's text label."""

        font: str = string_field("Arial")
        """Font family for the frame's text label."""

        text_style: int = optional_field(0)
        """Font style flags (bold, italic, etc.)."""

        no_text: bool = False
        """Hides all text when True."""

        upside_down_text: bool = False
        """Makes text upside down when True."""

        strings_x: int = optional_field(0)
        """X offset of the text relative to object."""

        strings_y: int = optional_field(0)
        """Y offset of the text relative to object."""

        first_corners: IntCoords = field(
            default_factory=list,
            metadata=config(encoder=encode_int_coords, decoder=decode_int_coords),
        )
        """Coordinates defining the frame shape vertices (e.g., 4 corners for rectangle)."""

        def serialize(self) -> str:
            """Serialize FramePresentation properties to GNF format.

            Returns:
                Space-separated property string for the #Presentation section.

            """
            return serialize_properties(
                write_guid("Sheet", self.sheet),
                write_quote_string("Sort", self.sort, skip=FrameShape.RECTANGLE),
                write_integer("NameX", self.name_x),
                write_integer("NameY", self.name_y),
                write_boolean("Filled", value=self.filled),
                write_delphi_color("FillColor", self.fill_color, skip=CL_BLUE),
                write_integer("ImageSize", self.image_size, skip=100),
                write_delphi_color("Color", self.color, skip=CL_BLUE),
                write_integer("Width", self.width, skip=1),
                write_quote_string("Style", self.style, skip=LineStyle.SOLID),
                write_delphi_color("TextColor", self.text_color, skip=CL_BLACK),
                write_integer("TextSize", self.text_size, skip=10),
                write_quote_string("Font", self.font, skip="Arial"),
                write_integer("TextStyle", self.text_style),
                write_boolean("NoText", value=self.no_text),
                write_boolean("UpsideDownText", value=self.upside_down_text),
                write_integer("StringsX", self.strings_x),
                write_integer("StringsY", self.strings_y),
            ) + (f" FirstCorners:{encode_int_coords(self.first_corners)}" if self.first_corners else "")

        @classmethod
        def deserialize(cls, data: dict) -> FrameLV.FramePresentation:
            """Parse FramePresentation properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized FramePresentation instance with parsed properties.

            """
            return cls(
                sheet=decode_guid(data.get("Sheet", str(NIL_GUID))),
                sort=FrameShape(data.get("Sort", FrameShape.RECTANGLE)),
                name_x=data.get("NameX", 0),
                name_y=data.get("NameY", 0),
                filled=data.get("Filled", False),
                fill_color=data.get("FillColor", CL_BLUE),
                image_size=data.get("ImageSize", 100),
                color=data.get("Color", CL_BLUE),
                width=data.get("Width", 1),
                style=LineStyle(data.get("Style", LineStyle.SOLID)),
                text_color=data.get("TextColor", CL_BLACK),
                text_size=data.get("TextSize", 10),
                font=data.get("Font", "Arial"),
                text_style=data.get("TextStyle", 0),
                no_text=data.get("NoText", False),
                upside_down_text=data.get("UpsideDownText", False),
                strings_x=data.get("StringsX", 0),
                strings_y=data.get("StringsY", 0),
                first_corners=decode_int_coords(data.get("FirstCorners", "")),
            )

    general: General
    presentations: list[FramePresentation]
    lines: list[str] = field(default_factory=list)
    extras: list[Extra] = field(default_factory=list)
    geo_series: list[Geography] = field(default_factory=list)

    def register(self, network: NetworkLV) -> None:
        """Register frame in the network with GUID-based indexing.

        Args:
            network: Target low-voltage network for registration.

        Warns:
            Logs critical warning if GUID already exists in network frames.

        """
        if self.general.guid in network.frames:
            logger.critical("Frames %s already exists, overwriting", self.general.guid)
        network.frames[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete frame element to GNF format.

        Combines all frame sections (#General, #Line, #Geo, #Extra, #Presentation)
        into the complete GNF representation for the frame element.

        Returns:
            Multi-line string with all frame sections for GNF file.

        """
        out = []
        out.append(f"#General {self.general.serialize()}")

        if self.lines:
            out.extend(f"#Line Text:{line}" for line in self.lines)

        if self.geo_series:
            out.extend(f"#Geo {geo.serialize()}" for geo in self.geo_series)

        if self.extras:
            out.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        out.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(out)

    @classmethod
    def deserialize(cls, data: dict) -> FrameLV:
        """Parse frame element from GNF section data.

        Args:
            data: Dictionary containing parsed GNF sections with keys:
                - 'general': General properties section
                - 'lines': List of text line data
                - 'geo_series': List of geographical coordinate series
                - 'extras': List of extra properties
                - 'presentations': List of presentation configurations

        Returns:
            Fully initialized FrameLV instance with all parsed data.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        lines_data = data.get("lines", [])
        lines: list[str] = []
        for line_data in lines_data:
            # Extract text from dict format {"Text": "value"} or use string directly
            if isinstance(line_data, dict):
                lines.append(line_data.get("Text", ""))
            else:
                lines.append(str(line_data))

        # Parse geo_series as list of Geography objects
        geo_data_list = data.get("geo_series", data.get("geo", []))
        geo_series = [Geography.deserialize(geo_data) for geo_data in geo_data_list]

        extras_data = data.get("extras", [])
        extras = [Extra.deserialize(extra_data) for extra_data in extras_data]

        presentations_data = data.get("presentations", [])
        presentations = [cls.FramePresentation.deserialize(pres_data) for pres_data in presentations_data]

        return cls(
            general=general,
            lines=lines,
            extras=extras,
            geo_series=geo_series,
            presentations=presentations,
        )
