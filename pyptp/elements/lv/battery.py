"""Battery energy storage element for low-voltage networks.

Provides energy storage and power conversion capabilities with inverter
control, efficiency modeling, and state-of-charge management for LV
network optimization and grid balancing applications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import (
    DEFAULT_PROFILE_GUID,
    NIL_GUID,
    Guid,
    config,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.lv.presentations import ElementPresentation
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
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.lv.shared import EfficiencyType, HarmonicsType, PControl
    from pyptp.network_lv import NetworkLV


@dataclass_json
@dataclass
class BatteryLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Battery energy storage system for low-voltage network modeling.

    Integrates battery storage with power electronics for bidirectional
    energy flow, supporting grid stabilization, peak shaving, and renewable
    energy integration in LV distribution networks.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """Core battery system configuration and electrical connection properties."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        name: str = string_field()
        s_L1: bool = True  # noqa: N815
        s_L2: bool = True  # noqa: N815
        s_L3: bool = True  # noqa: N815
        s_N: bool = True  # noqa: N815
        field_name: str = string_field()
        """Name of the connection field."""
        single_phase: bool = False
        phase: int = 0
        pref: float = 0.0
        """Active power generation in MW (positive = charging from network)."""
        state_of_charge: float = 0.0
        """Initial state of charge in %."""
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        capacity: float = 100
        """Storage capacity in MWh."""
        c_rate: float = 0.5
        """1 hour nominal discharge rate in /h."""
        harmonics_type: str = string_field()

        def serialize(self) -> str:
            """Serialize general properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_guid("Node", self.node, skip=NIL_GUID),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date),
                write_double("RevisionDate", self.revision_date),
                write_quote_string("Name", self.name),
                write_boolean_no_skip("s_L1", value=self.s_L1),
                write_boolean_no_skip("s_L2", value=self.s_L2),
                write_boolean_no_skip("s_L3", value=self.s_L3),
                write_boolean_no_skip("s_N", value=self.s_N),
                write_quote_string("FieldName", self.field_name),
                write_boolean_no_skip("OnePhase", value=self.single_phase),
                write_integer_no_skip("Phase", self.phase),
                write_double_no_skip("Pref", self.pref),
                write_double_no_skip("StateOfCharge", self.state_of_charge),
                write_guid("Profile", self.profile),
                write_double_no_skip("Capacity", self.capacity),
                write_double_no_skip("Crate", self.c_rate),
                write_quote_string("HarmonicsType", self.harmonics_type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> BatteryLV.General:
            """Parse general properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed battery configuration.

            """
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
                single_phase=data.get("OnePhase", False),
                phase=data.get("Phase", 0),
                pref=data.get("Pref", 0.0),
                state_of_charge=data.get("StateOfCharge", 0.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                capacity=data.get("Capacity", 100),
                c_rate=data.get("Crate", 0.5),
                harmonics_type=data.get("HarmonicsType", ""),
            )

    @dataclass
    class Inverter(DataClassJsonMixin):
        """Power electronics inverter parameters for battery energy conversion.

        Defines AC/DC conversion characteristics and efficiency curves for
        accurate power flow modeling in both charging and discharging modes.
        """

        s_nom: float = 12.5
        """Nominal power of the inverter in MVA."""
        charge_efficiency_type: str = string_field()
        """Type of the charging efficiency, as function of the input power."""
        discharge_efficiency_type: str = string_field()
        """Type of the discharging efficiency, as function of the output power."""
        cos_ref: float = 1.0
        """Power factor."""

        def serialize(self) -> str:
            """Serialize inverter properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_double_no_skip("Snom", self.s_nom),
                write_quote_string("ChargeEfficiencyType", self.charge_efficiency_type),
                write_quote_string("DischargeEfficiencyType", self.discharge_efficiency_type),
                write_double_no_skip("Cosref", self.cos_ref),
            )

        @classmethod
        def deserialize(cls, data: dict) -> BatteryLV.Inverter:
            """Parse inverter properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized Inverter instance with parsed power electronics parameters.

            """
            return cls(
                s_nom=data.get("Snom", 12.5),
                charge_efficiency_type=data.get("ChargeEfficiencyType", ""),
                discharge_efficiency_type=data.get("DischargeEfficiencyType", ""),
                cos_ref=data.get("Cosref", 1.0),
            )

    general: General
    presentations: list[ElementPresentation]
    charge_efficiency: EfficiencyType
    discharge_efficiency: EfficiencyType
    power_control: PControl | None = None
    inverter: Inverter | None = None
    harmonics: HarmonicsType | None = None

    def __post_init__(self) -> None:
        """Initialize mixins for extras, notes, and presentations handling."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Register battery in LV network with duplicate detection.

        Args:
            network: Target LV network for battery registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.batteries:
            logger.critical("Battery %s already exists, overwriting", self.general.guid)
        network.batteries[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete battery system to GNF format.

        Returns:
            Multi-line string with all battery sections for GNF file.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.inverter:
            lines.append(f"#Inverter {self.inverter.serialize()}")

        if self.power_control:
            lines.append(f"#PControl {self.power_control.serialize()}")

        if self.charge_efficiency:
            lines.append(f"#ChargeEfficiencyType {self.charge_efficiency.serialize()}")

        if self.discharge_efficiency:
            lines.append(f"#DischargeEfficiencyType {self.discharge_efficiency.serialize()}")

        if self.harmonics:
            lines.append(f"#HarmonicsType {self.harmonics.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> BatteryLV:
        """Parse battery system from GNF format data.

        Args:
            data: Dictionary containing parsed GNF section data with general,
                  inverter, efficiency, and control information.

        Returns:
            Initialized TBatteryLS instance with all parsed battery components.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        inverter_data = data.get("inverter", [{}])[0] if data.get("inverter") else None
        inverter = cls.Inverter.deserialize(inverter_data) if inverter_data else None

        power_control_data = data.get("power_control", [{}])[0] if data.get("power_control") else None
        power_control = None
        if power_control_data:
            from pyptp.elements.lv.shared import PControl

            power_control = PControl.deserialize(power_control_data)

        charge_efficiency_data = data.get("charge_efficiency", [{}])[0] if data.get("charge_efficiency") else {}
        from pyptp.elements.lv.shared import EfficiencyType

        charge_efficiency = EfficiencyType.deserialize(charge_efficiency_data)

        discharge_efficiency_data = (
            data.get("discharge_efficiency", [{}])[0] if data.get("discharge_efficiency") else {}
        )
        discharge_efficiency = EfficiencyType.deserialize(discharge_efficiency_data)

        harmonics_data = data.get("harmonics", [{}])[0] if data.get("harmonics") else None
        harmonics = None
        if harmonics_data:
            from pyptp.elements.lv.shared import HarmonicsType

            harmonics = HarmonicsType.deserialize(harmonics_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            charge_efficiency=charge_efficiency,
            discharge_efficiency=discharge_efficiency,
            power_control=power_control,
            inverter=inverter,
            harmonics=harmonics,
        )
