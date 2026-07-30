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
    encode_guid_optional,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin, IconMixin
from pyptp.elements.serialization_helpers import (
    serialize_notes,
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
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.lv.shared import HarmonicsType
    from pyptp.elements.mv.presentations import ElementPresentation
    from pyptp.elements.mv.shared import EfficiencyType
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class BatteryMV(ExtrasNotesMixin, HasPresentationsMixin, IconMixin):
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
        switch_state: bool = True
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
                write_boolean_as_byte_no_skip("SwitchState", value=self.switch_state),
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
                switch_state=bool(data.get("SwitchState", True)),
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
        k: float = 0.0
        charge_efficiency_type: str = string_field()
        """Type of the charging efficiency, as function of the input power."""
        discharge_efficiency_type: str = string_field()
        """Type of the discharging efficiency, as function of the output power."""

        def serialize(self) -> str:
            """Serialize Inverter properties."""
            return serialize_properties(
                write_double("Snom", self.snom),
                write_double("Unom", self.unom),
                write_double("Ik/Inom", self.ik_inom),
                write_double("k", self.k),
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
                k=data.get("k", 0.0),
                charge_efficiency_type=data.get("ChargeEfficiencyType", ""),
                discharge_efficiency_type=data.get("DischargeEfficiencyType", ""),
            )

    @dataclass_json
    @dataclass
    class QControl(DataClassJsonMixin):
        """Reactive power control of the battery inverter."""

        sort: int = 0
        cos_ref: float = 1.0
        direction: int = 0
        no_p_no_q: bool = True
        input1: float = 1.0
        output1: float = 0.0
        input2: float = 0.0
        output2: float = 0.0
        input3: float = 0.0
        output3: float = 0.0
        input4: float = 0.0
        output4: float = 0.0
        input5: float = 0.0
        output5: float = 0.0

        def serialize(self) -> str:
            """Serialize QControl properties."""
            return serialize_properties(
                write_integer("Sort", self.sort),
                write_double("CosRef", self.cos_ref),
                write_integer("Direction", self.direction),
                write_boolean_no_skip("NoPNoQ", value=self.no_p_no_q),
                write_double_no_skip("Input1", self.input1),
                write_double_no_skip("Output1", self.output1),
                write_double_no_skip("Input2", self.input2),
                write_double_no_skip("Output2", self.output2),
                write_double_no_skip("Input3", self.input3),
                write_double_no_skip("Output3", self.output3),
                write_double_no_skip("Input4", self.input4),
                write_double_no_skip("Output4", self.output4),
                write_double_no_skip("Input5", self.input5),
                write_double_no_skip("Output5", self.output5),
            )

        @classmethod
        def deserialize(cls, data: dict) -> BatteryMV.QControl:
            """Deserialize QControl properties."""
            return cls(
                sort=data.get("Sort", 0),
                cos_ref=data.get("CosRef", 1.0),
                direction=data.get("Direction", 0),
                no_p_no_q=data.get("NoPNoQ", True),
                input1=data.get("Input1", 1.0),
                output1=data.get("Output1", 0.0),
                input2=data.get("Input2", 0.0),
                output2=data.get("Output2", 0.0),
                input3=data.get("Input3", 0.0),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
            )

    @dataclass_json
    @dataclass
    class PUControl(DataClassJsonMixin):
        """Power(voltage) control of the battery inverter."""

        sort: int = 0
        input1: float = 1.0
        output1: float = 0.0
        input2: float = 0.0
        output2: float = 0.0
        input3: float = 0.0
        output3: float = 0.0
        input4: float = 0.0
        output4: float = 0.0
        input5: float = 0.0
        output5: float = 0.0

        def serialize(self) -> str:
            """Serialize PUControl properties."""
            return serialize_properties(
                write_integer_no_skip("Sort", self.sort),
                write_double_no_skip("Input1", self.input1),
                write_double_no_skip("Output1", self.output1),
                write_double_no_skip("Input2", self.input2),
                write_double_no_skip("Output2", self.output2),
                write_double_no_skip("Input3", self.input3),
                write_double_no_skip("Output3", self.output3),
                write_double_no_skip("Input4", self.input4),
                write_double_no_skip("Output4", self.output4),
                write_double_no_skip("Input5", self.input5),
                write_double_no_skip("Output5", self.output5),
            )

        @classmethod
        def deserialize(cls, data: dict) -> BatteryMV.PUControl:
            """Deserialize PUControl properties."""
            return cls(
                sort=data.get("Sort", 0),
                input1=data.get("Input1", 1.0),
                output1=data.get("Output1", 0.0),
                input2=data.get("Input2", 0.0),
                output2=data.get("Output2", 0.0),
                input3=data.get("Input3", 0.0),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
            )

    @dataclass_json
    @dataclass
    class PIControl(DataClassJsonMixin):
        """Power(current) control of the battery inverter."""

        sort: int = 0
        input1: float = 1.0
        output1: float = 0.0
        input2: float = 0.0
        output2: float = 0.0
        input3: float = 0.0
        output3: float = 0.0
        input4: float = 0.0
        output4: float = 0.0
        input5: float = 0.0
        output5: float = 0.0
        measure_field1: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        measure_field2: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        measure_field3: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )

        def serialize(self) -> str:
            """Serialize PIControl properties."""
            return serialize_properties(
                write_integer_no_skip("Sort", self.sort),
                write_double_no_skip("Input1", self.input1),
                write_double_no_skip("Output1", self.output1),
                write_double_no_skip("Input2", self.input2),
                write_double_no_skip("Output2", self.output2),
                write_double_no_skip("Input3", self.input3),
                write_double_no_skip("Output3", self.output3),
                write_double_no_skip("Input4", self.input4),
                write_double_no_skip("Output4", self.output4),
                write_double_no_skip("Input5", self.input5),
                write_double_no_skip("Output5", self.output5),
                write_guid("MeasureField1", self.measure_field1) if self.measure_field1 else "",
                write_guid("MeasureField2", self.measure_field2) if self.measure_field2 else "",
                write_guid("MeasureField3", self.measure_field3) if self.measure_field3 else "",
            )

        @classmethod
        def deserialize(cls, data: dict) -> BatteryMV.PIControl:
            """Deserialize PIControl properties."""
            measure_field1 = data.get("MeasureField1")
            measure_field2 = data.get("MeasureField2")
            measure_field3 = data.get("MeasureField3")

            return cls(
                sort=data.get("Sort", 0),
                input1=data.get("Input1", 1.0),
                output1=data.get("Output1", 0.0),
                input2=data.get("Input2", 0.0),
                output2=data.get("Output2", 0.0),
                input3=data.get("Input3", 0.0),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
                measure_field1=decode_guid(measure_field1) if measure_field1 else None,
                measure_field2=decode_guid(measure_field2) if measure_field2 else None,
                measure_field3=decode_guid(measure_field3) if measure_field3 else None,
            )

    general: General
    inverter: Inverter
    presentations: list[ElementPresentation]
    charge_efficiency_type: EfficiencyType | None = None
    discharge_efficiency_type: EfficiencyType | None = None
    q_control: QControl | None = None
    pu_control: PUControl | None = None
    pi_control: PIControl | None = None
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

        if self.q_control:
            lines.append(f"#QControl {self.q_control.serialize()}")

        if self.pu_control:
            lines.append(f"#P(U)Control {self.pu_control.serialize()}")

        if self.pi_control:
            lines.append(f"#P(I)Control {self.pi_control.serialize()}")

        if self.charge_efficiency_type:
            lines.append(f"#ChargeEfficiencyType {self.charge_efficiency_type.serialize()}")

        if self.discharge_efficiency_type:
            lines.append(f"#DischargeEfficiencyType {self.discharge_efficiency_type.serialize()}")

        if self.harmonics_type:
            lines.append(f"#HarmonicsType {self.harmonics_type.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(serialize_notes(self.notes))

        if self.icon is not None:
            lines.append(f"#Icon {self.icon.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

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

        q_control = None
        if data.get("qControl"):
            q_control = cls.QControl.deserialize(data["qControl"][0])

        pu_control = None
        if data.get("puControl"):
            pu_control = cls.PUControl.deserialize(data["puControl"][0])

        pi_control = None
        if data.get("piControl"):
            pi_control = cls.PIControl.deserialize(data["piControl"][0])

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
            q_control=q_control,
            pu_control=pu_control,
            pi_control=pi_control,
            harmonics_type=harmonics_type,
        )
