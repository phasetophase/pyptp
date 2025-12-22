"""Battery energy storage element for medium-voltage networks.

Provides grid-scale energy storage capabilities with symmetrical modeling
for MV network optimization, load leveling, and renewable energy
integration in distribution and sub-transmission systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
    DEFAULT_PROFILE_GUID,
    NIL_GUID,
    Guid,
    decode_guid,
    encode_guid,
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
    from pyptp.elements.lv.shared import HarmonicsType
    from pyptp.elements.mv.presentations import ElementPresentation
    from pyptp.elements.mv.shared import EfficiencyType, PControl, QControl
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class BatteryMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Battery energy storage system for medium-voltage network modeling.

    Integrates large-scale battery storage with symmetrical power system
    modeling for grid stabilization, peak shaving, and renewable energy
    balancing in MV distribution networks.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a battery."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0.0
        mutation_date: int = 0
        revision_date: int = 0
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
        """Generation of active power in MW (positive = charging from network)."""
        state_of_charge: float = 50.0
        """Initial State of Charge in %."""
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        capacity: float = 0.0
        """Storage capacity in MWh."""
        c_rate: float = 0.5
        """1 hour nominal discharge rate in /h."""
        harmonics_type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node, skip=NIL_GUID),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
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
                write_double("StateOfCharge", self.state_of_charge),
                write_guid("Profile", self.profile, skip=NIL_GUID),
                write_double("Capacity", self.capacity),
                write_double("Crate", self.c_rate),
                write_quote_string("HarmonicsType", self.harmonics_type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> BatteryMV.General:
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
                state_of_charge=data.get("StateOfCharge", 50.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                capacity=data.get("Capacity", 0.0),
                c_rate=data.get("Crate", 0.5),
                harmonics_type=data.get("HarmonicsType", ""),
            )

    @dataclass_json
    @dataclass
    class Inverter(DataClassJsonMixin):
        """Battery inverter properties."""

        snom: float = 0.0
        """Nominal power of the inverter in MVA."""
        unom: float = 0.0
        """Nominal voltage of the inverter in kV."""
        ik_inom: float = field(metadata=config(field_name="Ik/Inom"), default=1.0)
        """Relation between the short circuit current and the nominal current."""
        charge_efficiency_type: str = string_field()
        """Type of the charging efficiency, as function of the input power."""
        discharge_efficiency_type: str = string_field()
        """Type of the discharging efficiency, as function of the output power."""

        def serialize(self) -> str:
            """Serialize Inverter properties."""
            return serialize_properties(
                write_double("Snom", self.snom),
                write_double("Unom", self.unom),
                write_double_no_skip("Ik/Inom", self.ik_inom),
                write_quote_string("ChargeEfficiencyType", self.charge_efficiency_type),
                write_quote_string("DischargeEfficiencyType", self.discharge_efficiency_type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> BatteryMV.Inverter:
            """Deserialize Inverter properties."""
            return cls(
                snom=data.get("Snom", 0.0),
                unom=data.get("Unom", 0.0),
                ik_inom=data.get("Ik/Inom", 1.0),
                charge_efficiency_type=data.get("ChargeEfficiencyType", ""),
                discharge_efficiency_type=data.get("DischargeEfficiencyType", ""),
            )

    general: General
    inverter: Inverter
    presentations: list[ElementPresentation]
    charge_efficiency_type: EfficiencyType | None = None
    discharge_efficiency_type: EfficiencyType | None = None
    p_control: PControl | None = None
    q_control: QControl | None = None
    harmonics_type: HarmonicsType | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add battery to the network."""
        if self.general.guid in network.batteries:
            logger.critical("Battery %s already exists, overwriting", self.general.guid)
        network.batteries[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the battery to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.append(f"#Inverter {self.inverter.serialize()}")

        if self.p_control:
            lines.append(f"#PControl {self.p_control.serialize()}")

        if self.q_control:
            lines.append(f"#QControl {self.q_control.serialize()}")

        if self.charge_efficiency_type:
            lines.append(f"#ChargeEfficiencyType {self.charge_efficiency_type.serialize()}")

        if self.discharge_efficiency_type:
            lines.append(f"#DischargeEfficiencyType {self.discharge_efficiency_type.serialize()}")

        if self.harmonics_type:
            lines.append(f"#HarmonicsType {self.harmonics_type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> BatteryMV:
        """Deserialization of the battery from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TBatteryMS: The deserialized battery

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        inverter_data = data.get("inverter", [{}])[0] if data.get("inverter") else {}
        inverter = cls.Inverter.deserialize(inverter_data)

        p_control = None
        if data.get("pControl"):
            from .shared import PControl

            p_control = PControl.deserialize(data["pControl"][0])

        q_control = None
        if data.get("qControl"):
            from .shared import QControl

            q_control = QControl.deserialize(data["qControl"][0])

        charge_efficiency = None
        if data.get("chargeEfficiencyType"):
            from .shared import EfficiencyType

            charge_efficiency = EfficiencyType.deserialize(data["chargeEfficiencyType"][0])

        discharge_efficiency = None
        if data.get("dischargeEfficiencyType"):
            from .shared import EfficiencyType

            discharge_efficiency = EfficiencyType.deserialize(data["dischargeEfficiencyType"][0])

        harmonics_type = None
        if data.get("harmonicsType"):
            from pyptp.elements.lv.shared import HarmonicsType

            harmonics_type = HarmonicsType.deserialize(data["harmonicsType"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            inverter=inverter,
            presentations=presentations,
            charge_efficiency_type=charge_efficiency,
            discharge_efficiency_type=discharge_efficiency,
            p_control=p_control,
            q_control=q_control,
            harmonics_type=harmonics_type,
        )
