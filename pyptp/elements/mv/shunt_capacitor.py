"""Shunt Capacitor (Element)."""

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
class ShuntCapacitorMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a shunt capacitor (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a shunt capacitor."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """GUID of the node to which the shunt capacitor is connected."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        """Unique identifier for the shunt capacitor."""

        creation_time: float = 0.0
        """Timestamp when the element was created."""

        mutation_date: int = 0
        """Date when the element was last modified."""

        revision_date: int = 0
        """Date when the element was last revised."""

        variant: bool = False
        """Indicates if this is a variant configuration."""

        name: str = string_field()
        """Name of the shunt capacitor."""

        switch_state: int = 0
        """Switch state: 1=closed (capacitor energized), 0=open (capacitor de-energized)."""

        field_name: str = string_field()
        """Name of the connection field."""

        failure_frequency: float = 0.0
        """Mean number of occurrences that the capacitor fails (short circuit) per year."""

        repair_duration: float = 0.0
        """Mean repair duration in hours per year."""

        maintenance_frequency: float = 0.0
        """Mean number of occurrences that the capacitor is in maintenance per year."""

        maintenance_duration: float = 0.0
        """Mean maintenance duration in hours per year."""

        maintenance_cancel_duration: float = 0.0
        """Mean duration of maintenance cancellation in hours per year."""

        not_preferred: bool = False
        """Indicates if this capacitor is not preferred for switching operations."""

        Q: float = 0.0
        """Reactive power in Mvar (three-phase)."""

        unom: float = 0.0
        """Nominal voltage in kV (defaults to node voltage if not specified)."""

        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """GUID of the load profile for time-varying behavior."""

        earthing: bool = False
        """Indicates if the capacitor neutral point is earthed."""

        re: float = 0.0
        """Earthing resistance in Ohm (with earthed star point)."""

        xe: float = 0.0
        """Earthing reactance in Ohm (with earthed star point)."""

        earthing_node: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        """GUID of external earthing node (if neutral connected elsewhere)."""

        voltage_control: bool = False
        """Enables automatic voltage-based switching control."""

        u_on: float = 0.0
        """Voltage in kV under which the capacitor switches on (voltage control)."""

        u_off: float = 0.0
        """Voltage in kV above which the capacitor switches off (voltage control)."""

        only_during_motorstart: bool = False
        """Capacitor only switches during motor start operations."""

        passive_filter_frequency: float = 0.0
        """Harmonic filter frequency in Hz for passive filtering applications."""

        passive_filter_quality_factor: float = 0.0
        """Quality factor (Q) for passive harmonic filter design."""

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
                write_boolean_no_skip("Earthing", value=self.earthing),
                write_double_no_skip("Re", self.re),
                write_double_no_skip("Xe", self.xe),
                write_guid("EarthingNode", self.earthing_node) if self.earthing_node else "",
                write_boolean_no_skip("VoltageControl", value=self.voltage_control),
                write_double_no_skip("Uon", self.u_on),
                write_double_no_skip("Uoff", self.u_off),
                write_boolean_no_skip("OnlyDuringMotorstart", value=self.only_during_motorstart),
                write_double_no_skip("PassiveFilterFrequency", self.passive_filter_frequency),
                write_double_no_skip("PassiveFilterQualityFactor", self.passive_filter_quality_factor),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ShuntCapacitorMV.General:
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
                earthing=data.get("Earthing", False),
                re=data.get("Re", 0.0),
                xe=data.get("Xe", 0.0),
                earthing_node=decode_guid(earthing_node) if earthing_node else None,
                voltage_control=data.get("VoltageControl", False),
                u_on=data.get("Uon", 0.0),
                u_off=data.get("Uoff", 0.0),
                only_during_motorstart=data.get("OnlyDuringMotorstart", False),
                passive_filter_frequency=data.get("PassiveFilterFrequency", 0.0),
                passive_filter_quality_factor=data.get("PassiveFilterQualityFactor", 0.0),
            )

    @dataclass_json
    @dataclass
    class ActiveFilter:
        """Active Filter."""

        measure_field: Guid | None = None
        """GUID of the measurement field for active filter control."""

        inom: float = 0.0
        """Nominal current in A for active filter operation."""

        h: dict[int, float] = field(default_factory=dict)
        """Harmonic compensation factors by harmonic number (e.g., {3: 0.1, 5: 0.05})."""

        def serialize(self) -> str:
            """Serialize ActiveFilter properties."""
            props = []
            if self.measure_field:
                props.append(write_guid_no_skip("MeasureField", self.measure_field))
            props.append(write_double_no_skip("Inom", self.inom))
            if self.h:
                # Sort by harmonic number to ensure consistent output
                props.extend(
                    write_double_no_skip(f"h{harmonic_num}", self.h[harmonic_num])
                    for harmonic_num in sorted(self.h.keys())
                )
            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> ShuntCapacitorMV.ActiveFilter:
            """Deserialize ActiveFilter properties."""
            measure_field = data.get("MeasureField")

            h_values = {}
            for key, value in data.items():
                if key.startswith("h") and key[1:].isdigit():
                    harmonic_num = int(key[1:])
                    h_values[harmonic_num] = float(value)

            return cls(
                measure_field=decode_guid(measure_field) if measure_field else None,
                inom=data.get("Inom", 0.0),
                h=h_values,
            )

    general: General
    presentations: list[ElementPresentation]
    active_filter: ActiveFilter | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add shunt capacitor to the network."""
        if self.general.guid in network.shunt_capacitors:
            logger.critical("Shunt Capacitor %s already exists, overwriting", self.general.guid)
        network.shunt_capacitors[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the shunt capacitor to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.active_filter:
            lines.append(f"#ActiveFilter {self.active_filter.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ShuntCapacitorMV:
        """Deserialization of the shunt capacitor from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TShuntCapacitorMS: The deserialized shunt capacitor

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        active_filter_data = data.get("activeFilter", [{}])[0] if data.get("activeFilter") else {}
        active_filter = cls.ActiveFilter.deserialize(active_filter_data) if active_filter_data else None

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            active_filter=active_filter,
            presentations=presentations,
        )
