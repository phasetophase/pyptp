"""Asynchronous generator element for medium-voltage networks.

Provides distributed generation capability with symmetrical modeling
for MV network power flow analysis, stability studies, and renewable
energy integration in distribution systems.
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
    from pyptp.network_mv import NetworkMV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class AsynchronousGeneratorMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Asynchronous generator element for medium-voltage network modeling.

    Supports distributed generation with symmetrical modeling approach
    including positive sequence impedance and power factor characteristics
    for accurate MV network power flow and stability analysis.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for an asynchronous generator."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        switch_state: int = 0
        field_name: str = string_field()
        """Name of the connection field."""
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        not_preferred: bool = False
        pref: float = 0.0
        """Actual electrical power in MW."""
        earthing: bool = False
        earthing_resistance: float = 0.0
        earthing_reactance: float = 0.0
        profile: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node, skip=NIL_GUID),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
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
                write_double("Re", self.earthing_resistance),
                write_double("Xe", self.earthing_reactance),
                write_guid("Profile", self.profile, skip=NIL_GUID),
                write_quote_string("AsynchronousGeneratorType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> AsynchronousGeneratorMV.General:
            """Deserialize General properties."""
            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
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
                earthing_resistance=data.get("Re", 0.0),
                earthing_reactance=data.get("Xe", 0.0),
                profile=decode_guid(data.get("Profile", str(NIL_GUID))),
                type=data.get("AsynchronousGeneratorType", ""),
            )

    @dataclass_json
    @dataclass
    class ASynchronousGeneratorType(DataClassJsonMixin):
        """Asynchronous generator type properties."""

        unom: float = 0.0
        pnom: float = 0.0
        r_x: float = field(default=0.0, metadata=config(field_name="R/X"))
        istart_inom: float = field(default=0.0, metadata=config(field_name="Istart/Inom"))
        poles: int = 0
        cosnom: float = 0.0
        """Power factor at nominal power (dimensionless)."""
        p2: float = 0.0
        """Curve point 2: electrical power in pu."""
        cos2: float = 0.0
        """Curve point 2: power factor (dimensionless)."""
        p3: float = 0.0
        """Curve point 3: electrical power in pu."""
        cos3: float = 0.0
        """Curve point 3: power factor (dimensionless)."""
        p4: float = 0.0
        """Curve point 4: electrical power in pu."""
        cos4: float = 0.0
        """Curve point 4: power factor (dimensionless)."""
        p5: float = 0.0
        """Curve point 5: electrical power in pu."""
        cos5: float = 0.0
        """Curve point 5: power factor (dimensionless)."""
        starting_torque: float = 0.0
        """Locked rotor torque in %."""
        critical_speed: float = 0.0
        """Critical speed in rpm."""
        critical_torque: float = 0.0
        """Critical torque in %."""
        nom_speed: float = 0.0
        """Nominal speed in rpm."""
        j: float = 0.0
        """Inertia in kg⋅m²."""
        efficiency: float = 0.0
        k2: float = 0.0
        """K-factor 2 in %."""
        k1: float = 0.0
        """K-factor 1 in %."""
        k0: float = 0.0
        """K-factor 0 in %."""
        double_cage: bool = False
        own_parameters: bool = False
        mechanical_torque_speed_characteristic: bool = False
        electrical_torque_speed_characteristic: bool = False
        m1: list[float] | None = field(default_factory=lambda: [0] * 10)
        m2: list[float] | None = field(default_factory=lambda: [0] * 10)
        e1: list[float] | None = field(default_factory=lambda: [0] * 10)
        e2: list[float] | None = field(default_factory=lambda: [0] * 10)
        rs: float = 0.0
        """Stator resistance in pu."""
        xsl: float = 0.0
        """Stator leakage reactance in pu."""
        xm: float = 0.0
        """Magnetizing reactance in pu."""
        rr: float = 0.0
        """Rotor resistance in pu."""
        xrl: float = 0.0
        """Rotor leakage reactance in pu."""
        rr2: float = 0.0
        """Rotor resistance 2 (double cage) in pu."""
        xr2l: float = 0.0
        """Rotor leakage reactance 2 (double cage) in pu."""

        def serialize(self) -> str:
            """Serialize ASynchronousGeneratorType properties."""
            arr_props = []
            if self.mechanical_torque_speed_characteristic and self.m1:
                for i, val in enumerate(self.m1, start=1):
                    arr_props.append(f"M1{i}:{val}")
            if self.mechanical_torque_speed_characteristic and self.m2:
                for i, val in enumerate(self.m2, start=1):
                    arr_props.append(f"M2{i}:{val}")
            if self.electrical_torque_speed_characteristic and self.e1:
                for i, val in enumerate(self.e1, start=1):
                    arr_props.append(f"E1{i}:{val}")
            if self.electrical_torque_speed_characteristic and self.e2:
                for i, val in enumerate(self.e2, start=1):
                    arr_props.append(f"E2{i}:{val}")
            return serialize_properties(
                write_double("Unom", self.unom),
                write_double("Pnom", self.pnom),
                write_double("R/X", self.r_x),
                write_double("Istart/Inom", self.istart_inom),
                write_integer("Poles", self.poles),
                write_double("CosNom", self.cosnom),
                write_double("p2", self.p2),
                write_double("cos2", self.cos2),
                write_double("p3", self.p3),
                write_double("cos3", self.cos3),
                write_double("p4", self.p4),
                write_double("cos4", self.cos4),
                write_double("p5", self.p5),
                write_double("cos5", self.cos5),
                write_double("StartingTorque", self.starting_torque),
                write_double("CriticalSpeed", self.critical_speed),
                write_double("CriticalTorque", self.critical_torque),
                write_double("NomSpeed", self.nom_speed),
                write_double("J", self.j),
                write_double("Efficiency", self.efficiency),
                write_double("K2", self.k2),
                write_double("K1", self.k1),
                write_double("K0", self.k0),
                write_boolean("DoubleCage", value=self.double_cage),
                write_boolean("OwnParameters", value=self.own_parameters),
                write_boolean("MechanicalTorqueSpeedCharacteristic", value=self.mechanical_torque_speed_characteristic),
                write_boolean("ElectricalTorqueSpeedCharacteristic", value=self.electrical_torque_speed_characteristic),
                *arr_props,
                write_double("Rs", self.rs),
                write_double("Xsl", self.xsl),
                write_double("Xm", self.xm),
                write_double("Rr", self.rr),
                write_double("Xrl", self.xrl),
                write_double("Rr2", self.rr2),
                write_double("Xr2l", self.xr2l),
            )

        @classmethod
        def deserialize(cls, data: dict) -> AsynchronousGeneratorMV.ASynchronousGeneratorType:
            """Deserialize ASynchronousGeneratorType properties."""
            # Extract arrays
            m1_values = []
            m2_values = []
            e1_values = []
            e2_values = []

            i = 1
            while f"M1{i}" in data:
                m1_values.append(data[f"M1{i}"])
                i += 1

            i = 1
            while f"M2{i}" in data:
                m2_values.append(data[f"M2{i}"])
                i += 1

            i = 1
            while f"E1{i}" in data:
                e1_values.append(data[f"E1{i}"])
                i += 1

            i = 1
            while f"E2{i}" in data:
                e2_values.append(data[f"E2{i}"])
                i += 1

            return cls(
                unom=data.get("Unom", 0.0),
                pnom=data.get("Pnom", 0.0),
                r_x=data.get("R/X", 0.0),
                istart_inom=data.get("Istart/Inom", 0.0),
                poles=data.get("Poles", 0),
                cosnom=data.get("Cosnom", 0.0),
                p2=data.get("p2", 0.0),
                cos2=data.get("cos2", 0.0),
                p3=data.get("p3", 0.0),
                cos3=data.get("cos3", 0.0),
                p4=data.get("p4", 0.0),
                cos4=data.get("cos4", 0.0),
                p5=data.get("p5", 0.0),
                cos5=data.get("cos5", 0.0),
                starting_torque=data.get("StartingTorque", 0.0),
                critical_speed=data.get("CriticalSpeed", 0.0),
                critical_torque=data.get("CriticalTorque", 0.0),
                nom_speed=data.get("NomSpeed", 0.0),
                j=data.get("J", 0.0),
                efficiency=data.get("Efficiency", 0.0),
                k2=data.get("K2", 0.0),
                k1=data.get("K1", 0.0),
                k0=data.get("K0", 0.0),
                double_cage=data.get("DoubleCage", False),
                own_parameters=data.get("OwnParameters", False),
                mechanical_torque_speed_characteristic=data.get("MechanicalTorqueSpeedCharacteristic", False),
                electrical_torque_speed_characteristic=data.get("ElectricalTorqueSpeedCharacteristic", False),
                m1=m1_values if m1_values else None,
                m2=m2_values if m2_values else None,
                e1=e1_values if e1_values else None,
                e2=e2_values if e2_values else None,
                rs=data.get("Rs", 0.0),
                xsl=data.get("Xsl", 0.0),
                xm=data.get("Xm", 0.0),
                rr=data.get("Rr", 0.0),
                xrl=data.get("Xrl", 0.0),
                rr2=data.get("Rr2", 0.0),
                xr2l=data.get("Xr2l", 0.0),
            )

    @dataclass_json
    @dataclass
    class Restriction(DataClassJsonMixin):
        """Restriction properties."""

        sort: str = string_field()
        begin_date: int = 0
        end_date: int = 0
        begin_time: float | int = 0
        end_time: float | int = 0
        p_max: float | int = 0

        def serialize(self) -> str:
            """Serialize Restriction properties."""
            return serialize_properties(
                write_quote_string("Sort", self.sort),
                write_integer("BeginDate", self.begin_date),
                write_integer("EndDate", self.end_date),
                write_double("BeginTime", self.begin_time),
                write_double("EndTime", self.end_time),
                write_double("Pmax", self.p_max),
            )

        @classmethod
        def deserialize(cls, data: dict) -> AsynchronousGeneratorMV.Restriction:
            """Deserialize Restriction properties."""
            return cls(
                sort=data.get("Sort", ""),
                begin_date=data.get("BeginDate", 0),
                end_date=data.get("EndDate", 0),
                begin_time=data.get("BeginTime", 0),
                end_time=data.get("EndTime", 0),
                p_max=data.get("Pmax", 0),
            )

    general: General
    presentations: list[ElementPresentation]
    type: ASynchronousGeneratorType
    restriction: Restriction | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def apply_node_defaults(self, network: NetworkMV) -> None:
        """Apply defaults based on the connected node's Unom.

        Logic:
        - If Unom <= 1: R_X = 0.42, else R_X = 0.1
        - Set various default values like IaInom=5, Poles=2, etc.
        """
        if self.general.node != NIL_GUID and self.general.node in network.nodes:
            node = network.nodes[self.general.node]
            unom = node.general.unom

            # Apply Unom from node
            if self.type.unom == 0:  # Only set if still default
                self.type.unom = unom

            # Set R_X based on Unom
            if self.type.r_x == 0.0:  # Only set if still default
                if unom <= 1:
                    self.type.r_x = 0.42
                else:
                    self.type.r_x = 0.1

        if self.type.istart_inom == 0.0:
            self.type.istart_inom = 5
        if self.type.poles == 0:
            self.type.poles = 2
        if self.type.cosnom == 0.0:
            self.type.cosnom = 0.85
        if self.type.p2 == 0.0:
            self.type.p2 = 1.25
        if self.type.cos2 == 0.0:
            self.type.cos2 = 0.86
        if self.type.p3 == 0.0:
            self.type.p3 = 0.75
        if self.type.cos3 == 0.0:
            self.type.cos3 = 0.81
        if self.type.p4 == 0.0:
            self.type.p4 = 0.5
        if self.type.cos4 == 0.0:
            self.type.cos4 = 0.72
        if self.type.p5 == 0.0:
            self.type.p5 = 0.25
        if self.type.cos5 == 0.0:
            self.type.cos5 = 0.5

    def register(self, network: NetworkMV) -> None:
        """Will add asynchronous generator to the network."""
        if self.general.guid in network.asynchronous_generators:
            logger.critical("Asynchronous Generator %s already exists, overwriting", self.general.guid)

        # Apply node-based defaults before registering
        self.apply_node_defaults(network)

        network.asynchronous_generators[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the asynchronous generator to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#AsynchronousGeneratorType {self.type.serialize()}")

        if self.restriction:
            lines.append(f"#Restriction {self.restriction.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> AsynchronousGeneratorMV:
        """Deserialization of the asynchronous generator from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TAsynchronousGeneratorMS: The deserialized asynchronous generator

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        type_data = data.get("type", [{}])[0] if data.get("type") else {}
        type_obj = cls.ASynchronousGeneratorType.deserialize(type_data)

        restriction = None
        if data.get("restriction"):
            restriction = cls.Restriction.deserialize(data["restriction"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=type_obj,
            restriction=restriction,
        )
