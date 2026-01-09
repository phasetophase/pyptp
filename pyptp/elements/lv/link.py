"""Link (Branch)."""

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
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean_no_skip,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.lv.shared import CurrentType, FuseType
if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import BranchPresentation


@dataclass
class LinkLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a link (LV)."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a link."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        name: str = string_field()

        switch_state1_L1: bool = True  # noqa: N815
        switch_state1_L2: bool = True  # noqa: N815
        switch_state1_L3: bool = True  # noqa: N815
        switch_state1_N: bool = True  # noqa: N815
        switch_state1_PE: bool = True  # noqa: N815
        switch_state2_L1: bool = True  # noqa: N815
        switch_state2_L2: bool = True  # noqa: N815
        switch_state2_L3: bool = True  # noqa: N815
        switch_state2_N: bool = True  # noqa: N815
        switch_state2_PE: bool = True  # noqa: N815

        field_name1: str = string_field()
        field_name2: str = string_field()
        failure_frequency: float = 0.0

        switch_state1_h1: bool = True
        switch_state1_h2: bool = True
        switch_state1_h3: bool = True
        switch_state1_h4: bool = True
        switch_state2_h1: bool = True
        switch_state2_h2: bool = True
        switch_state2_h3: bool = True
        switch_state2_h4: bool = True

        protection_type1_h1: str = optional_field("")
        protection_type1_h2: str = optional_field("")
        protection_type1_h3: str = optional_field("")
        protection_type1_h4: str = optional_field("")

        protection_type2_h1: str = optional_field("")
        protection_type2_h2: str = optional_field("")
        protection_type2_h3: str = optional_field("")
        protection_type2_h4: str = optional_field("")

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date),
                write_double("RevisionDate", self.revision_date),
                write_guid("Node1", self.node1, skip=NIL_GUID),
                write_guid("Node2", self.node2, skip=NIL_GUID),
                write_quote_string("Name", self.name),
                write_boolean_no_skip("SwitchState1_L1", value=self.switch_state1_L1),
                write_boolean_no_skip("SwitchState1_L2", value=self.switch_state1_L2),
                write_boolean_no_skip("SwitchState1_L3", value=self.switch_state1_L3),
                write_boolean_no_skip("SwitchState1_N", value=self.switch_state1_N),
                write_boolean_no_skip("SwitchState1_PE", value=self.switch_state1_PE),
                write_boolean_no_skip("SwitchState2_L1", value=self.switch_state2_L1),
                write_boolean_no_skip("SwitchState2_L2", value=self.switch_state2_L2),
                write_boolean_no_skip("SwitchState2_L3", value=self.switch_state2_L3),
                write_boolean_no_skip("SwitchState2_N", value=self.switch_state2_N),
                write_boolean_no_skip("SwitchState2_PE", value=self.switch_state2_PE),
                write_quote_string("FieldName1", self.field_name1),
                write_quote_string("FieldName2", self.field_name2),
                write_double("FailureFrequency", self.failure_frequency),
                write_boolean_no_skip("SwitchState1_h1", value=self.switch_state1_h1),
                write_boolean_no_skip("SwitchState1_h2", value=self.switch_state1_h2),
                write_boolean_no_skip("SwitchState1_h3", value=self.switch_state1_h3),
                write_boolean_no_skip("SwitchState1_h4", value=self.switch_state1_h4),
                write_boolean_no_skip("SwitchState2_h1", value=self.switch_state2_h1),
                write_boolean_no_skip("SwitchState2_h2", value=self.switch_state2_h2),
                write_boolean_no_skip("SwitchState2_h3", value=self.switch_state2_h3),
                write_boolean_no_skip("SwitchState2_h4", value=self.switch_state2_h4),
                write_quote_string("ProtectionType1_h1", self.protection_type1_h1),
                write_quote_string("ProtectionType1_h2", self.protection_type1_h2),
                write_quote_string("ProtectionType1_h3", self.protection_type1_h3),
                write_quote_string("ProtectionType1_h4", self.protection_type1_h4),
                write_quote_string("ProtectionType2_h1", self.protection_type2_h1),
                write_quote_string("ProtectionType2_h2", self.protection_type2_h2),
                write_quote_string("ProtectionType2_h3", self.protection_type2_h3),
                write_quote_string("ProtectionType2_h4", self.protection_type2_h4),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LinkLV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                node1=decode_guid(data.get("Node1", str(NIL_GUID))),
                node2=decode_guid(data.get("Node2", str(NIL_GUID))),
                name=data.get("Name", ""),
                switch_state1_L1=data.get("SwitchState1_L1", True),
                switch_state1_L2=data.get("SwitchState1_L2", True),
                switch_state1_L3=data.get("SwitchState1_L3", True),
                switch_state1_N=data.get("SwitchState1_N", True),
                switch_state1_PE=data.get("SwitchState1_PE", True),
                switch_state2_L1=data.get("SwitchState2_L1", True),
                switch_state2_L2=data.get("SwitchState2_L2", True),
                switch_state2_L3=data.get("SwitchState2_L3", True),
                switch_state2_N=data.get("SwitchState2_N", True),
                switch_state2_PE=data.get("SwitchState2_PE", True),
                field_name1=data.get("FieldName1", ""),
                field_name2=data.get("FieldName2", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
                switch_state1_h1=data.get("SwitchState1_h1", True),
                switch_state1_h2=data.get("SwitchState1_h2", True),
                switch_state1_h3=data.get("SwitchState1_h3", True),
                switch_state1_h4=data.get("SwitchState1_h4", True),
                switch_state2_h1=data.get("SwitchState2_h1", True),
                switch_state2_h2=data.get("SwitchState2_h2", True),
                switch_state2_h3=data.get("SwitchState2_h3", True),
                switch_state2_h4=data.get("SwitchState2_h4", True),
                protection_type1_h1=data.get("ProtectionType1_h1", ""),
                protection_type1_h2=data.get("ProtectionType1_h2", ""),
                protection_type1_h3=data.get("ProtectionType1_h3", ""),
                protection_type1_h4=data.get("ProtectionType1_h4", ""),
                protection_type2_h1=data.get("ProtectionType2_h1", ""),
                protection_type2_h2=data.get("ProtectionType2_h2", ""),
                protection_type2_h3=data.get("ProtectionType2_h3", ""),
                protection_type2_h4=data.get("ProtectionType2_h4", ""),
            )

    general: General
    presentations: list[BranchPresentation]
    fuse1_h1: FuseType | None = None
    fuse1_h2: FuseType | None = None
    fuse1_h3: FuseType | None = None
    fuse1_h4: FuseType | None = None
    fuse2_h2: FuseType | None = None
    fuse2_h1: FuseType | None = None
    fuse2_h3: FuseType | None = None
    fuse2_h4: FuseType | None = None

    current_protection1_h1: CurrentType | None = None
    current_protection1_h2: CurrentType | None = None
    current_protection1_h3: CurrentType | None = None
    current_protection1_h4: CurrentType | None = None
    current_protection2_h1: CurrentType | None = None
    current_protection2_h2: CurrentType | None = None
    current_protection2_h3: CurrentType | None = None
    current_protection2_h4: CurrentType | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add link to the network."""
        if self.general.guid in network.links:
            logger.critical("Link %s already exists, overwriting", self.general.guid)
        network.links[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the link to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.fuse1_h1 is not None:
            lines.append(f"#FuseType1_h1 {self.fuse1_h1.serialize()}")

        if self.fuse1_h2 is not None:
            lines.append(f"#FuseType1_h2 {self.fuse1_h2.serialize()}")

        if self.fuse1_h3 is not None:
            lines.append(f"#FuseType1_h3 {self.fuse1_h3.serialize()}")

        if self.fuse1_h4 is not None:
            lines.append(f"#FuseType1_h4 {self.fuse1_h4.serialize()}")

        if self.fuse2_h1 is not None:
            lines.append(f"#FuseType2_h1 {self.fuse2_h1.serialize()}")

        if self.fuse2_h2 is not None:
            lines.append(f"#FuseType2_h2 {self.fuse2_h2.serialize()}")

        if self.fuse2_h3 is not None:
            lines.append(f"#FuseType2_h3 {self.fuse2_h3.serialize()}")

        if self.fuse2_h4 is not None:
            lines.append(f"#FuseType2_h4 {self.fuse2_h4.serialize()}")

        if self.current_protection1_h1 is not None:
            lines.append(f"#CurrentType1_h1 {self.current_protection1_h1.serialize()}")

        if self.current_protection1_h2 is not None:
            lines.append(f"#CurrentType1_h2 {self.current_protection1_h2.serialize()}")

        if self.current_protection1_h3 is not None:
            lines.append(f"#CurrentType1_h3 {self.current_protection1_h3.serialize()}")

        if self.current_protection1_h4 is not None:
            lines.append(f"#CurrentType1_h4 {self.current_protection1_h4.serialize()}")

        if self.current_protection2_h1 is not None:
            lines.append(f"#CurrentType2_h1 {self.current_protection2_h1.serialize()}")

        if self.current_protection2_h2 is not None:
            lines.append(f"#CurrentType2_h2 {self.current_protection2_h2.serialize()}")

        if self.current_protection2_h3 is not None:
            lines.append(f"#CurrentType2_h3 {self.current_protection2_h3.serialize()}")

        if self.current_protection2_h4 is not None:
            lines.append(f"#CurrentType2_h4 {self.current_protection2_h4.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> LinkLV:
        """Deserialization of the link from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TLinkLS: The deserialized link

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        # Handle fuse types
        fuse1_h1 = None
        if data.get("fuse1_h1"):
            from .shared import FuseType

            fuse1_h1 = FuseType.deserialize(data["fuse1_h1"][0])

        fuse1_h2 = None
        if data.get("fuse1_h2"):
            from .shared import FuseType

            fuse1_h2 = FuseType.deserialize(data["fuse1_h2"][0])

        fuse1_h3 = None
        if data.get("fuse1_h3"):
            from .shared import FuseType

            fuse1_h3 = FuseType.deserialize(data["fuse1_h3"][0])

        fuse1_h4 = None
        if data.get("fuse1_h4"):
            from .shared import FuseType

            fuse1_h4 = FuseType.deserialize(data["fuse1_h4"][0])

        fuse2_h1 = None
        if data.get("fuse2_h1"):
            from .shared import FuseType

            fuse2_h1 = FuseType.deserialize(data["fuse2_h1"][0])

        fuse2_h2 = None
        if data.get("fuse2_h2"):
            from .shared import FuseType

            fuse2_h2 = FuseType.deserialize(data["fuse2_h2"][0])

        fuse2_h3 = None
        if data.get("fuse2_h3"):
            from .shared import FuseType

            fuse2_h3 = FuseType.deserialize(data["fuse2_h3"][0])

        fuse2_h4 = None
        if data.get("fuse2_h4"):
            from .shared import FuseType

            fuse2_h4 = FuseType.deserialize(data["fuse2_h4"][0])

        # Handle current protection types
        current_protection1_h1 = None
        if data.get("current_protection1_h1"):
            from .shared import CurrentType

            current_protection1_h1 = CurrentType.deserialize(data["current_protection1_h1"][0])

        current_protection1_h2 = None
        if data.get("current_protection1_h2"):
            from .shared import CurrentType

            current_protection1_h2 = CurrentType.deserialize(data["current_protection1_h2"][0])

        current_protection1_h3 = None
        if data.get("current_protection1_h3"):
            from .shared import CurrentType

            current_protection1_h3 = CurrentType.deserialize(data["current_protection1_h3"][0])

        current_protection1_h4 = None
        if data.get("current_protection1_h4"):
            from .shared import CurrentType

            current_protection1_h4 = CurrentType.deserialize(data["current_protection1_h4"][0])

        current_protection2_h1 = None
        if data.get("current_protection2_h1"):
            from .shared import CurrentType

            current_protection2_h1 = CurrentType.deserialize(data["current_protection2_h1"][0])

        current_protection2_h2 = None
        if data.get("current_protection2_h2"):
            from .shared import CurrentType

            current_protection2_h2 = CurrentType.deserialize(data["current_protection2_h2"][0])

        current_protection2_h3 = None
        if data.get("current_protection2_h3"):
            from .shared import CurrentType

            current_protection2_h3 = CurrentType.deserialize(data["current_protection2_h3"][0])

        current_protection2_h4 = None
        if data.get("current_protection2_h4"):
            from .shared import CurrentType

            current_protection2_h4 = CurrentType.deserialize(data["current_protection2_h4"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            fuse1_h1=fuse1_h1,
            fuse1_h2=fuse1_h2,
            fuse1_h3=fuse1_h3,
            fuse1_h4=fuse1_h4,
            fuse2_h1=fuse2_h1,
            fuse2_h2=fuse2_h2,
            fuse2_h3=fuse2_h3,
            fuse2_h4=fuse2_h4,
            current_protection1_h1=current_protection1_h1,
            current_protection1_h2=current_protection1_h2,
            current_protection1_h3=current_protection1_h3,
            current_protection1_h4=current_protection1_h4,
            current_protection2_h1=current_protection2_h1,
            current_protection2_h2=current_protection2_h2,
            current_protection2_h3=current_protection2_h3,
            current_protection2_h4=current_protection2_h4,
        )
