"""Shared mixins for electrical network elements.

Provides ExtrasNotesMixin for managing Extra and Note annotations,
and HasPresentationsMixin for ensuring presentation list consistency
across all GNF/VNF electrical elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dataclasses_json import DataClassJsonMixin, dataclass_json  # type: ignore[import-untyped]

from pyptp.elements.element_utils import string_field


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

    def _encode_extras_notes(self) -> list[dict[str, Any]]:
        """Encode extras and notes as GNF/VNF format sections.

        Returns:
            List of section dictionaries with '#Extra' and '#Note' keys
            for GNF/VNF serialization.

        """
        out: list[dict[str, Any]] = []
        out.extend({"#Extra": e.encode()} for e in self.extras)
        out.extend({"#Note": n.encode()} for n in self.notes)
        return out


class HasPresentationsMixin:
    """Mixin ensuring presentations attribute is always a list.

    Provides consistent presentation list handling for electrical
    elements that support graphical representations in GNF/VNF.
    """

    def __post_init__(self) -> None:
        """Normalize presentations to list format during initialization."""
        if hasattr(self, "presentations"):
            val = self.presentations
            if val is None:
                self.presentations = []
            elif not isinstance(val, list):
                self.presentations = [val]
