"""Reactance Coil (MV)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import NIL_GUID, Guid, decode_guid, encode_guid, string_field
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_boolean_as_byte_no_skip,
    write_double,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.mv.presentations import BranchPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class ReactanceCoilMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a reactance coil (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a reactance coil."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        name: str = string_field()
        switch_state1: bool = False
        switch_state2: bool = False
        field_name1: str = string_field()
        field_name2: str = string_field()
        subnet_border: bool = False
        source1: str = string_field()
        source2: str = string_field()
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
                write_boolean("Variant", value=self.variant),
                write_guid_no_skip("Node1", self.node1),
                write_guid_no_skip("Node2", self.node2),
                write_quote_string("Name", self.name),
                write_boolean_as_byte_no_skip("SwitchState1", value=self.switch_state1),
                write_boolean_as_byte_no_skip("SwitchState2", value=self.switch_state2),
                write_quote_string("FieldName1", self.field_name1),
                write_quote_string("FieldName2", self.field_name2, skip=""),
                write_boolean("SubnetBorder", value=self.subnet_border),
                write_quote_string("Source1", self.source1, skip=""),
                write_quote_string("Source2", self.source2, skip=""),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_quote_string("AsynchronousGeneratorType", self.type, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ReactanceCoilMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                node1=decode_guid(data.get("Node1", str(NIL_GUID))),
                node2=decode_guid(data.get("Node2", str(NIL_GUID))),
                name=data.get("Name", ""),
                switch_state1=data.get("SwitchState1", False),
                switch_state2=data.get("SwitchState2", False),
                field_name1=data.get("FieldName1", ""),
                field_name2=data.get("FieldName2", ""),
                subnet_border=data.get("SubnetBorder", False),
                source1=data.get("Source1", ""),
                source2=data.get("Source2", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                type=data.get("AsynchronousGeneratorType", ""),
            )

    @dataclass_json
    @dataclass
    class ReactanceCoilType(DataClassJsonMixin):
        """Reactance Coil type."""

        short_name: str = string_field()
        unom: float = 0.0
        inom: float = 0.0
        R: float = 0.0
        X: float = 0.0
        R0: float = 0.0
        X0: float = 0.0
        R2: float = 0.0
        X2: float = 0.0
        Ik2s: float = 0.0

        def serialize(self) -> str:
            """Serialize ReactanceCoilType properties."""
            return serialize_properties(
                write_quote_string("ShortName", self.short_name, skip=""),
                write_double_no_skip("Unom", self.unom),
                write_double_no_skip("Inom", self.inom),
                write_double_no_skip("R", self.R),
                write_double_no_skip("X", self.X),
                write_double_no_skip("R0", self.R0),
                write_double_no_skip("X0", self.X0),
                write_double_no_skip("R2", self.R2),
                write_double_no_skip("X2", self.X2),
                write_double("Ik2s", self.Ik2s),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ReactanceCoilMV.ReactanceCoilType:
            """Deserialize ReactanceCoilType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                unom=data.get("Unom", 0.0),
                inom=data.get("Inom", 0.0),
                R=data.get("R", 0.0),
                X=data.get("X", 0.0),
                R0=data.get("R0", 0.0),
                X0=data.get("X0", 0.0),
                R2=data.get("R2", 0.0),
                X2=data.get("X2", 0.0),
                Ik2s=data.get("Ik2s", 0.0),
            )

    general: General
    presentations: list[BranchPresentation]
    type: ReactanceCoilType

    def register(self, network: NetworkMV) -> None:
        """Will add reactance coil to the network."""
        if self.general.guid in network.reactance_coils:
            logger.critical("Reactance Coil %s already exists, overwriting", self.general.guid)
        network.reactance_coils[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the reactance coil to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.append(f"#ReactanceCoilType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ReactanceCoilMV:
        """Deserialization of the reactance coil from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TReactanceCoilMS: The deserialized reactance coil

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        reactance_coil_type_data = data.get("reactanceCoilType", [{}])[0] if data.get("reactanceCoilType") else {}
        reactance_coil_type = cls.ReactanceCoilType.deserialize(reactance_coil_type_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=reactance_coil_type,
            presentations=presentations,
        )
