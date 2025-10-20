"""Handler for parsing GNF Comment sections using a declarative recipe."""

from typing import ClassVar

from pyptp.elements.lv.shared import Comment
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class CommentHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF comments using a declarative recipe."""

    COMPONENT_CLS = Comment

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("text", "#Comment"),
    ]
