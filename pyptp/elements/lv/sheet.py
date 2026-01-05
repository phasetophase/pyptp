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
    write_delphi_color,
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

        coarse_grid_width: int = optional_field(0)
        coarse_grid_height: int = optional_field(0)
        map_sheet_width: int = optional_field(0)
        map_sheet_height: int = optional_field(0)
        map_sheet_grid_width: int = optional_field(0)
        map_sheet_grid_height: int = optional_field(0)
        map_sheet_grid_left: int = optional_field(0)
        map_sheet_grid_top: int = optional_field(0)
        map_sheet_numbering: int = optional_field(0)
        map_sheet_number_offset: int = optional_field(0)

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string("Name", self.name),
                write_delphi_color("Color", self.color),
                write_double("CoarseGridWidth", self.coarse_grid_width),
                write_double("CoarseGridHeight", self.coarse_grid_height),
                write_double("MapSheetWidth", self.map_sheet_width),
                write_double("MapSheetHeight", self.map_sheet_height),
                write_double("MapSheetGridWidth", self.map_sheet_grid_width),
                write_double("MapSheetGridHeight", self.map_sheet_grid_height),
                write_double("MapSheetGridLeft", self.map_sheet_grid_left),
                write_double("MapSheetGridTop", self.map_sheet_grid_top),
                write_double("MapSheetNumbering", self.map_sheet_numbering),
                write_double("MapSheetNumberOffset", self.map_sheet_number_offset),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SheetLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                color=DelphiColor(data.get("Color", "$00C0C0C0")),
                coarse_grid_width=data.get("CoarseGridWidth", 0),
                coarse_grid_height=data.get("CoarseGridHeight", 0),
                map_sheet_width=data.get("MapSheetWidth", 0),
                map_sheet_height=data.get("MapSheetHeight", 0),
                map_sheet_grid_width=data.get("MapSheetGridWidth", 0),
                map_sheet_grid_height=data.get("MapSheetGridHeight", 0),
                map_sheet_grid_left=data.get("MapSheetGridLeft", 0),
                map_sheet_grid_top=data.get("MapSheetGridTop", 0),
                map_sheet_numbering=data.get("MapSheetNumbering", 0),
                map_sheet_number_offset=data.get("MapSheetNumberOffset", 0),
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
