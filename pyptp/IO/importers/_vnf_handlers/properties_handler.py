"""Custom handler for parsing VNF Properties sections."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.mv.properties import PropertiesMV
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class PropertiesHandler:
    """Parses VNF Properties using a declarative recipe."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register properties from a PROPERTIES section chunk.

        Args:
            network: Target network for registration
            chunk: Raw text content from PROPERTIES section

        """
        system_data = {}
        network_data = {}
        general_data = {}
        invisible_data = {}
        history_data = {}
        history_items_data = {}
        users_data = {}

        # Find all property lines
        property_lines = re.findall(r"^#(\w+)\s+(.*)$", chunk, re.MULTILINE)

        for section_name, properties_text in property_lines:
            key_value_pattern = re.compile(r"(\w+):(?:'([^']*)'|(\S+))")
            parsed_properties = {}

            for match in key_value_pattern.finditer(properties_text):
                key = match.group(1)
                val_str = match.group(2) if match.group(2) is not None else match.group(3)

                # Convert numeric strings
                if match.group(2) is None:  # Unquoted value
                    if val_str.lower() in ("true", "false"):
                        parsed_properties[key] = val_str.lower() == "true"
                    elif "," in val_str and val_str.replace(",", ".").replace(".", "").isdigit():
                        # Handle European decimal format
                        parsed_properties[key] = float(val_str.replace(",", "."))
                    elif val_str.isdigit():
                        parsed_properties[key] = int(val_str)
                    elif val_str.replace(".", "").isdigit():
                        parsed_properties[key] = float(val_str)
                    else:
                        parsed_properties[key] = val_str
                else:  # Quoted value
                    parsed_properties[key] = val_str

            # Store in appropriate section
            if section_name == "System":
                system_data = parsed_properties
            elif section_name == "Network":
                network_data = parsed_properties
            elif section_name == "General":
                general_data = parsed_properties
            elif section_name == "Invisible":
                invisible_data = parsed_properties
            elif section_name == "History":
                history_data = parsed_properties
            elif section_name == "HistoryItems":
                history_items_data = parsed_properties
            elif section_name == "Users":
                users_data = parsed_properties

        data = {
            "system": [system_data] if system_data else [],
            "network": [network_data] if network_data else [],
            "general": [general_data] if general_data else [],
            "invisible": [invisible_data] if invisible_data else [],
            "history": [history_data] if history_data else [],
            "history_items": [history_items_data] if history_items_data else [],
            "users": [users_data] if users_data else [],
        }

        # Create and register properties
        try:
            properties = PropertiesMV.deserialize(data)
            properties.register(network)
        except (KeyError, ValueError, TypeError):
            logger.exception("Failed to deserialize properties")
            system = PropertiesMV.System()
            properties = PropertiesMV(system=system)
            properties.register(network)
