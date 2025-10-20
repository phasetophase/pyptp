"""Source (Element)."""

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
    from pyptp.elements.mv.presentations import ElementPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV
LOW_VOLTAGE_THRESHOLD_KV = 35


@dataclass_json
@dataclass
class SourceMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a source (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a source."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0
        mutation_date: int = optional_field(0)
        revision_date: int = optional_field(0)
        variant: bool = False
        name: str = string_field()
        switch_state: int = 1
        field_name: str = string_field()
        """Name of the connection field."""
        failure_frequency: float = 0.0
        """Mean number of occurrences that the source fails (short circuit) per year."""
        repair_duration: float = 0.0
        """Mean duration of repair or replacement in minutes."""
        maintenance_frequency: float = 0.0
        """Mean number of occurrences that the source is in maintenance per year."""
        maintenance_duration: float = 0.0
        """Mean duration of maintenance in minutes."""
        maintenance_cancel_duration: float = 0.0
        """Mean duration of cancellation of maintenance in case of emergency in minutes."""
        not_preferred: bool = False
        uref: float = 1
        """Reference voltage as a factor of Unom in pu."""

        angle: float = 0
        """Reference voltage phase angle in degrees."""
        sk2nom: float = 0
        """Sub-transient short-circuit power in MVA."""
        sk2min: float = 0
        """Minimum sub-transient short-circuit power in MVA."""
        sk2max: float = 0
        """Maximum sub-transient short-circuit power in MVA."""
        r_x: float = 0.0
        """Ratio between source impedance R and X (dimensionless)."""
        z0_z1: float = 1.0
        """Ratio between source impedance zero and normal sequence (dimensionless)."""
        smin: float = 0
        """Minimal to be tested power in MVA."""
        smax: float = 0
        """Maximal to be tested power in MVA."""
        pmin: float = 0
        """Minimum active power limit in MW."""
        pmax: float = 0
        """Maximum active power limit in MW."""

        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        """GUID reference to the voltage profile."""

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
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string("FieldName", self.field_name),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_double_no_skip("Uref", self.uref),
                write_double("Angle", self.angle),
                write_double("Sk2nom", self.sk2nom),
                write_double("Sk2min", self.sk2min),
                write_double("Sk2max", self.sk2max),
                write_double_no_skip("R/X", self.r_x),
                write_double_no_skip("Z0/Z1", self.z0_z1),
                write_double("Smin", self.smin),
                write_double("Smax", self.smax),
                write_double("Pmin", self.pmin),
                write_double("Pmax", self.pmax),
                write_guid("Profile", self.profile, skip=NIL_GUID),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SourceMV.General:
            """Deserialize General properties."""
            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                switch_state=data.get("SwitchState", 1),
                field_name=data.get("FieldName", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                not_preferred=data.get("NotPreferred", False),
                uref=data.get("Uref", 1),
                angle=data.get("Angle", 0),
                sk2nom=data.get("Sk2nom", 0),
                sk2min=data.get("Sk2min", 0),
                sk2max=data.get("Sk2max", 0),
                r_x=data.get("R/X", 0.0),
                z0_z1=data.get("Z0/Z1", 3),
                smin=data.get("Smin", 0),
                smax=data.get("Smax", 0),
                pmin=data.get("Pmin", 0),
                pmax=data.get("Pmax", 0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
            )

    general: General
    presentations: list[ElementPresentation]

    def apply_node_defaults(self, network: NetworkMV) -> None:
        """Apply defaults based on the connected node's Unom, same as Application Vision.

        Vision logic:
        - Sk2max = 100 * Unom (or 100 if no node)
        - Sk2min = 90 * Unom (or 90 if no node)
        - Sk2nom = 100 * Unom (or 100 if no node)
        - R_X = 0.1 if Unom <= 35 (or 0 if no node)
        """
        if self.general.node != NIL_GUID and self.general.node in network.nodes:
            node = network.nodes[self.general.node]
            unom = node.general.unom

            if self.general.sk2max == 0:  # Only set if still default
                self.general.sk2max = 100 * unom
            if self.general.sk2min == 0:  # Only set if still default
                self.general.sk2min = 90 * unom
            if self.general.sk2nom == 0:  # Only set if still default
                self.general.sk2nom = 100 * unom
            # Only set if still default and Unom <= 35kV
            if self.general.r_x == 0.0 and unom <= LOW_VOLTAGE_THRESHOLD_KV:
                self.general.r_x = 0.1
        else:
            # Fallback defaults when no node is assigned
            if self.general.sk2max == 0:
                self.general.sk2max = 100
            if self.general.sk2min == 0:
                self.general.sk2min = 90
            if self.general.sk2nom == 0:
                self.general.sk2nom = 100

    def register(self, network: NetworkMV) -> None:
        """Will add source to the network."""
        if self.general.guid in network.sources:
            logger.critical("Source %s already exists, overwriting", self.general.guid)

        # Apply node-based defaults before registering
        self.apply_node_defaults(network)

        network.sources[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the source to the VNF format.

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
    def deserialize(cls, data: dict) -> SourceMV:
        """Deserialization of the source from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TSourceMS: The deserialized source

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
