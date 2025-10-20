"""Load Switch (Secondary)."""

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
    encode_guid_optional,
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
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import SecondaryPresentation


@dataclass_json
@dataclass
class LoadSwitchMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a load switch (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a load switch."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        side: int = 1
        node: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        disconnector: bool = False
        remote_control: bool = False
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name),
                write_guid("InObject", self.in_object) if self.in_object is not None else "",
                write_integer("Side", self.side),
                write_guid("Node", self.node) if self.node is not None else "",
                write_boolean("Seperation", value=self.disconnector),
                write_boolean("RemoteControl", value=self.remote_control),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_quote_string("LoadSwitchType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LoadSwitchMV.General:
            """Deserialize General properties."""
            guid = data.get("GUID")
            node = data.get("Node")
            mutation_date = data.get("MutationDate")
            revision_date = data.get("RevisionDate")

            return cls(
                guid=decode_guid(guid) if guid else Guid(uuid4()),
                creation_time=data.get("CreationTime", 0),
                mutation_date=mutation_date if mutation_date is not None else 0,
                revision_date=revision_date if revision_date is not None else 0.0,
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                node=decode_guid(node) if node else None,
                disconnector=data.get("Seperation", False),
                remote_control=data.get("RemoteControl", False),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                type=data.get("LoadSwitchType", ""),
            )

    @dataclass_json
    @dataclass
    class LoadSwitchType(DataClassJsonMixin):
        """Type properties."""

        short_name: str = string_field()
        unom: float = 0.0
        inom: float = 0.0
        switch_time: float = 0.0
        ik_make: float = 0.0
        ik_break: float = 0.0
        ik_dynamic: float = 0.0
        ik_thermal: float = 0.0
        t_thermal: float = 0.0

        def serialize(self) -> str:
            """Serialize LoadSwitchType properties."""
            return serialize_properties(
                write_quote_string("ShortName", self.short_name),
                write_double("Unom", self.unom),
                write_double("Inom", self.inom),
                write_double("SwitchTime", self.switch_time),
                write_double("IkMake", self.ik_make),
                write_double("IkBreak", self.ik_break),
                write_double("IkDynamic", self.ik_dynamic),
                write_double("IkThermal", self.ik_thermal),
                write_double("TThermal", self.t_thermal, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LoadSwitchMV.LoadSwitchType:
            """Deserialize LoadSwitchType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                unom=data.get("Unom", 0.0),
                inom=data.get("Inom", 0.0),
                switch_time=data.get("SwitchTime", 0.0),
                ik_make=data.get("IkMake", 0.0),
                ik_break=data.get("IkBreak", 0.0),
                ik_dynamic=data.get("IkDynamic", 0.0),
                ik_thermal=data.get("IkThermal", 0.0),
                t_thermal=data.get("TThermal", 0.0),
            )

    general: General
    type: LoadSwitchType | None = None
    presentations: list[SecondaryPresentation] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Will add load switch to the network."""
        if self.general.guid in network.load_switches:
            logger.critical("Load Switch %s already exists, overwriting", self.general.guid)
        network.load_switches[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the load switch to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#LoadSwitchType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)
        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> LoadSwitchMV:
        """Deserialization of the load switch from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TLoadSwitchMS: The deserialized load switch

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        load_switch_type = None
        if data.get("loadSwitchType"):
            load_switch_type = cls.LoadSwitchType.deserialize(data["loadSwitchType"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import SecondaryPresentation

            presentation = SecondaryPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=load_switch_type,
            presentations=presentations,
        )
