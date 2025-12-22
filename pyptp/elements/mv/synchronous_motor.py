"""Synchronous Motor (Element)."""

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

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class SynchronousMotorMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a synchronous motor (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a synchronous motor."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = 0
        revision_date: float | int = 0
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
        pref: float | int = 0
        control_sort: str = "C"
        qref: float | int = 0
        cos_ref: float = 0.85
        is_contributing_q: bool = False
        control_measure_field: Guid | None = None
        is_contributing_to_short_circuit: bool = False
        earthing: int = 0
        re: float | int = 0
        xe: float | int = 0
        earthing_node: Guid | None = None
        profile: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties in exact Delphi order."""
            return serialize_properties(
                write_guid("Node", self.node) if self.node != NIL_GUID else "",
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name, skip=""),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string("FieldName", self.field_name, skip=""),
                write_double("FailureFrequency", self.failure_frequency, skip=0.0),
                write_double("RepairDuration", self.repair_duration, skip=0.0),
                write_double("MaintenanceFrequency", self.maintenance_frequency, skip=0.0),
                write_double("MaintenanceDuration", self.maintenance_duration, skip=0.0),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration, skip=0.0),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_double("Pref", self.pref, skip=0),
                write_quote_string_no_skip("ControlSort", self.control_sort),
                write_double_no_skip("Qref", self.qref),
                write_double_no_skip("CosRef", self.cos_ref),
                write_boolean("SuppliesQ", value=self.is_contributing_q),
                write_guid("ControlMeasureField", self.control_measure_field) if self.control_measure_field else "",
                write_boolean_no_skip("NoShortCircuitContribution", value=self.is_contributing_to_short_circuit),
                write_integer_no_skip("Earthing", self.earthing),
                write_double("Re", self.re, skip=0),
                write_double("Xe", self.xe, skip=0),
                write_guid("EarthingNode", self.earthing_node) if self.earthing_node else "",
                write_guid("Profile", self.profile) if self.profile else "",
                write_quote_string("SynchronousMotorType", self.type, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousMotorMV.General:
            """Deserialize General properties."""
            control_measure_field = data.get("ControlMeasureField")
            earthing_node = data.get("EarthingNode")
            profile = data.get("Profile")

            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
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
                pref=data.get("Pref", 0),
                control_sort=data.get("ControlSort", "C"),
                qref=data.get("Qref", 0),
                cos_ref=data.get("CosRef", 0.85),
                is_contributing_q=data.get("SuppliesQ", False),
                control_measure_field=decode_guid(control_measure_field) if control_measure_field else None,
                is_contributing_to_short_circuit=data.get("NoShortCircuitContribution", False),
                earthing=data.get("Earthing", 0),
                re=data.get("Re", 0),
                xe=data.get("Xe", 0),
                earthing_node=decode_guid(earthing_node) if earthing_node else None,
                profile=decode_guid(profile) if profile else None,
                type=data.get("SynchronousMotorType", ""),
            )

    @dataclass_json
    @dataclass
    class SynchronousMotorType(DataClassJsonMixin):
        """Electrotechnical properties of a synchronous motor."""

        unom: float | int = 0
        snom: float | int = 0
        cos_nom: float = 0.85
        rg: float | int = 0
        xd2: float = 0.2
        r_x: float = field(default=0.0, metadata=config(field_name="R/X"))
        istart_inom: float = field(default=5.0, metadata=config(field_name="Istart/Inom"))
        rotor: int = 0
        ik_p: float | int = 0
        Xl: float | int = 0
        Xd: float | int = 0
        Xq: float | int = 0
        X0: float | int = 0
        Xds: float | int = 0
        Xqs: float | int = 0
        Xqss: float | int = 0
        open_circuit_time_constants: bool = False
        Tds: float | int = 0
        Tqs: float | int = 0
        Tdss: float | int = 0
        Tqss: float | int = 0
        h: float | int = 0
        Kd: float | int = 0
        tdc: float | int = 0
        tdc_unknown: bool = False

        def serialize(self) -> str:
            """Serialize SynchronousMotorType properties in exact Delphi order."""
            return serialize_properties(
                write_double("Unom", self.unom, skip=0),
                write_double("Snom", self.snom, skip=0),
                write_double("CosNom", self.cos_nom, skip=0),
                write_double("Rg", self.rg, skip=0),
                write_double("Xd2", self.xd2, skip=0),
                write_double_no_skip("R/X", self.r_x),
                write_double("Istart/Inom", self.istart_inom, skip=0),
                write_integer("Rotor", self.rotor, skip=0),
                write_double("IkP", self.ik_p, skip=0),
                write_double("Xl", self.Xl, skip=0),
                write_double("Xd", self.Xd, skip=0),
                write_double("Xq", self.Xq, skip=0),
                write_double("X0", self.X0, skip=0),
                write_double("Xds", self.Xds, skip=0),
                write_double("Xqs", self.Xqs, skip=0),
                write_double("Xqss", self.Xqss, skip=0),
                write_boolean("OpenCircuitTimeConstants", value=self.open_circuit_time_constants),
                write_double("Tds", self.Tds, skip=0),
                write_double("Tqs", self.Tqs, skip=0),
                write_double("Tdss", self.Tdss, skip=0),
                write_double("Tqss", self.Tqss, skip=0),
                write_double("h", self.h, skip=0),
                write_double("Kd", self.Kd, skip=0),
                write_double("Tdc", self.tdc, skip=0),
                write_boolean("TdcUnknown", value=self.tdc_unknown),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousMotorMV.SynchronousMotorType:
            """Deserialize SynchronousMotorType properties."""
            return cls(
                unom=data.get("Unom", 0),
                snom=data.get("Snom", 0),
                cos_nom=data.get("CosNom", 0.85),
                rg=data.get("Rg", 0),
                xd2=data.get("Xd2", 0.2),
                r_x=data.get("R/X", 0.0),
                istart_inom=data.get("Istart/Inom", 5.0),
                rotor=data.get("Rotor", 0),
                ik_p=data.get("IkP", 0),
                Xl=data.get("Xl", 0),
                Xd=data.get("Xd", 0),
                Xq=data.get("Xq", 0),
                X0=data.get("X0", 0),
                Xds=data.get("Xds", 0),
                Xqs=data.get("Xqs", 0),
                Xqss=data.get("Xqss", 0),
                open_circuit_time_constants=data.get("OpenCircuitTimeConstants", False),
                Tds=data.get("Tds", 0),
                Tqs=data.get("Tqs", 0),
                Tdss=data.get("Tdss", 0),
                Tqss=data.get("Tqss", 0),
                h=data.get("h", 0),
                Kd=data.get("Kd", 0),
                tdc=data.get("Tdc", 0),
                tdc_unknown=data.get("TdcUnknown", False),
            )

    general: General
    presentations: list[ElementPresentation]
    type: SynchronousMotorType

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def apply_node_defaults(self, network: NetworkMV) -> None:
        """Apply defaults based on the connected node's Unom, matching Delphi behavior."""
        if self.general.node != NIL_GUID and self.general.node in network.nodes:
            node = network.nodes[self.general.node]
            unom = node.general.unom

            if self.type.unom == 0:
                self.type.unom = unom

            if self.type.rg == 0:
                if unom <= 1:
                    self.type.rg = 0.15 * self.type.xd2
                else:
                    self.type.rg = 0.07 * self.type.xd2

            if self.type.r_x == 0.0:
                if unom <= 1:
                    self.type.r_x = 0.42
                else:
                    self.type.r_x = 0.15

    def register(self, network: NetworkMV) -> None:
        """Will add synchronous motor to the network."""
        if self.general.guid in network.synchronous_motors:
            logger.critical("Synchronous Motor %s already exists, overwriting", self.general.guid)

        self.apply_node_defaults(network)

        network.synchronous_motors[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the synchronous motor to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.append(f"#SynchronousMotorType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SynchronousMotorMV:
        """Deserialization of the synchronous motor from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TSynchronousMotorMS: The deserialized synchronous motor

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        motor_type_data = data.get("synchronousMotorType", [{}])[0] if data.get("synchronousMotorType") else {}
        motor_type = cls.SynchronousMotorType.deserialize(motor_type_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=motor_type,
            presentations=presentations,
        )
