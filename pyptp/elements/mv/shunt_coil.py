"""Shunt Coil (Element)."""

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
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.mv.presentations import ElementPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class ShuntCoilMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a shunt coil (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a shunt coil."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        name: str = string_field()
        switch_state: int = 0
        field_name: str = string_field()
        """Name of the connection field."""
        failure_frequency: float = 0.0
        """Mean number of occurrences that the coil fails (short circuit) per year."""
        repair_duration: float = 0.0
        """Mean duration of repair or replacement in minutes."""
        maintenance_frequency: float = 0.0
        """Mean number of occurrences that the coil is in maintenance per year."""
        maintenance_duration: float = 0.0
        """Mean duration of maintenance in minutes."""
        maintenance_cancel_duration: float = 0.0
        """Mean duration of cancellation of maintenance in case of emergency in minutes."""
        not_preferred: bool = False
        Q: float = 0.0
        """Reactive power in Mvar."""
        unom: float = 0.0
        """Nominal voltage in kV."""
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """Name of the coil power profile."""
        earthing: int = 0
        """Star point earthing setting (0=no, 1=yes)."""
        re: float = 0.0
        """Earthing resistance with earthed star point in Ohm."""
        xe: float = 0.0
        """Earthing reactance with earthed star point in Ohm."""
        earthing_node: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        """Node with neutral earth connection."""
        voltage_control: bool = False
        """Indicates whether the voltage control has been switched on or off."""
        u_on: float = 0.0
        """Voltage above which the shunt reactor switches off in kV."""
        u_off: float = 0.0
        """Voltage under which the shunt reactor switches on in kV."""

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node) if self.node != NIL_GUID else "",
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
                write_boolean("Variant", value=self.variant),
                write_quote_string_no_skip("Name", self.name),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string_no_skip("FieldName", self.field_name),
                write_double_no_skip("FailureFrequency", self.failure_frequency),
                write_double_no_skip("RepairDuration", self.repair_duration),
                write_double_no_skip("MaintenanceFrequency", self.maintenance_frequency),
                write_double_no_skip("MaintenanceDuration", self.maintenance_duration),
                write_double_no_skip("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_boolean_no_skip("NotPreferred", value=self.not_preferred),
                write_double_no_skip("Q", self.Q),
                write_double_no_skip("Unom", self.unom),
                write_guid("Profile", self.profile, skip=DEFAULT_PROFILE_GUID),
                write_integer_no_skip("Earthing", self.earthing),
                write_double_no_skip("Re", self.re),
                write_double_no_skip("Xe", self.xe),
                write_guid("EarthingNode", self.earthing_node) if self.earthing_node else "",
                write_boolean_no_skip("VoltageControl", value=self.voltage_control),
                write_double_no_skip("Uon", self.u_on),
                write_double_no_skip("Uoff", self.u_off),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ShuntCoilMV.General:
            """Deserialize General properties."""
            earthing_node = data.get("EarthingNode")

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
                Q=data.get("Q", 0.0),
                unom=data.get("Unom", 0.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                earthing=data.get("Earthing", 0),
                re=data.get("Re", 0.0),
                xe=data.get("Xe", 0.0),
                earthing_node=decode_guid(earthing_node) if earthing_node else None,
                voltage_control=data.get("VoltageControl", False),
                u_on=data.get("Uon", 0.0),
                u_off=data.get("Uoff", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]

    def register(self, network: NetworkMV) -> None:
        """Will add shunt coil to the network."""
        if self.general.guid in network.shunt_coils:
            logger.critical("Shunt Coil %s already exists, overwriting", self.general.guid)
        network.shunt_coils[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the shunt coil to the VNF format.

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
    def deserialize(cls, data: dict) -> ShuntCoilMV:
        """Deserialization of the shunt coil from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TShuntCoilMS: The deserialized shunt coil

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
        )
