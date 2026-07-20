"""Shared mixins for electrical network elements.

Provides ExtrasNotesMixin for managing Extra and Note annotations,
and HasPresentationsMixin for ensuring presentation list consistency
across all GNF/VNF electrical elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dataclasses_json import DataClassJsonMixin, config, dataclass_json  # type: ignore[import-untyped]

from pyptp.elements.color_utils import CL_BLACK, DelphiColor
from pyptp.elements.element_utils import (
    FloatCoords,
    decode_float_coords,
    encode_float_coords,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_delphi_color,
    write_integer,
    write_quote_string,
)

if TYPE_CHECKING:
    from pyptp.elements.element_utils import Guid


@dataclass_json
@dataclass
class Extra(DataClassJsonMixin):
    """Extra text annotation for electrical network elements.

    Provides additional metadata or documentation that extends
    the core electrical properties of network elements.
    """

    text: str = string_field()

    def encode(self) -> dict[str, Any]:
        """Encode extra as GNF/VNF format dictionary.

        Returns:
            Dictionary with 'Text' key for GNF/VNF serialization.

        """
        return {"Text": self.text}

    @classmethod
    def deserialize(cls, data: dict) -> Extra:
        """Parse extra from GNF/VNF section data.

        Args:
            data: Property dictionary from GNF/VNF parsing.

        Returns:
            Initialized Extra instance with parsed text content.

        """
        return cls(
            text=data.get("text", data.get("Text", "")),
        )


@dataclass_json
@dataclass
class Line(DataClassJsonMixin):
    """Line text annotation for electrical network elements.

    Provides additional metadata or documentation that extends
    the core electrical properties of network elements.
    """

    text: str = string_field()

    def encode(self) -> dict[str, Any]:
        """Encode Line as GNF/VNF format dictionary.

        Returns:
            Dictionary with 'Text' key for GNF/VNF serialization.

        """
        return {"Text": self.text}

    @classmethod
    def deserialize(cls, data: dict) -> Line:
        """Parse Line from GNF/VNF section data.

        Args:
            data: Property dictionary from GNF/VNF parsing.

        Returns:
            Initialized Line instance with parsed text content.

        """
        return cls(
            text=data.get("text", data.get("Text", "")),
        )


@dataclass_json
@dataclass
class Note(DataClassJsonMixin):
    """A free-text annotation attached to a network element.

    Notes are persisted as a single block of text with one note per line. As a
    result, a note containing line breaks is split into one note per line when the
    network is reloaded, which may change the number of notes in the list. To keep
    the list identical across a save and reload, limit each note to a single line.

    Attributes:
        text: The note's text content.

    """

    text: str = string_field()

    def encode(self) -> dict[str, Any]:
        """Encode note as GNF/VNF format dictionary.

        Returns:
            Dictionary with 'Text' key for GNF/VNF serialization.

        """
        return {"Text": self.text}

    @classmethod
    def deserialize(cls, data: dict) -> Note:
        """Parse note from GNF/VNF section data.

        Args:
            data: Property dictionary from GNF/VNF parsing.

        Returns:
            Initialized Note instance with parsed text content.

        """
        return cls(
            text=data.get("text", data.get("Text", "")),
        )


@dataclass_json
@dataclass
class Geography(DataClassJsonMixin):
    """Geographical coordinate data for network elements.

    Stores coordinate pairs for geographical positioning of elements
    in GNF/VNF network files. Used for mapping and GIS integration.
    """

    coordinates: FloatCoords = field(
        default_factory=list,
        metadata=config(encoder=encode_float_coords, decoder=decode_float_coords),
    )

    def serialize(self) -> str:
        """Serialize Geography coordinates to GNF/VNF format.

        Returns:
            Formatted coordinate string for the #Geo section.

        """
        if self.coordinates:
            return f"Coordinates:{encode_float_coords(self.coordinates)}"
        return ""

    @classmethod
    def deserialize(cls, data: dict) -> Geography:
        """Parse Geography from GNF/VNF section data.

        Args:
            data: Property dictionary from GNF/VNF parsing.

        Returns:
            Initialized Geography instance with parsed coordinates.

        """
        return cls(
            coordinates=decode_float_coords(data.get("Coordinates", "''")),
        )


@dataclass_json
@dataclass
class Icon(DataClassJsonMixin):
    """Optional icon displayed near a network element in diagrams.

    A short text in a shaped background (configurable color, shape, size).
    """

    text: str = string_field()
    text_color: DelphiColor = CL_BLACK
    background_color: DelphiColor = CL_BLACK
    shape: int = 0
    size: int = 0

    def serialize(self) -> str:
        """Serialize icon properties to GNF/VNF format."""
        return serialize_properties(
            write_quote_string("Text", self.text),
            write_delphi_color("TextColor", self.text_color),
            write_delphi_color("BackgroundColor", self.background_color),
            write_integer("Shape", self.shape),
            write_integer("Size", self.size),
        )

    @classmethod
    def deserialize(cls, data: dict) -> Icon:
        """Parse icon properties from GNF/VNF section data."""
        return cls(
            text=data.get("Text", ""),
            text_color=DelphiColor(data.get("TextColor", str(CL_BLACK))),
            background_color=DelphiColor(data.get("BackgroundColor", str(CL_BLACK))),
            shape=data.get("Shape", 0),
            size=data.get("Size", 0),
        )


# Type aliases for convenient imports
E = Extra
N = Note


@dataclass(kw_only=True)
class ExtrasNotesMixin:
    """Mixin providing Extra and Note annotation support.

    Enables electrical network elements to carry additional metadata
    through Extra and Note annotations while ensuring list consistency
    during deserialization from GNF/VNF formats.
    """

    extras: list[E] = field(default_factory=list)
    notes: list[N] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize extras and notes to list format during initialization."""
        if self.extras is None:
            self.extras = []
        elif not isinstance(self.extras, list):
            self.extras = [self.extras]

        if self.notes is None:
            self.notes = []
        elif not isinstance(self.notes, list):
            self.notes = [self.notes]

    @property
    def safe_extras(self) -> list[E]:
        """Safe accessor for extras list.

        Returns:
            Extras list, guaranteed to be non-None for safe iteration.

        """
        if self.extras is None:
            return []
        return self.extras

    @property
    def safe_notes(self) -> list[N]:
        """Safe accessor for notes list.

        Returns:
            Notes list, guaranteed to be non-None for safe iteration.

        """
        if self.notes is None:
            return []
        return self.notes


@dataclass(kw_only=True)
class IconMixin:
    """Mixin providing an optional Icon annotation.

    Enables network elements to carry a diagram icon that is
    persisted as a `#Icon` section in GNF/VNF formats.
    """

    icon: Icon | None = None


class HasPresentationsMixin:
    """Mixin ensuring presentations attribute is always a list.

    Provides consistent presentation list handling for electrical
    elements that support graphical representations in GNF/VNF.
    """

    presentations: list[Any]

    def __post_init__(self) -> None:
        """Normalize presentations to list format during initialization."""
        if hasattr(self, "presentations"):
            val = self.presentations
            if val is None:
                self.presentations = []
            elif not isinstance(val, list):
                self.presentations = [val]

    def get_presentation_on_sheet(self, sheet_guid: Guid) -> Any | None:  # noqa: ANN401
        """Find this element's presentation on a specific sheet.

        Args:
            sheet_guid: GUID of the sheet to find presentation for.

        Returns:
            The presentation on the matching sheet, or None if not found.

        Note:
            Returns Any because presentation types vary by element (NodePresentation,
            BranchPresentation, etc.) and this mixin is used across all element types.

        """
        for pres in self.presentations:
            if pres.sheet == sheet_guid:
                return pres
        return None
