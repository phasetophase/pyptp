"""Dynamic Case (Other) [UNSUPPORTED]."""

from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import string_field
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double,
    write_quote_string,
)


@dataclass_json
@dataclass
class DynamicCaseMV:
    """Represents a dynamic case (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a dynamic case."""

        name: str = string_field()
        description: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_quote_string("Name", self.name),
                write_quote_string("Description", self.description),
            )

        @classmethod
        def deserialize(cls, data: dict) -> "DynamicCaseMV.General":
            """Deserialize General properties."""
            return cls(
                name=data.get("Name", ""),
                description=data.get("Description", ""),
            )

    @dataclass_json
    @dataclass
    class DynamicEvent(DataClassJsonMixin):
        """Dynamic Event properties."""

        start_time: float = 0.0
        action: str = string_field()
        vision_object: str = string_field()
        fault_sort: str = string_field()
        ref_sort: str = string_field()
        parameter1: float = 0.0
        parameter2: float = 0.0
        parameter3: float = 0.0

        def serialize(self) -> str:
            """Serialize DynamicEvent properties."""
            return serialize_properties(
                write_double("StartTime", self.start_time),
                write_quote_string("Action", self.action),
                write_quote_string("VisionObject", self.vision_object),
                write_quote_string("FaultSort", self.fault_sort),
                write_quote_string("RefSort", self.ref_sort),
                write_double("Parameter1", self.parameter1),
                write_double("Parameter2", self.parameter2),
                write_double("Parameter3", self.parameter3),
            )

        @classmethod
        def deserialize(cls, data: dict) -> "DynamicCaseMV.DynamicEvent":
            """Deserialize DynamicEvent properties."""
            return cls(
                start_time=data.get("StartTime", 0.0),
                action=data.get("Action", ""),
                vision_object=data.get("VisionObject", ""),
                fault_sort=data.get("FaultSort", ""),
                ref_sort=data.get("RefSort", ""),
                parameter1=data.get("Parameter1", 0.0),
                parameter2=data.get("Parameter2", 0.0),
                parameter3=data.get("Parameter3", 0.0),
            )

    general: General
    dynamic_events: list[DynamicEvent]

    def serialize(self) -> str:
        """Serialize the dynamic case to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.extend(f"#DynamicEvent {dynamic_event.serialize()}" for dynamic_event in self.dynamic_events)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> "DynamicCaseMV":
        """Deserialization of the dynamic case from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            "TDynamicCaseMS": The deserialized dynamic case

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        dynamic_events_data = data.get("dynamicEvents", [])
        dynamic_events = []
        for event_data in dynamic_events_data:
            dynamic_event = cls.DynamicEvent.deserialize(event_data)
            dynamic_events.append(dynamic_event)

        return cls(
            general=general,
            dynamic_events=dynamic_events,
        )
