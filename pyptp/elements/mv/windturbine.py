"""Windturbine (Element)."""

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
    from pyptp.elements.mv.presentations import ElementPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class WindTurbineMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a windturbine or wind park (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a windturbine."""

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
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        not_preferred: bool = False
        number_of: int = 1
        wind_speed_or_pref: str = "v"
        wind_speed: float = 14.0
        pref: float = 0.0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        axis_height: float = 30.0
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node) if self.node != NIL_GUID else "",
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date) if self.mutation_date != 0 else "",
                write_integer("RevisionDate", self.revision_date) if self.revision_date != 0 else "",
                write_boolean("Variant", value=self.variant),
                write_quote_string_no_skip("Name", self.name),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string("FieldName", self.field_name),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_integer_no_skip("NumberOf", self.number_of),
                write_quote_string_no_skip("WindSpeedOrPref", self.wind_speed_or_pref),
                write_double_no_skip("WindSpeed", self.wind_speed),
                write_double("Pref", self.pref),
                write_guid_no_skip("Profile", self.profile),
                write_double_no_skip("AxisHeight", self.axis_height),
                write_quote_string("WindTurbineType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> WindTurbineMV.General:
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
                number_of=data.get("NumberOf", 1),
                wind_speed_or_pref=data.get("WindSpeedOrPref", "v"),
                wind_speed=data.get("WindSpeed", 14.0),
                pref=data.get("Pref", 0.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                axis_height=data.get("AxisHeight", 30.0),
                type=data.get("WindTurbineType", ""),
            )

    @dataclass_json
    @dataclass
    class WindTurbineType(DataClassJsonMixin):
        """Electrotechnical properties of the windturbine."""

        pnom: float = 0.0
        unom: float = 0.0
        inom: float = 0.0
        ik_inom: float = 1.0
        R_X: float = 0.1
        wind_speed_cut_in: float = 3.0
        wind_speed_nom: float = 14.0
        wind_speed_cutting_out: float = 25.0
        wind_speed_cutted_out: float = 30.0

        def serialize(self) -> str:
            """Serialize WindTurbineType properties."""
            return serialize_properties(
                write_double("Pnom", self.pnom),
                write_double("Unom", self.unom),
                write_double("Inom", self.inom),
                write_double("Ik/Inom", self.ik_inom, skip=1.0),
                write_double_no_skip("R/X", self.R_X),
                write_double("WindSpeedCutIn", self.wind_speed_cut_in),
                write_double("WindSpeedNom", self.wind_speed_nom),
                write_double("WindSpeedCuttingOut", self.wind_speed_cutting_out),
                write_double("WindSpeedCuttedOut", self.wind_speed_cutted_out),
            )

        @classmethod
        def deserialize(cls, data: dict) -> WindTurbineMV.WindTurbineType:
            """Deserialize WindTurbineType properties."""
            return cls(
                pnom=data.get("Pnom", 0.0),
                unom=data.get("Unom", 0.0),
                inom=data.get("Inom", 0.0),
                ik_inom=data.get("Ik/Inom", 1.0),
                R_X=data.get("R/X", 0.1),
                wind_speed_cut_in=data.get("WindSpeedCutIn", 3.0),
                wind_speed_nom=data.get("WindSpeedNom", 14.0),
                wind_speed_cutting_out=data.get("WindSpeedCuttingOut", 25.0),
                wind_speed_cutted_out=data.get("WindSpeedCuttedOut", 30.0),
            )

    @dataclass_json
    @dataclass
    class QControl(DataClassJsonMixin):
        """QControl."""

        sort: int = 0
        cos_ref: float = 1.0
        no_p_no_q: bool = True
        input1: float = 0.95
        output1: float = 0.5
        input2: float = 1.0
        output2: float = 0.0
        input3: float = 1.0
        output3: float = 0.0
        input4: float = 1.03
        output4: float = -0.5
        input5: float = 1.05
        output5: float = -0.5

        def serialize(self) -> str:
            """Serialize QControl properties."""
            return serialize_properties(
                write_integer("Sort", self.sort),
                write_double_no_skip("CosRef", self.cos_ref),
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
        def deserialize(cls, data: dict) -> WindTurbineMV.QControl:
            """Deserialize QControl properties."""
            return cls(
                sort=data.get("Sort", 0),
                cos_ref=data.get("CosRef", 1.0),
                no_p_no_q=data.get("NoPNoQ", True),
                input1=data.get("Input1", 0.95),
                output1=data.get("Output1", 0.5),
                input2=data.get("Input2", 1.0),
                output2=data.get("Output2", 0.0),
                input3=data.get("Input3", 1.0),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 1.03),
                output4=data.get("Output4", -0.5),
                input5=data.get("Input5", 1.05),
                output5=data.get("Output5", -0.5),
            )

    @dataclass_json
    @dataclass
    class PUControl(DataClassJsonMixin):
        """PU Control."""

        input1: float = 0.95
        output1: float = 1.0
        input2: float = 1.0
        output2: float = 1.0
        input3: float = 1.0
        output3: float = 1.0
        input4: float = 1.047
        output4: float = 1.0
        input5: float = 1.057
        output5: float = 0.0

        def serialize(self) -> str:
            """Serialize PUControl properties."""
            return serialize_properties(
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
        def deserialize(cls, data: dict) -> WindTurbineMV.PUControl:
            """Deserialize PUControl properties."""
            return cls(
                input1=data.get("Input1", 0.95),
                output1=data.get("Output1", 1.0),
                input2=data.get("Input2", 1.0),
                output2=data.get("Output2", 1.0),
                input3=data.get("Input3", 1.0),
                output3=data.get("Output3", 1.0),
                input4=data.get("Input4", 1.047),
                output4=data.get("Output4", 1.0),
                input5=data.get("Input5", 1.057),
                output5=data.get("Output5", 0.0),
            )

    @dataclass_json
    @dataclass
    class PfControl(DataClassJsonMixin):
        """Power(frequency) control."""

        input1: float = 50.0
        output1: float = 1.0
        input2: float = 50.2
        output2: float = 1.0
        input3: float = 51.5
        output3: float = 0.48
        input4: float = 0.0
        output4: float = 0.0
        input5: float = 0.0
        output5: float = 0.0

        def serialize(self) -> str:
            """Serialize PfControl properties."""
            return serialize_properties(
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
        def deserialize(cls, data: dict) -> WindTurbineMV.PfControl:
            """Deserialize PfControl properties."""
            return cls(
                input1=data.get("Input1", 50.0),
                output1=data.get("Output1", 1.0),
                input2=data.get("Input2", 50.2),
                output2=data.get("Output2", 1.0),
                input3=data.get("Input3", 51.5),
                output3=data.get("Output3", 0.48),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
            )

    @dataclass_json
    @dataclass
    class PIControl(DataClassJsonMixin):
        """Power(current) Control."""

        input1: float = 0.0
        output1: float = 1.0
        input2: float = 0.95
        output2: float = 1.0
        input3: float = 1.05
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
        def deserialize(cls, data: dict) -> WindTurbineMV.PIControl:
            """Deserialize PIControl properties."""
            measure_field1 = data.get("MeasureField1")
            measure_field2 = data.get("MeasureField2")
            measure_field3 = data.get("MeasureField3")

            return cls(
                input1=data.get("Input1", 0.0),
                output1=data.get("Output1", 1.0),
                input2=data.get("Input2", 0.95),
                output2=data.get("Output2", 1.0),
                input3=data.get("Input3", 1.05),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
                measure_field1=decode_guid(measure_field1) if measure_field1 else None,
                measure_field2=decode_guid(measure_field2) if measure_field2 else None,
                measure_field3=decode_guid(measure_field3) if measure_field3 else None,
            )

    @dataclass_json
    @dataclass
    class Restriction(DataClassJsonMixin):
        """Restriction."""

        sort: str = string_field()
        begin_date: int = 0
        end_date: int = 0
        begin_time: float = 0.0
        end_time: float = 0.0
        p_max: float = 0.0

        def serialize(self) -> str:
            """Serialize Restriction properties."""
            return serialize_properties(
                write_quote_string_no_skip("Sort", self.sort),
                write_integer_no_skip("BeginDate", self.begin_date),
                write_integer_no_skip("EndDate", self.end_date),
                write_double_no_skip("BeginTime", self.begin_time),
                write_double_no_skip("EndTime", self.end_time),
                write_double_no_skip("Pmax", self.p_max),
            )

        @classmethod
        def deserialize(cls, data: dict) -> WindTurbineMV.Restriction:
            """Deserialize Restriction properties."""
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
    type: WindTurbineType
    q_control: QControl | None = None
    pu_control: PUControl | None = None
    pf_control: PfControl | None = None
    pi_control: PIControl | None = None
    restriction: Restriction | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add windturbine to the network."""
        if self.general.guid in network.windturbines:
            logger.critical("Windturbine %s already exists, overwriting", self.general.guid)
        network.windturbines[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the windturbine to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        if self.type:
            lines.append(f"#WindTurbineType {self.type.serialize()}")

        if self.q_control:
            lines.append(f"#QControl {self.q_control.serialize()}")

        if self.pu_control:
            lines.append(f"#P(U)Control {self.pu_control.serialize()}")

        if self.pf_control:
            lines.append(f"#P(f)Control {self.pf_control.serialize()}")

        if self.pi_control:
            lines.append(f"#P(I)Control {self.pi_control.serialize()}")

        if self.restriction:
            lines.append(f"#Restriction {self.restriction.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> WindTurbineMV:
        """Deserialization of the windturbine from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TWindTurbineMS: The deserialized windturbine

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        wind_turbine_type_data = data.get("windTurbineType", [{}])[0] if data.get("windTurbineType") else {}
        wind_turbine_type = cls.WindTurbineType.deserialize(wind_turbine_type_data)

        qcontrol_data = data.get("qControl", [{}])[0] if data.get("qControl") else {}
        qcontrol = None
        if qcontrol_data:
            qcontrol = cls.QControl.deserialize(qcontrol_data)

        pucontrol_data = data.get("puControl", [{}])[0] if data.get("puControl") else {}
        pucontrol = None
        if pucontrol_data:
            pucontrol = cls.PUControl.deserialize(pucontrol_data)

        pfcontrol_data = data.get("pfControl", [{}])[0] if data.get("pfControl") else {}
        pfcontrol = None
        if pfcontrol_data:
            pfcontrol = cls.PfControl.deserialize(pfcontrol_data)

        picontrol_data = data.get("piControl", [{}])[0] if data.get("piControl") else {}
        picontrol = None
        if picontrol_data:
            picontrol = cls.PIControl.deserialize(picontrol_data)

        restriction_data = data.get("restriction", [{}])[0] if data.get("restriction") else {}
        restriction = None
        if restriction_data:
            restriction = cls.Restriction.deserialize(restriction_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from pyptp.elements.mv.presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=wind_turbine_type,
            q_control=qcontrol,
            pu_control=pucontrol,
            pf_control=pfcontrol,
            pi_control=picontrol,
            restriction=restriction,
        )
