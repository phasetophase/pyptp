"""Handler for parsing VNF NETWORKOPTIONS sections."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.mv.network_options import NetworkOptionsMV

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class NetworkOptionsHandler:
    """Handler for VNF NETWORKOPTIONS sections."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register network options from a NETWORKOPTIONS section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from NETWORKOPTIONS section.

        """
        pattern = re.compile(r"^#General\s+WinterProfileItems:(\S+)", re.MULTILINE)

        match = pattern.search(chunk)
        if match:
            options = NetworkOptionsMV(winter_profile_items=match.group(1))
            options.register(network)
