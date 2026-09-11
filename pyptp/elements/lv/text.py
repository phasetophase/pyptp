"""Free text placed on a sheet of an unbalanced (Gaia, GNF) network diagram.

A text has one or more lines and one presentation per sheet it appears on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config

from pyptp.elements.color_utils import CL_BLACK, DelphiColor
from pyptp.elements.element_utils import (
    NIL_GUID,
    Guid,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_delphi_color,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass
class TextLV(HasPresentationsMixin):
    """Free text annotation on a diagram sheet.

    Lines are kept as plain strings, matching FrameLV. The VNF counterpart
    TextMV wraps each line in a Line object instead.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """Identification and timestamps of the text."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0.0
        mutation_date: int = optional_field(0)
        revision_date: int = optional_field(0)

        def serialize(self) -> str:
            """Serialize General properties to GNF format.

            Returns:
                Space-separated property string for the #General section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TextLV.General:
            """Parse General properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
            )

    @dataclass
    class Presentation(DataClassJsonMixin):
        """Position and font of the text on one sheet."""

        sheet: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """Sheet GUID where this presentation is displayed."""

        x: int = 0
        """X position of the text on the sheet."""

        y: int = 0
        """Y position of the text on the sheet."""

        text_color: DelphiColor = CL_BLACK
        """Color of the text."""

        text_size: int = 10
        """Size of the text."""

        font: str = string_field("Arial")
        """Font family of the text."""

        text_style: int = optional_field(0)
        """Delphi font style bitmask (bold, italic, underline, strikeout)."""

        upside_down_text: bool = False
        """Rendered rotated 180 degrees."""

        def serialize(self) -> str:
            """Serialize Presentation properties to GNF format.

            Returns:
                Space-separated property string for the #Presentation section.

            """
            return serialize_properties(
                write_guid_no_skip("Sheet", self.sheet),
                write_integer("X", self.x, skip=0),
                write_integer("Y", self.y, skip=0),
                write_delphi_color("TextColor", self.text_color, skip=CL_BLACK),
                write_integer("TextSize", self.text_size, skip=10),
                write_quote_string("Font", self.font),
                write_integer("TextStyle", self.text_style, skip=0),
                write_boolean("UpsideDownText", value=self.upside_down_text),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TextLV.Presentation:
            """Parse Presentation properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized Presentation instance with parsed properties.

            """
            return cls(
                sheet=decode_guid(data.get("Sheet", str(NIL_GUID))),
                x=data.get("X", 0),
                y=data.get("Y", 0),
                text_color=data.get("TextColor", CL_BLACK),
                text_size=data.get("TextSize", 10),
                font=data.get("Font", "Arial"),
                text_style=data.get("TextStyle", 0),
                upside_down_text=data.get("UpsideDownText", False),
            )

    general: General
    lines: list[str] = field(default_factory=list)
    presentations: list[Presentation] = field(default_factory=list)

    def register(self, network: NetworkLV) -> None:
        """Add the text to the network, keyed by GUID.

        Logs at critical level and overwrites when the GUID already exists.

        Args:
            network: Network to add the text to.

        """
        if self.general.guid in network.texts:
            logger.critical("Text %s already exists, overwriting", self.general.guid)
        network.texts[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the text to its GNF lines (#General, #Line, #Presentation)."""
        out = [f"#General {self.general.serialize()}"]
        out.extend(f"#Line Text:{line}" for line in self.lines)
        out.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(out)

    @classmethod
    def deserialize(cls, data: dict) -> TextLV:
        """Build a text from parsed GNF section data.

        Args:
            data: Parsed sections keyed by 'general', 'lines' (raw line strings)
                and 'presentations'.

        Returns:
            Parsed TextLV.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        lines = [str(line) for line in data.get("lines", [])]

        presentations_data = data.get("presentations", [])
        presentations = [cls.Presentation.deserialize(pres_data) for pres_data in presentations_data]

        return cls(
            general=general,
            lines=lines,
            presentations=presentations,
        )
