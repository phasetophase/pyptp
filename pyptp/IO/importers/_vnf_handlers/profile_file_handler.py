"""Handler for parsing VNF PROFILEFILES sections."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.mv.profile_file import ProfileFileMV

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class ProfileFileHandler:
    """Handler for VNF PROFILEFILES sections."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register profile files from a PROFILEFILES section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from PROFILEFILES section.

        """
        pattern = re.compile(r"^#File\s+FileName:(.+)$", re.MULTILINE)

        for match in pattern.finditer(chunk):
            profile_file = ProfileFileMV(filename=match.group(1).strip())
            profile_file.register(network)
