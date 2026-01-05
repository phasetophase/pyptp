"""Medium-voltage transformer element for Vision integration.

Provides MV transformer representation with symmetrical modeling
for balanced three-phase power system analysis and voltage control.
"""

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
    write_boolean_no_skip,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
    write_quote_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import BranchPresentation


@dataclass_json
@dataclass
class TransformerMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Medium-voltage transformer for symmetrical modeling.

    Supports balanced three-phase analysis with tap changing,
    voltage control, and comprehensive electrical modeling
    for MV distribution transformer applications.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for MV transformers."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: int = optional_field(0)
        variant: bool = False
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        name: str = string_field()
        switch_state1: int = 1
        switch_state2: int = 1
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
        loadrate_max: float = 0.0
        loadrate_max_winter: float = 0.0
        loadrate_max_emergency: float = 0.0
        loadrate_max_emergency_winter: float = 0.0
        type: str = string_field()
        snom: float = 0.0
        step_up: bool = False
        clock_number: int = 0
        phase_shift: float = 0.0
        earthing1: int = 0
        re1: float = 0.0
        xe1: float = 0.0
        earthing_node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        earthing2: int = 0
        re2: float = 0.0
        xe2: float = 0.0
        earthing_node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        tap_position: float = 0.0

        def serialize(self) -> str:
            """Serialize transformer properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date) if self.mutation_date != 0 else "",
                write_integer("RevisionDate", self.revision_date) if self.revision_date != 0 else "",
                write_boolean("Variant", value=self.variant),
                write_guid_no_skip("Node1", self.node1),
                write_guid_no_skip("Node2", self.node2),
                write_quote_string_no_skip("Name", self.name),
                write_integer_no_skip("SwitchState1", self.switch_state1),
                write_integer_no_skip("SwitchState2", self.switch_state2),
                write_quote_string("FieldName1", self.field_name1),
                write_quote_string("FieldName2", self.field_name2),
                write_boolean("SubnetBorder", value=self.subnet_border),
                write_quote_string("Source1", self.source1),
                write_quote_string("Source2", self.source2),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_double("LoadrateMax", self.loadrate_max),
                write_double("LoadrateMaxWinter", self.loadrate_max_winter),
                write_double("LoadrateMaxmax", self.loadrate_max_emergency),
                write_double("LoadrateMaxmaxWinter", self.loadrate_max_emergency_winter),
                write_quote_string_no_skip("TransformerType", self.type),
                write_double("Snom", self.snom),
                write_boolean("StepUp", value=self.step_up),
                write_integer_no_skip("ClockNumber", self.clock_number),
                write_double("PhaseShift", self.phase_shift),
                write_integer_no_skip("Earthing1", self.earthing1),
                write_double("Re1", self.re1),
                write_double("Xe1", self.xe1),
                write_guid("EarthingNode1", self.earthing_node1) if self.earthing_node1 != NIL_GUID else "",
                write_integer_no_skip("Earthing2", self.earthing2),
                write_double("Re2", self.re2),
                write_double("Xe2", self.xe2),
                write_guid("EarthingNode2", self.earthing_node2) if self.earthing_node2 != NIL_GUID else "",
                write_double_no_skip("TapPosition", self.tap_position),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerMV.General:
            """Parse transformer properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                node1=decode_guid(data.get("Node1", str(NIL_GUID))),
                node2=decode_guid(data.get("Node2", str(NIL_GUID))),
                name=data.get("Name", ""),
                switch_state1=data.get("SwitchState1", 1),
                switch_state2=data.get("SwitchState2", 1),
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
                loadrate_max=data.get("LoadrateMax", 0.0),
                loadrate_max_winter=data.get("LoadrateMaxWinter", 0.0),
                loadrate_max_emergency=data.get("LoadrateMaxmax", 0.0),
                loadrate_max_emergency_winter=data.get("LoadrateMaxmaxWinter", 0.0),
                type=data.get("TransformerType", ""),
                snom=data.get("Snom", 0.0),
                step_up=data.get("StepUp", False),
                clock_number=data.get("ClockNumber", 0),
                phase_shift=data.get("PhaseShift", 0.0),
                earthing1=data.get("Earthing1", 0),
                re1=data.get("Re1", 0.0),
                xe1=data.get("Xe1", 0.0),
                earthing_node1=decode_guid(data.get("EarthingNode1", str(NIL_GUID))),
                earthing2=data.get("Earthing2", 0),
                re2=data.get("Re2", 0.0),
                xe2=data.get("Xe2", 0.0),
                earthing_node2=decode_guid(data.get("EarthingNode2", str(NIL_GUID))),
                tap_position=data.get("TapPosition", 0.0),
            )

    @dataclass_json
    @dataclass
    class TransformerType(DataClassJsonMixin):
        """Electrical specifications and parameters for transformer modeling."""

        short_name: str = string_field()
        snom: float = 0.0
        unom1: float = 0.0
        unom2: float = 0.0
        uk: float = 0.0
        pk: float = 0.0
        po: float = 0.0
        io: float = 0.0
        r0: float = 0.0
        z0: float = 0.0
        side_z0: int = 0
        ik2s: float = 0.0
        c1: float = 0.0
        c2: float = 0.0
        c12: float = 0.0
        winding_connection1: str = string_field()
        winding_connection2: str = string_field()
        clock_number: int = 0
        tap_side: int = 1
        tap_size: float = 0.0
        tap_min: int = 0
        tap_nom: int = 0
        tap_max: int = 0
        ki: float = 0.0
        tau: float = 0.0

        def serialize(self) -> str:
            """Serialize transformer type properties to VNF format."""
            return serialize_properties(
                write_quote_string("ShortName", self.short_name),
                write_double("Snom", self.snom),
                write_double("Unom1", self.unom1),
                write_double("Unom2", self.unom2),
                write_double("Uk", self.uk),
                write_double("Pk", self.pk),
                write_double("Po", self.po),
                write_double("Io", self.io),
                write_double("R0", self.r0),
                write_double("Z0", self.z0),
                write_integer("Side_Z0", self.side_z0),
                write_double("Ik2s", self.ik2s),
                write_double("C1", self.c1),
                write_double("C2", self.c2),
                write_double("C12", self.c12),
                write_quote_string_no_skip("WindingConnection1", self.winding_connection1),
                write_quote_string_no_skip("WindingConnection2", self.winding_connection2),
                write_integer_no_skip("ClockNumber", self.clock_number),
                write_integer_no_skip("TapSide", self.tap_side),
                write_double("TapSize", self.tap_size),
                write_integer_no_skip("TapMin", self.tap_min),
                write_integer_no_skip("TapNom", self.tap_nom),
                write_integer_no_skip("TapMax", self.tap_max),
                write_double("Ki", self.ki),
                write_double("Tau", self.tau),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerMV.TransformerType:
            """Parse transformer type properties from VNF data."""
            return cls(
                short_name=data.get("ShortName", ""),
                snom=data.get("Snom", 0.0),
                unom1=data.get("Unom1", 0.0),
                unom2=data.get("Unom2", 0.0),
                uk=data.get("Uk", 0.0),
                pk=data.get("Pk", 0.0),
                po=data.get("Po", 0.0),
                io=data.get("Io", 0.0),
                r0=data.get("R0", 0.0),
                z0=data.get("Z0", 0.0),
                side_z0=data.get("Side_Z0", 0),
                ik2s=data.get("Ik2s", 0.0),
                c1=data.get("C1", 0.0),
                c2=data.get("C2", 0.0),
                c12=data.get("C12", 0.0),
                winding_connection1=data.get("WindingConnection1", ""),
                winding_connection2=data.get("WindingConnection2", ""),
                clock_number=data.get("ClockNumber", 0),
                tap_side=data.get("TapSide", 1),
                tap_size=data.get("TapSize", 0.0),
                tap_min=data.get("TapMin", 0),
                tap_nom=data.get("TapNom", 0),
                tap_max=data.get("TapMax", 0),
                ki=data.get("Ki", 0.0),
                tau=data.get("Tau", 0.0),
            )

    @dataclass_json
    @dataclass
    class VoltageControl(DataClassJsonMixin):
        """Automatic voltage control settings for tap-changing transformers."""

        own_control: bool = False
        control_status: int = 1
        measure_side: int = 1
        control_node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        setpoint: float = 0.0
        deadband: float = 0.0
        control_sort: int = 0
        rc: float = 0.0
        xc: float = 0.0
        compounding_at_generation: bool = True
        pmin1: int = -100
        umin1: float = 0.0
        pmax1: int = 100
        umax1: float = 0.0
        pmin2: int = 0
        umin2: float = 0.0
        pmax2: int = 0
        umax2: float = 0.0
        master_transformer: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize voltage control properties to VNF format."""
            return serialize_properties(
                write_boolean_no_skip("OwnControl", value=self.own_control),
                write_integer_no_skip("ControlStatus", self.control_status),
                write_integer_no_skip("MeasureSide", self.measure_side),
                write_guid("ControlNode", self.control_node) if self.control_node != NIL_GUID else "",
                write_double("SetPoint", self.setpoint),
                write_double("DeadBand", self.deadband),
                write_integer_no_skip("ControlSort", self.control_sort),
                write_double("Rc", self.rc),
                write_double("Xc", self.xc),
                write_boolean_no_skip("CompoundingAtGeneration", value=self.compounding_at_generation),
                write_integer_no_skip("Pmin1", self.pmin1),
                write_double("Umin1", self.umin1),
                write_integer_no_skip("Pmax1", self.pmax1),
                write_double("Umax1", self.umax1),
                write_integer_no_skip("Pmin2", self.pmin2),
                write_double("Umin2", self.umin2),
                write_integer_no_skip("Pmax2", self.pmax2),
                write_double("Umax2", self.umax2),
                write_guid("MasterTransformer", self.master_transformer) if self.master_transformer != NIL_GUID else "",
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerMV.VoltageControl:
            """Parse voltage control properties from VNF data."""
            return cls(
                own_control=data.get("OwnControl", False),
                control_status=data.get("ControlStatus", 1),
                measure_side=data.get("MeasureSide", 1),
                control_node=decode_guid(data.get("ControlNode", str(NIL_GUID))),
                setpoint=data.get("SetPoint", 0.0),
                deadband=data.get("DeadBand", 0.0),
                control_sort=data.get("ControlSort", 0),
                rc=data.get("Rc", 0.0),
                xc=data.get("Xc", 0.0),
                compounding_at_generation=data.get("CompoundingAtGeneration", True),
                pmin1=data.get("Pmin1", -100),
                umin1=data.get("Umin1", 0.0),
                pmax1=data.get("Pmax1", 100),
                umax1=data.get("Umax1", 0.0),
                pmin2=data.get("Pmin2", 0),
                umin2=data.get("Umin2", 0.0),
                pmax2=data.get("Pmax2", 0),
                umax2=data.get("Umax2", 0.0),
                master_transformer=decode_guid(data.get("MasterTransformer", str(NIL_GUID))),
            )

    @dataclass_json
    @dataclass
    class Dynamics(DataClassJsonMixin):
        """Dynamic modeling properties for transient analysis."""

        non_linear_model: bool = False
        knee_flux_leg1: float = 1.04
        knee_flux_leg2: float = 1.04
        knee_flux_leg3: float = 1.04
        magnetizing_inductance_ratio_leg1: float = 1000.0
        magnetizing_inductance_ratio_leg2: float = 1000.0
        magnetizing_inductance_ratio_leg3: float = 1000.0
        remanent_flux: bool = False
        remanent_flux_leg1: float = 0.7
        remanent_flux_leg2: float = 0.7
        remanent_flux_leg3: float = 0.7

        def serialize(self) -> str:
            """Serialize dynamics properties to VNF format."""
            return serialize_properties(
                write_boolean("NonlinearModel", value=self.non_linear_model),
                write_double("KneeFluxLeg1", self.knee_flux_leg1),
                write_double("KneeFluxLeg2", self.knee_flux_leg2),
                write_double("KneeFluxLeg3", self.knee_flux_leg3),
                write_double("MagnetizingInductanceRatioLeg1", self.magnetizing_inductance_ratio_leg1),
                write_double("MagnetizingInductanceRatioLeg2", self.magnetizing_inductance_ratio_leg2),
                write_double("MagnetizingInductanceRatioLeg3", self.magnetizing_inductance_ratio_leg3),
                write_boolean("RemanentFlux", value=self.remanent_flux),
                write_double("RemanentFluxLeg1", self.remanent_flux_leg1),
                write_double("RemanentFluxLeg2", self.remanent_flux_leg2),
                write_double("RemanentFluxLeg3", self.remanent_flux_leg3),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerMV.Dynamics:
            """Parse dynamics properties from VNF data."""
            return cls(
                non_linear_model=data.get("NonlinearModel", False),
                knee_flux_leg1=data.get("KneeFluxLeg1", 1.04),
                knee_flux_leg2=data.get("KneeFluxLeg2", 1.04),
                knee_flux_leg3=data.get("KneeFluxLeg3", 1.04),
                magnetizing_inductance_ratio_leg1=data.get("MagnetizingInductanceRatioLeg1", 1000.0),
                magnetizing_inductance_ratio_leg2=data.get("MagnetizingInductanceRatioLeg2", 1000.0),
                magnetizing_inductance_ratio_leg3=data.get("MagnetizingInductanceRatioLeg3", 1000.0),
                remanent_flux=data.get("RemanentFlux", False),
                remanent_flux_leg1=data.get("RemanentFluxLeg1", 0.7),
                remanent_flux_leg2=data.get("RemanentFluxLeg2", 0.7),
                remanent_flux_leg3=data.get("RemanentFluxLeg3", 0.7),
            )

    general: General
    presentations: list[BranchPresentation]
    type: TransformerType
    voltage_control: VoltageControl | None = None
    dynamics: Dynamics | None = None

    def __post_init__(self) -> None:
        """Initialize mixins for extras, notes, and presentations."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkMV) -> None:
        """Register transformer in MV network with GUID-based indexing.

        Args:
            network: Target MV network for transformer registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.transformers:
            logger.critical("Transformer %s already exists, overwriting", self.general.guid)
        network.transformers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the transformer to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.voltage_control:
            lines.append(f"#VoltageControl {self.voltage_control.serialize()}")

        if self.type is not None:
            lines.append(f"#TransformerType {self.type.serialize()}")

        if self.dynamics:
            lines.append(f"#Dynamics {self.dynamics.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> TransformerMV:
        """Parse transformer from VNF format data.

        Args:
            data: Dictionary containing parsed VNF section data.

        Returns:
            Initialized TTransformerMS instance with parsed properties.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        transformer_type_data = data.get("transformerType", [{}])[0] if data.get("transformerType") else None
        if transformer_type_data is not None:
            transformer_type = cls.TransformerType.deserialize(transformer_type_data)
        else:
            transformer_type = cls.TransformerType()

        voltage_control = None
        if data.get("voltageControl"):
            voltage_control = cls.VoltageControl.deserialize(data["voltageControl"][0])

        dynamics = None
        if data.get("dynamics"):
            dynamics = cls.Dynamics.deserialize(data["dynamics"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=transformer_type,
            presentations=presentations,
            voltage_control=voltage_control,
            dynamics=dynamics,
        )
