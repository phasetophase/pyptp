"""Circuit Breaker (Secondary)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config

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
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

from .presentations import SecundairPresentation
from .shared import Fields

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass
class CircuitBreakerLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a circuit breaker (LV)."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a circuit breaker."""

        guid: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        name: str = string_field()
        """Circuit breaker name."""
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """GUID of the containing object."""
        side: int = 1
        """Side of the branch (1 or 2)."""
        standardizable: bool = True
        type: str = string_field()
        """Circuit breaker type name."""
        current_protection1_present: bool = False
        """First overcurrent protection present."""
        current_protection1_type: str = string_field()
        """Type of first overcurrent protection."""
        voltage_protection_present: bool = False
        """Voltage protection present."""
        voltage_protection_type: str = string_field()
        """Type of voltage protection."""
        earth_fault_protection1_present: bool = False
        """First earth fault protection present."""

        def serialize(self) -> str:
            """Serialize General properties to GNF format."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_quote_string("Name", self.name),
                (write_guid_no_skip("InObject", self.in_object) if self.in_object is not NIL_GUID else ""),
                write_integer("Side", self.side),
                write_boolean("Standardizable", value=self.standardizable),
                write_quote_string("CircuitBreakerType", self.type),
                write_boolean("CurrentProtection1Present", value=self.current_protection1_present),
                write_quote_string("CurrentProtection1Type", self.current_protection1_type),
                write_boolean("VoltageProtectionPresent", value=self.voltage_protection_present),
                write_quote_string("VoltageProtectionType", self.voltage_protection_type),
                write_boolean(
                    "EarthFaultProtection1Present",
                    value=self.earth_fault_protection1_present,
                ),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerLV.General:
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
                type=data.get("CircuitBreakerType", ""),
                current_protection1_present=data.get("CurrentProtection1Present", False),
                current_protection1_type=data.get("CurrentProtection1Type", ""),
                voltage_protection_present=data.get("VoltageProtectionPresent", False),
                voltage_protection_type=data.get("VoltageProtectionType", ""),
                earth_fault_protection1_present=data.get("EarthFaultProtection1Present", False),
            )

    @dataclass
    class CircuitBreakerType(DataClassJsonMixin):
        """CircuitBreakerType properties."""

        short_name: str = string_field()
        unom: float = 0.0
        inom: float = 0.0
        switch_time: float = 0.0
        ik_make: float = 0.0
        ik_break: float = 0.0
        ik_dynamic: float = 0.0
        ik_thermal: float = 0.0
        t_thermal: float = 0.0

        def serialize(self) -> str:
            """Serialize CircuitBreakerType properties."""
            return serialize_properties(
                write_quote_string("ShortName", self.short_name),
                write_double("Unom", self.unom),
                write_double("Inom", self.inom),
                write_double("SwitchTime", self.switch_time),
                write_double("IkMake", self.ik_make),
                write_double("IkBreak", self.ik_break),
                write_double("IkDynamic", self.ik_dynamic),
                write_double("IkThermal", self.ik_thermal),
                write_double("TThermal", self.t_thermal),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerLV.CircuitBreakerType:
            """Deserialize CircuitBreakerType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                unom=data.get("Unom", 0.0),
                inom=data.get("Inom", 0.0),
                switch_time=data.get("SwitchTime", 0.0),
                ik_make=data.get("IkMake", 0.0),
                ik_break=data.get("IkBreak", 0.0),
                ik_dynamic=data.get("IkDynamic", 0.0),
                ik_thermal=data.get("IkThermal", 0.0),
                t_thermal=data.get("TThermal", 0.0),
            )

    @dataclass
    class VoltageProtectionType(DataClassJsonMixin):
        """Voltage Protection Type properties."""

        short_name: str = string_field()
        unom: float = 0.0
        t_input: float = 0.0
        t_output: float = 0.0
        u_small: float = 0.0
        t_small: float = 0.0
        u_smaller: float = 0.0
        t_smaller: float = 0.0
        u_great: float = 0.0
        t_great: float = 0.0
        u_greater: float = 0.0
        t_greater: float = 0.0
        ue_great: float = 0.0
        te_great: float = 0.0

        def serialize(self) -> str:
            """Serialize VoltageProtectionType properties."""
            return serialize_properties(
                write_quote_string("ShortName", self.short_name),
                write_double("Unom", self.unom),
                write_double("Tinput", self.t_input),
                write_double("Toutput", self.t_output),
                write_double_no_skip("U<", self.u_small),
                write_double_no_skip("T<", self.t_small),
                write_double_no_skip("U<<", self.u_smaller),
                write_double_no_skip("T<<", self.t_smaller),
                write_double_no_skip("U>", self.u_great),
                write_double_no_skip("T>", self.t_great),
                write_double_no_skip("U>>", self.u_greater),
                write_double_no_skip("T>>", self.t_greater),
                write_double("Ue>", self.ue_great),
                write_double("Te>", self.te_great),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerLV.VoltageProtectionType:
            """Deserialize VoltageProtectionType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                unom=data.get("Unom", 0.0),
                t_input=data.get("Tinput", 0.0),
                t_output=data.get("Toutput", 0.0),
                u_small=data.get("U<", 0.0),
                t_small=data.get("T<", 0.0),
                u_smaller=data.get("U<<", 0.0),
                t_smaller=data.get("T<<", 0.0),
                u_great=data.get("U>", 0.0),
                t_great=data.get("T>", 0.0),
                u_greater=data.get("U>>", 0.0),
                t_greater=data.get("T>>", 0.0),
                ue_great=data.get("Ue>", 0.0),
                te_great=data.get("Te>", 0.0),
            )

    @dataclass
    class CurrentProtectionType(DataClassJsonMixin):
        """Current Protection Type properties."""

        short_name: str = string_field()
        inom: float = 0.0
        setting_sort: int = 0

        I1: float = 0.0
        T1: float = 0.0
        I2: float = 0.0
        T2: float = 0.0
        I3: float = 0.0
        T3: float = 0.0
        I4: float = 0.0
        T4: float = 0.0
        I5: float = 0.0
        T5: float = 0.0
        I6: float = 0.0
        T6: float = 0.0
        I7: float = 0.0
        T7: float = 0.0
        I8: float = 0.0
        T8: float = 0.0
        I9: float = 0.0
        T9: float = 0.0
        I10: float = 0.0
        T10: float = 0.0
        I11: float = 0.0
        T11: float = 0.0
        I12: float = 0.0
        T12: float = 0.0
        I13: float = 0.0
        T13: float = 0.0
        I14: float = 0.0
        T14: float = 0.0
        I15: float = 0.0
        T15: float = 0.0
        I16: float = 0.0
        T16: float = 0.0

        # SettingSort 1, 11-15, 21, 31-32, 41: Standard protection settings
        I_great: float = field(default=0.0, metadata=config(field_name="I>"))
        T_great: float = field(default=0.0, metadata=config(field_name="T>"))
        I_greater: float = field(default=0.0, metadata=config(field_name="I>>"))
        T_greater: float = field(default=0.0, metadata=config(field_name="T>>"))
        I_greatest: float = field(default=0.0, metadata=config(field_name="I>>>"))
        T_greatest: float = field(default=0.0, metadata=config(field_name="T>>>"))
        ilt: float = 0.0
        ist: float = 0.0
        alpha: float = 0.0
        beta: float = 0.0
        m: float = 0.0
        id: float = 0.0

        def serialize(self) -> str:
            """Serialize CurrentProtectionType properties."""
            return serialize_properties(
                write_quote_string("ShortName", self.short_name),
                write_double("Inom", self.inom),
                write_integer("SettingSort", self.setting_sort),
                write_double("I1", self.I1),
                write_double("T1", self.T1),
                write_double("I2", self.I2),
                write_double("T2", self.T2),
                write_double("I3", self.I3),
                write_double("T3", self.T3),
                write_double("I4", self.I4),
                write_double("T4", self.T4),
                write_double("I5", self.I5),
                write_double("T5", self.T5),
                write_double("I6", self.I6),
                write_double("T6", self.T6),
                write_double("I7", self.I7),
                write_double("T7", self.T7),
                write_double("I8", self.I8),
                write_double("T8", self.T8),
                write_double("I9", self.I9),
                write_double("T9", self.T9),
                write_double("I10", self.I10),
                write_double("T10", self.T10),
                write_double("I11", self.I11),
                write_double("T11", self.T11),
                write_double("I12", self.I12),
                write_double("T12", self.T12),
                write_double("I13", self.I13),
                write_double("T13", self.T13),
                write_double("I14", self.I14),
                write_double("T14", self.T14),
                write_double("I15", self.I15),
                write_double("T15", self.T15),
                write_double("I16", self.I16),
                write_double("T16", self.T16),
                write_double("I>", self.I_great),
                write_double("t>", self.T_great),
                write_double("I>>", self.I_greater),
                write_double("t>>", self.T_greater),
                write_double("I>>>", self.I_greatest),
                write_double("t>>>", self.T_greatest),
                write_double("Ilt", self.ilt),
                write_double("Ist", self.ist),
                write_double("Alpha", self.alpha),
                write_double("Beta", self.beta),
                write_double("m", self.m),
                write_double("Id", self.id),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerLV.CurrentProtectionType:
            """Deserialize CurrentProtectionType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                inom=data.get("Inom", 0.0),
                setting_sort=data.get("SettingSort", 0),
                I1=data.get("I1", 0.0),
                T1=data.get("T1", 0.0),
                I2=data.get("I2", 0.0),
                T2=data.get("T2", 0.0),
                I3=data.get("I3", 0.0),
                T3=data.get("T3", 0.0),
                I4=data.get("I4", 0.0),
                T4=data.get("T4", 0.0),
                I5=data.get("I5", 0.0),
                T5=data.get("T5", 0.0),
                I6=data.get("I6", 0.0),
                T6=data.get("T6", 0.0),
                I7=data.get("I7", 0.0),
                T7=data.get("T7", 0.0),
                I8=data.get("I8", 0.0),
                T8=data.get("T8", 0.0),
                I9=data.get("I9", 0.0),
                T9=data.get("T9", 0.0),
                I10=data.get("I10", 0.0),
                T10=data.get("T10", 0.0),
                I11=data.get("I11", 0.0),
                T11=data.get("T11", 0.0),
                I12=data.get("I12", 0.0),
                T12=data.get("T12", 0.0),
                I13=data.get("I13", 0.0),
                T13=data.get("T13", 0.0),
                I14=data.get("I14", 0.0),
                T14=data.get("T14", 0.0),
                I15=data.get("I15", 0.0),
                T15=data.get("T15", 0.0),
                I16=data.get("I16", 0.0),
                T16=data.get("T16", 0.0),
                I_great=data.get("I>", 0.0),
                T_great=data.get("t>", 0.0),
                I_greater=data.get("I>>", 0.0),
                T_greater=data.get("t>>", 0.0),
                I_greatest=data.get("I>>>", 0.0),
                T_greatest=data.get("t>>>", 0.0),
                ilt=data.get("Ilt", 0.0),
                ist=data.get("Ist", 0.0),
                alpha=data.get("Alpha", 0.0),
                beta=data.get("Beta", 0.0),
                m=data.get("m", 0.0),
                id=data.get("Id", 0.0),
            )

    general: General
    presentations: list[SecundairPresentation]
    circuit_breaker_type: CircuitBreakerType | None = None
    current_protection_type: CurrentProtectionType | None = None
    earth_fault_protection_type: CurrentProtectionType | None = None
    voltage_protection_type: VoltageProtectionType | None = None
    fields: Fields | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add circuit breaker to the network."""
        if self.general.guid in network.circuit_breakers:
            logger.critical("Circuit Breaker %s already exists, overwriting", self.general.guid)
        network.circuit_breakers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the circuit breaker to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.fields:
            lines.append(f"#Fields {self.fields.serialize()}")

        if self.circuit_breaker_type:
            lines.append(f"#CircuitBreakerType {self.circuit_breaker_type.serialize()}")

        if self.current_protection_type:
            lines.append(f"#CurrentProtectionType {self.current_protection_type.serialize()}")

        if self.earth_fault_protection_type:
            lines.append(f"#EarthFaultProtectionType {self.earth_fault_protection_type.serialize()}")

        if self.voltage_protection_type:
            lines.append(f"#VoltageProtectionType {self.voltage_protection_type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> CircuitBreakerLV:
        """Deserialization of the circuit breaker from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TCircuitBreakerLS: The deserialized circuit breaker

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        fields_data = data.get("fields", [{}])[0] if data.get("fields") else None
        fields = Fields.deserialize(fields_data) if fields_data else None

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            presentation = SecundairPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            fields=fields,
        )
