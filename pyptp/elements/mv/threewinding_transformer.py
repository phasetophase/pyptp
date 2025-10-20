"""Threewinding Transformer (Other)."""

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
    write_boolean_no_skip,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import DWPresentation


@dataclass_json
@dataclass
class ThreewindingTransformerMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a threewinding transformer (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a threewinding transformer."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node3: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        name: str = string_field()
        switch_state1: int = 1
        switch_state2: int = 1
        switch_state3: int = 1
        field_name1: str = string_field()
        field_name2: str = string_field()
        field_name3: str = string_field()

        failure_frequency: float = 0
        repair_duration: float = 0
        maintenance_frequency: float = 0
        maintenance_duration: float = 0
        maintenance_cancel_duration: float = 0
        type: str = string_field()

        loadrate_max: float = 0
        loadrate_max_winter: float = 0
        loadrate_max_emergency: float = 0
        loadrate_max_emergency_winter: float = 0
        snom1: float = 0
        snom2: float = 0
        snom3: float = 0
        phase_shift12: float = 0
        phase_shift13: float = 0
        earthing1: int = 0
        re1: float = 0
        xe1: float = 0
        earthing2: int = 0
        re2: float = 0
        xe2: float = 0
        earthing3: int = 0
        re3: float = 0
        xe3: float = 0
        tap_controlled: float = 0
        tap_fixed: int = 0

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date) if self.mutation_date != 0 else "",
                write_double("RevisionDate", self.revision_date) if self.revision_date != 0.0 else "",
                write_boolean_no_skip("Variant", value=self.variant) if self.variant else "",
                write_guid("Node1", self.node1) if self.node1 != NIL_GUID else "",
                write_guid("Node2", self.node2) if self.node2 != NIL_GUID else "",
                write_guid("Node3", self.node3) if self.node3 != NIL_GUID else "",
                write_quote_string_no_skip("Name", self.name),
                write_integer_no_skip("SwitchState1", self.switch_state1),
                write_integer_no_skip("SwitchState2", self.switch_state2),
                write_integer_no_skip("SwitchState3", self.switch_state3),
                write_quote_string_no_skip("FieldName1", self.field_name1),
                write_quote_string_no_skip("FieldName2", self.field_name2),
                write_quote_string_no_skip("FieldName3", self.field_name3),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_quote_string_no_skip("ThreewindingsTransformerType", self.type),
                write_double("LoadrateMax", self.loadrate_max),
                write_double("LoadrateMaxWinter", self.loadrate_max_winter),
                write_double("LoadrateMaxmax", self.loadrate_max_emergency),
                write_double("LoadrateMaxmaxWinter", self.loadrate_max_emergency_winter),
                write_double("Snom1", self.snom1),
                write_double("Snom2", self.snom2),
                write_double("Snom3", self.snom3),
                write_double("PhaseShift12", self.phase_shift12),
                write_double("PhaseShift13", self.phase_shift13),
                write_integer_no_skip("Earthing1", self.earthing1),
                write_double("Re1", self.re1),
                write_double("Xe1", self.xe1),
                write_integer_no_skip("Earthing2", self.earthing2),
                write_double("Re2", self.re2),
                write_double("Xe2", self.xe2),
                write_integer_no_skip("Earthing3", self.earthing3),
                write_double("Re3", self.re3),
                write_double("Xe3", self.xe3),
                write_double_no_skip("TapControlled", self.tap_controlled),
                write_integer_no_skip("TapFixed", self.tap_fixed),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ThreewindingTransformerMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                variant=data.get("Variant", False),
                node1=decode_guid(data.get("Node1", str(NIL_GUID))),
                node2=decode_guid(data.get("Node2", str(NIL_GUID))),
                node3=decode_guid(data.get("Node3", str(NIL_GUID))),
                name=data.get("Name", ""),
                switch_state1=data.get("SwitchState1", 1),
                switch_state2=data.get("SwitchState2", 1),
                switch_state3=data.get("SwitchState3", 1),
                field_name1=data.get("FieldName1", ""),
                field_name2=data.get("FieldName2", ""),
                field_name3=data.get("FieldName3", ""),
                failure_frequency=data.get("FailureFrequency", 0),
                repair_duration=data.get("RepairDuration", 0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0),
                maintenance_duration=data.get("MaintenanceDuration", 0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0),
                type=data.get("ThreewindingsTransformerType", ""),
                loadrate_max=data.get("LoadrateMax", 0),
                loadrate_max_winter=data.get("LoadrateMaxWinter", 0),
                loadrate_max_emergency=data.get("LoadrateMaxmax", 0),
                loadrate_max_emergency_winter=data.get("LoadrateMaxmaxWinter", 0),
                snom1=data.get("Snom1", 0),
                snom2=data.get("Snom2", 0),
                snom3=data.get("Snom3", 0),
                phase_shift12=data.get("PhaseShift12", 0),
                phase_shift13=data.get("PhaseShift13", 0),
                earthing1=data.get("Earthing1", 0),
                re1=data.get("Re1", 0),
                xe1=data.get("Xe1", 0),
                earthing2=data.get("Earthing2", 0),
                re2=data.get("Re2", 0),
                xe2=data.get("Xe2", 0),
                earthing3=data.get("Earthing3", 0),
                re3=data.get("Re3", 0),
                xe3=data.get("Xe3", 0),
                tap_controlled=data.get("TapControlled", 0),
                tap_fixed=data.get("TapFixed", 0),
            )

    @dataclass_json
    @dataclass
    class ThreewindingTransformerType(DataClassJsonMixin):
        """Electrotechnical properties of the threewinding transformer."""

        snom1: float = 0
        snom2: float = 0
        snom3: float = 0
        unom1: float = 0
        unom2: float = 0
        unom3: float = 0
        uk12: float = 0
        uk13: float = 0
        uk23: float = 0
        pk12: float = 0
        pk13: float = 0
        pk23: float = 0
        s_at12: float = 0
        s_at13: float = 0
        s_at23: float = 0
        Po: float = 0
        Io: float = 0
        R012: float = 0
        Z012: float = 0
        R013: float = 0
        Z013: float = 0
        R023: float = 0
        Z023: float = 0
        Ik2s1: float = 0
        Ik2s2: float = 0
        Ik2s3: float = 0
        C1: float = 0
        C2: float = 0
        C3: float = 0
        C12: float = 0
        C13: float = 0
        C23: float = 0

        connection1: str = string_field()
        connection2: str = string_field()
        connection3: str = string_field()

        clock_number12: int = 0
        clock_number13: int = 0
        tap_side_controlled: int = 0
        tap_size_controlled: float = 0
        tapmin_controlled: int = 0
        tapnom_controlled: int = 0
        tap_size_fixed: float = 0
        tapmax_controlled: float = 0
        tap_side_fixed: int = 0
        tapmin_fixed: int = 0
        tapnom_fixed: int = 0
        tapmax_fixed: int = 0

        def serialize(self) -> str:
            """Serialize ThreewindingTransformerType properties."""
            return serialize_properties(
                write_double("Snom1", self.snom1),
                write_double("Snom2", self.snom2),
                write_double("Snom3", self.snom3),
                write_double("Unom1", self.unom1),
                write_double("Unom2", self.unom2),
                write_double("Unom3", self.unom3),
                write_double("Uk12", self.uk12),
                write_double("Uk13", self.uk13),
                write_double("Uk23", self.uk23),
                write_double("Pk12", self.pk12),
                write_double("Pk13", self.pk13),
                write_double("Pk23", self.pk23),
                write_double("SAt12", self.s_at12),
                write_double("SAt13", self.s_at13),
                write_double("SAt23", self.s_at23),
                write_double("Po", self.Po),
                write_double("Io", self.Io),
                write_double("R012", self.R012),
                write_double("Z012", self.Z012),
                write_double("R013", self.R013),
                write_double("Z013", self.Z013),
                write_double("R023", self.R023),
                write_double("Z023", self.Z023),
                write_double("Ik2s1", self.Ik2s1),
                write_double("Ik2s2", self.Ik2s2),
                write_double("Ik2s3", self.Ik2s3),
                write_double("C1", self.C1),
                write_double("C2", self.C2),
                write_double("C3", self.C3),
                write_double("C12", self.C12),
                write_double("C13", self.C13),
                write_double("C23", self.C23),
                write_quote_string_no_skip("Connection1", self.connection1),
                write_quote_string_no_skip("Connection2", self.connection2),
                write_quote_string_no_skip("Connection3", self.connection3),
                write_integer_no_skip("ClockNumber12", self.clock_number12),
                write_integer_no_skip("ClockNumber13", self.clock_number13),
                write_integer_no_skip("TapSideControlled", self.tap_side_controlled),
                write_double("TapSizeControlled", self.tap_size_controlled),
                write_integer("TapminControlled", self.tapmin_controlled),
                write_integer("TapnomControlled", self.tapnom_controlled),
                write_double("TapmaxControlled", self.tapmax_controlled),
                write_integer_no_skip("TapSideFixed", self.tap_side_fixed),
                write_double("TapSizeFixed", self.tap_size_fixed),
                write_integer("TapminFixed", self.tapmin_fixed),
                write_integer("TapnomFixed", self.tapnom_fixed),
                write_integer("TapmaxFixed", self.tapmax_fixed),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ThreewindingTransformerMV.ThreewindingTransformerType:
            """Deserialize ThreewindingTransformerType properties."""
            return cls(
                snom1=data.get("Snom1", 0),
                snom2=data.get("Snom2", 0),
                snom3=data.get("Snom3", 0),
                unom1=data.get("Unom1", 0),
                unom2=data.get("Unom2", 0),
                unom3=data.get("Unom3", 0),
                uk12=data.get("Uk12", 0),
                uk13=data.get("Uk13", 0),
                uk23=data.get("Uk23", 0),
                pk12=data.get("Pk12", 0),
                pk13=data.get("Pk13", 0),
                pk23=data.get("Pk23", 0),
                s_at12=data.get("SAt12", 0),
                s_at13=data.get("SAt13", 0),
                s_at23=data.get("SAt23", 0),
                Po=data.get("Po", 0),
                Io=data.get("Io", 0),
                R012=data.get("R012", 0),
                Z012=data.get("Z012", 0),
                R013=data.get("R013", 0),
                Z013=data.get("Z013", 0),
                R023=data.get("R023", 0),
                Z023=data.get("Z023", 0),
                Ik2s1=data.get("Ik2s1", 0),
                Ik2s2=data.get("Ik2s2", 0),
                Ik2s3=data.get("Ik2s3", 0),
                C1=data.get("C1", 0),
                C2=data.get("C2", 0),
                C3=data.get("C3", 0),
                C12=data.get("C12", 0),
                C13=data.get("C13", 0),
                C23=data.get("C23", 0),
                connection1=data.get("Connection1", ""),
                connection2=data.get("Connection2", ""),
                connection3=data.get("Connection3", ""),
                clock_number12=data.get("ClockNumber12", 0),
                clock_number13=data.get("ClockNumber13", 0),
                tap_side_controlled=data.get("TapSideControlled", 0),
                tap_size_controlled=data.get("TapSizeControlled", 0),
                tapmin_controlled=data.get("TapminControlled", 0),
                tapnom_controlled=data.get("TapnomControlled", 0),
                tap_size_fixed=data.get("TapSizeFixed", 0),
                tapmax_controlled=data.get("TapmaxControlled", 0),
                tap_side_fixed=data.get("TapSideFixed", 0),
                tapmin_fixed=data.get("TapminFixed", 0),
                tapnom_fixed=data.get("TapnomFixed", 0),
                tapmax_fixed=data.get("TapmaxFixed", 0),
            )

    @dataclass_json
    @dataclass
    class VoltageControl(DataClassJsonMixin):
        """Voltage Control."""

        present: bool = False
        status: int = 0
        measuring_side: int = 1
        setpoint: float = 0.0
        deadband: float = 0.0
        control_sort: int = 0
        rc: float = 0.0
        xc: float = 0.0
        compounding_at_generation: bool = False
        pmin1: int = 0
        umin1: float = 0.0
        pmax1: int = 0
        umax1: float = 0.0
        pmin2: int = 0
        umin2: float = 0.0
        pmax2: int = 0
        umax2: float = 0.0
        master_threewinding_transformer: Guid = field(
            default=NIL_GUID,
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )

        def serialize(self) -> str:
            """Serialize VoltageControl properties."""
            return serialize_properties(
                write_boolean_no_skip("Present", value=self.present),
                write_integer_no_skip("Status", self.status),
                write_integer_no_skip("MeasuringSide", self.measuring_side),
                write_double_no_skip("Setpoint", self.setpoint),
                write_double_no_skip("Deadband", self.deadband),
                write_integer("ControlSort", self.control_sort),
                write_double("Rc", self.rc),
                write_double("Xc", self.xc),
                write_boolean_no_skip("CompoundingAtGeneration", value=self.compounding_at_generation),
                write_integer("Pmin1", self.pmin1),
                write_double("Umin1", self.umin1),
                write_integer("Pmax1", self.pmax1),
                write_double("Umax1", self.umax1),
                write_integer("Pmin2", self.pmin2),
                write_double("Umin2", self.umin2),
                write_integer("Pmax2", self.pmax2),
                write_double("Umax2", self.umax2),
                (
                    write_guid("MasterThreewindingsTransformer", self.master_threewinding_transformer)
                    if self.master_threewinding_transformer != NIL_GUID
                    else ""
                ),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ThreewindingTransformerMV.VoltageControl:
            """Deserialize VoltageControl properties."""
            return cls(
                present=data.get("Present", False),
                status=data.get("Status", 0),
                measuring_side=data.get("MeasuringSide", 1),
                setpoint=data.get("Setpoint", 0.0),
                deadband=data.get("Deadband", 0.0),
                control_sort=data.get("ControlSort", 0),
                rc=data.get("Rc", 0.0),
                xc=data.get("Xc", 0.0),
                compounding_at_generation=data.get("CompoundingAtGeneration", False),
                pmin1=data.get("Pmin1", 0),
                umin1=data.get("Umin1", 0.0),
                pmax1=data.get("Pmax1", 0),
                umax1=data.get("Umax1", 0.0),
                pmin2=data.get("Pmin2", 0),
                umin2=data.get("Umin2", 0.0),
                pmax2=data.get("Pmax2", 0),
                umax2=data.get("Umax2", 0.0),
                master_threewinding_transformer=decode_guid(data.get("MasterThreewindingsTransformer", str(NIL_GUID))),
            )

    general: General
    type: ThreewindingTransformerType
    presentations: list[DWPresentation]
    voltage_control: VoltageControl | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add threewinding transformer to the network."""
        if self.general.guid in network.threewinding_transformers:
            logger.critical("Threewinding Transformer %s already exists, overwriting", self.general.guid)
        network.threewinding_transformers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the threewinding transformer to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.voltage_control:
            lines.append(f"#VoltageControl {self.voltage_control.serialize()}")

        lines.append(f"#ThreewindingsTransformerType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ThreewindingTransformerMV:
        """Deserialization of the threewinding transformer from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TThreewindingTransformerMS: The deserialized threewinding transformer

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        transformer_type_data = (
            data.get("threewindingTransformerType", [{}])[0] if data.get("threewindingTransformerType") else {}
        )
        transformer_type = cls.ThreewindingTransformerType.deserialize(transformer_type_data)

        voltage_control = None
        if data.get("voltageControl"):
            voltage_control = cls.VoltageControl.deserialize(data["voltageControl"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import DWPresentation

            presentation = DWPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=transformer_type,
            presentations=presentations,
            voltage_control=voltage_control,
        )
