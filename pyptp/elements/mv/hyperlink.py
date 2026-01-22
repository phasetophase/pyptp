"""Medium-voltage hyperlink element for external references.

Provides URL storage for linking MV distribution network diagrams
to external documentation, resources, or related network files.
"""

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
    """Medium-voltage hyperlink storing external URL references.

    Supports linking network diagrams to external documentation,
    resources, or related files through URL storage.
    """

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
