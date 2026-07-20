"""Handler for parsing GNF MEASUREMENTFILES sections."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.lv.measurement_file import MeasurementFileLV

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


class MeasurementFileHandler:
    """Handler for GNF MEASUREMENTFILES sections."""

    def handle(self, network: "NetworkLV", chunk: str) -> None:
        """Parse and register measurement files from a MEASUREMENTFILES section chunk.

        Args:
            network: Target network for registration.
            chunk: Raw text content from MEASUREMENTFILES section.

        """
        pattern = re.compile(r"^#File\s+FileName:(.+)$", re.MULTILINE)

        for match in pattern.finditer(chunk):
            measurement_file = MeasurementFileLV(filename=match.group(1).strip())
            measurement_file.register(network)
