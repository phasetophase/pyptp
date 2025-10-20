"""Fuse (Secondary)."""

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
class FuseMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a fuse (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a fuse."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        name: str = string_field()
        in_object: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        side: int = 1
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name),
                (write_guid("InObject", self.in_object) if self.in_object is not None else ""),
                write_integer("Side", self.side),
                write_quote_string("FuseType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> FuseMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                in_object=decode_guid(data.get("InObject", str(NIL_GUID))),
                side=data.get("Side", 1),
                type=data.get("FuseType", ""),
            )

    @dataclass_json
    @dataclass
    class FuseType(DataClassJsonMixin):
        """Fuse electrotechnical type properties."""

        short_name: str = string_field()
        unom: float | int = 0
        inom: float | int = 0
        three_phase: bool = False
        I1: float = 0.0
        T1: float = 0.0
        I2: float = 0.0
        T2: float = 0.0
        I3: float = 0.0
        T3: float = 0.0
        I4: float = 0.0
        T4: float = 0.0
        I5: float = 0.0
        T5: float = 0.0
        I6: float = 0.0
        T6: float = 0.0
        I7: float = 0.0
        T7: float = 0.0
        I8: float = 0.0
        T8: float = 0.0
        I9: float = 0.0
        T9: float = 0.0
        I10: float = 0.0
        T10: float = 0.0
        I11: float = 0.0
        T11: float = 0.0
        I12: float = 0.0
        T12: float = 0.0
        I13: float = 0.0
        T13: float = 0.0
        I14: float = 0.0
        T14: float = 0.0
        I15: float = 0.0
        T15: float = 0.0
        I16: float = 0.0
        T16: float = 0.0

        def serialize(self) -> str:
            """Serialize FuseType properties."""
            return serialize_properties(
                write_quote_string("ShortName", self.short_name),
                write_double("Unom", self.unom),
                write_double("Inom", self.inom),
                write_boolean("ThreePhase", value=self.three_phase),
                write_double_no_skip("I1", self.I1),
                write_double_no_skip("T1", self.T1),
                write_double_no_skip("I2", self.I2),
                write_double_no_skip("T2", self.T2),
                write_double_no_skip("I3", self.I3),
                write_double_no_skip("T3", self.T3),
                write_double_no_skip("I4", self.I4),
                write_double_no_skip("T4", self.T4),
                write_double_no_skip("I5", self.I5),
                write_double_no_skip("T5", self.T5),
                write_double_no_skip("I6", self.I6),
                write_double_no_skip("T6", self.T6),
                write_double_no_skip("I7", self.I7),
                write_double_no_skip("T7", self.T7),
                write_double_no_skip("I8", self.I8),
                write_double_no_skip("T8", self.T8),
                write_double_no_skip("I9", self.I9),
                write_double_no_skip("T9", self.T9),
                write_double_no_skip("I10", self.I10),
                write_double_no_skip("T10", self.T10),
                write_double_no_skip("I11", self.I11),
                write_double_no_skip("T11", self.T11),
                write_double_no_skip("I12", self.I12),
                write_double_no_skip("T12", self.T12),
                write_double_no_skip("I13", self.I13),
                write_double_no_skip("T13", self.T13),
                write_double_no_skip("I14", self.I14),
                write_double_no_skip("T14", self.T14),
                write_double_no_skip("I15", self.I15),
                write_double_no_skip("T15", self.T15),
                write_double_no_skip("I16", self.I16),
                write_double_no_skip("T16", self.T16),
            )

        @classmethod
        def deserialize(cls, data: dict) -> FuseMV.FuseType:
            """Deserialize FuseType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                unom=data.get("Unom", 0),
                inom=data.get("Inom", 0),
                three_phase=data.get("ThreePhase", False),
                I1=data.get("I1", 0),
                T1=data.get("T1", 0),
                I2=data.get("I2", 0),
                T2=data.get("T2", 0),
                I3=data.get("I3", 0),
                T3=data.get("T3", 0),
                I4=data.get("I4", 0),
                T4=data.get("T4", 0),
                I5=data.get("I5", 0),
                T5=data.get("T5", 0),
                I6=data.get("I6", 0),
                T6=data.get("T6", 0),
                I7=data.get("I7", 0),
                T7=data.get("T7", 0),
                I8=data.get("I8", 0),
                T8=data.get("T8", 0),
                I9=data.get("I9", 0),
                T9=data.get("T9", 0),
                I10=data.get("I10", 0),
                T10=data.get("T10", 0),
                I11=data.get("I11", 0),
                T11=data.get("T11", 0),
                I12=data.get("I12", 0),
                T12=data.get("T12", 0),
                I13=data.get("I13", 0),
                T13=data.get("T13", 0),
                I14=data.get("I14", 0),
                T14=data.get("T14", 0),
                I15=data.get("I15", 0),
                T15=data.get("T15", 0),
                I16=data.get("I16", 0),
                T16=data.get("T16", 0),
            )

    general: General
    type: FuseType
    presentations: list[SecondaryPresentation]

    def register(self, network: NetworkMV) -> None:
        """Will add fuse to the network."""
        if self.general.guid in network.fuses:
            logger.critical("Fuse %s already exists, overwriting", self.general.guid)
        network.fuses[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the fuse to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        lines.append(f"#FuseType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> FuseMV:
        """Deserialization of the fuse from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TFuseMS: The deserialized fuse

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        fuse_type_data = data.get("fuseType", [{}])[0] if data.get("fuseType") else {}
        fuse_type = cls.FuseType.deserialize(fuse_type_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import SecondaryPresentation

            presentation = SecondaryPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=fuse_type,
            presentations=presentations,
        )
