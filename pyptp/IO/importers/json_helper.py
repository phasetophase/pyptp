"""GNF/VNF format parsing utilities.

Provides high-performance parsing of key-value property lines from GNF and VNF files
into typed Python dictionaries. Handles electrical data format conversions and
optimizations for large-scale network file processing.
"""

from __future__ import annotations

import re
from typing import Any

from pyptp.elements.element_utils import gnf_string_to_standard_float_string

__all__: list[str] = ["parse_gnf_line_to_dict"]

# Pre-compile regex for better performance
_KEY_VALUE_PATTERN = re.compile(r"(\w+):(?:'([^']*)'|(\S+))")


def parse_gnf_line_to_dict(payload: str) -> dict[str, Any]:
    """Parse GNF/VNF property line into typed dictionary.

    Converts space-separated key-value pairs from network file formats into
    Python dictionaries with automatic type inference for strings, numbers,
    and booleans.

    Args:
        payload: Property line containing key-value pairs.

    Returns:
        Dictionary with parsed properties and appropriate Python types.

    Example:
        >>> parse_gnf_line_to_dict("Name:'Generator' Voltage:11000 Active:true")
        {'Name': 'Generator', 'Voltage': 11000.0, 'Active': True}

    """
    parsed_dict = {}

    # Use pre-compiled regex for better performance
    for match in _KEY_VALUE_PATTERN.finditer(payload):
        key = match.group(1)
        # Value is either the quoted group (2) or the unquoted group (3)
        val_str = match.group(2) if match.group(2) is not None else match.group(3)

        # If the value was not quoted, it's a number or a special literal
        if match.group(2) is None:
            # Optimize boolean checks - use direct string comparison
            if val_str == "true":
                parsed_dict[key] = True
                continue
            if val_str == "false":
                parsed_dict[key] = False
                continue

            if "." in val_str:
                # Likely a float
                try:
                    standard_format_str = gnf_string_to_standard_float_string(val_str)
                    parsed_dict[key] = float(standard_format_str)
                except (ValueError, TypeError):
                    parsed_dict[key] = val_str
            elif val_str.isdigit():
                # Definitely an integer
                parsed_dict[key] = int(val_str)
            else:
                # Try float conversion for non-digit strings
                try:
                    standard_format_str = gnf_string_to_standard_float_string(val_str)
                    parsed_dict[key] = float(standard_format_str)
                except (ValueError, TypeError):
                    parsed_dict[key] = val_str
        else:
            # Quoted value - keep as string
            parsed_dict[key] = val_str

    return parsed_dict


def parse_gnf_line_to_dict_optimized(lines: list[str]) -> list[dict[str, Any]]:
    """Parse multiple GNF/VNF lines into dictionaries with optimized batching.

    This function processes multiple lines at once for better performance.
    """
    if not lines:
        return []

    return [parse_gnf_line_to_dict(line) for line in lines if line.strip()]
