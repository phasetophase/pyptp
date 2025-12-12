"""Circuit Breaker (Secondary)."""

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
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import SecondaryPresentation


@dataclass_json
@dataclass
class CircuitBreakerMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a circuit breaker (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a circuit breaker."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        side: int = 1
        is_loadswitch: bool = False
        spontaneous_frequency: float = 0.0
        remote_status_indication: bool = False
        remote_controlled: bool = False
        refusal_chance: float = 0.0
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        ignore_for_selectivity: bool = False
        type: str = string_field()

        current_protection1_present: bool = False
        current_protection1_active: bool = False
        current_protection1_info: str = string_field()
        current_protection1_direction: int = 0
        current_protection1_rca: float = 45.0
        current_protection1_type: str = string_field()

        current_protection2_present: bool = False
        current_protection2_active: bool = False
        current_protection2_info: str = string_field()
        current_protection2_direction: int = 0
        current_protection2_rca: float = 45.0
        current_protection2_type: str = string_field()

        earth_fault_protection1_present: bool = False
        earth_fault_protection1_active: bool = False
        earth_fault_protection1_info: str = string_field()
        earth_fault_protection1_direction: int = 0
        earth_fault_protection1_rca: float = 0.0
        earth_fault_protection1_type: str = string_field()

        earth_fault_protection2_present: bool = False
        earth_fault_protection2_active: bool = False
        earth_fault_protection2_info: str = string_field()
        earth_fault_protection2_direction: int = 0
        earth_fault_protection2_rca: float = 0.0
        earth_fault_protection2_type: str = string_field()

        voltage_protection_present: bool = False
        voltage_protection_active: bool = False
        voltage_protection_info: str = string_field()
        voltage_protection_direction: int = 0
        voltage_protection_rca: float = 45.0
        voltage_protection_type: str = string_field()

        differential_protection_present: bool = False
        differential_protection_active: bool = False
        differential_protection_info: str = string_field()
        distance_protection_present: bool = False
        distance_protection_active: bool = False
        distance_protection_info: str = string_field()
        distance_protection_type: str = string_field()

        voltage_protection2_present: bool = False
        voltage_protection2_active: bool = False
        voltage_protection2_info: str = string_field()
        voltage_protection2_direction: int = 0
        voltage_protection2_rca: float = 0.0
        voltage_protection2_type: str = string_field()

        differential_protection2_present: bool = False
        differential_protection2_active: bool = False
        differential_protection2_info: str = string_field()
        unbalance_protection_present: bool = False
        unbalance_protection_active: bool = False
        unbalance_protection_info: str = string_field()
        unbalance_protection_type: str = string_field()

        thermal_protection_present: bool = False
        thermal_protection_active: bool = False
        thermal_protection_info: str = string_field()
        earth_fault_differential_protection_present: bool = False
        earth_fault_differential_protection_active: bool = False
        earth_fault_differential_protection_info: str = string_field()
        vector_shift_protection_present: bool = False
        vector_shift_protection_active: bool = False
        vector_shift_protection_info: str = string_field()
        frequency_protection_present: bool = False
        frequency_protection_active: bool = False
        frequency_protection_info: str = string_field()
        transfer_trip_ability: bool = False
        transfer_trip_runtime: float = 0.0
        block_ability: bool = False
        reserve_ability: bool = False
        reserve_extra_time: float = 0.0

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name),
                (write_guid("InObject", self.in_object) if self.in_object != NIL_GUID else ""),
                write_integer_no_skip("Side", self.side),
                write_boolean("IsLoadSwitch", value=self.is_loadswitch),
                write_double("SpontaneousFrequency", self.spontaneous_frequency),
                write_boolean("RemoteStatusIndication", value=self.remote_status_indication),
                write_boolean("RemoteControl", value=self.remote_controlled),
                write_double("RefusalChance", self.refusal_chance),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_boolean("IgnoreForSelectivity", value=self.ignore_for_selectivity),
                write_quote_string("CircuitBreakerType", self.type),
                write_boolean("CurrentProtection1Present", value=self.current_protection1_present),
                write_boolean("CurrentProtection1Active", value=self.current_protection1_active),
                write_quote_string("CurrentProtection1Info", self.current_protection1_info),
                write_integer(
                    "CurrentProtection1Direction",
                    self.current_protection1_direction,
                    skip=0,
                ),
                write_double("CurrentProtection1RCA", self.current_protection1_rca),
                write_quote_string("CurrentProtection1Type", self.current_protection1_type),
                write_boolean("CurrentProtection2Present", value=self.current_protection2_present),
                write_boolean("CurrentProtection2Active", value=self.current_protection2_active),
                write_quote_string("CurrentProtection2Info", self.current_protection2_info),
                write_integer(
                    "CurrentProtection2Direction",
                    self.current_protection2_direction,
                    skip=0,
                ),
                write_double("CurrentProtection2RCA", self.current_protection2_rca),
                write_quote_string("CurrentProtection2Type", self.current_protection2_type),
                write_boolean(
                    "EarthFaultProtection1Present",
                    value=self.earth_fault_protection1_present,
                ),
                write_boolean(
                    "EarthFaultProtection1Active",
                    value=self.earth_fault_protection1_active,
                ),
                write_quote_string("EarthFaultProtection1Info", self.earth_fault_protection1_info),
                write_integer(
                    "EarthFaultProtection1Direction",
                    self.earth_fault_protection1_direction,
                    skip=0,
                ),
                write_double("EarthFaultProtection1RCA", self.earth_fault_protection1_rca),
                write_quote_string("EarthFaultProtection1Type", self.earth_fault_protection1_type),
                write_boolean(
                    "EarthFaultProtection2Present",
                    value=self.earth_fault_protection2_present,
                ),
                write_boolean(
                    "EarthFaultProtection2Active",
                    value=self.earth_fault_protection2_active,
                ),
                write_quote_string("EarthFaultProtection2Info", self.earth_fault_protection2_info),
                write_integer(
                    "EarthFaultProtection2Direction",
                    self.earth_fault_protection2_direction,
                    skip=0,
                ),
                write_double("EarthFaultProtection2RCA", self.earth_fault_protection2_rca),
                write_quote_string("EarthFaultProtection2Type", self.earth_fault_protection2_type),
                write_boolean("VoltageProtectionPresent", value=self.voltage_protection_present),
                write_boolean("VoltageProtectionActive", value=self.voltage_protection_active),
                write_quote_string("VoltageProtectionInfo", self.voltage_protection_info),
                write_integer(
                    "VoltageProtectionDirection",
                    self.voltage_protection_direction,
                    skip=0,
                ),
                write_double("VoltageProtectionRCA", self.voltage_protection_rca),
                write_quote_string("VoltageProtectionType", self.voltage_protection_type),
                write_boolean(
                    "DifferentialProtectionPresent",
                    value=self.differential_protection_present,
                ),
                write_boolean(
                    "DifferentialProtectionActive",
                    value=self.differential_protection_active,
                ),
                write_quote_string("DifferentialProtectionInfo", self.differential_protection_info),
                write_boolean("DistanceProtectionPresent", value=self.distance_protection_present),
                write_boolean("DistanceProtectionActive", value=self.distance_protection_active),
                write_quote_string("DistanceProtectionInfo", self.distance_protection_info),
                write_quote_string("DistanceProtectionType", self.distance_protection_type),
                write_boolean("VoltageProtection2Present", value=self.voltage_protection2_present),
                write_boolean("VoltageProtection2Active", value=self.voltage_protection2_active),
                write_quote_string("VoltageProtection2Info", self.voltage_protection2_info),
                write_integer(
                    "VoltageProtection2Direction",
                    self.voltage_protection2_direction,
                    skip=0,
                ),
                write_double("VoltageProtection2RCA", self.voltage_protection2_rca),
                write_quote_string("VoltageProtection2Type", self.voltage_protection2_type),
                write_boolean(
                    "DifferentialProtection2Present",
                    value=self.differential_protection2_present,
                ),
                write_boolean(
                    "DifferentialProtection2Active",
                    value=self.differential_protection2_active,
                ),
                write_quote_string("DifferentialProtection2Info", self.differential_protection2_info),
                write_boolean(
                    "UnbalanceProtectionPresent",
                    value=self.unbalance_protection_present,
                ),
                write_boolean("UnbalanceProtectionActive", value=self.unbalance_protection_active),
                write_quote_string("UnbalanceProtectionInfo", self.unbalance_protection_info),
                write_quote_string("UnbalanceProtectionType", self.unbalance_protection_type),
                write_boolean("ThermalProtectionPresent", value=self.thermal_protection_present),
                write_boolean("ThermalProtectionActive", value=self.thermal_protection_active),
                write_quote_string("ThermalProtectionInfo", self.thermal_protection_info),
                write_boolean(
                    "EarthFaultDifferentialProtectionPresent",
                    value=self.earth_fault_differential_protection_present,
                ),
                write_boolean(
                    "EarthFaultDifferentialProtectionActive",
                    value=self.earth_fault_differential_protection_active,
                ),
                write_quote_string(
                    "EarthFaultDifferentialProtectionInfo",
                    self.earth_fault_differential_protection_info,
                ),
                write_boolean(
                    "VectorJumpProtectionPresent",
                    value=self.vector_shift_protection_present,
                ),
                write_boolean(
                    "VectorJumpProtectionActive",
                    value=self.vector_shift_protection_active,
                ),
                write_quote_string("VectorJumpProtectionInfo", self.vector_shift_protection_info),
                write_boolean(
                    "FrequencyProtectionPresent",
                    value=self.frequency_protection_present,
                ),
                write_boolean("FrequencyProtectionActive", value=self.frequency_protection_active),
                write_quote_string("FrequencyProtectionInfo", self.frequency_protection_info),
                write_boolean("TransferTripAbility", value=self.transfer_trip_ability),
                write_double("TransferTripRuntime", self.transfer_trip_runtime),
                write_boolean("BlockAbility", value=self.block_ability),
                write_boolean("ReserveAbility", value=self.reserve_ability),
                write_double("ReserveExtraTime", self.reserve_extra_time),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.General:
            """Deserialize General properties."""
            guid_val = data.get("GUID", str(uuid4()))
            return cls(
                guid=decode_guid(guid_val if guid_val is not None else str(uuid4())),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                is_loadswitch=data.get("IsLoadSwitch", False),
                spontaneous_frequency=data.get("SpontaneousFrequency", 0.0),
                remote_status_indication=data.get("RemoteStatusIndication", False),
                remote_controlled=data.get("RemoteControl", False),
                refusal_chance=data.get("RefusalChance", 0.0),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                ignore_for_selectivity=data.get("IgnoreForSelectivity", False),
                type=data.get("CircuitBreakerType", ""),
                current_protection1_present=data.get("CurrentProtection1Present", False),
                current_protection1_active=data.get("CurrentProtection1Active", False),
                current_protection1_info=data.get("CurrentProtection1Info", ""),
                current_protection1_direction=data.get("CurrentProtection1Direction", 0),
                current_protection1_rca=data.get("CurrentProtection1RCA", 45.0),
                current_protection1_type=data.get("CurrentProtection1Type", ""),
                current_protection2_present=data.get("CurrentProtection2Present", False),
                current_protection2_active=data.get("CurrentProtection2Active", False),
                current_protection2_info=data.get("CurrentProtection2Info", ""),
                current_protection2_direction=data.get("CurrentProtection2Direction", 0),
                current_protection2_rca=data.get("CurrentProtection2RCA", 45.0),
                current_protection2_type=data.get("CurrentProtection2Type", ""),
                earth_fault_protection1_present=data.get("EarthFaultProtection1Present", False),
                earth_fault_protection1_active=data.get("EarthFaultProtection1Active", False),
                earth_fault_protection1_info=data.get("EarthFaultProtection1Info", ""),
                earth_fault_protection1_direction=data.get("EarthFaultProtection1Direction", 0),
                earth_fault_protection1_rca=data.get("EarthFaultProtection1RCA", 0.0),
                earth_fault_protection1_type=data.get("EarthFaultProtection1Type", ""),
                earth_fault_protection2_present=data.get("EarthFaultProtection2Present", False),
                earth_fault_protection2_active=data.get("EarthFaultProtection2Active", False),
                earth_fault_protection2_info=data.get("EarthFaultProtection2Info", ""),
                earth_fault_protection2_direction=data.get("EarthFaultProtection2Direction", 0),
                earth_fault_protection2_rca=data.get("EarthFaultProtection2RCA", 0.0),
                earth_fault_protection2_type=data.get("EarthFaultProtection2Type", ""),
                voltage_protection_present=data.get("VoltageProtectionPresent", False),
                voltage_protection_active=data.get("VoltageProtectionActive", False),
                voltage_protection_info=data.get("VoltageProtectionInfo", ""),
                voltage_protection_direction=data.get("VoltageProtectionDirection", 0),
                voltage_protection_rca=data.get("VoltageProtectionRCA", 45.0),
                voltage_protection_type=data.get("VoltageProtectionType", ""),
                differential_protection_present=data.get("DifferentialProtectionPresent", False),
                differential_protection_active=data.get("DifferentialProtectionActive", False),
                differential_protection_info=data.get("DifferentialProtectionInfo", ""),
                distance_protection_present=data.get("DistanceProtectionPresent", False),
                distance_protection_active=data.get("DistanceProtectionActive", False),
                distance_protection_info=data.get("DistanceProtectionInfo", ""),
                distance_protection_type=data.get("DistanceProtectionType", ""),
                voltage_protection2_present=data.get("VoltageProtection2Present", False),
                voltage_protection2_active=data.get("VoltageProtection2Active", False),
                voltage_protection2_info=data.get("VoltageProtection2Info", ""),
                voltage_protection2_direction=data.get("VoltageProtection2Direction", 0),
                voltage_protection2_rca=data.get("VoltageProtection2RCA", 0.0),
                voltage_protection2_type=data.get("VoltageProtection2Type", ""),
                differential_protection2_present=data.get("DifferentialProtection2Present", False),
                differential_protection2_active=data.get("DifferentialProtection2Active", False),
                differential_protection2_info=data.get("DifferentialProtection2Info", ""),
                unbalance_protection_present=data.get("UnbalanceProtectionPresent", False),
                unbalance_protection_active=data.get("UnbalanceProtectionActive", False),
                unbalance_protection_info=data.get("UnbalanceProtectionInfo", ""),
                unbalance_protection_type=data.get("UnbalanceProtectionType", ""),
                thermal_protection_present=data.get("ThermalProtectionPresent", False),
                thermal_protection_active=data.get("ThermalProtectionActive", False),
                thermal_protection_info=data.get("ThermalProtectionInfo", ""),
                earth_fault_differential_protection_present=data.get("EarthFaultDifferentialProtectionPresent", False),
                earth_fault_differential_protection_active=data.get("EarthFaultDifferentialProtectionActive", False),
                earth_fault_differential_protection_info=data.get("EarthFaultDifferentialProtectionInfo", ""),
                vector_shift_protection_present=data.get("VectorJumpProtectionPresent", False),
                vector_shift_protection_active=data.get("VectorJumpProtectionActive", False),
                vector_shift_protection_info=data.get("VectorJumpProtectionInfo", ""),
                frequency_protection_present=data.get("FrequencyProtectionPresent", False),
                frequency_protection_active=data.get("FrequencyProtectionActive", False),
                frequency_protection_info=data.get("FrequencyProtectionInfo", ""),
                transfer_trip_ability=data.get("TransferTripAbility", False),
                transfer_trip_runtime=data.get("TransferTripRuntime", 0.0),
                block_ability=data.get("BlockAbility", False),
                reserve_ability=data.get("ReserveAbility", False),
                reserve_extra_time=data.get("ReserveExtraTime", 0.0),
            )

    @dataclass_json
    @dataclass
    class CircuitBreakerType(DataClassJsonMixin):
        """Type properties."""

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
                write_double("Tthermal", self.t_thermal),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.CircuitBreakerType:
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
                t_thermal=data.get("Tthermal", 0.0),
            )

    @dataclass_json
    @dataclass
    class ProtectionType(DataClassJsonMixin):
        """Protection type properties (Stroomtype equivalent)."""

        # SettingSort constants
        SETTING_ARRAY_BASED = 0
        SETTING_STANDARD = 1
        SETTING_EXTENDED_MIN = 11
        SETTING_EXTENDED_MAX = 15
        SETTING_INVERSE_TIME = 21
        SETTING_SIMPLE_1 = 31
        SETTING_SIMPLE_2 = 32
        SETTING_ADDITIONAL_CURRENT = 41

        short_name: str = string_field()
        inom: float = 0.0
        t_input: float = 0.0
        t_output: float = 0.0
        setting_sort: int = 0

        # SettingSort 0: Array-based settings (I1-I16, T1-T16)
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
        drop_off_pickup_ratio: float = 0.95
        t_reset: float = 0.0

        # SettingSort 11-15, 21: Additional properties
        m: float = 0.0
        id: float = field(default=0.0, metadata=config(field_name="Id"))
        u_proportional: bool = field(default=False, metadata=config(field_name="UProportional"))
        reset_method: int = 0

        # SettingSort 21: Inverse time characteristics
        alpha: float = 0.0
        beta: float = 0.0
        C: float = field(default=0.0, metadata=config(field_name="c"))
        D: float = field(default=0.0, metadata=config(field_name="d"))
        E: float = field(default=0.0, metadata=config(field_name="e"))

        # SettingSort 41: Additional current settings
        ilt: float = 0.0
        ist: float = 0.0

        def serialize(self) -> str:
            """Serialize ProtectionType properties based on SettingSort."""
            props = [
                write_quote_string("ShortName", self.short_name),
                write_double("Inom", self.inom),
                write_double("Tinput", self.t_input),
                write_double("Toutput", self.t_output),
                write_integer_no_skip("SettingSort", self.setting_sort),
            ]

            # Conditional serialization based on SettingSort value
            if self.setting_sort == self.SETTING_ARRAY_BASED:
                # Array-based settings I1-I16, T1-T16
                for i in range(1, 17):
                    i_val = getattr(self, f"I{i}")
                    t_val = getattr(self, f"T{i}")
                    props.extend(
                        [
                            write_double_no_skip(f"I{i}", i_val),
                            write_double_no_skip(f"T{i}", t_val),
                        ],
                    )
            elif self.setting_sort == self.SETTING_STANDARD:
                # Standard protection settings
                props.extend(
                    [
                        write_double_no_skip("I>", self.I_great),
                        write_double_no_skip("T>", self.T_great),
                        write_double_no_skip("I>>", self.I_greater),
                        write_double_no_skip("T>>", self.T_greater),
                        write_double_no_skip("I>>>", self.I_greatest),
                        write_double_no_skip("T>>>", self.T_greatest),
                        write_double("DropOffPickupRatio", self.drop_off_pickup_ratio),
                        write_double("Treset", self.t_reset),
                    ],
                )
            elif self.SETTING_EXTENDED_MIN <= self.setting_sort <= self.SETTING_EXTENDED_MAX:
                # Extended settings with additional properties
                props.extend(
                    [
                        write_double_no_skip("I>", self.I_great),
                        write_double_no_skip("I>>", self.I_greater),
                        write_double_no_skip("T>>", self.T_greater),
                        write_double_no_skip("I>>>", self.I_greatest),
                        write_double_no_skip("T>>>", self.T_greatest),
                        write_double_no_skip("m", self.m),
                        write_double("Id", self.id),
                        write_boolean("UProportional", value=self.u_proportional),
                        write_double("DropOffPickupRatio", self.drop_off_pickup_ratio),
                        write_double("Treset", self.t_reset),
                        write_integer("ResetMethod", self.reset_method),
                    ],
                )
            elif self.setting_sort == self.SETTING_INVERSE_TIME:
                # Inverse time characteristics
                props.extend(
                    [
                        write_double_no_skip("I>", self.I_great),
                        write_double_no_skip("I>>", self.I_greater),
                        write_double_no_skip("T>>", self.T_greater),
                        write_double_no_skip("I>>>", self.I_greatest),
                        write_double_no_skip("T>>>", self.T_greatest),
                        write_double_no_skip("m", self.m),
                        write_double_no_skip("Alfa", self.alpha),
                        write_double_no_skip("Beta", self.beta),
                        write_double_no_skip("c", self.C),
                        write_double_no_skip("d", self.D),
                        write_double_no_skip("e", self.E),
                        write_double("Id", self.id),
                        write_double("DropOffPickupRatio", self.drop_off_pickup_ratio),
                        write_double("Treset", self.t_reset),
                    ],
                )
            elif self.setting_sort in (self.SETTING_SIMPLE_1, self.SETTING_SIMPLE_2):
                # Simple settings
                props.extend(
                    [
                        write_double_no_skip("I>", self.I_great),
                        write_double_no_skip("I>>", self.I_greater),
                        write_double_no_skip("T>>", self.T_greater),
                        write_double_no_skip("m", self.m),
                    ],
                )
            elif self.setting_sort == self.SETTING_ADDITIONAL_CURRENT:
                # Additional current settings
                props.extend(
                    [
                        write_double_no_skip("I>", self.I_great),
                        write_double_no_skip("T>", self.T_great),
                        write_double_no_skip("I>>", self.I_greater),
                        write_double_no_skip("T>>", self.T_greater),
                        write_double_no_skip("I>>>", self.I_greatest),
                        write_double_no_skip("T>>>", self.T_greatest),
                        write_double_no_skip("Ilt", self.ilt),
                        write_double_no_skip("Ist", self.ist),
                        write_double_no_skip("Alfa", self.alpha),
                        write_double("DropOffPickupRatio", self.drop_off_pickup_ratio),
                    ],
                )

            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.ProtectionType:
            """Deserialize ProtectionType properties."""
            # Create instance with all possible fields
            instance = cls(
                short_name=data.get("ShortName", ""),
                inom=data.get("Inom", 0.0),
                t_input=data.get("Tinput", 0.0),
                t_output=data.get("Toutput", 0.0),
                setting_sort=data.get("SettingSort", 0),
                drop_off_pickup_ratio=data.get("DropOffPickupRatio", 0.95),
                t_reset=data.get("Treset", 0.0),
                m=data.get("m", 0.0),
                id=data.get("Id", 0.0),
                u_proportional=data.get("UProportional", False),
                reset_method=data.get("ResetMethod", 0),
                alpha=data.get("Alfa", 0.0),
                beta=data.get("Beta", 0.0),
                C=data.get("c", 0.0),
                D=data.get("d", 0.0),
                E=data.get("e", 0.0),
                ilt=data.get("Ilt", 0.0),
                ist=data.get("Ist", 0.0),
                I_great=data.get("I>", 0.0),
                T_great=data.get("T>", 0.0),
                I_greater=data.get("I>>", 0.0),
                T_greater=data.get("T>>", 0.0),
                I_greatest=data.get("I>>>", 0.0),
                T_greatest=data.get("T>>>", 0.0),
            )

            # Set array-based settings I1-I16, T1-T16
            for i in range(1, 17):
                setattr(instance, f"I{i}", data.get(f"I{i}", 0.0))
                setattr(instance, f"T{i}", data.get(f"T{i}", 0.0))

            return instance

    @dataclass_json
    @dataclass
    class Protection(DataClassJsonMixin):
        """Protection properties."""

        present: bool = False
        active: bool = False
        info: str = string_field()
        direction: int = 0
        rca: float = 0.0

        def serialize(self) -> str:
            """Serialize Protection properties."""
            props = []
            props.append(f"Present:{str(self.present).lower()}")
            props.append(f"Active:{str(self.active).lower()}")
            props.append(f"Info:'{self.info}'")
            props.append(f"Direction:{self.direction}")
            props.append(f"RCA:{self.rca}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.Protection:
            """Deserialize Protection properties."""
            return cls(
                present=data.get("Present", False),
                active=data.get("Active", False),
                info=data.get("Info", ""),
                direction=data.get("Direction", 0),
                rca=data.get("RCA", 0.0),
            )

    @dataclass_json
    @dataclass
    class ThermalProtection(DataClassJsonMixin):
        """Thermal protection properties."""

        i_pre: float = 0.0
        fa: float = 1.0
        Q: float = 3.0
        I_great: float = field(default=0.0, metadata=config(field_name="I>"))
        tau_great: float = field(default=0.0, metadata=config(field_name="Tau>"))
        I_start: float = field(default=0.0, metadata=config(field_name="IStart"))
        tau_start: float = field(default=0.0, metadata=config(field_name="TauStart"))
        I_greater: float = field(default=0.0, metadata=config(field_name="I>>"))
        T_greater: float = field(default=0.0, metadata=config(field_name="T>>"))
        drop_off_pickup_ratio: float = 0.95

        def serialize(self) -> str:
            """Serialize ThermalProtection properties."""
            return serialize_properties(
                write_double_no_skip("Ipre", self.i_pre),
                write_double_no_skip("Fa", self.fa),
                write_double_no_skip("Q", self.Q),
                write_double_no_skip("I>", self.I_great),
                write_double_no_skip("Tau>", self.tau_great),
                write_double_no_skip("IStart", self.I_start),
                write_double_no_skip("TauStart", self.tau_start),
                write_double_no_skip("I>>", self.I_greater),
                write_double_no_skip("T>>", self.T_greater),
                write_double("DropOffPickupRatio", self.drop_off_pickup_ratio),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.ThermalProtection:
            """Deserialize ThermalProtection properties."""
            return cls(
                i_pre=data.get("Ipre", 0.0),
                fa=data.get("Fa", 1.0),
                Q=data.get("Q", 3.0),
                I_great=data.get("I>", 0.0),
                tau_great=data.get("Tau>", 0.0),
                I_start=data.get("IStart", 0.0),
                tau_start=data.get("TauStart", 0.0),
                I_greater=data.get("I>>", 0.0),
                T_greater=data.get("T>>", 0.0),
                drop_off_pickup_ratio=data.get("DropOffPickupRatio", 0.95),
            )

    @dataclass_json
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
                write_double_no_skip("Ue>", self.ue_great),
                write_double_no_skip("Te>", self.te_great),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.VoltageProtectionType:
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

    @dataclass_json
    @dataclass
    class DistanceSetting(DataClassJsonMixin):
        """Distance setting properties."""

        R: float = 0.0
        X: float = 0.0
        Z: float = 0.0

    @dataclass_json
    @dataclass
    class DistanceZone(DataClassJsonMixin):
        """Distance protection zone properties."""

        present: bool = False
        characteristic: str = string_field()
        settings: list[CircuitBreakerMV.DistanceSetting] = field(default_factory=list)
        earth_fault: bool = False
        earth_fault_characteristic: str = string_field()
        earth_fault_settings: list[CircuitBreakerMV.DistanceSetting] = field(default_factory=list)

    @dataclass_json
    @dataclass
    class DistanceProtectionType(DataClassJsonMixin):
        """Distance protection type properties."""

        # Polygon characteristic requires 5 points
        POLYGON_POINT_COUNT = 5

        short_name: str = string_field()
        t_input: float = 0.0
        t_output: float = 0.0
        ie_great: float = field(default=0.0, metadata=config(field_name="Ie>"))
        i_great: float = field(default=0.0, metadata=config(field_name="I>"))
        u_small: float = field(default=0.0, metadata=config(field_name="U<"))
        z_small: float = field(default=0.0, metadata=config(field_name="Z<"))
        kn: float = 0.0
        kn_angle: float = 0.0

        # Distance protection zones (1-4, with zone 4 mapped to -1)
        zone1: CircuitBreakerMV.DistanceZone = field(default_factory=lambda: CircuitBreakerMV.DistanceZone())
        zone2: CircuitBreakerMV.DistanceZone = field(default_factory=lambda: CircuitBreakerMV.DistanceZone())
        zone3: CircuitBreakerMV.DistanceZone = field(default_factory=lambda: CircuitBreakerMV.DistanceZone())
        zone_reverse: CircuitBreakerMV.DistanceZone = field(
            default_factory=lambda: CircuitBreakerMV.DistanceZone(),
        )

        # Zone timing (T[zone])
        t1: float = 0.0
        t2: float = 0.0
        t3: float = 0.0
        t_reverse: float = 0.0  # T-1
        t4: float = 0.0
        t0: float = 0.0

        # Zone-indexed properties for all characteristics (C, M, P)
        # Zone 1 properties (normal phase)
        R10: float = 0.0
        X10: float = 0.0
        Z10: float = 0.0
        R11: float = 0.0
        X11: float = 0.0
        Z11: float = 0.0
        R12: float = 0.0
        X12: float = 0.0
        Z12: float = 0.0
        R13: float = 0.0
        X13: float = 0.0
        Z13: float = 0.0
        R14: float = 0.0
        X14: float = 0.0
        Z14: float = 0.0

        # Zone 1 earth fault properties
        Re10: float = 0.0
        Xe10: float = 0.0
        Ze10: float = 0.0
        Re11: float = 0.0
        Xe11: float = 0.0
        Ze11: float = 0.0
        Re12: float = 0.0
        Xe12: float = 0.0
        Ze12: float = 0.0
        Re13: float = 0.0
        Xe13: float = 0.0
        Ze13: float = 0.0
        Re14: float = 0.0
        Xe14: float = 0.0
        Ze14: float = 0.0

        # Zone 2 properties (normal phase)
        R20: float = 0.0
        X20: float = 0.0
        Z20: float = 0.0
        R21: float = 0.0
        X21: float = 0.0
        Z21: float = 0.0
        R22: float = 0.0
        X22: float = 0.0
        Z22: float = 0.0
        R23: float = 0.0
        X23: float = 0.0
        Z23: float = 0.0
        R24: float = 0.0
        X24: float = 0.0
        Z24: float = 0.0

        # Zone 2 earth fault properties
        Re20: float = 0.0
        Xe20: float = 0.0
        Ze20: float = 0.0
        Re21: float = 0.0
        Xe21: float = 0.0
        Ze21: float = 0.0
        Re22: float = 0.0
        Xe22: float = 0.0
        Ze22: float = 0.0
        Re23: float = 0.0
        Xe23: float = 0.0
        Ze23: float = 0.0
        Re24: float = 0.0
        Xe24: float = 0.0
        Ze24: float = 0.0

        # Zone 3 properties (normal phase)
        R30: float = 0.0
        X30: float = 0.0
        Z30: float = 0.0
        R31: float = 0.0
        X31: float = 0.0
        Z31: float = 0.0
        R32: float = 0.0
        X32: float = 0.0
        Z32: float = 0.0
        R33: float = 0.0
        X33: float = 0.0
        Z33: float = 0.0
        R34: float = 0.0
        X34: float = 0.0
        Z34: float = 0.0

        # Zone 3 earth fault properties
        Re30: float = 0.0
        Xe30: float = 0.0
        Ze30: float = 0.0
        Re31: float = 0.0
        Xe31: float = 0.0
        Ze31: float = 0.0
        Re32: float = 0.0
        Xe32: float = 0.0
        Ze32: float = 0.0
        Re33: float = 0.0
        Xe33: float = 0.0
        Ze33: float = 0.0
        Re34: float = 0.0
        Xe34: float = 0.0
        Ze34: float = 0.0

        # Zone -1/Reverse properties (normal phase)
        R_10: float = 0.0
        X_10: float = 0.0
        Z_10: float = 0.0
        R_11: float = 0.0
        X_11: float = 0.0
        Z_11: float = 0.0
        R_12: float = 0.0
        X_12: float = 0.0
        Z_12: float = 0.0
        R_13: float = 0.0
        X_13: float = 0.0
        Z_13: float = 0.0
        R_14: float = 0.0
        X_14: float = 0.0
        Z_14: float = 0.0

        # Zone -1 earth fault properties
        Re_10: float = 0.0
        Xe_10: float = 0.0
        Ze_10: float = 0.0
        Re_11: float = 0.0
        Xe_11: float = 0.0
        Ze_11: float = 0.0
        Re_12: float = 0.0
        Xe_12: float = 0.0
        Ze_12: float = 0.0
        Re_13: float = 0.0
        Xe_13: float = 0.0
        Ze_13: float = 0.0
        Re_14: float = 0.0
        Xe_14: float = 0.0
        Ze_14: float = 0.0

        def serialize(self) -> str:
            """Serialize DistanceProtectionType properties."""
            props = [
                write_quote_string("ShortName", self.short_name),
                write_double("TInput", self.t_input),
                write_double("TOutput", self.t_output),
                write_double_no_skip("Ie>", self.ie_great),
                write_double_no_skip("I>", self.i_great),
                write_double_no_skip("U<", self.u_small),
                write_double_no_skip("Z<", self.z_small),
                write_double_no_skip("Kn", self.kn),
                write_double_no_skip("KnAngle", self.kn_angle),
            ]

            # Direct zone property serialization using no_skip
            props.extend(
                [
                    # Zone 1 properties (normal phase)
                    write_double_no_skip("R10", self.R10),
                    write_double_no_skip("X10", self.X10),
                    write_double_no_skip("Z10", self.Z10),
                    write_double_no_skip("R11", self.R11),
                    write_double_no_skip("X11", self.X11),
                    write_double_no_skip("Z11", self.Z11),
                    write_double_no_skip("R12", self.R12),
                    write_double_no_skip("X12", self.X12),
                    write_double_no_skip("Z12", self.Z12),
                    write_double_no_skip("R13", self.R13),
                    write_double_no_skip("X13", self.X13),
                    write_double_no_skip("Z13", self.Z13),
                    write_double_no_skip("R14", self.R14),
                    write_double_no_skip("X14", self.X14),
                    write_double_no_skip("Z14", self.Z14),
                    # Zone 1 earth fault properties
                    write_double_no_skip("Re10", self.Re10),
                    write_double_no_skip("Xe10", self.Xe10),
                    write_double_no_skip("Ze10", self.Ze10),
                    write_double_no_skip("Re11", self.Re11),
                    write_double_no_skip("Xe11", self.Xe11),
                    write_double_no_skip("Ze11", self.Ze11),
                    write_double_no_skip("Re12", self.Re12),
                    write_double_no_skip("Xe12", self.Xe12),
                    write_double_no_skip("Ze12", self.Ze12),
                    write_double_no_skip("Re13", self.Re13),
                    write_double_no_skip("Xe13", self.Xe13),
                    write_double_no_skip("Ze13", self.Ze13),
                    write_double_no_skip("Re14", self.Re14),
                    write_double_no_skip("Xe14", self.Xe14),
                    write_double_no_skip("Ze14", self.Ze14),
                    # Zone 2 properties (normal phase)
                    write_double_no_skip("R20", self.R20),
                    write_double_no_skip("X20", self.X20),
                    write_double_no_skip("Z20", self.Z20),
                    write_double_no_skip("R21", self.R21),
                    write_double_no_skip("X21", self.X21),
                    write_double_no_skip("Z21", self.Z21),
                    write_double_no_skip("R22", self.R22),
                    write_double_no_skip("X22", self.X22),
                    write_double_no_skip("Z22", self.Z22),
                    write_double_no_skip("R23", self.R23),
                    write_double_no_skip("X23", self.X23),
                    write_double_no_skip("Z23", self.Z23),
                    write_double_no_skip("R24", self.R24),
                    write_double_no_skip("X24", self.X24),
                    write_double_no_skip("Z24", self.Z24),
                    # Zone 2 earth fault properties
                    write_double_no_skip("Re20", self.Re20),
                    write_double_no_skip("Xe20", self.Xe20),
                    write_double_no_skip("Ze20", self.Ze20),
                    write_double_no_skip("Re21", self.Re21),
                    write_double_no_skip("Xe21", self.Xe21),
                    write_double_no_skip("Ze21", self.Ze21),
                    write_double_no_skip("Re22", self.Re22),
                    write_double_no_skip("Xe22", self.Xe22),
                    write_double_no_skip("Ze22", self.Ze22),
                    write_double_no_skip("Re23", self.Re23),
                    write_double_no_skip("Xe23", self.Xe23),
                    write_double_no_skip("Ze23", self.Ze23),
                    write_double_no_skip("Re24", self.Re24),
                    write_double_no_skip("Xe24", self.Xe24),
                    write_double_no_skip("Ze24", self.Ze24),
                    # Zone 3 properties (normal phase)
                    write_double_no_skip("R30", self.R30),
                    write_double_no_skip("X30", self.X30),
                    write_double_no_skip("Z30", self.Z30),
                    write_double_no_skip("R31", self.R31),
                    write_double_no_skip("X31", self.X31),
                    write_double_no_skip("Z31", self.Z31),
                    write_double_no_skip("R32", self.R32),
                    write_double_no_skip("X32", self.X32),
                    write_double_no_skip("Z32", self.Z32),
                    write_double_no_skip("R33", self.R33),
                    write_double_no_skip("X33", self.X33),
                    write_double_no_skip("Z33", self.Z33),
                    write_double_no_skip("R34", self.R34),
                    write_double_no_skip("X34", self.X34),
                    write_double_no_skip("Z34", self.Z34),
                    # Zone 3 earth fault properties
                    write_double_no_skip("Re30", self.Re30),
                    write_double_no_skip("Xe30", self.Xe30),
                    write_double_no_skip("Ze30", self.Ze30),
                    write_double_no_skip("Re31", self.Re31),
                    write_double_no_skip("Xe31", self.Xe31),
                    write_double_no_skip("Ze31", self.Ze31),
                    write_double_no_skip("Re32", self.Re32),
                    write_double_no_skip("Xe32", self.Xe32),
                    write_double_no_skip("Ze32", self.Ze32),
                    write_double_no_skip("Re33", self.Re33),
                    write_double_no_skip("Xe33", self.Xe33),
                    write_double_no_skip("Ze33", self.Ze33),
                    write_double_no_skip("Re34", self.Re34),
                    write_double_no_skip("Xe34", self.Xe34),
                    write_double_no_skip("Ze34", self.Ze34),
                    # Zone -1/Reverse properties (normal phase)
                    write_double_no_skip("R-10", self.R_10),
                    write_double_no_skip("X-10", self.X_10),
                    write_double_no_skip("Z-10", self.Z_10),
                    write_double_no_skip("R-11", self.R_11),
                    write_double_no_skip("X-11", self.X_11),
                    write_double_no_skip("Z-11", self.Z_11),
                    write_double_no_skip("R-12", self.R_12),
                    write_double_no_skip("X-12", self.X_12),
                    write_double_no_skip("Z-12", self.Z_12),
                    write_double_no_skip("R-13", self.R_13),
                    write_double_no_skip("X-13", self.X_13),
                    write_double_no_skip("Z-13", self.Z_13),
                    write_double_no_skip("R-14", self.R_14),
                    write_double_no_skip("X-14", self.X_14),
                    write_double_no_skip("Z-14", self.Z_14),
                    # Zone -1 earth fault properties
                    write_double_no_skip("Re-10", self.Re_10),
                    write_double_no_skip("Xe-10", self.Xe_10),
                    write_double_no_skip("Ze-10", self.Ze_10),
                    write_double_no_skip("Re-11", self.Re_11),
                    write_double_no_skip("Xe-11", self.Xe_11),
                    write_double_no_skip("Ze-11", self.Ze_11),
                    write_double_no_skip("Re-12", self.Re_12),
                    write_double_no_skip("Xe-12", self.Xe_12),
                    write_double_no_skip("Ze-12", self.Ze_12),
                    write_double_no_skip("Re-13", self.Re_13),
                    write_double_no_skip("Xe-13", self.Xe_13),
                    write_double_no_skip("Ze-13", self.Ze_13),
                    write_double_no_skip("Re-14", self.Re_14),
                    write_double_no_skip("Xe-14", self.Xe_14),
                    write_double_no_skip("Ze-14", self.Ze_14),
                ],
            )

            zones = [
                (1, self.zone1, self.t1),
                (2, self.zone2, self.t2),
                (3, self.zone3, self.t3),
                (-1, self.zone_reverse, self.t_reverse),
            ]

            for z_num, zone, t_val in zones:
                zone_str = str(z_num) if z_num != -1 else "-1"
                props.append(write_boolean_no_skip(f"Present{zone_str}", value=zone.present))

                if zone.present:
                    props.append(write_quote_string(f"Characteristic{zone_str}", zone.characteristic))

                    # Serialize settings based on characteristic
                    if zone.characteristic == "C" and zone.settings:
                        props.append(write_double_no_skip(f"Z{abs(z_num)}", zone.settings[0].Z))
                    elif zone.characteristic == "M" and zone.settings:
                        props.append(write_double_no_skip(f"R{abs(z_num)}", zone.settings[0].R))
                        props.append(write_double_no_skip(f"X{abs(z_num)}", zone.settings[0].X))
                        props.append(write_double_no_skip(f"Z{abs(z_num)}", zone.settings[0].Z))
                    elif zone.characteristic == "P" and len(zone.settings) >= self.POLYGON_POINT_COUNT:
                        for j in range(self.POLYGON_POINT_COUNT):
                            props.append(write_double_no_skip(f"R{abs(z_num)}{j}", zone.settings[j].R))
                            props.append(write_double_no_skip(f"X{abs(z_num)}{j}", zone.settings[j].X))
                            props.append(write_double_no_skip(f"Z{abs(z_num)}{j}", zone.settings[j].Z))

                    # Earth fault settings
                    props.append(write_boolean_no_skip(f"EarthFault{zone_str}Present", value=zone.earth_fault))
                    if zone.earth_fault:
                        props.append(
                            write_quote_string(
                                f"EarthFault{zone_str}Characteristic",
                                zone.earth_fault_characteristic,
                            ),
                        )

                        if zone.earth_fault_characteristic == "C" and zone.earth_fault_settings:
                            props.append(write_double_no_skip(f"Ze{abs(z_num)}", zone.earth_fault_settings[0].Z))
                        elif zone.earth_fault_characteristic == "M" and zone.earth_fault_settings:
                            props.append(write_double_no_skip(f"Re{abs(z_num)}", zone.earth_fault_settings[0].R))
                            props.append(write_double_no_skip(f"Xe{abs(z_num)}", zone.earth_fault_settings[0].X))
                            props.append(write_double_no_skip(f"Ze{abs(z_num)}", zone.earth_fault_settings[0].Z))
                        elif (
                            zone.earth_fault_characteristic == "P"
                            and len(zone.earth_fault_settings) >= self.POLYGON_POINT_COUNT
                        ):
                            for j in range(self.POLYGON_POINT_COUNT):
                                props.append(
                                    write_double_no_skip(
                                        f"Re{abs(z_num)}{j}",
                                        zone.earth_fault_settings[j].R,
                                    )
                                )
                                props.append(
                                    write_double_no_skip(
                                        f"Xe{abs(z_num)}{j}",
                                        zone.earth_fault_settings[j].X,
                                    )
                                )
                                props.append(
                                    write_double_no_skip(
                                        f"Ze{abs(z_num)}{j}",
                                        zone.earth_fault_settings[j].Z,
                                    )
                                )

                props.append(write_double_no_skip(f"T{zone_str}", t_val))

            props.extend(
                [
                    write_double_no_skip("T4", self.t4),
                    write_double_no_skip("T0", self.t0),
                ],
            )

            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.DistanceProtectionType:
            """Deserialize DistanceProtectionType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                t_input=data.get("TInput", 0.0),
                t_output=data.get("TOutput", 0.0),
                ie_great=data.get("Ie>", 0.0),
                i_great=data.get("I>", 0.0),
                u_small=data.get("U<", 0.0),
                z_small=data.get("Z<", 0.0),
                kn=data.get("Kn", 0.0),
                kn_angle=data.get("KnAngle", 0.0),
                t1=data.get("T1", 0.0),
                t2=data.get("T2", 0.0),
                t3=data.get("T3", 0.0),
                t_reverse=data.get("T-1", 0.0),
                t4=data.get("T4", 0.0),
                t0=data.get("T0", 0.0),
                # Zone 1 properties (normal phase)
                R10=data.get("R10", 0.0),
                X10=data.get("X10", 0.0),
                Z10=data.get("Z10", 0.0),
                R11=data.get("R11", 0.0),
                X11=data.get("X11", 0.0),
                Z11=data.get("Z11", 0.0),
                R12=data.get("R12", 0.0),
                X12=data.get("X12", 0.0),
                Z12=data.get("Z12", 0.0),
                R13=data.get("R13", 0.0),
                X13=data.get("X13", 0.0),
                Z13=data.get("Z13", 0.0),
                R14=data.get("R14", 0.0),
                X14=data.get("X14", 0.0),
                Z14=data.get("Z14", 0.0),
                # Zone 1 earth fault properties
                Re10=data.get("Re10", 0.0),
                Xe10=data.get("Xe10", 0.0),
                Ze10=data.get("Ze10", 0.0),
                Re11=data.get("Re11", 0.0),
                Xe11=data.get("Xe11", 0.0),
                Ze11=data.get("Ze11", 0.0),
                Re12=data.get("Re12", 0.0),
                Xe12=data.get("Xe12", 0.0),
                Ze12=data.get("Ze12", 0.0),
                Re13=data.get("Re13", 0.0),
                Xe13=data.get("Xe13", 0.0),
                Ze13=data.get("Ze13", 0.0),
                Re14=data.get("Re14", 0.0),
                Xe14=data.get("Xe14", 0.0),
                Ze14=data.get("Ze14", 0.0),
                # Zone 2 properties (normal phase)
                R20=data.get("R20", 0.0),
                X20=data.get("X20", 0.0),
                Z20=data.get("Z20", 0.0),
                R21=data.get("R21", 0.0),
                X21=data.get("X21", 0.0),
                Z21=data.get("Z21", 0.0),
                R22=data.get("R22", 0.0),
                X22=data.get("X22", 0.0),
                Z22=data.get("Z22", 0.0),
                R23=data.get("R23", 0.0),
                X23=data.get("X23", 0.0),
                Z23=data.get("Z23", 0.0),
                R24=data.get("R24", 0.0),
                X24=data.get("X24", 0.0),
                Z24=data.get("Z24", 0.0),
                # Zone 2 earth fault properties
                Re20=data.get("Re20", 0.0),
                Xe20=data.get("Xe20", 0.0),
                Ze20=data.get("Ze20", 0.0),
                Re21=data.get("Re21", 0.0),
                Xe21=data.get("Xe21", 0.0),
                Ze21=data.get("Ze21", 0.0),
                Re22=data.get("Re22", 0.0),
                Xe22=data.get("Xe22", 0.0),
                Ze22=data.get("Ze22", 0.0),
                Re23=data.get("Re23", 0.0),
                Xe23=data.get("Xe23", 0.0),
                Ze23=data.get("Ze23", 0.0),
                Re24=data.get("Re24", 0.0),
                Xe24=data.get("Xe24", 0.0),
                Ze24=data.get("Ze24", 0.0),
                # Zone 3 properties (normal phase)
                R30=data.get("R30", 0.0),
                X30=data.get("X30", 0.0),
                Z30=data.get("Z30", 0.0),
                R31=data.get("R31", 0.0),
                X31=data.get("X31", 0.0),
                Z31=data.get("Z31", 0.0),
                R32=data.get("R32", 0.0),
                X32=data.get("X32", 0.0),
                Z32=data.get("Z32", 0.0),
                R33=data.get("R33", 0.0),
                X33=data.get("X33", 0.0),
                Z33=data.get("Z33", 0.0),
                R34=data.get("R34", 0.0),
                X34=data.get("X34", 0.0),
                Z34=data.get("Z34", 0.0),
                # Zone 3 earth fault properties
                Re30=data.get("Re30", 0.0),
                Xe30=data.get("Xe30", 0.0),
                Ze30=data.get("Ze30", 0.0),
                Re31=data.get("Re31", 0.0),
                Xe31=data.get("Xe31", 0.0),
                Ze31=data.get("Ze31", 0.0),
                Re32=data.get("Re32", 0.0),
                Xe32=data.get("Xe32", 0.0),
                Ze32=data.get("Ze32", 0.0),
                Re33=data.get("Re33", 0.0),
                Xe33=data.get("Xe33", 0.0),
                Ze33=data.get("Ze33", 0.0),
                Re34=data.get("Re34", 0.0),
                Xe34=data.get("Xe34", 0.0),
                Ze34=data.get("Ze34", 0.0),
                # Zone -1/Reverse properties (normal phase)
                R_10=data.get("R-10", 0.0),
                X_10=data.get("X-10", 0.0),
                Z_10=data.get("Z-10", 0.0),
                R_11=data.get("R-11", 0.0),
                X_11=data.get("X-11", 0.0),
                Z_11=data.get("Z-11", 0.0),
                R_12=data.get("R-12", 0.0),
                X_12=data.get("X-12", 0.0),
                Z_12=data.get("Z-12", 0.0),
                R_13=data.get("R-13", 0.0),
                X_13=data.get("X-13", 0.0),
                Z_13=data.get("Z-13", 0.0),
                R_14=data.get("R-14", 0.0),
                X_14=data.get("X-14", 0.0),
                Z_14=data.get("Z-14", 0.0),
                # Zone -1 earth fault properties
                Re_10=data.get("Re-10", 0.0),
                Xe_10=data.get("Xe-10", 0.0),
                Ze_10=data.get("Ze-10", 0.0),
                Re_11=data.get("Re-11", 0.0),
                Xe_11=data.get("Xe-11", 0.0),
                Ze_11=data.get("Ze-11", 0.0),
                Re_12=data.get("Re-12", 0.0),
                Xe_12=data.get("Xe-12", 0.0),
                Ze_12=data.get("Ze-12", 0.0),
                Re_13=data.get("Re-13", 0.0),
                Xe_13=data.get("Xe-13", 0.0),
                Ze_13=data.get("Ze-13", 0.0),
                Re_14=data.get("Re-14", 0.0),
                Xe_14=data.get("Xe-14", 0.0),
                Ze_14=data.get("Ze-14", 0.0),
            )

    @dataclass_json
    @dataclass
    class DifferentialProtectionType(DataClassJsonMixin):
        """Differential protection type properties."""

        name: str = string_field()
        t_input: float = 0.0
        t_output: float = 0.0
        setting_sort: int = 1
        dI_great: float = field(default=0.0, metadata=config(field_name="dI>"))  # noqa: N815
        t_great: float = field(default=0.0, metadata=config(field_name="T>"))
        dI_greater: float = field(default=0.0, metadata=config(field_name="dI>>"))  # noqa: N815
        t_greater: float = field(default=0.0, metadata=config(field_name="T>>"))
        m: float = 1.0
        d_Id: float = 20.0  # noqa: N815
        k1: float = 0.0
        k2: float = 0.0
        k3: float = 0.0
        k4: float = 0.0
        release_by_current_protection: bool = False
        no_own_measurement: bool = False

        def serialize(self) -> str:
            """Serialize DifferentialProtectionType properties."""
            return serialize_properties(
                write_quote_string("Name", self.name),
                write_double("Tinput", self.t_input),
                write_double("Toutput", self.t_output),
                write_integer_no_skip("SettingSort", self.setting_sort),
                write_double_no_skip("dI>", self.dI_great),
                write_double_no_skip("T>", self.t_great),
                write_double_no_skip("dI>>", self.dI_greater),
                write_double_no_skip("T>>", self.t_greater),
                write_double_no_skip("m", self.m),
                write_double("dId", self.d_Id),
                write_double_no_skip("k1", self.k1),
                write_double_no_skip("k2", self.k2),
                write_double_no_skip("k3", self.k3),
                write_double_no_skip("k4", self.k4),
                write_boolean(
                    "ReleaseByCurrentProtection",
                    value=self.release_by_current_protection,
                ),
                write_boolean("NoOwnMeasurement", value=self.no_own_measurement),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.DifferentialProtectionType:
            """Deserialize DifferentialProtectionType properties from VNF format."""
            return cls(
                name=data.get("Name", ""),
                t_input=data.get("Tinput", 0.0),
                t_output=data.get("Toutput", 0.0),
                setting_sort=data.get("SettingSort", 1),
                dI_great=data.get("dI>", 0.0),
                t_great=data.get("T>", 0.0),
                dI_greater=data.get("dI>>", 0.0),
                t_greater=data.get("T>>", 0.0),
                m=data.get("m", 1.0),
                d_Id=data.get("dId", 20.0),
                k1=data.get("k1", 0.0),
                k2=data.get("k2", 0.0),
                k3=data.get("k3", 0.0),
                k4=data.get("k4", 0.0),
                release_by_current_protection=data.get("ReleaseByCurrentProtection", False),
                no_own_measurement=data.get("NoOwnMeasurement", False),
            )

    @dataclass_json
    @dataclass
    class EarthFaultDifferentialProtection(DataClassJsonMixin):
        """Earth fault differential protection properties."""

        dI_great: float = field(default=0.0, metadata=config(field_name="dI>"))  # noqa: N815
        t_great: float = field(default=0.0, metadata=config(field_name="T>"))
        other_measure_point: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )

        def serialize(self) -> str:
            """Serialize EarthFaultDifferentialProtection properties."""
            props = [
                write_double_no_skip("dI>", self.dI_great),
                write_double_no_skip("T>", self.t_great),
            ]
            if self.other_measure_point:
                props.append(write_guid("OtherMeasurePoint", self.other_measure_point))
            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.EarthFaultDifferentialProtection:
            """Deserialize EarthFaultDifferentialProtection properties."""
            other_measure_point = data.get("OtherMeasurePoint")
            return cls(
                dI_great=data.get("dI>", 0.0),
                t_great=data.get("T>", 0.0),
                other_measure_point=(decode_guid(other_measure_point) if other_measure_point else None),
            )

    @dataclass_json
    @dataclass
    class VectorShiftProtection(DataClassJsonMixin):
        """Vector jump protection properties."""

        d_phi_great: float = 0.0
        t_great: float = 0.0

        def serialize(self) -> str:
            """Serialize VectorShiftProtection properties."""
            return serialize_properties(
                write_double_no_skip("Phi>", self.d_phi_great),
                write_double_no_skip("T>", self.t_great),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.VectorShiftProtection:
            """Deserialize VectorShiftProtection properties."""
            return cls(
                d_phi_great=data.get("Phi>", 0.0),
                t_great=data.get("T>", 0.0),
            )

    @dataclass_json
    @dataclass
    class FrequencyProtection(DataClassJsonMixin):
        """Frequency protection properties."""

        Fsmall: float = field(default=0.0, metadata=config(field_name="F<"))
        Fgreat: float = field(default=0.0, metadata=config(field_name="F>"))

        def serialize(self) -> str:
            """Serialize FrequencyProtection properties."""
            return serialize_properties(
                write_double_no_skip("F<", self.Fsmall),
                write_double_no_skip("F>", self.Fgreat),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerMV.FrequencyProtection:
            """Deserialize FrequencyProtection properties."""
            return cls(
                Fsmall=data.get("F<", 0.0),
                Fgreat=data.get("F>", 0.0),
            )

    general: General
    type: CircuitBreakerType | None = None
    current_protection1: Protection | None = None
    current_protection2: Protection | None = None
    earth_fault_protection1: Protection | None = None
    earth_fault_protection2: Protection | None = None
    unbalance_protection: Protection | None = None
    thermal_protection: ThermalProtection | None = None
    voltage_protection: VoltageProtectionType | None = None
    distance_protection: DistanceProtectionType | None = None
    differential_protection_type: DifferentialProtectionType | None = None
    earth_fault_differential_protection: EarthFaultDifferentialProtection | None = None
    vector_shift_protection: VectorShiftProtection | None = None
    frequency_protection: FrequencyProtection | None = None
    presentations: list[SecondaryPresentation] = field(default_factory=list)

    # Protection type instances
    current_protection1_type: ProtectionType | None = None
    current_protection2_type: ProtectionType | None = None
    earth_fault_protection1_type: ProtectionType | None = None
    earth_fault_protection2_type: ProtectionType | None = None
    unbalance_protection_type: ProtectionType | None = None

    differential_measure_points: list[Guid] = field(default_factory=list)
    block_protections: list[tuple[int, Guid, int]] = field(
        default_factory=list,
    )  # (ProtectionIndex, BlockCircuitBreaker, BlockProtectionIndex)
    reserve_switches: list[Guid] = field(default_factory=list)  # CircuitBreaker GUIDs
    transfer_trip_switches: list[tuple[int, Guid]] = field(
        default_factory=list,
    )  # (ProtectionIndex, TransferCircuitBreaker)

    def register(self, network: NetworkMV) -> None:
        """Will add circuit breaker to the network."""
        if self.general.guid in network.circuit_breakers:
            logger.critical("Circuit Breaker %s already exists, overwriting", self.general.guid)
        network.circuit_breakers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the circuit breaker to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#CircuitBreakerType {self.type.serialize()}")

        # Conditional sections based on Present flags
        if self.general.current_protection1_present and self.current_protection1_type:
            lines.append(f"#CurrentProtection1Type {self.current_protection1_type.serialize()}")
        if self.general.current_protection2_present and self.current_protection2_type:
            lines.append(f"#CurrentProtection2Type {self.current_protection2_type.serialize()}")
        if self.general.earth_fault_protection1_present and self.earth_fault_protection1_type:
            lines.append(f"#EarthFaultProtection1Type {self.earth_fault_protection1_type.serialize()}")
        if self.general.earth_fault_protection2_present and self.earth_fault_protection2_type:
            lines.append(f"#EarthFaultProtection2Type {self.earth_fault_protection2_type.serialize()}")
        if self.general.unbalance_protection_present and self.unbalance_protection_type:
            lines.append(f"#UnbalanceProtectionType {self.unbalance_protection_type.serialize()}")
        if self.general.thermal_protection_present and self.thermal_protection:
            lines.append(f"#ThermalProtection {self.thermal_protection.serialize()}")
        if self.general.voltage_protection_present and self.voltage_protection:
            lines.append(f"#VoltageProtectionType {self.voltage_protection.serialize()}")
        if self.general.distance_protection_present and self.distance_protection:
            lines.append(f"#DistanceProtectionType {self.distance_protection.serialize()}")
        if self.differential_protection_type:
            lines.append(f"#DifferentialProtectionType {self.differential_protection_type.serialize()}")
        # Multiple differential measure points
        lines.extend(
            f"#DifferentialProtectionMeasurePoint Object:'{{{str(guid).upper()}}}'"
            for guid in self.differential_measure_points
        )

        if self.general.earth_fault_differential_protection_present and self.earth_fault_differential_protection:
            lines.append(f"#EarthFaultDifferentialProtection {self.earth_fault_differential_protection.serialize()}")
        if self.general.vector_shift_protection_present and self.vector_shift_protection:
            lines.append(f"#VectorJumpProtection {self.vector_shift_protection.serialize()}")
        if self.general.frequency_protection_present and self.frequency_protection:
            lines.append(f"#FrequencyProtection {self.frequency_protection.serialize()}")

        # Block protections (only if BlockAbility is True)
        if self.general.block_ability:
            for (
                prot_index,
                block_breaker_guid,
                block_prot_index,
            ) in self.block_protections:
                block_props = serialize_properties(
                    write_integer_no_skip("ProtectionIndex", prot_index),
                    write_guid("BlockCircuitBreaker", block_breaker_guid),
                    write_integer_no_skip("BlockProtectionIndex", block_prot_index),
                )
                lines.append(f"#BlockProtection {block_props}")

        # Reserve switches (only if ReserveAbility is True)
        if self.general.reserve_ability:
            lines.extend(f"#ReserveSwitch CircuitBreaker:'{{{str(guid).upper()}}}'" for guid in self.reserve_switches)

        # Transfer trip switches (only if TransferTripAbility is True)
        if self.general.transfer_trip_ability:
            for prot_index, transfer_guid in self.transfer_trip_switches:
                transfer_props = serialize_properties(
                    write_integer_no_skip("ProtectionIndex", prot_index),
                    write_guid("TransferCircuitBreaker", transfer_guid),
                )
                lines.append(f"#TransferTripSwitch {transfer_props}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> CircuitBreakerMV:
        """Deserialization of the circuit breaker from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TCircuitBreakerMS: The deserialized circuit breaker

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        breaker_type = None
        if data.get("breakerType"):
            breaker_type = cls.CircuitBreakerType.deserialize(data["breakerType"][0])

        current_protection1 = None
        if data.get("currentProtection1"):
            current_protection1 = cls.Protection.deserialize(data["currentProtection1"][0])

        current_protection2 = None
        if data.get("currentProtection2"):
            current_protection2 = cls.Protection.deserialize(data["currentProtection2"][0])

        earth_fault_protection1 = None
        if data.get("earthFaultProtection1"):
            earth_fault_protection1 = cls.Protection.deserialize(data["earthFaultProtection1"][0])

        earth_fault_protection2 = None
        if data.get("earthFaultProtection2"):
            earth_fault_protection2 = cls.Protection.deserialize(data["earthFaultProtection2"][0])

        unbalance_protection = None
        if data.get("unbalanceProtection"):
            unbalance_protection = cls.Protection.deserialize(data["unbalanceProtection"][0])

        # Protection type instances
        current_protection1_type = None
        if data.get("currentProtection1Type"):
            current_protection1_type = cls.ProtectionType.deserialize(data["currentProtection1Type"][0])

        current_protection2_type = None
        if data.get("currentProtection2Type"):
            current_protection2_type = cls.ProtectionType.deserialize(data["currentProtection2Type"][0])

        earth_fault_protection1_type = None
        if data.get("earthFaultProtection1Type"):
            earth_fault_protection1_type = cls.ProtectionType.deserialize(data["earthFaultProtection1Type"][0])

        earth_fault_protection2_type = None
        if data.get("earthFaultProtection2Type"):
            earth_fault_protection2_type = cls.ProtectionType.deserialize(data["earthFaultProtection2Type"][0])

        unbalance_protection_type = None
        if data.get("unbalanceProtectionType"):
            unbalance_protection_type = cls.ProtectionType.deserialize(data["unbalanceProtectionType"][0])

        thermal_protection = None
        if data.get("thermalProtection"):
            thermal_protection = cls.ThermalProtection.deserialize(data["thermalProtection"][0])

        voltage_protection = None
        if data.get("voltageProtection"):
            voltage_protection = cls.VoltageProtectionType.deserialize(data["voltageProtection"][0])

        distance_protection = None
        if data.get("distanceProtection"):
            distance_protection = cls.DistanceProtectionType.deserialize(data["distanceProtection"][0])

        differential_protection_type = None
        if data.get("differentialProtectionType"):
            differential_protection_type = cls.DifferentialProtectionType.deserialize(
                data["differentialProtectionType"][0],
            )

        earth_fault_differential_protection = None
        if data.get("earthFaultDifferentialProtection"):
            earth_fault_differential_protection = cls.EarthFaultDifferentialProtection.deserialize(
                data["earthFaultDifferentialProtection"][0],
            )

        vector_shift_protection = None
        if data.get("vectorJumpProtection"):
            vector_shift_protection = cls.VectorShiftProtection.deserialize(data["vectorJumpProtection"][0])

        frequency_protection = None
        if data.get("frequencyProtection"):
            frequency_protection = cls.FrequencyProtection.deserialize(data["frequencyProtection"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import SecondaryPresentation

            presentation = SecondaryPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=breaker_type,
            current_protection1=current_protection1,
            current_protection2=current_protection2,
            earth_fault_protection1=earth_fault_protection1,
            earth_fault_protection2=earth_fault_protection2,
            unbalance_protection=unbalance_protection,
            thermal_protection=thermal_protection,
            voltage_protection=voltage_protection,
            distance_protection=distance_protection,
            differential_protection_type=differential_protection_type,
            earth_fault_differential_protection=earth_fault_differential_protection,
            vector_shift_protection=vector_shift_protection,
            frequency_protection=frequency_protection,
            presentations=presentations,
            current_protection1_type=current_protection1_type,
            current_protection2_type=current_protection2_type,
            earth_fault_protection1_type=earth_fault_protection1_type,
            earth_fault_protection2_type=earth_fault_protection2_type,
            unbalance_protection_type=unbalance_protection_type,
            differential_measure_points=data.get("differentialMeasurePoints", []),
            block_protections=data.get("blockProtections", []),
            reserve_switches=data.get("reserveSwitches", []),
            transfer_trip_switches=data.get("transferTripSwitches", []),
        )
