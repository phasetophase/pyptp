"""Source representing a different network, often MV, powering the LV network (Element)."""

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
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class SourceLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a source which would often be a different network or a MV network (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a source."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int | None = optional_field(0)
        revision_date: float | int | None = optional_field(0.0)
        name: str = string_field()
        s_L1: bool = True  # noqa: N815
        s_L2: bool = True  # noqa: N815
        s_L3: bool = True  # noqa: N815
        s_N: bool = True  # noqa: N815
        field_name: str = string_field()
        umin: float | int = 0.4
        umax: float | int = 0.4
        uref: float | int = 0.4
        sk2nom: int | float = 40
        is_sk2_used_for_loadflow: bool = False
        failure_frequency: float | int | None = optional_field(0)

        def serialize(self) -> str:
            """Serialize General properties."""
            props = []
            if self.node != NIL_GUID:
                props.append(f"Node:'{{{str(self.node).upper()}}}'")
            props.append(f"GUID:'{{{str(self.guid).upper()}}}'")
            props.append(f"CreationTime:{self.creation_time}")
            if self.mutation_date is not None and self.mutation_date != 0:
                props.append(f"MutationDate:{self.mutation_date}")
            if self.revision_date is not None and self.revision_date != 0.0:
                props.append(f"RevisionDate:{self.revision_date}")
            props.append(f"Name:'{self.name}'")
            props.append(f"s_L1:{self.s_L1!s}")
            props.append(f"s_L2:{self.s_L2!s}")
            props.append(f"s_L3:{self.s_L3!s}")
            props.append(f"s_N:{self.s_N!s}")
            props.append(f"FieldName:'{self.field_name}'")
            props.append(f"Umin:{self.umin}")
            props.append(f"Umax:{self.umax}")
            props.append(f"Uref:{self.uref}")
            props.append(f"Sk2nom:{self.sk2nom}")
            props.append(f"Sk2TakeWith:{self.is_sk2_used_for_loadflow!s}")
            if self.failure_frequency is not None and self.failure_frequency != 0:
                props.append(f"FailureFrequency:{self.failure_frequency}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> SourceLV.General:
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
                umin=data.get("Umin", 0.4),
                umax=data.get("Umax", 0.4),
                uref=data.get("Uref", 0.4),
                sk2nom=data.get("Sk2nom", 40),
                is_sk2_used_for_loadflow=data.get("Sk2TakeWith", False),
                failure_frequency=data.get("FailureFrequency", 0),
            )

    general: General
    presentations: list[ElementPresentation]

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add source to the network."""
        if self.general.guid in network.sources:
            logger.critical("Source %s already exists, overwriting", self.general.guid)
        network.sources[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the source to the GNF format.

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
    def deserialize(cls, data: dict) -> SourceLV:
        """Deserialization of the source from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TSourceLS: The deserialized source

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
