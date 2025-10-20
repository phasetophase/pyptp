"""Mutual (Secondary)."""

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
    optional_field,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double,
    write_guid,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import SecondaryPresentation


@dataclass_json
@dataclass
class MutualMV(ExtrasNotesMixin):
    """Represents a mutual (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a mutual."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        line1: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        line2: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        R00: float = 0.0
        X00: float = 0.0

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Line1", self.line1) if self.line1 is not None else "",
                write_guid("Line2", self.line2) if self.line2 is not None else "",
                write_double("R00", self.R00),
                write_double("X00", self.X00),
            )

        @classmethod
        def deserialize(cls, data: dict) -> MutualMV.General:
            """Deserialize General properties."""
            guid = data.get("GUID")
            line1 = data.get("Line1")
            line2 = data.get("Line2")
            mutation_date = data.get("MutationDate")
            revision_date = data.get("RevisionDate")

            return cls(
                guid=decode_guid(guid) if guid else Guid(uuid4()),
                creation_time=data.get("CreationTime", 0),
                mutation_date=mutation_date if mutation_date is not None else 0,
                revision_date=revision_date if revision_date is not None else 0.0,
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                line1=decode_guid(line1) if line1 else None,
                line2=decode_guid(line2) if line2 else None,
                R00=data.get("R00", 0.0),
                X00=data.get("X00", 0.0),
            )

    @dataclass_json
    @dataclass
    class MutualType(DataClassJsonMixin):
        """Type properties."""

        short_name: str = string_field()
        R_mutual: float = 0.0
        X_mutual: float = 0.0
        Z_mutual: float = 0.0

        def serialize(self) -> str:
            """Serialize MutualType properties."""
            props = []
            props.append(f"ShortName:'{self.short_name}'")
            props.append(f"Rmutual:{self.R_mutual}")
            props.append(f"Xmutual:{self.X_mutual}")
            props.append(f"Zmutual:{self.Z_mutual}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> MutualMV.MutualType:
            """Deserialize MutualType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                R_mutual=data.get("Rmutual", 0.0),
                X_mutual=data.get("Xmutual", 0.0),
                Z_mutual=data.get("Zmutual", 0.0),
            )

    general: General
    type: MutualType | None = None
    presentations: list[SecondaryPresentation] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Will add mutual to the network."""
        key = f"{self.general.line1}_{self.general.line2}"
        if key in network.mutuals:
            logger.critical("Mutual %s already exists, overwriting", key)
        network.mutuals[key] = self

    def serialize(self) -> str:
        """Serialize the mutual to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#MutualType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> MutualMV:
        """Deserialization of the mutual from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TMutualMS: The deserialized mutual

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        mutual_type = None
        if data.get("mutualType"):
            mutual_type = cls.MutualType.deserialize(data["mutualType"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import SecondaryPresentation

            presentation = SecondaryPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=mutual_type,
            presentations=presentations,
        )
