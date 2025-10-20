"""Handler for parsing VNF Hyperlink sections with custom parsing logic."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.mv.hyperlink import HyperlinkMV

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class HyperlinkHandler:
    """Custom handler for VNF hyperlinks."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register hyperlinks from a HYPERLINKS section chunk.

        Args:
            network: Target network for registration
            chunk: Raw text content from HYPERLINKS section

        """
        # Find all hyperlink lines starting with #Hyperlink URL:
        hyperlink_pattern = re.compile(r"^#Hyperlink\s+URL:'([^']*)'", re.MULTILINE)

        for match in hyperlink_pattern.finditer(chunk):
            url = match.group(1)
            hyperlink = HyperlinkMV(url=url)
            hyperlink.register(network)
