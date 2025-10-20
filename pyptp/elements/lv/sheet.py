"""Sheet / Tab on which objects can be visualized and annotated."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import (
    Guid,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double,
    write_guid_no_skip,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .shared import Comment


@dataclass_json
@dataclass
class SheetLV:
    """Represents a sheet or tab for visualizing objects (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a sheet."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        name: str = string_field()
        color: DelphiColor = field(default=DelphiColor("$ff00ff"))

        coarse_grid_width: int | None = optional_field()
        coarse_grid_height: int | None = optional_field()
        map_sheet_width: int | None = optional_field()
        map_sheet_height: int | None = optional_field()
        map_sheet_grid_width: int | None = optional_field()
        map_sheet_grid_height: int | None = optional_field()
        map_sheet_grid_left: int | None = optional_field()
        map_sheet_grid_top: int | None = optional_field()
        map_sheet_numbering: int | None = optional_field()
        map_sheet_number_offset: int | None = optional_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
                write_quote_string("Color", str(self.color)),
                write_double("CoarseGridWidth", self.coarse_grid_width) if self.coarse_grid_width is not None else "",
                (
                    write_double("CoarseGridHeight", self.coarse_grid_height)
                    if self.coarse_grid_height is not None
                    else ""
                ),
                write_double("MapSheetWidth", self.map_sheet_width) if self.map_sheet_width is not None else "",
                write_double("MapSheetHeight", self.map_sheet_height) if self.map_sheet_height is not None else "",
                (
                    write_double("MapSheetGridWidth", self.map_sheet_grid_width)
                    if self.map_sheet_grid_width is not None
                    else ""
                ),
                (
                    write_double("MapSheetGridHeight", self.map_sheet_grid_height)
                    if self.map_sheet_grid_height is not None
                    else ""
                ),
                (
                    write_double("MapSheetGridLeft", self.map_sheet_grid_left)
                    if self.map_sheet_grid_left is not None
                    else ""
                ),
                write_double("MapSheetGridTop", self.map_sheet_grid_top) if self.map_sheet_grid_top is not None else "",
                (
                    write_double("MapSheetNumbering", self.map_sheet_numbering)
                    if self.map_sheet_numbering is not None
                    else ""
                ),
                (
                    write_double("MapSheetNumberOffset", self.map_sheet_number_offset)
                    if self.map_sheet_number_offset is not None
                    else ""
                ),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SheetLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                color=DelphiColor(data.get("Color", "$ff00ff")),
                coarse_grid_width=data.get("CoarseGridWidth"),
                coarse_grid_height=data.get("CoarseGridHeight"),
                map_sheet_width=data.get("MapSheetWidth"),
                map_sheet_height=data.get("MapSheetHeight"),
                map_sheet_grid_width=data.get("MapSheetGridWidth"),
                map_sheet_grid_height=data.get("MapSheetGridHeight"),
                map_sheet_grid_left=data.get("MapSheetGridLeft"),
                map_sheet_grid_top=data.get("MapSheetGridTop"),
                map_sheet_numbering=data.get("MapSheetNumbering"),
                map_sheet_number_offset=data.get("MapSheetNumberOffset"),
            )

    general: General
    comment: Comment | None = None

    def register(self, network: NetworkLV) -> None:
        """Will add sheet to the network."""
        # Auto-name empty sheets
        if not self.general.name.strip():
            sheet_count = len(network.sheets) + 1
            self.general.name = f"Sheet{sheet_count}"
            logger.warning("Sheet with empty name auto-named to %r", self.general.name)

        if self.general.guid in network.sheets:
            logger.critical("Sheet %s already exists, overwriting", self.general.guid)
        network.sheets[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the sheet to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.comment:
            lines.append(f"#Comment {self.comment.serialize()}")

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SheetLV:
        """Deserialization of the sheet from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TSheetLS: The deserialized sheet

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        comment = None
        if data.get("comment"):
            from .shared import Comment

            comment = Comment.deserialize(data["comment"][0])

        return cls(
            general=general,
            comment=comment,
        )
