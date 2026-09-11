"""Handler for the HYPERLINKS section of a GNF file."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pyptp.elements.lv.hyperlink import HyperlinkLV

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

_HYPERLINK_LINE = re.compile(r"^#Hyperlink\s+URL:'([^']*)'", re.MULTILINE)


class HyperlinkHandler:
    """Parses the HYPERLINKS section of a GNF file.

    The section holds bare #Hyperlink lines without a #General header, so the
    declarative handler cannot split it into components. Each line is matched
    directly instead.
    """

    def handle(self, network: NetworkLV, chunk: str) -> None:
        """Register one HyperlinkLV per #Hyperlink line in the section.

        Args:
            network: Network to add the hyperlinks to.
            chunk: Raw text of the HYPERLINKS section.

        """
        for match in _HYPERLINK_LINE.finditer(chunk):
            HyperlinkLV(url=match.group(1)).register(network)
