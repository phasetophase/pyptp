"""Handler for parsing GNF Comment sections."""

from typing import TYPE_CHECKING

from pyptp.IO.importers._shared_handlers import CommentParser

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


class CommentHandler:
    """Handler for GNF COMMENTS sections using shared parsing logic."""

    def handle(self, network: "NetworkLV", chunk: str) -> None:
        """Parse and register comments from a COMMENTS section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from COMMENTS section.

        """
        CommentParser.parse_and_register(network, chunk)
