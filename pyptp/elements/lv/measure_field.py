"""Measure Field (Secondary)."""

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
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import SecundairPresentation


@dataclass
class MeasureFieldLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a measure field (LV)."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a measure field."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        name: str = string_field()
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        side: int = 1
        standardizable: bool = False
        voltage_measure_transformer_present: bool = False
        voltage_measure_transformer_function: str = string_field()
        current_measure_transformer1_present: bool = False
        current_measure_transformer1_function: str = string_field()
        current_measure_transformer2_present: bool = False
        current_measure_transformer2_function: str = string_field()
        current_measure_transformer3_present: bool = False
        current_measure_transformer3_function: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            props = []
            props.append(f"GUID:'{{{str(self.guid).upper()}}}'")
            props.append(f"CreationTime:{self.creation_time}")
            if self.mutation_date != 0:
                props.append(f"MutationDate:{self.mutation_date}")
            if self.revision_date != 0.0:
                props.append(f"RevisionDate:{self.revision_date}")
            props.append(f"Name:'{self.name}'")
            if self.in_object is not NIL_GUID:
                props.append(f"InObject:'{{{str(self.in_object).upper()}}}'")
            props.append(f"Side:{self.side}")
            props.append(f"Standardizable:{str(self.standardizable).lower()}")
            props.append(f"VoltageMeasureTransformerPresent:{str(self.voltage_measure_transformer_present).lower()}")
            props.append(f"VoltageMeasureTransformerFunction:'{self.voltage_measure_transformer_function}'")
            props.append(f"CurrentMeasureTransformer1Present:{str(self.current_measure_transformer1_present).lower()}")
            props.append(f"CurrentMeasureTransformer1Function:'{self.current_measure_transformer1_function}'")
            props.append(f"CurrentMeasureTransformer2Present:{str(self.current_measure_transformer2_present).lower()}")
            props.append(f"CurrentMeasureTransformer2Function:'{self.current_measure_transformer2_function}'")
            props.append(f"CurrentMeasureTransformer3Present:{str(self.current_measure_transformer3_present).lower()}")
            props.append(f"CurrentMeasureTransformer3Function:'{self.current_measure_transformer3_function}'")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                name=data.get("Name", ""),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                standardizable=data.get("Standardizable", False),
                voltage_measure_transformer_present=data.get("VoltageMeasureTransformerPresent", False),
                voltage_measure_transformer_function=data.get("VoltageMeasureTransformerFunction", ""),
                current_measure_transformer1_present=data.get("CurrentMeasureTransformer1Present", False),
                current_measure_transformer1_function=data.get("CurrentMeasureTransformer1Function", ""),
                current_measure_transformer2_present=data.get("CurrentMeasureTransformer2Present", False),
                current_measure_transformer2_function=data.get("CurrentMeasureTransformer2Function", ""),
                current_measure_transformer3_present=data.get("CurrentMeasureTransformer3Present", False),
                current_measure_transformer3_function=data.get("CurrentMeasureTransformer3Function", ""),
            )

    @dataclass
    class MeasurementsFile(DataClassJsonMixin):
        """Reference to measurement files."""

        file_name: str = string_field()
        column: str = string_field()

        def serialize(self) -> str:
            """Serialize MeasurementsFile properties."""
            props = []
            props.append(f"FileName:'{self.file_name}'")
            props.append(f"Column:'{self.column}'")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> MeasureFieldLV.MeasurementsFile:
            """Deserialize MeasurementsFile properties."""
            return cls(
                file_name=data.get("FileName", ""),
                column=data.get("Column", ""),
            )

    general: General
    presentations: list[SecundairPresentation]
    measurement_file: MeasurementsFile | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add measure field to the network."""
        if self.general.guid in network.measure_fields:
            logger.critical("Measure Field %s already exists, overwriting", self.general.guid)
        network.measure_fields[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the measure field to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.measurement_file:
            lines.append(f"#MeasurementFile {self.measurement_file.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> MeasureFieldLV:
        """Deserialization of the measure field from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TMeasureFieldLS: The deserialized measure field

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        measurement_file = None
        if data.get("measurementFile"):
            measurement_file = cls.MeasurementsFile.deserialize(data["measurementFile"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import SecundairPresentation

            presentation = SecundairPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            measurement_file=measurement_file,
        )
