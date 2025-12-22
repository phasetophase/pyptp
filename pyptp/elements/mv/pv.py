"""PV (Element)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
    DEFAULT_PROFILE_GUID,
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
    from pyptp.elements.mv.shared import EfficiencyType, QControl
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class PVMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a PV (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a PV."""

        node: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
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
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        not_preferred: bool = False
        scaling: float = 1000.0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        longitude: float = 52.0
        latitude: float = 5.0
        panel1_pnom: float = 0.0
        panel1_orientation: float = 180.0
        panel1_slope: float = 30.0
        panel2_pnom: float = 0.0
        panel2_orientation: float = 180.0
        panel2_slope: float = 30.0
        panel3_pnom: float = 0.0
        panel3_orientation: float = 180.0
        panel3_slope: float = 30.0
        harmonics_type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node) if self.node is not None else "",
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
                write_double_no_skip("Scaling", self.scaling),
                write_guid_no_skip("Profile", self.profile),
                write_double("Longitude", self.longitude, skip=0.0),
                write_double("Latitude", self.latitude, skip=0.0),
                write_double("Panel1Pnom", self.panel1_pnom, skip=0.0),
                write_double_no_skip("Panel1Orientation", self.panel1_orientation),
                write_double_no_skip("Panel1Slope", self.panel1_slope),
                write_double("Panel2Pnom", self.panel2_pnom, skip=0.0),
                write_double_no_skip("Panel2Orientation", self.panel2_orientation),
                write_double_no_skip("Panel2Slope", self.panel2_slope),
                write_double("Panel3Pnom", self.panel3_pnom, skip=0.0),
                write_double_no_skip("Panel3Orientation", self.panel3_orientation),
                write_double_no_skip("Panel3Slope", self.panel3_slope),
                write_quote_string("HarmonicsType", self.harmonics_type, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVMV.General:
            """Deserialize General properties."""
            guid = data.get("GUID")
            node = data.get("Node")
            profile = data.get("Profile")
            mutation_date = data.get("MutationDate")
            revision_date = data.get("RevisionDate")

            return cls(
                guid=decode_guid(guid) if guid else Guid(uuid4()),
                node=decode_guid(node) if node else None,
                creation_time=data.get("CreationTime", 0),
                mutation_date=mutation_date if mutation_date is not None else 0,
                revision_date=revision_date if revision_date is not None else 0.0,
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
                scaling=data.get("Scaling", 1000.0),
                profile=decode_guid(profile) if profile else DEFAULT_PROFILE_GUID,
                longitude=data.get("Longitude", 52.0),
                latitude=data.get("Latitude", 5.0),
                panel1_pnom=data.get("Panel1Pnom", 0.0),
                panel1_orientation=data.get("Panel1Orientation", 180.0),
                panel1_slope=data.get("Panel1Slope", 30.0),
                panel2_pnom=data.get("Panel2Pnom", 0.0),
                panel2_orientation=data.get("Panel2Orientation", 180.0),
                panel2_slope=data.get("Panel2Slope", 30.0),
                panel3_pnom=data.get("Panel3Pnom", 0.0),
                panel3_orientation=data.get("Panel3Orientation", 180.0),
                panel3_slope=data.get("Panel3Slope", 30.0),
                harmonics_type=data.get("HarmonicsType", ""),
            )

    @dataclass_json
    @dataclass
    class Inverter(DataClassJsonMixin):
        """PV inverter."""

        snom: float = 12.5
        unom: float = 0.0
        ik_inom: float = field(default=1.0, metadata=config(field_name="Ik/Inom"))
        efficiency_type: str = string_field()
        u_off: float = 0.0

        def serialize(self) -> str:
            """Serialize Inverter properties."""
            return serialize_properties(
                write_double_no_skip("Snom", self.snom),
                write_double("Unom", self.unom, skip=0.0),
                write_double_no_skip("Ik/Inom", self.ik_inom),
                write_quote_string("EfficiencyType", self.efficiency_type, skip=""),
                write_double("Uoff", self.u_off, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVMV.Inverter:
            """Deserialize Inverter properties."""
            return cls(
                snom=data.get("Snom", 12.5),
                unom=data.get("Unom", 0.0),
                ik_inom=data.get("Ik/Inom", 1.0),
                efficiency_type=data.get("EfficiencyType", ""),
                u_off=data.get("Uoff", 0.0),
            )

    @dataclass_json
    @dataclass
    class PUControl(DataClassJsonMixin):
        """Power(voltage) control."""

        input1: float = 0.0
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
                write_double("Input1", self.input1, skip=0.0),
                write_double("Output1", self.output1, skip=0.0),
                write_double("Input2", self.input2, skip=0.0),
                write_double("Output2", self.output2, skip=0.0),
                write_double("Input3", self.input3, skip=0.0),
                write_double("Output3", self.output3, skip=0.0),
                write_double("Input4", self.input4, skip=0.0),
                write_double("Output4", self.output4, skip=0.0),
                write_double("Input5", self.input5, skip=0.0),
                write_double("Output5", self.output5, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVMV.PUControl:
            """Deserialize PUControl properties."""
            return cls(
                input1=data.get("Input1", 0.0),
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
    class PFControl(DataClassJsonMixin):
        """Power(frequency) control."""

        input1: float = 0.0
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
            """Serialize PFControl properties."""
            return serialize_properties(
                write_double("Input1", self.input1, skip=0.0),
                write_double("Output1", self.output1, skip=0.0),
                write_double("Input2", self.input2, skip=0.0),
                write_double("Output2", self.output2, skip=0.0),
                write_double("Input3", self.input3, skip=0.0),
                write_double("Output3", self.output3, skip=0.0),
                write_double("Input4", self.input4, skip=0.0),
                write_double("Output4", self.output4, skip=0.0),
                write_double("Input5", self.input5, skip=0.0),
                write_double("Output5", self.output5, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVMV.PFControl:
            """Deserialize PFControl properties."""
            return cls(
                input1=data.get("Input1", 0.0),
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
        """Power(current) control."""

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
        measure_field1: str = string_field()
        measure_field2: str = string_field()
        measure_field3: str = string_field()

        def serialize(self) -> str:
            """Serialize PIControl properties."""
            return serialize_properties(
                write_double("Input1", self.input1, skip=0.0),
                write_double("Output1", self.output1, skip=0.0),
                write_double("Input2", self.input2, skip=0.0),
                write_double("Output2", self.output2, skip=0.0),
                write_double("Input3", self.input3, skip=0.0),
                write_double("Output3", self.output3, skip=0.0),
                write_double("Input4", self.input4, skip=0.0),
                write_double("Output4", self.output4, skip=0.0),
                write_double("Input5", self.input5, skip=0.0),
                write_double("Output5", self.output5, skip=0.0),
                write_quote_string("MeasureField1", self.measure_field1, skip=""),
                write_quote_string("MeasureField2", self.measure_field2, skip=""),
                write_quote_string("MeasureField3", self.measure_field3, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVMV.PIControl:
            """Deserialize PIControl properties."""
            return cls(
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
                measure_field1=data.get("MeasureField1", ""),
                measure_field2=data.get("MeasureField2", ""),
                measure_field3=data.get("MeasureField3", ""),
            )

    @dataclass_json
    @dataclass
    class Capacity(DataClassJsonMixin):
        """Capacity."""

        sort: str = string_field()
        begin_date: int = 0
        end_date: int = 0
        begin_time: float = 0.0
        end_time: float = 0.0
        p_max: float = 0.0

        def serialize(self) -> str:
            """Serialize Capacity properties."""
            return serialize_properties(
                write_quote_string("Sort", self.sort, skip=""),
                write_integer("BeginDate", self.begin_date, skip=0),
                write_integer("EndDate", self.end_date, skip=0),
                write_double("BeginTime", self.begin_time, skip=0.0),
                write_double("EndTime", self.end_time, skip=0.0),
                write_double("Pmax", self.p_max, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVMV.Capacity:
            """Deserialize Capacity properties."""
            return cls(
                sort=data.get("Sort", ""),
                begin_date=data.get("BeginDate", 0),
                end_date=data.get("EndDate", 0),
                begin_time=data.get("BeginTime", 0.0),
                end_time=data.get("EndTime", 0.0),
                p_max=data.get("Pmax", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]
    inverter: Inverter
    efficiency_type: EfficiencyType | None = None
    harmonics_type: HarmonicsType | None = None
    q_control: QControl | None = None
    pu_control: PUControl | None = None
    pf_control: PFControl | None = None
    pi_control: PIControl | None = None
    inverter_efficiency: EfficiencyType | None = None
    restrictions: Capacity | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add PV to the network."""
        if self.general.guid in network.pvs:
            logger.critical("PV %s already exists, overwriting", self.general.guid)
        network.pvs[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the pv to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.inverter:
            lines.append(f"#Inverter {self.inverter.serialize()}")

        if self.q_control:
            lines.append(f"#QControl {self.q_control.serialize()}")

        if self.pu_control:
            lines.append(f"#P(U)Control {self.pu_control.serialize()}")

        if self.pf_control:
            lines.append(f"#P(f)Control {self.pf_control.serialize()}")

        if self.pi_control:
            lines.append(f"#P(I)Control {self.pi_control.serialize()}")

        if self.efficiency_type:
            lines.append(f"#EfficiencyType {self.efficiency_type.serialize()}")

        if self.harmonics_type:
            lines.append(f"#HarmonicsType {self.harmonics_type.serialize()}")

        if self.inverter_efficiency:
            lines.append(f"#InverterRendement {self.inverter_efficiency.serialize()}")

        if self.restrictions:
            lines.append(f"#Restriction {self.restrictions.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> PVMV:
        """Deserialization of the PV from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TPvMS: The deserialized PV

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        inverter_data = data.get("inverter", [{}])[0] if data.get("inverter") else {}
        inverter = cls.Inverter.deserialize(inverter_data)

        efficiency_type_data = data.get("efficiencyType", [{}])[0] if data.get("efficiencyType") else {}
        efficiency_type = None
        if efficiency_type_data:
            from .shared import EfficiencyType

            efficiency_type = EfficiencyType.deserialize(efficiency_type_data)

        harmonics_type_data = data.get("harmonicsType", [{}])[0] if data.get("harmonicsType") else {}
        harmonics_type = None
        if harmonics_type_data:
            from pyptp.elements.lv.shared import HarmonicsType

            harmonics_type = HarmonicsType.deserialize(harmonics_type_data)

        qcontrol_data = data.get("Qcontrol", [{}])[0] if data.get("Qcontrol") else {}
        qcontrol = None
        if qcontrol_data:
            from .shared import QControl

            qcontrol = QControl.deserialize(qcontrol_data)

        pucontrol_data = data.get("PUcontrol", [{}])[0] if data.get("PUcontrol") else {}
        pucontrol = None
        if pucontrol_data:
            pucontrol = cls.PUControl.deserialize(pucontrol_data)

        pfcontrol_data = data.get("PFcontrol", [{}])[0] if data.get("PFcontrol") else {}
        pfcontrol = None
        if pfcontrol_data:
            pfcontrol = cls.PFControl.deserialize(pfcontrol_data)

        picontrol_data = data.get("PIcontrol", [{}])[0] if data.get("PIcontrol") else {}
        picontrol = None
        if picontrol_data:
            picontrol = cls.PIControl.deserialize(picontrol_data)

        inverter_rendement_data = data.get("InverterRendement", [{}])[0] if data.get("InverterRendement") else {}
        inverter_rendement = None
        if inverter_rendement_data:
            from .shared import EfficiencyType

            inverter_rendement = EfficiencyType.deserialize(inverter_rendement_data)

        restrictions_data = data.get("restrictions", [{}])[0] if data.get("restrictions") else {}
        restrictions = None
        if restrictions_data:
            restrictions = cls.Capacity.deserialize(restrictions_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            inverter=inverter,
            efficiency_type=efficiency_type,
            harmonics_type=harmonics_type,
            q_control=qcontrol,
            pu_control=pucontrol,
            pf_control=pfcontrol,
            pi_control=picontrol,
            inverter_efficiency=inverter_rendement,
            restrictions=restrictions,
        )
