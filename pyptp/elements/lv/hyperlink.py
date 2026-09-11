"""Hyperlink entries of an unbalanced (Gaia, GNF) network.

A network keeps a plain list of URLs or file paths that Gaia shows in
its hyperlinks menu, for example the data dump a network was generated from.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.serialization_helpers import write_quote_string_no_skip

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass_json
@dataclass
class HyperlinkLV(DataClassJsonMixin):
    """A single hyperlink (URL or file path) attached to the network."""

    url: str = ""

    def serialize(self) -> str:
        """Serialize to a GNF #Hyperlink line."""
        return f"#Hyperlink {write_quote_string_no_skip('URL', self.url)}"

    @classmethod
    def deserialize(cls, data: dict) -> HyperlinkLV:
        """Build a hyperlink from a parsed #Hyperlink property dictionary."""
        return cls(
            url=data.get("URL", ""),
        )

    def register(self, network: NetworkLV) -> None:
        """Append the hyperlink to the network."""
        network.hyperlinks.append(self)
