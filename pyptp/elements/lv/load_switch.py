"""Load Switch (Secondary)."""

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

from .presentations import SecundairPresentation

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass
class LoadSwitchLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a load switch (LV)."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a load switch."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        name: str = string_field()
        revision_date: float | int = optional_field(0.0)
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        side: int = 1
        standardizable: bool = False

        def serialize(self) -> str:
            """Serialize General properties."""
            props = []
            props.append(f"GUID:'{{{str(self.guid).upper()}}}'")
            props.append(f"CreationTime:{self.creation_time}")
            if self.mutation_date != 0:
                props.append(f"MutationDate:{self.mutation_date}")
            props.append(f"Name:'{self.name}'")
            if self.revision_date != 0.0:
                props.append(f"RevisionDate:{self.revision_date}")
            if self.in_object != NIL_GUID:
                props.append(f"InObject:'{{{str(self.in_object).upper()}}}'")
            props.append(f"Side:{self.side}")
            props.append(f"Standardizable:{str(self.standardizable).lower()}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> LoadSwitchLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                name=data.get("Name", ""),
                revision_date=data.get("RevisionDate", 0.0),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                standardizable=data.get("Standardizable", False),
            )

    @dataclass
    class LoadSwitchType(DataClassJsonMixin):
        """Electrotechnical properties of the loadswitch."""

        short_name: str = string_field()
        unom: float = 0.0
        inom: float = 0.0
        ik_thermal: float = 0.0
        t_thermal: float = 0.0

        def serialize(self) -> str:
            """Serialize LoadSwitchType properties."""
            props = []
            props.append(f"ShortName:'{self.short_name}'")
            props.append(f"Unom:{self.unom}")
            props.append(f"Inom:{self.inom}")
            props.append(f"IkThermal:{self.ik_thermal}")
            props.append(f"TThermal:{self.t_thermal}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> LoadSwitchLV.LoadSwitchType:
            """Deserialize LoadSwitchType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                unom=data.get("Unom", 0.0),
                inom=data.get("Inom", 0.0),
                ik_thermal=data.get("IkThermal", 0.0),
                t_thermal=data.get("TThermal", 0.0),
            )

    general: General
    presentations: list[SecundairPresentation]
    type: LoadSwitchType

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add load switch to the network."""
        if self.general.guid in network.load_switches:
            logger.critical("Load Switch %s already exists, overwriting", self.general.guid)
        network.load_switches[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the load switch to the GNF format.

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
    def deserialize(cls, data: dict) -> LoadSwitchLV:
        """Deserialization of the load switch from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TLoadSwitchLS: The deserialized load switch

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        loadswitch_data = data.get("loadswitch", [{}])[0] if data.get("loadswitch") else {}
        load_switch_type = cls.LoadSwitchType.deserialize(loadswitch_data)

        presentations_data = data.get("presentations", [])
        presentations: list[SecundairPresentation] = []
        for pres_data in presentations_data:
            presentation = SecundairPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=load_switch_type,
        )
