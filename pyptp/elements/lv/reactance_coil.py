"""Reactance Coil (Element)."""

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
    encode_string,
    optional_field,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import BranchPresentation


@dataclass_json
@dataclass
class ReactanceCoilLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a reactance coil (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a reactance coil."""

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
        type: str = field(default="", metadata=config(encoder=encode_string))

        def serialize(self) -> str:
            """Serialize General properties."""
            props = []
            props.append(f"GUID:'{{{str(self.guid).upper()}}}'")
            props.append(f"CreationTime:{self.creation_time}")
            if self.mutation_date != 0:
                props.append(f"MutationDate:{self.mutation_date}")
            if self.revision_date != 0.0:
                props.append(f"RevisionDate:{self.revision_date}")
            if self.node1 != NIL_GUID:
                props.append(f"Node1:'{{{str(self.node1).upper()}}}'")
            if self.node2 != NIL_GUID:
                props.append(f"Node2:'{{{str(self.node2).upper()}}}'")
            props.append(f"Name:'{self.name}'")
            props.append(f"SwitchState1_L1:{str(self.switch_state1_L1).lower()}")
            props.append(f"SwitchState1_L2:{str(self.switch_state1_L2).lower()}")
            props.append(f"SwitchState1_L3:{str(self.switch_state1_L3).lower()}")
            props.append(f"SwitchState1_N:{str(self.switch_state1_N).lower()}")
            props.append(f"SwitchState1_PE:{str(self.switch_state1_PE).lower()}")
            props.append(f"SwitchState2_L1:{str(self.switch_state2_L1).lower()}")
            props.append(f"SwitchState2_L2:{str(self.switch_state2_L2).lower()}")
            props.append(f"SwitchState2_L3:{str(self.switch_state2_L3).lower()}")
            props.append(f"SwitchState2_N:{str(self.switch_state2_N).lower()}")
            props.append(f"SwitchState2_PE:{str(self.switch_state2_PE).lower()}")
            props.append(f"FieldName1:'{self.field_name1}'")
            props.append(f"FieldName2:'{self.field_name2}'")
            if self.type:
                props.append(f"ReactanceCoilType:'{self.type}'")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> ReactanceCoilLV.General:
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
                type=data.get("ReactanceCoilType", ""),
            )

    @dataclass_json
    @dataclass
    class ReactanceCoilType(DataClassJsonMixin):
        """Electrotechnical properties for the Reactance Coil."""

        short_name: str = string_field()
        unom: float | int = optional_field(0)
        inom: float | int = optional_field(0)
        R: float | int = optional_field(0)
        X: int | float = optional_field(0)
        R0: int | float = optional_field(0)
        X0: int | float = optional_field(0)
        R2: float | int = optional_field(0)
        X2: float | int = optional_field(0)
        ik2s: float | int = optional_field(0)

        def serialize(self) -> str:
            """Serialize ReactanceCoilType properties."""
            props = []
            props.append(f"ShortName:'{self.short_name}'")
            if self.unom != 0:
                props.append(f"Unom:{self.unom}")
            if self.inom != 0:
                props.append(f"Inom:{self.inom}")
            if self.R != 0:
                props.append(f"R:{self.R}")
            if self.X != 0:
                props.append(f"X:{self.X}")
            if self.R0 != 0:
                props.append(f"R0:{self.R0}")
            if self.X0 != 0:
                props.append(f"X0:{self.X0}")
            if self.R2 != 0:
                props.append(f"R2:{self.R2}")
            if self.X2 != 0:
                props.append(f"X2:{self.X2}")
            if self.ik2s != 0:
                props.append(f"Ik2s:{self.ik2s}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> ReactanceCoilLV.ReactanceCoilType:
            """Deserialize ReactanceCoilType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                unom=data.get("Unom", 0),
                inom=data.get("Inom", 0),
                R=data.get("R", 0),
                X=data.get("X", 0),
                R0=data.get("R0", 0),
                X0=data.get("X0", 0),
                R2=data.get("R2", 0),
                X2=data.get("X2", 0),
                ik2s=data.get("Ik2s", 0),
            )

    general: General
    presentations: list[BranchPresentation]
    type: ReactanceCoilType

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add reactance coil to the network."""
        if self.general.guid in network.reactance_coils:
            logger.critical("Reactance Coil %s already exists, overwriting", self.general.guid)
        network.reactance_coils[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the reactance coil to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#ReactanceCoilType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ReactanceCoilLV:
        """Deserialization of the reactance coil from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TReactanceCoilLS: The deserialized reactance coil

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        reactance_coil_type_data = data.get("reactanceCoilType", [{}])[0] if data.get("reactanceCoilType") else {}
        reactance_coil_type = cls.ReactanceCoilType.deserialize(reactance_coil_type_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=reactance_coil_type,
        )
