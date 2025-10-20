"""Shunt Capacitor (Element)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

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
    write_guid,
    write_guid_no_skip,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class ShuntCapacitorLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a shunt capacitor (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a shunt capacitor."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int | None = optional_field(0)
        revision_date: float | int | None = optional_field(0.0)
        name: str = string_field()
        s_L1: bool = True  # noqa: N815
        s_L2: bool = True  # noqa: N815
        s_L3: bool = True  # noqa: N815
        s_N: bool = True  # noqa: N815
        field_name: str = string_field()
        Q: float = 0.0
        passive_filter_frequency: float = 0.0
        passive_filter_quality_factor: float = 0.0

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node),
                write_guid_no_skip("GUID", self.guid),
                write_double("CreationTime", self.creation_time, skip=0),
                write_double("MutationDate", self.mutation_date, skip=0) if self.mutation_date is not None else "",
                write_double("RevisionDate", self.revision_date, skip=0.0) if self.revision_date is not None else "",
                write_quote_string("Name", self.name),
                write_boolean("s_L1", value=self.s_L1),
                write_boolean("s_L2", value=self.s_L2),
                write_boolean("s_L3", value=self.s_L3),
                write_boolean("s_N", value=self.s_N),
                write_quote_string("FieldName", self.field_name),
                write_double("Q", self.Q, skip=0.0),
                write_double("PassiveFilterFrequency", self.passive_filter_frequency, skip=0.0),
                write_double("PassiveFilterQualityFactor", self.passive_filter_quality_factor, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ShuntCapacitorLV.General:
            """Deserialize General properties."""
            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                name=data.get("Name", ""),
                s_L1=data.get("s_L1", True),
                s_L2=data.get("s_L2", True),
                s_L3=data.get("s_L3", True),
                s_N=data.get("s_N", True),
                field_name=data.get("FieldName", ""),
                Q=data.get("Q", 0.0),
                passive_filter_frequency=data.get("PassiveFilterFrequency", 0.0),
                passive_filter_quality_factor=data.get("PassiveFilterQualityFactor", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add shunt capacitor to the network."""
        if self.general.guid in network.shunt_capacitors:
            logger.critical("Shunt Capacitor %s already exists, overwriting", self.general.guid)
        network.shunt_capacitors[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the shunt capacitor to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ShuntCapacitorLV:
        """Deserialization of the shunt capacitor from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TShuntCapacitorLS: The deserialized shunt capacitor

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
        )
