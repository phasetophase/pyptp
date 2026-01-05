"""Medium-voltage network link element for Vision integration.

Provides MV link/branch representation with symmetrical modeling
for balanced three-phase power system analysis.
"""

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
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import BranchPresentation


@dataclass_json
@dataclass
class LinkMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Medium-voltage network link for symmetrical modeling.

    Represents electrical connections between nodes in MV networks
    with balanced three-phase analysis capabilities.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for MV links."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float = 0
        mutation_date: int = optional_field(0)
        revision_date: float = optional_field(0.0)
        variant: bool = False
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        name: str = string_field()
        switch_state1: int = 1
        switch_state2: int = 1
        field_name1: str = string_field()
        field_name2: str = string_field()
        subnet_border: bool = False
        source1: str = string_field()
        source2: str = string_field()
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        loadrate_max: float = 0.0
        loadrate_max_winter: float = 0.0
        loadrate_max_emergency: float = 0.0
        loadrate_max_emergency_winter: float = 0.0
        rail_connectivity: int = 1
        limited: bool = False
        inom: float = 0.0
        ik1s: float = 0.0

        def serialize(self) -> str:
            """Serialize link properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_guid("Node1", self.node1, skip=NIL_GUID),
                write_guid("Node2", self.node2, skip=NIL_GUID),
                write_quote_string("Name", self.name),
                write_integer_no_skip("SwitchState1", self.switch_state1),
                write_integer_no_skip("SwitchState2", self.switch_state2),
                write_quote_string("FieldName1", self.field_name1),
                write_quote_string("FieldName2", self.field_name2),
                write_boolean("SubnetBorder", value=self.subnet_border),
                write_quote_string("Source1", self.source1),
                write_quote_string("Source2", self.source2),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_double("LoadrateMax", self.loadrate_max),
                write_double("LoadrateMaxWinter", self.loadrate_max_winter),
                write_double("LoadrateMaxmax", self.loadrate_max_emergency),
                write_double("LoadrateMaxmaxWinter", self.loadrate_max_emergency_winter),
                write_integer_no_skip("RailConnectivity", self.rail_connectivity),
                write_boolean("Limited", value=self.limited),
                write_double("Inom", self.inom) if self.limited else "",
                write_double("Ik1s", self.ik1s) if self.limited else "",
            )

        @classmethod
        def deserialize(cls, data: dict) -> LinkMV.General:
            """Parse link properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                variant=data.get("Variant", False),
                node1=decode_guid(data.get("Node1", str(NIL_GUID))),
                node2=decode_guid(data.get("Node2", str(NIL_GUID))),
                name=data.get("Name", ""),
                switch_state1=data.get("SwitchState1", 0),
                switch_state2=data.get("SwitchState2", 1),
                field_name1=data.get("FieldName1", ""),
                field_name2=data.get("FieldName2", ""),
                subnet_border=data.get("SubnetBorder", False),
                source1=data.get("Source1", ""),
                source2=data.get("Source2", ""),
                rail_connectivity=data.get("RailConnectivity", 1),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                loadrate_max=data.get("LoadrateMax", 0.0),
                loadrate_max_winter=data.get("LoadrateMaxWinter", 0.0),
                loadrate_max_emergency=data.get("LoadrateMaxmax", 0.0),
                loadrate_max_emergency_winter=data.get("LoadrateMaxmaxWinter", 0.0),
                limited=data.get("Limited", False),
                inom=data.get("Inom", 0.0),
                ik1s=data.get("Ik1s", 0.0),
            )

    general: General
    presentations: list[BranchPresentation]

    def register(self, network: NetworkMV) -> None:
        """Register link in MV network with GUID-based indexing.

        Args:
            network: Target MV network for link registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.links:
            logger.critical("Link %s already exists, overwriting", self.general.guid)
        network.links[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the link to the VNF format.

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
    def deserialize(cls, data: dict) -> LinkMV:
        """Parse link from VNF format data.

        Args:
            data: Dictionary containing parsed VNF section data.

        Returns:
            Initialized TLinkMS instance with parsed properties.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
        )
