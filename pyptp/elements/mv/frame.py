"""Frame element for medium-voltage networks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

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
from pyptp.elements.mixins import Extra, Geography
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
    write_quote_string_no_skip,
)

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class FrameMV(DataClassJsonMixin):
    """Frame element for MV networks."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for frame."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        name: str = string_field()
        container: bool = False
        image: str = string_field()

        def serialize(self) -> str:
            """Serialize general properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date) if self.mutation_date != 0 else "",
                write_integer("RevisionDate", self.revision_date) if self.revision_date != 0 else "",
                write_boolean("Variant", value=self.variant),
                write_quote_string_no_skip("Name", self.name),
                write_boolean("Container", value=self.container),
                write_quote_string("Image", self.image),
            )

        @classmethod
        def deserialize(cls, data: dict) -> FrameMV.General:
            """Parse general properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                container=data.get("Container", False),
                image=data.get("Image", ""),
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
        """X offset of the name text relative to object."""

        name_y: int = optional_field(0)
        """Y offset of the name text relative to object."""

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
        """X offset of the strings text relative to object."""

        strings_y: int = optional_field(0)
        """Y offset of the strings text relative to object."""

        first_corners: IntCoords = field(
            default_factory=list,
            metadata=config(encoder=encode_int_coords, decoder=decode_int_coords),
        )
        """Coordinates defining the frame shape vertices (e.g., 4 corners for rectangle)."""

        def serialize(self) -> str:
            """Serialize FramePresentation properties to VNF format.

            Returns:
                Space-separated property string for the #Presentation section.

            """
            return serialize_properties(
                write_guid_no_skip("Sheet", self.sheet),
                write_quote_string("Sort", self.sort, skip=FrameShape.RECTANGLE),
                write_integer("NameX", self.name_x, skip=0),
                write_integer("NameY", self.name_y, skip=0),
                write_boolean("Filled", value=self.filled),
                write_delphi_color("FillColor", self.fill_color, skip=CL_BLUE),
                write_integer("ImageSize", self.image_size, skip=100),
                write_delphi_color("Color", self.color, skip=CL_BLUE),
                write_integer("Width", self.width, skip=1),
                write_quote_string("Style", self.style, skip=LineStyle.SOLID),
                write_delphi_color("TextColor", self.text_color, skip=CL_BLACK),
                write_integer("TextSize", self.text_size, skip=10),
                write_quote_string("Font", self.font, skip="Arial"),
                write_integer("TextStyle", self.text_style, skip=0),
                write_boolean("NoText", value=self.no_text),
                write_boolean("UpsideDownText", value=self.upside_down_text),
                write_integer("StringsX", self.strings_x, skip=0),
                write_integer("StringsY", self.strings_y, skip=0),
                f"FirstCorners:{encode_int_coords(self.first_corners)}" if self.first_corners else "",
            )

        @classmethod
        def deserialize(cls, data: dict) -> FrameMV.FramePresentation:
            """Parse FramePresentation properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

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
    geo_series: list[Geography] = field(default_factory=list)
    extras: list[Extra] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Register frame in network with GUID-based indexing.

        Args:
            network: Target network for registration.

        Warns:
            Logs critical warning if GUID already exists in network.

        """
        from pyptp.ptp_log import logger

        if self.general.guid in network.frames:
            logger.critical("Frame %s already exists, overwriting", self.general.guid)
        network.frames[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete frame to VNF format.

        Returns:
            Multi-line string with all frame sections for VNF file.

        """
        out = []
        out.append(f"#General {self.general.serialize()}")

        # Add line sections
        if self.lines:
            out.extend(f"#Line Text:{line_text}" for line_text in self.lines)

        # Add geo sections
        if self.geo_series:
            out.extend(f"#Geo {geo.serialize()}" for geo in self.geo_series)

        # Add extra sections
        if self.extras:
            out.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        # Add presentation sections
        out.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(out)

    @classmethod
    def deserialize(cls, data: dict) -> FrameMV:
        """Deserialize frame from VNF section data.

        Args:
            data: Dictionary containing parsed frame data with keys:
                - 'general': General properties section
                - 'lines': List of text line data
                - 'geo_series': List of geographical coordinate series
                - 'extras': List of extra properties
                - 'presentations': List of presentation configurations

        Returns:
            Initialized FrameMV instance with all parsed data.

        """
        general_data = data.get("general", {})
        general = cls.General.deserialize(general_data)

        lines_data = data.get("lines", [])
        lines: list[str] = []
        for line_data in lines_data:
            if isinstance(line_data, dict):
                lines.append(line_data.get("Text", ""))
            else:
                lines.append(str(line_data))

        geo_data_list = data.get("geo_series", [])
        geo_series = [Geography.deserialize(geo_data) for geo_data in geo_data_list]

        extras_data = data.get("extras", [])
        extras = [Extra.deserialize(extra_data) for extra_data in extras_data]

        presentations_data = data.get("presentations", [])
        presentations = [cls.FramePresentation.deserialize(pres_data) for pres_data in presentations_data]

        return cls(
            general=general,
            lines=lines,
            geo_series=geo_series,
            presentations=presentations,
            extras=extras,
        )
