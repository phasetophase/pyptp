"""Handler for parsing VNF Comment sections."""

from typing import TYPE_CHECKING

from pyptp.IO.importers._shared_handlers import CommentParser

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class CommentHandler:
    """Handler for VNF COMMENTS sections using shared parsing logic."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register comments from a COMMENTS section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from COMMENTS section.

        """
        CommentParser.parse_and_register(network, chunk)
