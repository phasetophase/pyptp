"""Indicator (Secondary)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
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
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.mv.presentations import SecondaryPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class IndicatorMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents an indicator (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for an Indicator."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        name: str = string_field()
        in_object: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        side: int = 1
        phase_current: float | int = 0.0
        phase_direction_sensitive: bool = False
        phase_response_time: float | int = 0.0
        earth_current: float | int = 0.0
        earth_voltage: float | int = 0.0
        earth_response_time: float | int = 0.0
        auto_reset: bool = False
        remote_signaling: bool = False

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name),
                write_guid("InObject", self.in_object) if self.in_object is not None else "",
                write_integer("Side", self.side),
                write_double("PhaseCurrent", self.phase_current),
                write_boolean("PhaseDirectionSensitive", value=self.phase_direction_sensitive),
                write_double("PhaseResponseTime", self.phase_response_time),
                write_double("EarthCurrent", self.earth_current),
                write_double("EarthVoltage", self.earth_voltage),
                write_double("EarthResponseTime", self.earth_response_time),
                write_boolean("AutoReset", value=self.auto_reset),
                write_boolean("RemoteSignaling", value=self.remote_signaling),
            )

        @classmethod
        def deserialize(cls, data: dict) -> IndicatorMV.General:
            """Deserialize General properties."""
            in_object = data.get("InObject")

            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                in_object=decode_guid(in_object) if in_object else None,
                side=data.get("Side", 1),
                phase_current=data.get("PhaseCurrent", 0.0),
                phase_direction_sensitive=data.get("PhaseDirectionSensitive", False),
                phase_response_time=data.get("PhaseResponseTime", 0.0),
                earth_current=data.get("EarthCurrent", 0.0),
                earth_voltage=data.get("EarthVoltage", 0.0),
                earth_response_time=data.get("EarthResponseTime", 0.0),
                auto_reset=data.get("AutoReset", False),
                remote_signaling=data.get("RemoteSignaling", False),
            )

    general: General
    presentations: list[SecondaryPresentation]

    def register(self, network: NetworkMV) -> None:
        """Will add indicator to the network."""
        if self.general.guid in network.indicators:
            logger.critical("Indicator %s already exists, overwriting", self.general.guid)
        network.indicators[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the indicator to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> IndicatorMV:
        """Deserialization of the indicator from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TIndicatorMS: The deserialized indicator

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import SecondaryPresentation

            presentation = SecondaryPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
        )
