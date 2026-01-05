"""Handler for parsing GNF Properties sections."""

from typing import TYPE_CHECKING

from pyptp.IO.importers._shared_handlers import PropertiesParser

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


class PropertiesHandler:
    """Handler for GNF PROPERTIES sections using shared parsing logic."""

    def handle(self, network: "NetworkLV", chunk: str) -> None:
        """Parse and register properties from a PROPERTIES section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from PROPERTIES section.

        """
        PropertiesParser.parse_and_register(network, chunk)
