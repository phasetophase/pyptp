"""Handler for parsing VNF Comment sections with custom parsing logic."""

import re
from typing import TYPE_CHECKING

from pyptp.elements.mv.comment import CommentMV
from pyptp.elements.mv.shared import Comment

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


class CommentHandler:
    """Custom handler for VNF comments that handles unquoted text properly."""

    def handle(self, network: "NetworkMV", chunk: str) -> None:
        """Parse and register comments from a COMMENTS section chunk.

        Args:
            network: Target network for registration
            chunk: Raw text content from COMMENTS section

        """
        comment_pattern = re.compile(r"^#Comment\s+Text:(.*)$", re.MULTILINE)

        for match in comment_pattern.finditer(chunk):
            comment_text = match.group(1)
            comment = Comment(text=comment_text)
            comment_element = CommentMV(comment=comment)
            comment_element.register(network)
