"""Handler for parsing VNF Properties sections."""

from typing import TYPE_CHECKING

from pyptp.IO.importers._shared_handlers import PropertiesParser

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class PropertiesHandler:
    """Handler for VNF PROPERTIES sections using shared parsing logic."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register properties from a PROPERTIES section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from PROPERTIES section.

        """
        PropertiesParser.parse_and_register(network, chunk)
