"""Circuit Breaker (Secondary)."""

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
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_double,
    write_double_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

from .presentations import SecundairPresentation
from .shared import Fields

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass
class CircuitBreakerLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a circuit breaker (LV)."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a circuit breaker."""

        guid: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        name: str = string_field()
        """Circuit breaker name."""
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """GUID of the containing object."""
        side: int = 1
        """Side of the branch (1 or 2)."""
        standardizable: bool = True
        type: str = string_field()
        """Circuit breaker type name."""
        current_protection1_present: bool = False
        """First overcurrent protection present."""
        current_protection1_type: str = string_field()
        """Type of first overcurrent protection."""
        voltage_protection_present: bool = False
        """Voltage protection present."""
        voltage_protection_type: str = string_field()
        """Type of voltage protection."""
        earth_fault_protection1_present: bool = False
        """First earth fault protection present."""

        def serialize(self) -> str:
            """Serialize General properties to GNF format."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_quote_string("Name", self.name),
                (write_guid_no_skip("InObject", self.in_object) if self.in_object is not NIL_GUID else ""),
                write_integer("Side", self.side),
                write_boolean("Standardizable", value=self.standardizable),
                write_quote_string("CircuitBreakerType", self.type),
                write_boolean("CurrentProtection1Present", value=self.current_protection1_present),
                write_quote_string("CurrentProtection1Type", self.current_protection1_type),
                write_boolean("VoltageProtectionPresent", value=self.voltage_protection_present),
                write_quote_string("VoltageProtectionType", self.voltage_protection_type),
                write_boolean(
                    "EarthFaultProtection1Present",
                    value=self.earth_fault_protection1_present,
                ),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CircuitBreakerLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                name=data.get("Name", ""),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                standardizable=data.get("Standardizable", True),
                type=data.get("CircuitBreakerType", ""),
                current_protection1_present=data.get("CurrentProtection1Present", False),
                current_protection1_type=data.get("CurrentProtection1Type", ""),
                voltage_protection_present=data.get("VoltageProtectionPresent", False),
                voltage_protection_type=data.get("VoltageProtectionType", ""),
                earth_fault_protection1_present=data.get("EarthFaultProtection1Present", False),
            )

    general: General
    presentations: list[SecundairPresentation]
    fields: Fields | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add circuit breaker to the network."""
        if self.general.guid in network.circuit_breakers:
            logger.critical("Circuit Breaker %s already exists, overwriting", self.general.guid)
        network.circuit_breakers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the circuit breaker to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.fields:
            lines.append(f"#Fields {self.fields.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> CircuitBreakerLV:
        """Deserialization of the circuit breaker from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TCircuitBreakerLS: The deserialized circuit breaker

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        fields_data = data.get("fields", [{}])[0] if data.get("fields") else None
        fields = Fields.deserialize(fields_data) if fields_data else None

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            presentation = SecundairPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            fields=fields,
        )
