"""Handler for parsing GNF PROFILEFILES sections."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.lv.profile_file import ProfileFileLV

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


class ProfileFileHandler:
    """Handler for GNF PROFILEFILES sections."""

    def handle(self, network: "NetworkLV", chunk: str) -> None:
        """Parse and register profile files from a PROFILEFILES section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from PROFILEFILES section.

        """
        pattern = re.compile(r"^#File\s+FileName:(.+)$", re.MULTILINE)

        for match in pattern.finditer(chunk):
            profile_file = ProfileFileLV(filename=match.group(1).strip())
            profile_file.register(network)
