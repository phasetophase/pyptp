"""Shared comment parsing logic for GNF and VNF formats.

Both GNF (LV) and VNF (MV) use identical COMMENTS section structure,
so this module provides common parsing utilities.
"""

from __future__ import annotations

import re

from pyptp.elements.lv.comment import CommentLV
from pyptp.elements.lv.shared import Comment as CommentLVShared
from pyptp.elements.mv.comment import CommentMV
from pyptp.elements.mv.shared import Comment as CommentMVShared
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV


class CommentParser:
    """Shared parser for COMMENTS sections in GNF/VNF files."""

    @classmethod
    def parse_and_register(cls, network: NetworkLV | NetworkMV, chunk: str) -> None:
        """Parse comments from chunk and register in network.

        Args:
            network: Target network for registration.
            chunk: Raw text content from COMMENTS section.

        """
        # Match Comment Text: ...  Comment ... lines
        comment_pattern = re.compile(r"^#Comment\s+Text:(.*)$", re.MULTILINE)

        for match in comment_pattern.finditer(chunk):
            comment_text = match.group(1)

            if isinstance(network, NetworkLV):
                comment = CommentLVShared(text=comment_text)
                comment_element = CommentLV(comment=comment)
                comment_element.register(network)
            elif isinstance(network, NetworkMV):
                comment = CommentMVShared(text=comment_text)
                comment_element = CommentMV(comment=comment)
                comment_element.register(network)
            else:
                msg = f"Unsupported network type: {type(network).__name__}"
                raise TypeError(msg)
