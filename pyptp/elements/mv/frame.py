"""Frame element for medium-voltage networks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.color_utils import CL_BLACK, DelphiColor
from pyptp.elements.element_utils import (
    Guid,
    IntCoords,
    decode_guid,
    decode_int_coords,
    encode_guid,
    encode_int_coords,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import Extra
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
    write_quote_string_no_skip,
    write_string_no_skip,
)

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class FramePresentation(DataClassJsonMixin):
    """Presentation properties for a frame (MV)."""

    sheet: Guid = field(
        default_factory=lambda: Guid(uuid4()),
        metadata=config(encoder=encode_guid, decoder=decode_guid),
    )
    sort: str = string_field()
    name_x: int = optional_field(0)
    name_y: int = optional_field(0)
    is_filled: bool = False
    fill_color: DelphiColor = field(default=CL_BLACK)
    image_size: int = optional_field(0)
    color: DelphiColor = field(default=CL_BLACK)
    width: int = optional_field(1)
    style: str = string_field()
    text_color: DelphiColor = field(default=CL_BLACK)
    text_size: int = optional_field(10)
    text_font: str = field(default="Arial")
    text_style: int = optional_field(0)
    is_text_hidden: bool = False
    is_text_upside_down: bool = False
    strings_x: int = optional_field(0)
    strings_y: int = optional_field(0)
    first_corners: IntCoords = field(
        default_factory=list,
        metadata=config(encoder=encode_int_coords, decoder=decode_int_coords),
    )

    def serialize(self) -> str:
        """Serialize frame presentation properties."""
        return serialize_properties(
            write_guid_no_skip("Sheet", self.sheet),
            write_quote_string_no_skip("Sort", self.sort),
            write_integer("NameX", self.name_x, skip=0),
            write_integer("NameY", self.name_y, skip=0),
            write_boolean("Filled", value=self.is_filled),
            write_delphi_color("FillColor", self.fill_color),
            write_integer("ImageSize", self.image_size, skip=0),
            write_delphi_color("Color", self.color),
            write_integer("Width", self.width, skip=1),
            write_quote_string("Style", self.style),
            write_delphi_color("TextColor", self.text_color),
            write_integer("TextSize", self.text_size, skip=10),
            write_quote_string("Font", self.text_font),
            write_integer("TextStyle", self.text_style, skip=0),
            write_boolean("NoText", value=self.is_text_hidden),
            write_boolean("UpsideDownText", value=self.is_text_upside_down),
            write_integer("StringsX", self.strings_x, skip=0),
            write_integer("StringsY", self.strings_y, skip=0),
            f"FirstCorners:{encode_int_coords(self.first_corners)}" if self.first_corners else "",
        )

    @classmethod
    def deserialize(cls, data: dict) -> FramePresentation:
        """Deserialize frame presentation."""
        return cls(
            sheet=decode_guid(data.get("Sheet", str(uuid4()))),
            sort=data.get("Sort", ""),
            name_x=data.get("NameX", 0),
            name_y=data.get("NameY", 0),
            is_filled=data.get("Filled", False),
            fill_color=data.get("FillColor", CL_BLACK),
            image_size=data.get("ImageSize", 0),
            color=data.get("Color", CL_BLACK),
            width=data.get("Width", 1),
            style=data.get("Style", ""),
            text_color=data.get("TextColor", CL_BLACK),
            text_size=data.get("TextSize", 10),
            text_font=data.get("Font", "Arial"),
            text_style=data.get("TextStyle", 0),
            is_text_hidden=data.get("NoText", False),
            is_text_upside_down=data.get("UpsideDownText", False),
            strings_x=data.get("StringsX", 0),
            strings_y=data.get("StringsY", 0),
            first_corners=decode_int_coords(data.get("FirstCorners", "")),
        )


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

    general: General = field(default_factory=General)
    lines: list[str] = field(default_factory=list)  # Text lines
    geo_series: list[list[tuple[float, float]]] = field(default_factory=list)  # Geometry series
    presentations: list[FramePresentation] = field(default_factory=list)
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
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        # Add line sections
        lines.extend(f"#Line {write_string_no_skip('Text', line_text)}" for line_text in self.lines)

        # Add geo sections
        for geo_serie in self.geo_series:
            coord_str = " ".join(f"({x} {y})" for x, y in geo_serie)
            lines.append(f"#Geo Coordinates:'{{{coord_str} }}'")

        # Add extra sections
        lines.extend(f"#Extra {extra.encode()['Text']}" for extra in self.extras)

        # Add presentation sections
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> FrameMV:
        """Deserialize frame from VNF section data.

        Args:
            data: Dictionary containing parsed frame data.

        Returns:
            Initialized TFrameMS instance.

        """
        return cls(
            general=cls.General.deserialize(data.get("general", {})),
            lines=data.get("lines", []),
            geo_series=data.get("geo_series", []),
            presentations=[FramePresentation.deserialize(p) for p in data.get("presentations", [])],
            extras=[Extra.deserialize(e) for e in data.get("extras", [])],
        )
