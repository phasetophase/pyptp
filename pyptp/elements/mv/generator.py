"""Medium-voltage load element for Vision integration.

Provides MV load representation with symmetrical modeling
for balanced three-phase power system analysis and control.
"""

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
    serialize_notes,
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
    from pyptp.network_mv import NetworkMV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class GeneratorMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Medium-voltage generator element for symmetrical modelin."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for MV loads."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        switch_state: int = 1
        field_name: str = string_field()
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        not_preferred: bool = False
        sort: str = "G"
        snom: float = 0.0
        P: float = 0.0
        Q: float = 0.0
        ik_inom: float = 1.0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize load properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("Node", self.node),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string("FieldName", self.field_name, skip=""),
                write_double("FailureFrequency", self.failure_frequency, skip=0.0),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_quote_string("Sort", value=self.sort, skip="?"),
                write_double("Snom", self.snom),
                write_double("P", self.P, skip=0.0),
                write_double("Q", self.Q, skip=0.0),
                write_double("Ik/Inom", self.ik_inom),
                write_guid("Profile", self.profile, skip=NIL_GUID),
            )

        @classmethod
        def deserialize(cls, data: dict) -> GeneratorMV.General:
            """Parse load properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
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
                snom=data.get("Snom", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                not_preferred=data.get("NotPreferred", False),
                ik_inom=data.get("Ik/Inom", 0),
                sort=data.get("Sort", "G"),
                P=data.get("P", 0.0),
                Q=data.get("Q", 0.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
            )

    @dataclass_json
    @dataclass
    class CapacityRestriction(DataClassJsonMixin):
        """Load capacity restrictions and time-based limitations."""

        sort: str = string_field()
        begin_date: int = 0
        end_date: int = 0
        begin_time: float = 0.0
        end_time: float = 0.0
        p_max: float = 0.0

        def serialize(self) -> str:
            """Serialize capacity properties to VNF format."""
            props = []
            props.append(f"Sort:'{self.sort}'")
            props.append(f"BeginDate:{self.begin_date}")
            props.append(f"EndDate:{self.end_date}")
            props.append(f"BeginTime:{self.begin_time}")
            props.append(f"EndTime:{self.end_time}")
            props.append(f"Pmax:{self.p_max}")
            return " ".join(props) + " "

        @classmethod
        def deserialize(cls, data: dict) -> GeneratorMV.CapacityRestriction:
            """Parse capacity properties from VNF data."""
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
    restrictions: list[CapacityRestriction] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Register load in MV network with GUID-based indexing.

        Args:
            network: Target MV network for load registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.generators:
            logger.critical("Generator %s already exists, overwriting", self.general.guid)
        network.generators[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the load to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.restrictions:
            lines.extend(f"#Restriction {restriction.serialize()}" for restriction in self.restrictions)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(serialize_notes(self.notes))

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> GeneratorMV:
        """Parse load from VNF format data.

        Args:
            data: Dictionary containing parsed VNF section data.

        Returns:
            Initialized TLoadMS instance with parsed properties.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        restriction_data_list = data.get("geo_series", [])
        restrictions = [
            cls.CapacityRestriction.deserialize(restriction_data) for restriction_data in restriction_data_list
        ]

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            restrictions=restrictions,
        )
