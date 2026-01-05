"""Fuse protection element for low-voltage networks.

Provides overcurrent protection modeling with current-time characteristics
and breaking capacity specifications for LV network fault analysis
and protection coordination studies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.element_utils import (
    NIL_GUID,
    Guid,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_double,
    write_double_no_skip,
    write_guid,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

from .presentations import SecundairPresentation, config
from .shared import FuseType

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.type_reader import Types


@dataclass
class FuseLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Fuse protection element for low-voltage network modeling.

    Models overcurrent protection devices with thermal characteristics,
    breaking capacity, and current-time curves for accurate fault
    analysis and protection system coordination in LV networks.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """Core fuse configuration and electrical protection properties."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        name: str = string_field()
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        side: int = 1
        standardizable: bool = True
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_quote_string("Name", self.name),
                write_guid("InObject", self.in_object),
                write_integer("Side", self.side),
                write_boolean("Standardizable", value=self.standardizable),
                write_quote_string("FuseType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> FuseLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                name=data.get("Name", ""),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                standardizable=data.get("Standardizable", True),
                type=data.get("FuseType", ""),
            )

    general: General
    type: FuseType | None = None
    presentations: list[SecundairPresentation] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def set_fuse_type(self, default_types: Types, fusetype: str) -> None:
        """Set `fuse_type` from the Excel-backed types provider by name."""
        obj = default_types.get_lv_fuse(fusetype)
        if isinstance(obj, FuseType):
            self.type = obj

    def register(self, network: NetworkLV) -> None:
        """Will add fuse to the network."""
        if self.general.guid in network.fuses:
            logger.critical("Fuse %s already exists, overwriting", self.general.guid)
        network.fuses[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the fuse to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []

        general_line = f"#General {self.general.serialize()}"
        lines.append(general_line)

        if self.type:
            lines.append(f"#FuseType {self.type.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> FuseLV:
        """Deserialization of the fuse from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TFuseLS: The deserialized fuse

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)
        fuse_type = None
        if data.get("fuse_type"):
            fuse_type_data = data["fuse_type"]
            # Handle both list and dict formats
            if isinstance(fuse_type_data, list):
                type_data = fuse_type_data[0] if fuse_type_data else {}
            else:
                type_data = fuse_type_data
            fuse_type = FuseType.deserialize(type_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            presentation = SecundairPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=fuse_type,
            presentations=presentations,
        )
