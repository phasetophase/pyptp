"""Comment element for medium-voltage network documentation.

Provides text-based annotations and documentation capability
for MV network elements, supporting network documentation
and operational notes within VNF format files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyptp.elements.serialization_helpers import write_unquoted_string_no_skip

if TYPE_CHECKING:
    from pyptp.elements.mv.shared import Comment
    from pyptp.network_mv import NetworkMV


@dataclass
class CommentMV:
    """Text comment element for MV network documentation.

    Provides annotation capability for adding descriptive text,
    operational notes, and documentation to medium-voltage network
    models within the VNF format structure.
    """

    comment: Comment

    def register(self, network: NetworkMV) -> None:
        """Register comment in MV network for documentation purposes.

        Args:
            network: Target MV network for comment registration.

        """
        network.comments.append(self)

    def serialize(self) -> str:
        """Serialize comment to VNF format.

        Returns:
            Single line string with comment text for VNF file.

        """
        return f"#Comment {write_unquoted_string_no_skip('Text', self.comment.text)}"

    @classmethod
    def deserialize(cls, data: dict) -> CommentMV:
        """Parse comment from VNF format data.

        Args:
            data: Dictionary containing parsed VNF section data
                  with comment text information.

        Returns:
            Initialized TCommentMS instance with parsed text content.

        """
        comment_data = data.get("comment", [{}])[0] if data.get("comment") else {}
        from .shared import Comment

        comment = Comment.deserialize(comment_data)
        return cls(comment=comment)
