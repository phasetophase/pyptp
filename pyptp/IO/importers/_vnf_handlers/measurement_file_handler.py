"""Handler for parsing VNF MEASUREMENTFILES sections."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.mv.measurement_file import MeasurementFileMV

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class MeasurementFileHandler:
    """Handler for VNF MEASUREMENTFILES sections."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register measurement files from a MEASUREMENTFILES section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from MEASUREMENTFILES section.

        """
        pattern = re.compile(r"^#File\s+FileName:(.+)$", re.MULTILINE)

        for match in pattern.finditer(chunk):
            measurement_file = MeasurementFileMV(filename=match.group(1).strip())
            measurement_file.register(network)
