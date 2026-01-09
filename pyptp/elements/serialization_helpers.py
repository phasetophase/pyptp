"""Serialization helpers for GNF/VNF format output.

Provides standardized functions for serializing different data types to GNF/VNF format
with consistent formatting and optional default value skipping for minimal file output.
"""

from __future__ import annotations

from pyptp.ptp_log import logger

from .color_utils import CL_BLACK, DelphiColor
from .element_utils import NIL_GUID, Guid


def write_guid(prop: str, value: Guid, skip: Guid = NIL_GUID) -> str:
    """Serialize GUID property with optional skipping.

    Args:
        prop: Property name.
        value: GUID value to serialize.
        skip: Value to skip (default: NIL_GUID).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if value != skip:
        return f"{prop}:'{{{str(value).upper()}}}'"
    return ""


def write_guid_no_skip(prop: str, value: Guid) -> str:
    """Serialize GUID property without skipping.

    Args:
        prop: Property name.
        value: GUID value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:'{{{str(value).upper()}}}'"


def sanitize_quoted_string(value: str, prop: str | None = None) -> str:
    """Sanitize string for quoted serialization by replacing illegal characters.

    Single quotes in quoted strings would break the GNF/VNF file format since
    quoted properties use the format `Property:'value'`. This function replaces
    single quotes with underscores and logs a warning when sanitization occurs.

    Args:
        value: String value to sanitize.
        prop: Optional property name for warning context.

    Returns:
        Sanitized string safe for quoted serialization.

    """
    if "'" in value:
        sanitized = value.replace("'", "_")
        context = f" for property '{prop}'" if prop else ""
        logger.warning(
            "Sanitized single quote in quoted string%s: '%s' -> '%s'",
            context,
            value,
            sanitized,
        )
        return sanitized
    return value


def write_quote_string(prop: str, value: str, skip: str = "") -> str:
    """Serialize quoted string property with optional skipping.

    Automatically sanitizes single quotes to prevent format corruption.

    Args:
        prop: Property name.
        value: String value to serialize.
        skip: Value to skip (default: empty string).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if value != skip:
        sanitized = sanitize_quoted_string(value, prop)
        return f"{prop}:'{sanitized}'"
    return ""


def write_quote_string_no_skip(prop: str, value: str) -> str:
    """Serialize quoted string property without skipping.

    Automatically sanitizes single quotes to prevent format corruption.

    Args:
        prop: Property name.
        value: String value to serialize.

    Returns:
        Formatted property string.

    """
    sanitized = sanitize_quoted_string(value, prop)
    return f"{prop}:'{sanitized}'"


def write_string_no_skip(prop: str, value: str) -> str:
    """Serialize unquoted string property without skipping.

    Args:
        prop: Property name.
        value: String value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:{value}"


def write_unquoted_string_no_skip(prop: str, value: str) -> str:
    """Serialize unquoted string property without skipping.

    Used for comments and text fields that don't require quotes.

    Args:
        prop: Property name.
        value: String value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:{value}"


def write_float_no_skip(prop: str, value: float) -> str:
    """Serialize float property without skipping.

    Args:
        prop: Property name.
        value: Float/int value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:{value}"


def write_double(prop: str, value: float, skip: float = 0.0) -> str:
    """Serialize float property with optional skipping.

    Args:
        prop: Property name.
        value: Float/int value to serialize.
        skip: Value to skip (default: 0.0).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if value != skip:
        return f"{prop}:{value}"
    return ""


def write_double_no_skip(prop: str, value: float) -> str:
    """Serialize float property without skipping.

    Args:
        prop: Property name.
        value: Float/int value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:{value}"


def write_boolean(prop: str, value: bool, skip: bool = False) -> str:  # noqa: FBT001, FBT002
    """Serialize boolean property with optional skipping.

    Args:
        prop: Property name.
        value: Boolean value to serialize.
        skip: Value to skip (default: False).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if value != skip:
        return f"{prop}:{value!s}"
    return ""


def write_boolean_no_skip(prop: str, value: bool) -> str:  # noqa: FBT001
    """Serialize boolean property without skipping.

    Args:
        prop: Property name.
        value: Boolean value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:{value!s}"


def write_boolean_as_byte(prop: str, *, value: bool, skip: bool = False) -> str:
    """Serialize boolean property as byte (0/1) with optional skipping.

    Args:
        prop: Property name.
        value: Boolean value to serialize.
        skip: Value to skip (default: False).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if value != skip:
        return f"{prop}:{1 if value else 0}"
    return ""


def write_boolean_as_byte_no_skip(prop: str, *, value: bool) -> str:
    """Serialize boolean property as byte (0/1) without skipping.

    Args:
        prop: Property name.
        value: Boolean value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:{1 if value else 0}"


def write_integer(prop: str, value: int, skip: int = 0) -> str:
    """Serialize integer property with optional skipping.

    Args:
        prop: Property name.
        value: Integer value to serialize (will be cast to int).
        skip: Value to skip (default: 0).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if int(value) != skip:
        return f"{prop}:{int(value)}"
    return ""


def write_integer_no_skip(prop: str, value: int) -> str:
    """Serialize integer property without skipping.

    Args:
        prop: Property name.
        value: Integer value to serialize (will be cast to int).

    Returns:
        Formatted property string.

    """
    return f"{prop}:{int(value)}"


def write_color(prop: str, value: int, skip: int = 0) -> str:
    """Serialize color property with optional skipping.

    Args:
        prop: Property name.
        value: Color value as integer.
        skip: Value to skip (default: 0, which is black).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if value != skip:
        return f"{prop}:0x{value:08x}"
    return ""


def write_color_no_skip(prop: str, value: int) -> str:
    """Serialize color property without skipping.

    Args:
        prop: Property name.
        value: Color value as integer.

    Returns:
        Formatted property string.

    """
    return f"{prop}:0x{value:08x}"


def write_delphi_color(prop: str, value: DelphiColor, skip: DelphiColor = CL_BLACK) -> str:
    """Serialize DelphiColor property with optional skipping.

    Args:
        prop: Property name.
        value: DelphiColor value to serialize.
        skip: Value to skip (default: CL_BLACK).

    Returns:
        Formatted property string or empty string if skipped.

    """
    if value != skip:
        return f"{prop}:{value}"
    return ""


def write_delphi_color_no_skip(prop: str, value: DelphiColor) -> str:
    """Serialize DelphiColor property without skipping.

    Args:
        prop: Property name.
        value: DelphiColor value to serialize.

    Returns:
        Formatted property string.

    """
    return f"{prop}:{value}"


def serialize_properties(*props: str) -> str:
    """Combine multiple property strings into space-separated output.

    Args:
        *props: Property strings to combine.

    Returns:
        Space-separated property string with empty strings filtered out.

    """
    return " ".join(prop for prop in props if prop) + " "


def write_section_if_not_empty(section_name: str, serialized_content: str | None) -> str:
    """Write section header only if content is not empty.

    Args:
        section_name: Name of the section (e.g., "Fields", "Presentation").
        serialized_content: The serialized content of the section.

    Returns:
        Full section line or empty string if content is empty.

    """
    if serialized_content and serialized_content.strip():
        return f"#{section_name} {serialized_content}"
    return ""
