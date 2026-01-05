"""Shared properties parsing logic for GNF and VNF formats.

Both GNF (LV) and VNF (MV) use identical PROPERTIES section structure,
so this module provides common parsing utilities.
"""

from __future__ import annotations

import re

from pyptp.elements.lv.properties import PropertiesLV
from pyptp.elements.mv.properties import PropertiesMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.ptp_log import logger


class PropertiesParser:
    """Shared parser for PROPERTIES sections in GNF/VNF files.

    Properties sections have a unique structure with multiple sub-sections
    (#System, #Network, #General, etc.) that don't follow the standard
    #General-based element pattern used by other file sections.
    """

    SECTION_NAMES = ("System", "Network", "General", "Invisible", "History", "HistoryItems", "Users")

    @classmethod
    def parse_and_register(cls, network: NetworkLV | NetworkMV, chunk: str) -> None:
        """Parse properties from chunk and register in network.

        Args:
            network: Target network for registration.
            chunk: Raw text content from PROPERTIES section.

        """
        section_data = cls._parse_sections(chunk)
        data = cls._to_deserialize_format(section_data)

        if isinstance(network, NetworkLV):
            try:
                properties = PropertiesLV.deserialize(data)
                properties.register(network)
            except (KeyError, ValueError, TypeError):
                logger.exception("Failed to deserialize LV properties, using defaults")
                properties = PropertiesLV(system=PropertiesLV.System())
                properties.register(network)
        elif isinstance(network, NetworkMV):
            try:
                properties = PropertiesMV.deserialize(data)
                properties.register(network)
            except (KeyError, ValueError, TypeError):
                logger.exception("Failed to deserialize MV properties, using defaults")
                properties = PropertiesMV(system=PropertiesMV.System())
                properties.register(network)
        else:
            msg = f"Unsupported network type: {type(network).__name__}"
            raise TypeError(msg)

    @classmethod
    def _parse_sections(cls, chunk: str) -> dict[str, dict]:
        """Parse all property sections from chunk.

        Args:
            chunk: Raw text content from PROPERTIES section.

        Returns:
            Dictionary mapping section names to parsed properties.

        """
        section_data: dict[str, dict] = {name: {} for name in cls.SECTION_NAMES}

        # Find all property lines: #SectionName Property:Value ...
        property_lines = re.findall(r"^#(\w+)\s*(.*)$", chunk, re.MULTILINE)

        for section_name, properties_text in property_lines:
            if section_name in section_data:
                section_data[section_name] = cls._parse_properties(properties_text)

        return section_data

    @classmethod
    def _to_deserialize_format(cls, section_data: dict[str, dict]) -> dict[str, list[dict]]:
        """Convert parsed sections to deserialize() format.

        Args:
            section_data: Dictionary of section name to properties dict.

        Returns:
            Dictionary with lowercase keys and list-wrapped values.

        """
        return {
            "system": [section_data["System"]] if section_data["System"] else [],
            "network": [section_data["Network"]] if section_data["Network"] else [],
            "general": [section_data["General"]] if section_data["General"] else [],
            "invisible": [section_data["Invisible"]] if section_data["Invisible"] else [],
            "history": [section_data["History"]] if section_data["History"] else [],
            "history_items": [section_data["HistoryItems"]] if section_data["HistoryItems"] else [],
            "users": [section_data["Users"]] if section_data["Users"] else [],
        }

    @classmethod
    def _parse_properties(cls, text: str) -> dict:
        """Parse property key-value pairs from a line.

        Args:
            text: Property string like "Key1:'value1' Key2:123"

        Returns:
            Dictionary of parsed properties with type coercion.

        """
        parsed: dict = {}
        pattern = re.compile(r"(\w+):(?:'([^']*)'|(\S+))")

        for match in pattern.finditer(text):
            key = match.group(1)
            # Value is either quoted (group 2) or unquoted (group 3)
            val_str = match.group(2) if match.group(2) is not None else match.group(3)

            if match.group(2) is None:  # Unquoted - apply type coercion
                parsed[key] = cls._coerce_value(val_str)
            else:  # Quoted - keep as string
                parsed[key] = val_str

        return parsed

    @classmethod
    def _coerce_value(cls, val_str: str) -> bool | int | float | str:
        """Coerce string value to appropriate Python type.

        Args:
            val_str: Raw string value from file.

        Returns:
            Converted value (bool, int, float, or str).

        """
        if val_str.lower() in ("true", "false"):
            return val_str.lower() == "true"

        # Handle European decimal format (comma as decimal separator)
        if "," in val_str:
            normalized = val_str.replace(",", ".")
            if normalized.replace(".", "").replace("-", "").isdigit():
                return float(normalized)

        if val_str.lstrip("-").isdigit():
            return int(val_str)

        if val_str.replace(".", "").replace("-", "").isdigit():
            return float(val_str)

        return val_str
