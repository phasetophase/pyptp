"""Shared mixins for electrical network elements.

Provides ExtrasNotesMixin for managing Extra and Note annotations,
and HasPresentationsMixin for ensuring presentation list consistency
across all GNF/VNF electrical elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dataclasses_json import DataClassJsonMixin, config, dataclass_json  # type: ignore[import-untyped]

from pyptp.elements.element_utils import (
    FloatCoords,
    decode_float_coords,
    encode_float_coords,
    string_field,
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
    """Free-text note annotation for electrical network elements.

    Provides descriptive commentary or operational notes for
    electrical elements that aid in network understanding.
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
