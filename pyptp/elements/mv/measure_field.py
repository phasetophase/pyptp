"""Measure Field (Secondary)."""

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
    write_quote_string_no_skip,
    write_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.mv.presentations import SecondaryPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class MeasureFieldMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a measure field (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a measure field."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: int = optional_field(0)
        variant: bool = False
        name: str = string_field()
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        side: int = 1
        is_voltage_measure_transformer_present: bool = False
        voltage_measure_transformer_function: str = string_field()
        voltage_measure_transformer_type: str = string_field()

        is_current_measure_transformer1_present: bool = False
        current_measure_transformer1_function: str = string_field()
        current_measure_transformer1_type: str = string_field()

        is_current_measure_transformer2_present: bool = False
        current_measure_transformer2_function: str = string_field()
        current_measure_transformer2_type: str = string_field()

        is_current_measure_transformer3_present: bool = False
        current_measure_transformer3_function: str = string_field()
        current_measure_transformer3_type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name),
                write_guid("InObject", self.in_object) if self.in_object != NIL_GUID else "",
                write_integer_no_skip("Side", self.side),
                write_boolean("VoltageMeasureTransformerPresent", value=self.is_voltage_measure_transformer_present),
                write_quote_string("VoltageMeasureTransformerFunction", self.voltage_measure_transformer_function),
                write_quote_string("VoltageMeasureTransformerType", self.voltage_measure_transformer_type),
                write_boolean("CurrentMeasureTransformer1Present", value=self.is_current_measure_transformer1_present),
                write_quote_string("CurrentMeasureTransformer1Function", self.current_measure_transformer1_function),
                write_quote_string("CurrentMeasureTransformer1Type", self.current_measure_transformer1_type),
                write_boolean("CurrentMeasureTransformer2Present", value=self.is_current_measure_transformer2_present),
                write_quote_string("CurrentMeasureTransformer2Function", self.current_measure_transformer2_function),
                write_quote_string("CurrentMeasureTransformer2Type", self.current_measure_transformer2_type),
                write_boolean("CurrentMeasureTransformer3Present", value=self.is_current_measure_transformer3_present),
                write_quote_string("CurrentMeasureTransformer3Function", self.current_measure_transformer3_function),
                write_quote_string("CurrentMeasureTransformer3Type", self.current_measure_transformer3_type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                is_voltage_measure_transformer_present=data.get("VoltageMeasureTransformerPresent", False),
                voltage_measure_transformer_function=data.get("VoltageMeasureTransformerFunction", ""),
                voltage_measure_transformer_type=data.get("VoltageMeasureTransformerType", ""),
                is_current_measure_transformer1_present=data.get("CurrentMeasureTransformer1Present", False),
                current_measure_transformer1_function=data.get("CurrentMeasureTransformer1Function", ""),
                current_measure_transformer1_type=data.get("CurrentMeasureTransformer1Type", ""),
                is_current_measure_transformer2_present=data.get("CurrentMeasureTransformer2Present", False),
                current_measure_transformer2_function=data.get("CurrentMeasureTransformer2Function", ""),
                current_measure_transformer2_type=data.get("CurrentMeasureTransformer2Type", ""),
                is_current_measure_transformer3_present=data.get("CurrentMeasureTransformer3Present", False),
                current_measure_transformer3_function=data.get("CurrentMeasureTransformer3Function", ""),
                current_measure_transformer3_type=data.get("CurrentMeasureTransformer3Type", ""),
            )

    @dataclass_json
    @dataclass
    class VoltageMeasureTransformerType(DataClassJsonMixin):
        """VoltageMeasureTransformerType."""

        transfer_ratio: str = string_field()
        transformer_class: str = string_field()
        """Accuracy class of the voltage measuring transformer."""
        power: float = 0.0
        """Rated power of the voltage measuring transformer in VA."""

        def serialize(self) -> str:
            """Serialize VoltageMeasureTransformerType properties."""
            return serialize_properties(
                write_quote_string("TransferRatio", self.transfer_ratio),
                write_quote_string("Class", self.transformer_class),
                write_double("Power", self.power),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldMV.VoltageMeasureTransformerType:
            """Deserialize VoltageMeasureTransformerType properties."""
            return cls(
                transfer_ratio=data.get("TransferRatio", ""),
                transformer_class=data.get("Class", ""),
                power=data.get("Power", 0.0),
            )

    @dataclass_json
    @dataclass
    class CurrentMeasureTransformer1Type(DataClassJsonMixin):
        """CurrentMeasureTransformer1Type."""

        transfer_ratio: str = string_field()
        transformer_class: str = string_field()
        """Accuracy class of the current measuring transformer."""
        power: float = 0.0
        """Rated power of the current measuring transformer in VA."""
        inom: float = 0.0
        """Rated current of the current measurement transformer in A."""
        ik_dynamic: float = 0.0
        """Dynamic short-circuit current in kA."""
        ik_thermal: float = 0.0
        """Thermal short-circuit current in kA."""
        t_thermal: float = 0.0
        """Thermal short-circuit duration in s."""

        def serialize(self) -> str:
            """Serialize CurrentMeasureTransformer1Type properties."""
            return serialize_properties(
                write_quote_string("TransferRatio", self.transfer_ratio),
                write_quote_string("Class", self.transformer_class),
                write_double("Power", self.power),
                write_double("Inom", self.inom),
                write_double("IkDynamic", self.ik_dynamic),
                write_double("IkThermal", self.ik_thermal),
                write_double("TThermal", self.t_thermal),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldMV.CurrentMeasureTransformer1Type:
            """Deserialize CurrentMeasureTransformer1Type properties."""
            return cls(
                transfer_ratio=data.get("TransferRatio", ""),
                transformer_class=data.get("Class", ""),
                power=data.get("Power", 0.0),
                inom=data.get("Inom", 0.0),
                ik_dynamic=data.get("IkDynamic", 0.0),
                ik_thermal=data.get("IkThermal", 0.0),
                t_thermal=data.get("TThermal", 0.0),
            )

    @dataclass_json
    @dataclass
    class CurrentMeasureTransformer2Type(DataClassJsonMixin):
        """CurrentMeasureTransformer2Type."""

        transfer_ratio: str = string_field()
        transformer_class: str = string_field()
        """Accuracy class of the current measuring transformer."""
        power: float = 0.0
        """Rated power of the current measuring transformer in VA."""
        inom: float = 0.0
        """Rated current of the current measurement transformer in A."""
        ik_dynamic: float = 0.0
        """Dynamic short-circuit current in kA."""
        ik_thermal: float = 0.0
        """Thermal short-circuit current in kA."""
        t_thermal: float = 0.0
        """Thermal short-circuit duration in s."""

        def serialize(self) -> str:
            """Serialize CurrentMeasureTransformer2Type properties."""
            return serialize_properties(
                write_quote_string("TransferRatio", self.transfer_ratio),
                write_quote_string("Class", self.transformer_class),
                write_double("Power", self.power),
                write_double("Inom", self.inom),
                write_double("IkDynamic", self.ik_dynamic),
                write_double("IkThermal", self.ik_thermal),
                write_double("TThermal", self.t_thermal),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldMV.CurrentMeasureTransformer2Type:
            """Deserialize CurrentMeasureTransformer2Type properties."""
            return cls(
                transfer_ratio=data.get("TransferRatio", ""),
                transformer_class=data.get("Class", ""),
                power=data.get("Power", 0.0),
                inom=data.get("Inom", 0.0),
                ik_dynamic=data.get("IkDynamic", 0.0),
                ik_thermal=data.get("IkThermal", 0.0),
                t_thermal=data.get("TThermal", 0.0),
            )

    @dataclass_json
    @dataclass
    class CurrentMeasureTransformer3Type(DataClassJsonMixin):
        """CurrentMeasureTransformer3Type."""

        transfer_ratio: str = string_field()
        transformer_class: str = string_field()
        """Accuracy class of the current measuring transformer."""
        power: float = 0.0
        """Rated power of the current measuring transformer in VA."""
        inom: float = 0.0
        """Rated current of the current measurement transformer in A."""
        ik_dynamic: float = 0.0
        """Dynamic short-circuit current in kA."""
        ik_thermal: float = 0.0
        """Thermal short-circuit current in kA."""
        t_thermal: float = 0.0
        """Thermal short-circuit duration in s."""

        def serialize(self) -> str:
            """Serialize CurrentMeasureTransformer3Type properties."""
            return serialize_properties(
                write_quote_string("TransferRatio", self.transfer_ratio),
                write_quote_string("Class", self.transformer_class),
                write_double("Power", self.power),
                write_double("Inom", self.inom),
                write_double("IkDynamic", self.ik_dynamic),
                write_double("IkThermal", self.ik_thermal),
                write_double("TThermal", self.t_thermal),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldMV.CurrentMeasureTransformer3Type:
            """Deserialize CurrentMeasureTransformer3Type properties."""
            return cls(
                transfer_ratio=data.get("TransferRatio", ""),
                transformer_class=data.get("Class", ""),
                power=data.get("Power", 0.0),
                inom=data.get("Inom", 0.0),
                ik_dynamic=data.get("IkDynamic", 0.0),
                ik_thermal=data.get("IkThermal", 0.0),
                t_thermal=data.get("TThermal", 0.0),
            )

    @dataclass_json
    @dataclass
    class Measurement(DataClassJsonMixin):
        """Measurement."""

        text: str = string_field()

        def serialize(self) -> str:
            """Serialize Measurement properties."""
            return serialize_properties(
                write_string_no_skip("Text", self.text),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldMV.Measurement:
            """Deserialize Measurement properties."""
            return cls(
                text=data.get("Text", ""),
            )

    @dataclass_json
    @dataclass
    class MeasurementsFile(DataClassJsonMixin):
        """MeasurementsFile."""

        file_name: str = string_field()
        column: str = string_field()

        def serialize(self) -> str:
            """Serialize MeasurementsFile properties."""
            return serialize_properties(
                write_quote_string_no_skip("FileName", self.file_name),
                write_quote_string_no_skip("Column", self.column),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldMV.MeasurementsFile:
            """Deserialize MeasurementsFile properties."""
            return cls(
                file_name=data.get("FileName", ""),
                column=data.get("Column", ""),
            )

    general: General
    presentations: list[SecondaryPresentation]
    voltage_measure_transformer_type: VoltageMeasureTransformerType | None = None
    current_measure_transformer1_type: CurrentMeasureTransformer1Type | None = None
    current_measure_transformer2_type: CurrentMeasureTransformer2Type | None = None
    current_measure_transformer3_type: CurrentMeasureTransformer3Type | None = None
    measurements: list[Measurement] = field(default_factory=list)
    measurementfiles: list[MeasurementsFile] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Will add measure field to the network."""
        if self.general.guid in network.measure_fields:
            logger.critical("Measure Field %s already exists, overwriting", self.general.guid)
        network.measure_fields[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the measure field to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.general.is_voltage_measure_transformer_present:
            if self.voltage_measure_transformer_type:
                lines.append(f"#VoltageMeasureTransformerType {self.voltage_measure_transformer_type.serialize()}")
            else:
                lines.append("#VoltageMeasureTransformerType ")

        if self.general.is_current_measure_transformer1_present:
            if self.current_measure_transformer1_type:
                lines.append(f"#CurrentMeasureTransformer1Type {self.current_measure_transformer1_type.serialize()}")
            else:
                lines.append("#CurrentMeasureTransformer1Type ")
        if self.general.is_current_measure_transformer2_present:
            if self.current_measure_transformer2_type:
                lines.append(f"#CurrentMeasureTransformer2Type {self.current_measure_transformer2_type.serialize()}")
            else:
                lines.append("#CurrentMeasureTransformer2Type ")
        if self.general.is_current_measure_transformer3_present:
            if self.current_measure_transformer3_type:
                lines.append(f"#CurrentMeasureTransformer3Type {self.current_measure_transformer3_type.serialize()}")
            else:
                lines.append("#CurrentMeasureTransformer3Type ")

        lines.extend(f"#Measurement {measurement.serialize()}" for measurement in self.measurements)

        lines.extend(f"#MeasurementsFile {measurement_file.serialize()}" for measurement_file in self.measurementfiles)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> MeasureFieldMV:
        """Deserialization of the measure field from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TMeasureFieldMS: The deserialized measure field

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        voltage_measure_transformer_type = None
        if data.get("voltageMeasureTransformerType"):
            voltage_measure_transformer_type = cls.VoltageMeasureTransformerType.deserialize(
                data["voltageMeasureTransformerType"][0],
            )

        current_measure_transformer1_type = None
        if data.get("currentMeasureTransformer1Type"):
            current_measure_transformer1_type = cls.CurrentMeasureTransformer1Type.deserialize(
                data["currentMeasureTransformer1Type"][0],
            )

        current_measure_transformer2_type = None
        if data.get("currentMeasureTransformer2Type"):
            current_measure_transformer2_type = cls.CurrentMeasureTransformer2Type.deserialize(
                data["currentMeasureTransformer2Type"][0],
            )

        current_measure_transformer3_type = None
        if data.get("currentMeasureTransformer3Type"):
            current_measure_transformer3_type = cls.CurrentMeasureTransformer3Type.deserialize(
                data["currentMeasureTransformer3Type"][0],
            )

        measurements_data = data.get("measurements", [])
        measurements = []
        for meas_data in measurements_data:
            measurement = cls.Measurement.deserialize(meas_data)
            measurements.append(measurement)

        measurement_files_data = data.get("measurementfiles", [])
        measurement_files = []
        for file_data in measurement_files_data:
            measurement_file = cls.MeasurementsFile.deserialize(file_data)
            measurement_files.append(measurement_file)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import SecondaryPresentation

            presentation = SecondaryPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            voltage_measure_transformer_type=voltage_measure_transformer_type,
            current_measure_transformer1_type=current_measure_transformer1_type,
            current_measure_transformer2_type=current_measure_transformer2_type,
            current_measure_transformer3_type=current_measure_transformer3_type,
            measurements=measurements,
            measurementfiles=measurement_files,
        )
