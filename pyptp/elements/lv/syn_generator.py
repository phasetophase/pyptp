"""Synchronous Generator (Element)."""

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
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class SynchronousGeneratorLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a synchronous generator (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a synchronous generator."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        name: str = string_field()
        s_L1: bool = True  # noqa: N815
        s_L2: bool = True  # noqa: N815
        s_L3: bool = True  # noqa: N815
        s_N: bool = True  # noqa: N815
        field_name: str = string_field()
        pref: float = 0.8
        control_sort: str = string_field()
        cos_ref: float = 0.95
        uref: float = 0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node),
                write_guid_no_skip("GUID", self.guid),
                write_double("CreationTime", self.creation_time, skip=0),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_quote_string("Name", self.name),
                write_boolean("s_L1", value=self.s_L1),
                write_boolean("s_L2", value=self.s_L2),
                write_boolean("s_L3", value=self.s_L3),
                write_boolean("s_N", value=self.s_N),
                write_quote_string("FieldName", self.field_name),
                write_double("Pref", self.pref, skip=0.8),
                write_quote_string("ControlSort", self.control_sort),
                write_double("CosRef", self.cos_ref),
                write_double("Uref", self.uref, skip=0),
                write_guid("Profile", self.profile),
                write_quote_string("SynchronousGeneratorType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousGeneratorLV.General:
            """Deserialize General properties."""
            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                name=data.get("Name", ""),
                s_L1=data.get("s_L1", True),
                s_L2=data.get("s_L2", True),
                s_L3=data.get("s_L3", True),
                s_N=data.get("s_N", True),
                field_name=data.get("FieldName", ""),
                pref=data.get("Pref", 0.8),
                control_sort=data.get("ControlSort", ""),
                cos_ref=data.get("CosRef", 0.95),
                uref=data.get("Uref", 0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                type=data.get("SynchronousGeneratorType", ""),
            )

    @dataclass_json
    @dataclass
    class SynchronousGeneratorType(DataClassJsonMixin):
        """Electrotechnical properties for the synchronous generator."""

        unom: float | int = 0
        snom: float | int = 0
        cos_nom: float | int = 0
        q_min: float | int = 0
        q_max: float | int = 0
        rg: float | int = 0
        xd2sat: float | int = 0

        def serialize(self) -> str:
            """Serialize SynchronousGeneratorType properties."""
            return serialize_properties(
                write_double("Unom", self.unom, skip=0),
                write_double("Snom", self.snom, skip=0),
                write_double("CosNom", self.cos_nom, skip=0),
                write_double("Qmin", self.q_min, skip=0),
                write_double("Qmax", self.q_max, skip=0),
                write_double("Rg", self.rg, skip=0),
                write_double("Xd2sat", self.xd2sat, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousGeneratorLV.SynchronousGeneratorType:
            """Deserialize SynchronousGeneratorType properties."""
            return cls(
                unom=data.get("Unom", 0),
                snom=data.get("Snom", 0),
                cos_nom=data.get("CosNom", 0),
                q_min=data.get("Qmin", 0),
                q_max=data.get("Qmax", 0),
                rg=data.get("Rg", 0),
                xd2sat=data.get("Xd2sat", 0),
            )

    general: General
    presentations: list[ElementPresentation]
    type: SynchronousGeneratorType

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add Synchronous Generator to the network."""
        if self.general.guid in network.syn_generators:
            logger.critical("Synchronous Generator %s already exists, overwriting", self.general.guid)
        network.syn_generators[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the synchronous generator to the GNF format."""
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        if self.type:
            lines.append(f"#SynchronousGeneratorType {self.type.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(str(line) for line in lines)

    @classmethod
    def deserialize(cls, data: dict) -> SynchronousGeneratorLV:
        """Deserialization of the synchronous generator from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            SynchronousGeneratorLV: The deserialized synchronous generator

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        synchronous_generator_type_data = (
            data.get("synchronousGeneratorType", [{}])[0] if data.get("synchronousGeneratorType") else {}
        )
        synchronous_generator_type = cls.SynchronousGeneratorType.deserialize(synchronous_generator_type_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=synchronous_generator_type,
        )
