"""Special Transformer (Branch)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import NIL_GUID, Guid, decode_guid, encode_guid, string_field
from pyptp.elements.enums import SpecialTransformerSort
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_boolean_as_byte_no_skip,
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
    from pyptp.elements.mv.presentations import BranchPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class SpecialTransformerMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a special transformer (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a special transformer."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        name: str = string_field()
        """Name of transformer."""
        switch_state1: bool = True
        """Switch state on side 1 (closed=True, open=False)."""
        switch_state2: bool = True
        """Switch state on side 2 (closed=True, open=False)."""
        field_name1: str = string_field()
        """Name of the connection field on side 1."""
        field_name2: str = string_field()
        """Name of the connection field on side 2."""
        subnet_border: bool = False
        """Indicates if transformer is on subnet border."""
        source1: str = string_field()
        """Source identifier for side 1."""
        source2: str = string_field()
        """Source identifier for side 2."""
        failure_frequency: float | int = 0
        """Mean number of occurrences that the transformer fails per year."""
        repair_duration: float | int = 0
        """Mean duration of repair or replacement in minutes."""
        maintenance_frequency: float | int = 0
        """Mean number of occurrences that the transformer is in maintenance per year."""
        maintenance_duration: float | int = 0
        """Mean duration of maintenance in minutes."""
        maintenance_cancel_duration: float | int = 0
        """Mean duration of cancellation of maintenance in case of emergency in minutes."""
        loadrate_max: float | int = 0
        """Alternative maximum load rating in normal situation in %."""
        loadrate_max_winter: float | int = 0
        """Alternative maximum winter load rating in normal situation in %."""
        loadrate_max_emergency: float | int = 0
        """Alternative maximum load rating in emergency situations in %."""
        loadrate_max_emergency_winter: float | int = 0
        """Alternative maximum winter load rating in failure situation in %."""
        type: str = string_field()
        """Transformer type identifier."""
        snom: float | int = 0
        """Maximum apparent power in MVA."""
        phase_shift: float | int = 0
        """Phase shift of the transformer windings in degrees."""
        earthing: int = 0
        """Earthing of the neutral point (0=no, 1=own)."""
        re: float | int = 0
        """Earthing resistance with earthed neutral point in Ohm."""
        xe: float | int = 0
        """Earthing reactance with earthed neutral point in Ohm."""
        at_motorstart: bool = False
        """The transformer is used for motor start (affects IEC 60909 calculations)."""
        tap_position: float | int = 0
        """Actual transformer tap position."""
        tap_position_b: float | int = 0
        """Actual transformer tap position for phase B (asymmetric control)."""
        tap_position_c: float | int = 0
        """Actual transformer tap position for phase C (asymmetric control)."""

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
                write_boolean("Variant", value=self.variant),
                write_guid("Node1", self.node1) if self.node1 != NIL_GUID else "",
                write_guid("Node2", self.node2) if self.node2 != NIL_GUID else "",
                write_quote_string_no_skip("Name", self.name),
                write_boolean_as_byte_no_skip("SwitchState1", value=self.switch_state1),
                write_boolean_as_byte_no_skip("SwitchState2", value=self.switch_state2),
                write_quote_string_no_skip("FieldName1", self.field_name1),
                write_quote_string_no_skip("FieldName2", self.field_name2),
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
                write_quote_string_no_skip("SpecialTransformerType", self.type),
                write_double("Snom", self.snom),
                write_double("PhaseShift", self.phase_shift),
                write_integer_no_skip("Earthing", self.earthing),
                write_double("Re", self.re),
                write_double("Xe", self.xe),
                write_boolean("AtMotorstart", value=self.at_motorstart),
                write_double_no_skip("TapPosition", self.tap_position),
                write_double_no_skip("TapPosition_b", self.tap_position_b),
                write_double_no_skip("TapPosition_c", self.tap_position_c),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerMV.General:
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
                switch_state1=data.get("SwitchState1", True),
                switch_state2=data.get("SwitchState2", True),
                field_name1=data.get("FieldName1", ""),
                field_name2=data.get("FieldName2", ""),
                subnet_border=data.get("SubnetBorder", False),
                source1=data.get("Source1", ""),
                source2=data.get("Source2", ""),
                failure_frequency=data.get("FailureFrequency", 0),
                repair_duration=data.get("RepairDuration", 0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0),
                maintenance_duration=data.get("MaintenanceDuration", 0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0),
                loadrate_max=data.get("LoadrateMax", 0),
                loadrate_max_winter=data.get("LoadrateMaxWinter", 0),
                loadrate_max_emergency=data.get("LoadrateMaxmax", 0),
                loadrate_max_emergency_winter=data.get("LoadrateMaxmaxWinter", 0),
                type=data.get("SpecialTransformerType", ""),
                snom=data.get("Snom", 0),
                phase_shift=data.get("PhaseShift", 0),
                earthing=data.get("Earthing", 0),
                re=data.get("Re", 0),
                xe=data.get("Xe", 0),
                at_motorstart=data.get("AtMotorstart", False),
                tap_position=data.get("TapPosition", 0),
                tap_position_b=data.get("TapPosition_b", 0),
                tap_position_c=data.get("TapPosition_c", 0),
            )

    @dataclass_json
    @dataclass
    class VoltageControl(DataClassJsonMixin):
        """Voltage Control."""

        own_control: bool = False
        """Presence of voltage control."""
        control_status: bool = False
        """Indicates whether the voltage control is active."""
        measure_side: int = 3
        """Measuring side of voltage control (1=winding1, 2=winding2)."""
        setpoint: float = 0.4
        """Setpoint of the voltage control in kV."""
        deadband: float = 0
        """Deadband of the voltage control in kV."""
        control_sort: int = 0
        """Control type/sort identifier."""
        rc: float = 0
        """Real part of the voltage control compounding impedance in Ohm."""
        xc: float = 0
        """Reactive part of the voltage control compounding impedance in Ohm."""
        compounding_at_generation: bool = True
        """Also compounding when the power goes back (generation direction)."""
        pmin1: int = -100
        """Power where voltage Umin1 is controlled in %."""
        umin1: float = 0.4
        """Control voltage at power Pmin1 in kV."""
        pmax1: int = 100
        """Power where voltage Umax1 is controlled in %."""
        umax1: float = 0.0
        """Control voltage at power Pmax1 in kV."""
        pmin2: int = -100
        """Second power point where voltage Umin2 is controlled in %."""
        umin2: float = 0.4
        """Control voltage at power Pmin2 in kV."""
        pmax2: int = 100
        """Second power point where voltage Umax2 is controlled in %."""
        umax2: float = 0.4
        """Control voltage at power Pmax2 in kV."""

        def serialize(self) -> str:
            """Serialize VoltageControl properties."""
            return serialize_properties(
                write_boolean_no_skip("Present", value=self.own_control),
                write_boolean_no_skip("Status", value=self.control_status),
                write_integer_no_skip("MeasureSide", self.measure_side),
                write_double_no_skip("Setpoint", self.setpoint),
                write_double_no_skip("Deadband", self.deadband),
                write_integer_no_skip("ControlSort", self.control_sort),
                write_double_no_skip("Rc", self.rc),
                write_double_no_skip("Xc", self.xc),
                write_boolean_no_skip("CompoundingAtGeneration", value=self.compounding_at_generation),
                write_integer_no_skip("Pmin1", self.pmin1),
                write_double_no_skip("Umin1", self.umin1),
                write_integer_no_skip("Pmax1", self.pmax1),
                write_double_no_skip("Umax1", self.umax1),
                write_integer_no_skip("Pmin2", self.pmin2),
                write_double_no_skip("Umin2", self.umin2),
                write_integer_no_skip("Pmax2", self.pmax2),
                write_double_no_skip("Umax2", self.umax2),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerMV.VoltageControl:
            """Deserialize VoltageControl properties."""
            return cls(
                own_control=data.get("Present", False),
                control_status=data.get("Status", 0),
                measure_side=data.get("MeasureSide", 3),
                setpoint=data.get("Setpoint", 0.4),
                deadband=data.get("Deadband", 0),
                control_sort=data.get("ControlSort", 0),
                rc=data.get("Rc", 0),
                xc=data.get("Xc", 0),
                compounding_at_generation=data.get("CompoundingAtGeneration", True),
                pmin1=data.get("Pmin1", -100),
                umin1=data.get("Umin1", 0.4),
                pmax1=data.get("Pmax1", 100),
                umax1=data.get("Umax1", 0.0),
                pmin2=data.get("Pmin2", -100),
                umin2=data.get("Umin2", 0.4),
                pmax2=data.get("Pmax2", 100),
                umax2=data.get("Umax2", 0.4),
            )

    @dataclass_json
    @dataclass
    class PControl(DataClassJsonMixin):
        """Power Control."""

        present: bool = False
        """Presence of power control."""
        on: bool = False
        """Indicates whether the power control is active."""
        pmin: int = 0
        """Lower bound of the active power control from primary to secondary side in MW."""
        pmax: float = 0
        """Upper bound of the active power control from primary to secondary side in MW."""

        def serialize(self) -> str:
            """Serialize PControl properties."""
            return serialize_properties(
                write_boolean_no_skip("Present", value=self.present),
                write_boolean_no_skip("On", value=self.on),
                write_integer_no_skip("Pmin", self.pmin),
                write_double_no_skip("Pmax", self.pmax),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerMV.PControl:
            """Deserialize PControl properties."""
            return cls(
                present=data.get("Present", False),
                on=data.get("On", False),
                pmin=data.get("Pmin", 0),
                pmax=data.get("Pmax", 0),
            )

    @dataclass_json
    @dataclass
    class TapSpecial(DataClassJsonMixin):
        """Tap settings of the special transformer."""

        tap_position: int = 0
        uk: float | int = 0
        pk: float | int = 0
        z0: float | int = 0

        def serialize(self) -> str:
            """Serialize TapSpecial properties."""
            return serialize_properties(
                write_integer_no_skip("TapPosition", self.tap_position),
                write_double_no_skip("Uk", self.uk),
                write_double_no_skip("Pk", self.pk),
                write_double_no_skip("Z0", self.z0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerMV.TapSpecial:
            """Deserialize TapSpecial properties."""
            return cls(
                tap_position=data.get("TapPosition", 0),
                uk=data.get("Uk", 0),
                pk=data.get("Pk", 0),
                z0=data.get("Z0", 0),
            )

    @dataclass_json
    @dataclass
    class SpecialTransformerType(DataClassJsonMixin):
        """Electrotechnical properties of the special transformer."""

        sort: SpecialTransformerSort = SpecialTransformerSort.NONE
        short_name: str = string_field()
        snom: float | int = 0
        unom1: float | int = 0
        unom2: float | int = 0
        ukmin: int | float = 0
        uknom: int | float = 0
        ukmax: int | float = 0
        pkmin: float | int = 0
        pknom: float | int = 0
        pkmax: float | int = 0
        po: float = 0
        io: float = 0
        r0: float | int = 0
        z0: float | int = 0
        ik2s: float | int = 0
        tap_side: int = 0
        tap_size: float = 0
        tap_min: int = 0
        tap_nom: int = 0
        tap_max: int = 0
        ki: float = 0
        tau: float = 0

        def serialize(self) -> str:
            """Serialize SpecialTransformerType properties."""
            return serialize_properties(
                write_integer_no_skip("Sort", int(self.sort)),
                write_quote_string_no_skip("ShortName", self.short_name),
                write_double_no_skip("Snom", self.snom),
                write_double_no_skip("Unom1", self.unom1),
                write_double_no_skip("Unom2", self.unom2),
                write_double_no_skip("Ukmin", self.ukmin),
                write_double_no_skip("Uknom", self.uknom),
                write_double_no_skip("Ukmax", self.ukmax),
                write_double_no_skip("Pkmin", self.pkmin),
                write_double_no_skip("Pknom", self.pknom),
                write_double_no_skip("Pkmax", self.pkmax),
                write_double_no_skip("Po", self.po),
                write_double("Io", self.io),
                write_double_no_skip("R0", self.r0),
                write_double_no_skip("Z0", self.z0),
                write_double_no_skip("Ik2s", self.ik2s),
                write_integer_no_skip("TapSide", self.tap_side),
                write_double_no_skip("TapSize", self.tap_size),
                write_integer_no_skip("TapMin", self.tap_min),
                write_integer_no_skip("TapNom", self.tap_nom),
                write_integer_no_skip("TapMax", self.tap_max),
                write_double_no_skip("Ki", self.ki),
                write_double("Tau", self.tau),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerMV.SpecialTransformerType:
            """Deserialize SpecialTransformerType properties."""
            return cls(
                sort=SpecialTransformerSort(int(data.get("Sort", 0))),
                short_name=data.get("ShortName", ""),
                snom=data.get("Snom", 0),
                unom1=data.get("Unom1", 0),
                unom2=data.get("Unom2", 0),
                ukmin=data.get("Ukmin", 0),
                uknom=data.get("Uknom", 0),
                ukmax=data.get("Ukmax", 0),
                pkmin=data.get("Pkmin", 0),
                pknom=data.get("Pknom", 0),
                pkmax=data.get("Pkmax", 0),
                po=data.get("Po", 0),
                io=data.get("Io", 0),
                r0=data.get("R0", 0),
                z0=data.get("Z0", 0),
                ik2s=data.get("Ik2s", 0),
                tap_side=data.get("TapSide", 0),
                tap_size=data.get("TapSize", 0),
                tap_min=data.get("TapMin", 0),
                tap_nom=data.get("TapNom", 0),
                tap_max=data.get("TapMax", 0),
                ki=data.get("Ki", 0),
                tau=data.get("Tau", 0),
            )

    general: General
    presentations: list[BranchPresentation]
    type: SpecialTransformerType
    voltage_control: VoltageControl | None = None
    p_control: PControl | None = None
    tap_special: TapSpecial | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add special transformer to the network."""
        if self.general.guid in network.special_transformers:
            logger.critical("Special Transformer %s already exists, overwriting", self.general.guid)
        network.special_transformers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the special transformer to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.voltage_control:
            lines.append(f"#VoltageControl {self.voltage_control.serialize()}")

        if self.p_control:
            lines.append(f"#PControl {self.p_control.serialize()}")

        if self.tap_special:
            lines.append(f"#TapSpecial {self.tap_special.serialize()}")

        lines.append(f"#SpecialTransformerType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SpecialTransformerMV:
        """Deserialization of the special transformer from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TSpecialTransformerMS: The deserialized special transformer

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        voltage_control = None
        if data.get("voltageControl"):
            voltage_control = cls.VoltageControl.deserialize(data["voltageControl"][0])

        p_control = None
        if data.get("pControl"):
            p_control = cls.PControl.deserialize(data["pControl"][0])

        tap_special = None
        if data.get("tapSpecial"):
            tap_special = cls.TapSpecial.deserialize(data["tapSpecial"][0])

        transformer_type_data = (
            data.get("specialTransformerType", [{}])[0] if data.get("specialTransformerType") else {}
        )
        transformer_type = cls.SpecialTransformerType.deserialize(transformer_type_data)

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
            p_control=p_control,
            tap_special=tap_special,
        )
