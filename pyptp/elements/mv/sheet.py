"""Sheet (Other)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.color_utils import CL_CREAM, DelphiColor
from pyptp.elements.element_utils import (
    Guid,
    decode_guid,
    encode_guid,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_delphi_color,
    write_guid_no_skip,
    write_integer,
    write_quote_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.mv.shared import Comment
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class SheetMV:
    """Represents a sheet or tab for visualizing objects (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a sheet."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        """Unique identifier for the sheet."""

        name: str = string_field()
        """Name of the sheet tab."""

        color: DelphiColor = field(default=CL_CREAM)
        """Background color of the sheet tab."""

        coarse_grid_width: int = 0
        """Major grid width in number of fine grid points (20 pixels each)."""

        coarse_grid_height: int = 0
        """Major grid height in number of fine grid points (20 pixels each)."""

        map_sheet_width: int = 0
        """Mapping sheet width in number of fine grid points."""

        map_sheet_height: int = 0
        """Mapping sheet height in number of fine grid points."""

        map_sheet_grid_width: int = 0
        """Mapping grid width in number of maps."""

        map_sheet_grid_height: int = 0
        """Mapping grid height in number of maps."""

        map_sheet_grid_left: int = 0
        """Mapping grid left offset in number of maps from upper-left corner."""

        map_sheet_grid_top: int = 0
        """Mapping grid top offset in number of maps from upper-left corner."""

        map_sheet_numbering: int = 0
        """Mapping sheet numbering scheme (left-to-right or top-to-bottom)."""

        map_sheet_number_offset: int = 0
        """Number offset added to first map (top-left map gets 1 + offset)."""

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_quote_string_no_skip("Name", self.name),
                write_delphi_color("Color", self.color, skip=CL_CREAM),
                write_integer("CoarseGridWidth", self.coarse_grid_width),
                write_integer("CoarseGridHeight", self.coarse_grid_height),
                write_integer("MapSheetWidth", self.map_sheet_width),
                write_integer("MapSheetHeight", self.map_sheet_height),
                write_integer("MapSheetGridWidth", self.map_sheet_grid_width),
                write_integer("MapSheetGridHeight", self.map_sheet_grid_height),
                write_integer("MapSheetGridLeft", self.map_sheet_grid_left),
                write_integer("MapSheetGridTop", self.map_sheet_grid_top),
                write_integer("MapSheetNumbering", self.map_sheet_numbering),
                write_integer("MapSheetNumberOffset", self.map_sheet_number_offset),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SheetMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                name=data.get("Name", ""),
                color=data.get("Color", CL_CREAM),
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

    def register(self, network: NetworkMV) -> None:
        """Will add sheet to the network."""
        if self.general.guid in network.sheets:
            logger.critical("Sheet %s already exists, overwriting", self.general.guid)
        network.sheets[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the sheet to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.comment:
            lines.append(f"#Comment {self.comment.serialize()}")

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SheetMV:
        """Deserialization of the sheet from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TSheetMS: The deserialized sheet

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
