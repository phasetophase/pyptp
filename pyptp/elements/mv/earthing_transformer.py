"""Earthing Transformer (Element)."""

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
    encode_guid_optional,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.mv.presentations import ElementPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class EarthingTransformerMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents an earthing transformer (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for an Earthing Transformer."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        name: str = string_field()
        switch_state: int = 0
        field_name: str = string_field()
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        not_preferred: bool = False
        pref: float = 0.0
        earthing: bool = False
        re: float = 0.0
        xe: float = 0.0
        earthing_node: Guid | None = field(
            default=None,
            metadata=config(
                encoder=encode_guid_optional,
                exclude=lambda x: x is None,
            ),
        )
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node, skip=NIL_GUID),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date),
                write_integer("RevisionDate", self.revision_date),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string("FieldName", self.field_name),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_double("Pref", self.pref),
                write_boolean("Earthing", value=self.earthing),
                write_double("Re", self.re),
                write_double("Xe", self.xe),
                write_guid("EarthingNode", self.earthing_node) if self.earthing_node is not None else "",
                write_quote_string("EarthingTransformerType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> EarthingTransformerMV.General:
            """Deserialize General properties."""
            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                switch_state=data.get("SwitchState", 0),
                field_name=data.get("FieldName", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                not_preferred=data.get("NotPreferred", False),
                pref=data.get("Pref", 0.0),
                earthing=data.get("Earthing", False),
                re=data.get("Re", 0.0),
                xe=data.get("Xe", 0.0),
                earthing_node=decode_guid(data["EarthingNode"]) if data.get("EarthingNode") is not None else None,
                type=data.get("EarthingTransformerType", ""),
            )

    @dataclass_json
    @dataclass
    class EarthingTransformerType(DataClassJsonMixin):
        """Earthing Transformer type properties."""

        r0: float = 0.0
        x0: float = 0.0

        def serialize(self) -> str:
            """Serialize EarthingTransformerType properties."""
            return serialize_properties(
                write_double("R0", self.r0),
                write_double("X0", self.x0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> EarthingTransformerMV.EarthingTransformerType:
            """Deserialize EarthingTransformerType properties."""
            return cls(
                r0=data.get("R0", 0.0),
                x0=data.get("X0", 0.0),
            )

    general: General
    presentations: list[ElementPresentation] = field(default_factory=list)
    type: EarthingTransformerType | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add earthing transformer to the network."""
        if self.general.guid in network.earthing_transformers:
            logger.critical("Earthing Transformer %s already exists, overwriting", self.general.guid)
        network.earthing_transformers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the earthing transformer to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#EarthingTransformerType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> EarthingTransformerMV:
        """Deserialization of the earthing transformer from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TEarthingTransformerMS: The deserialized earthing transformer

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        earthing_transformer_type = None
        if data.get("earthingTransformerType"):
            earthing_transformer_type = cls.EarthingTransformerType.deserialize(data["earthingTransformerType"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=earthing_transformer_type,
            presentations=presentations,
        )
