"""Text element for MV networks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.color_utils import CL_BLACK, DelphiColor
from pyptp.elements.element_utils import (
    Guid,
    config,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
    write_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class TextMV(ExtrasNotesMixin):
    """Represents a text annotation element for MV networks.

    Text elements provide documentation and annotation capabilities for electrical
    network diagrams, supporting multiple lines and presentation styling.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core properties for text annotations."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0.0
        mutation_date: int = optional_field(0)
        revision_date: int = optional_field(0)
        variant: bool = False

        def serialize(self) -> str:
            """Serialize General properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
                write_boolean("Variant", value=self.variant),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TextMV.General:
            """Parse General properties from VNF section data.

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
            )

    @dataclass_json
    @dataclass
    class Line(DataClassJsonMixin):
        """Represents a single line of text content."""

        text: str = string_field()

        def serialize(self) -> str:
            """Serialize Line properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_string_no_skip("Text", self.text),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TextMV.Line:
            """Parse Line properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized Line instance with parsed properties.

            """
            return cls(
                text=data.get("Text", ""),
            )

    @dataclass_json
    @dataclass
    class Presentation(DataClassJsonMixin):
        """Presentation properties for text display and positioning."""

        sheet: Guid = field(
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        x: int = 0
        y: int = 0
        text_color: DelphiColor = CL_BLACK
        """Color of the text."""

        text_size: int = 10
        """Size of the text."""
        font: str = string_field("Arial")
        text_style: int = 0
        upside_down_text: bool = False
        """Makes text upside down when True."""

        def serialize(self) -> str:
            """Serialize Presentation properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("Sheet", self.sheet),
                write_integer("X", self.x, skip=0),
                write_integer("Y", self.y, skip=0),
                write_delphi_color("TextColor", self.text_color, skip=CL_BLACK),
                write_integer("TextSize", self.text_size, skip=10),
                write_quote_string("Font", self.font, skip="Arial"),
                write_integer("TextStyle", self.text_style, skip=0),
                write_boolean("UpsideDownText", value=self.upside_down_text),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TextMV.Presentation:
            """Parse Presentation properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized Presentation instance with parsed properties.

            """
            return cls(
                sheet=decode_guid(data.get("Sheet", "")),
                x=data.get("X", 0),
                y=data.get("Y", 0),
                text_color=data.get("TextColor", CL_BLACK),
                text_size=data.get("TextSize", 10),
                font=data.get("Font", "Arial"),
                text_style=data.get("TextStyle", 0),
                upside_down_text=data.get("UpsideDownText", False),
            )

    general: General
    lines: list[Line] = field(default_factory=list)
    presentations: list[Presentation] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Register text element in network with GUID-based indexing.

        Args:
            network: Target network for registration.

        Warns:
            Logs critical warning if GUID already exists in network.

        """
        if self.general.guid in network.texts:
            logger.critical("Text %s already exists, overwriting", self.general.guid)
        network.texts[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete text element to VNF format.

        Returns:
            Multi-line string with all element sections for VNF file.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Line {line.serialize()}" for line in self.lines)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> TextMV:
        """Parse complete text element from VNF section data.

        Args:
            data: Dictionary containing parsed VNF section data with keys:
                - general: List of general property dictionaries
                - lines: List of line property dictionaries
                - presentations: List of presentation property dictionaries

        Returns:
            Initialized TTextMS instance with parsed properties.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        lines_data = data.get("lines", [])
        lines = [cls.Line.deserialize(line_data) for line_data in lines_data]

        presentations_data = data.get("presentations", [])
        presentations = [cls.Presentation.deserialize(pres_data) for pres_data in presentations_data]

        return cls(
            general=general,
            lines=lines,
            presentations=presentations,
        )
