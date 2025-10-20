"""Hyperlink element for MV networks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.serialization_helpers import write_quote_string_no_skip

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class HyperlinkMV(DataClassJsonMixin):
    """Represents a hyperlink (MV)."""

    url: str = ""

    def serialize(self) -> str:
        """Serialize hyperlink to VNF format."""
        return f"#Hyperlink {write_quote_string_no_skip('URL', self.url)}"

    @classmethod
    def deserialize(cls, data: dict) -> HyperlinkMV:
        """Deserialize hyperlink from VNF format."""
        return cls(
            url=data.get("URL", ""),
        )

    def register(self, network: NetworkMV) -> None:
        """Register hyperlink in network."""
        network.hyperlinks.append(self)
