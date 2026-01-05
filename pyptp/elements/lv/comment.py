"""Comment element for low-voltage network documentation.

Provides text-based annotations and documentation capability
for LV network elements, supporting network documentation
and operational notes within GNF format files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyptp.elements.serialization_helpers import write_unquoted_string_no_skip

if TYPE_CHECKING:
    from pyptp.elements.lv.shared import Comment
    from pyptp.network_lv import NetworkLV


@dataclass
class CommentLV:
    """Text comment element for LV network documentation.

    Provides annotation capability for adding descriptive text,
    operational notes, and documentation to low-voltage network
    models within the GNF format structure.
    """

    comment: Comment

    def register(self, network: NetworkLV) -> None:
        """Register comment in LV network for documentation purposes.

        Args:
            network: Target LV network for comment registration.

        """
        network.comments.append(self)

    def serialize(self) -> str:
        """Serialize comment to GNF format.

        Returns:
            Single line string with comment text for GNF file.

        """
        return f"#Comment {write_unquoted_string_no_skip('Text', self.comment.text)}"

    @classmethod
    def deserialize(cls, data: dict) -> CommentLV:
        """Parse comment from GNF format data.

        Args:
            data: Dictionary containing parsed GNF section data
                  with comment text information.

        Returns:
            Initialized TComment instance with parsed text content.

        """
        comment_data = data.get("comment", [{}])[0] if data.get("comment") else {}
        from .shared import Comment

        comment = Comment.deserialize(comment_data)

        return cls(comment=comment)
