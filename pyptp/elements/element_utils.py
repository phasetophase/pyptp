"""Core utilities for electrical network element management.

Provides GUID management, coordinate encoding/decoding, and type-safe utilities
for electrical network elements in both GNF (Gaia) and VNF (Vision) formats.
Includes field factories for dataclass configuration and format conversion helpers.
"""

from __future__ import annotations

import re
from dataclasses import field
from enum import StrEnum
from typing import TYPE_CHECKING, NewType, Protocol, TypeAlias, TypeVar, cast
from uuid import NAMESPACE_DNS, UUID, uuid3, uuid4

from dataclasses_json import config

from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from collections.abc import Callable

Guid = NewType("Guid", UUID)

DEFAULT_PROFILE_GUID: Guid = Guid(
    UUID("A4D813DF-1EE1-4153-806C-DC228D251A79"),
)


class HasGuid(Protocol):
    """Protocol for objects with GUID identification.

    Defines the interface for electrical network elements that can be
    uniquely identified by GUID for network topology management.
    """


IntCoords: TypeAlias = list[tuple[int, int]]
FloatCoords: TypeAlias = list[tuple[float, float]]

FuseTypeIT = NewType("FuseTypeIT", list[list[int | float]])

T = TypeVar("T")

NIL_GUID = Guid(UUID(int=0))

# Branch side identifiers for electrical elements connected to branches
SIDE_NODE1 = 1
SIDE_NODE2 = 2


class LineStyle(StrEnum):
    """Line drawing styles for visual elements."""

    SOLID = "Solid"
    DASH = "Dash"
    DOT = "Dot"
    DASH_DOT = "DashDot"
    DASH_DOT_DOT = "DashDotDot"


class FrameShape(StrEnum):
    """Frame shape types for container elements."""

    RECTANGLE = "Rectangle"
    POLYGON = "Polygon"
    ELLIPSE = "Ellipse"
    PICTURE = "Picture"


def optional_field(default_value: T = None) -> T:
    """Create dataclass field that excludes default values from serialization.

    Args:
        default_value: Value to exclude from serialized output.

    Returns:
        Configured dataclass field with exclusion metadata.

    """
    return cast(
        "T",
        field(
            default=default_value,
            metadata=config(exclude=lambda x: x is default_value),
        ),
    )


def string_field(default: str = "") -> str:
    """Create string field that excludes empty values from serialization.

    Args:
        default: Default string value (typically empty).

    Returns:
        Configured string field with proper encoding and empty string exclusion.

    """
    return field(
        default=default,
        metadata=config(encoder=encode_string, exclude=lambda x: x == ""),
    )


def guid_field(generator: Callable[[], UUID] = uuid4) -> Guid:
    """Create GUID field with automatic generation for new elements.

    Args:
        generator: UUID factory function for generating new GUIDs.

    Returns:
        Configured GUID field with encoder/decoder and automatic generation.

    """
    return field(
        default_factory=lambda: Guid(generator()),
        metadata=config(encoder=encode_guid, decoder=decode_guid),
    )


def nil_guid_field() -> Guid:
    """Create GUID field defaulting to NIL_GUID with serialization exclusion.

    Returns:
        GUID field that excludes NIL_GUID from serialized output.

    """
    return field(
        default=NIL_GUID,
        metadata=config(encoder=encode_guid, exclude=lambda x: x == NIL_GUID),
    )


def required_guid_field() -> Guid:
    """Create mandatory GUID field that errors if unset during serialization.

    Returns:
        GUID field that raises TypeError if NIL_GUID during serialization.

    """
    return field(metadata=config(encoder=encode_guid_required))


def gnf_string_to_standard_float_string(s: str) -> str:
    """Convert GNF regional number format to standard float string.

    Handles European number formatting where comma is decimal separator
    and dot is thousands separator, converting to standard dot-decimal format.

    Args:
        s: GNF-formatted number string with regional formatting.

    Returns:
        Standard float string with dot as decimal separator.

    """
    s = str(s).strip()
    last_dot = s.rfind(".")
    last_comma = s.rfind(",")

    # Comma after dot indicates European format: comma is decimal separator
    if last_comma > last_dot:
        return s.replace(".", "").replace(",", ".")

    # Dot is decimal separator or no comma present
    return s.replace(",", "")


def encode_int_coords(coords: IntCoords) -> str:
    """Encode integer coordinates to GNF format string.

    Args:
        coords: List of integer coordinate tuples (x, y)

    Returns:
        GNF formatted string representation of coordinates

    """
    if not coords or not coords[0]:
        return "''"
    inner = " ".join(f"({x} {y})" for x, y in coords)
    return f"'{{{inner} }}'"


def decode_int_coords(raw: str) -> IntCoords:
    """Decode GNF format string to integer coordinates.

    Args:
        raw: GNF formatted string representation of coordinates

    Returns:
        List of integer coordinate tuples (x, y)

    """
    if not raw or raw == "''":
        return []
    pairs = re.findall(r"\(([^)\s]+)\s+([^)\s]+)\)", raw)
    coords: IntCoords = []
    for xs, ys in pairs:
        x = int(float(gnf_string_to_standard_float_string(xs)))
        y = int(float(gnf_string_to_standard_float_string(ys)))
        coords.append((x, y))
    return coords


def encode_float_coords(coords: FloatCoords) -> str:
    """Encode float coordinates to GNF format string.

    Args:
        coords: List of float coordinate tuples (x, y)

    Returns:
        GNF formatted string representation of coordinates

    """
    if not coords:
        return "''"

    processed_coords = []

    for x, y in coords:
        xs = f"{x:.15G}".replace("E-0", "E-")
        ys = f"{y:.15G}".replace("E-0", "E-")
        processed_coords.append(f"({xs} {ys})")

    if not processed_coords:
        return "''"

    inner = " ".join(processed_coords)
    return f"'{{{inner} }}'"


def decode_float_coords(raw: str) -> FloatCoords:
    """Decode GNF format string to float coordinates.

    Args:
        raw: GNF formatted string representation of coordinates

    Returns:
        List of float coordinate tuples (x, y)

    """
    if not raw or raw == "''":
        return []
    pairs = re.findall(r"\(([^)\s]+)\s+([^)\s]+)\)", raw)
    coords: FloatCoords = []
    for xs, ys in pairs:
        x = float(gnf_string_to_standard_float_string(xs))
        y = float(gnf_string_to_standard_float_string(ys))
        coords.append((x, y))
    return coords


def encode_guid(raw: Guid | HasGuid | UUID | str) -> str:
    """Encode GUID to GNF format string with error handling.

    Converts various GUID representations to GNF format string like
    '{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}'. Handles invalid inputs
    by defaulting to DEFAULT_PROFILE_GUID with warning logging.

    Args:
        raw: GUID in various formats (GUID, HasGuid object, UUID, or string).

    Returns:
        GNF-formatted GUID string or empty string for NIL_GUID.

    """
    if isinstance(raw, str):
        s = raw.strip().strip("'\"")
        try:
            guid = UUID(s.strip("{}"))
        except ValueError:
            logger.warning(
                "Invalid GUID %r encountered; defaulting to DEFAULT_PROFILE_GUID",
                raw,
            )
            guid = DEFAULT_PROFILE_GUID

    elif isinstance(raw, UUID):
        guid = raw

    else:
        candidate = getattr(raw, "GUID", None)
        if not isinstance(candidate, UUID):
            logger.warning(
                "Cannot extract .GUID from %r; defaulting to DEFAULT_PROFILE_GUID",
                raw,
            )
            guid = DEFAULT_PROFILE_GUID
        else:
            guid = candidate

    if guid == NIL_GUID:
        return "''"

    return f"'{{{str(guid).upper()}}}'"


def encode_guid_optional(raw: Guid | HasGuid | UUID | str | None) -> str:
    """Encode optional GUID with None handling.

    Args:
        raw: Optional GUID in various formats or None.

    Returns:
        GNF-formatted GUID string or empty string for None/NIL_GUID.

    """
    if raw is None:
        return "''"
    return encode_guid(raw)


def encode_guid_required(raw: Guid | HasGuid | UUID | str | None) -> str:
    """Encode mandatory GUID with validation.

    Args:
        raw: GUID in various formats that must not be None or NIL_GUID.

    Returns:
        GNF-formatted GUID string.

    Raises:
        TypeError: If GUID is None or NIL_GUID after processing.

    """
    result = encode_guid_optional(raw)
    if result == "''":
        logger.error("Required GUID was missing or nil after decode")
        msg = "Required GUID was not set or was nil"
        raise TypeError(msg)
    return result


def decode_guid(raw: str | Guid) -> Guid:
    """Parse GNF-formatted GUID string back to typed GUID.

    Inverse operation of encode_guid, parsing GNF format strings like
    '{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}' back to type-safe GUID objects
    for electrical element identification.

    Args:
        raw: GNF-formatted GUID string or existing GUID.

    Returns:
        Type-safe GUID object for network element identification.

    """
    if isinstance(raw, UUID):
        return Guid(raw)

    s = raw.strip().strip("'\"")  # e.g. "{59A01667-...}"
    s = s.strip("{}")  # e.g. "59A01667-..."
    return Guid(UUID(s))


def encode_string(string: str) -> str:
    """Encode string for GNF/VNF format output.

    Args:
        string: String to encode.

    Returns:
        Single-quoted string for GNF/VNF format.

    """
    return f"'{string}'"


def create_uuid(identifier: str) -> Guid:
    """Generate deterministic GUID from string identifier.

    Creates reproducible v3 UUID using DNS namespace for consistent
    GUID generation across application runs.

    Args:
        identifier: String identifier for GUID generation.

    Returns:
        Deterministic GUID based on identifier.

    """
    return Guid(uuid3(NAMESPACE_DNS, identifier))


def get_props_as_gv(input_list: list[dict[str, dict[str, object]]]) -> str:
    """Convert property dictionaries to GNF/VNF format lines.

    Args:
        input_list: List of section dictionaries with property key-value pairs.

    Returns:
        Multi-line string with formatted property sections.

    """
    lines: list[str] = []
    for section in input_list:
        for tag, props in section.items():
            kvs = " ".join(f"{k}:{v}" for k, v in props.items())
            lines.append(f"{tag} {kvs}")

    return "\n".join(lines)


def guid_to_string(g: Guid) -> str:
    """Convert GUID to formatted string representation.

    Args:
        g: GUID to convert.

    Returns:
        Uppercase GUID in braces format or empty string for NIL_GUID.

    """
    nil = Guid(UUID(int=0))
    if g == nil:
        return ""
    return f"{{{str(g).upper()}}}"
