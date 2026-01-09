"""Special Transformer (Branch)."""

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
from pyptp.elements.enums import SpecialTransformerSort
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
    from pyptp.network_lv import NetworkLV

    from .presentations import BranchPresentation


@dataclass_json
@dataclass
class SpecialTransformerLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a special transformer (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a special transformer."""

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
        failure_frequency: float | int = optional_field(0)
        type: str = string_field()
        switch_state_N_PE: bool = False  # noqa: N815
        switch_state_PE_e: bool = False  # noqa: N815
        re: float = optional_field(0)
        tap_position: float = 0

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double("CreationTime", self.creation_time, skip=0),
                write_double("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_guid("Node1", self.node1),
                write_guid("Node2", self.node2),
                write_quote_string("Name", self.name),
                write_boolean("SwitchState1_L1", value=self.switch_state1_L1),
                write_boolean("SwitchState1_L2", value=self.switch_state1_L2),
                write_boolean("SwitchState1_L3", value=self.switch_state1_L3),
                write_boolean("SwitchState1_N", value=self.switch_state1_N),
                write_boolean("SwitchState1_PE", value=self.switch_state1_PE),
                write_boolean("SwitchState2_L1", value=self.switch_state2_L1),
                write_boolean("SwitchState2_L2", value=self.switch_state2_L2),
                write_boolean("SwitchState2_L3", value=self.switch_state2_L3),
                write_boolean("SwitchState2_N", value=self.switch_state2_N),
                write_boolean("SwitchState2_PE", value=self.switch_state2_PE),
                write_quote_string("FieldName1", self.field_name1),
                write_quote_string("FieldName2", self.field_name2),
                write_double("FailureFrequency", self.failure_frequency, skip=0),
                write_quote_string("SpecialTransformerType", self.type),
                write_boolean("SwitchState_N_PE", value=self.switch_state_N_PE),
                write_boolean("SwitchState_PE_e", value=self.switch_state_PE_e),
                write_double("Re", self.re, skip=0),
                write_double_no_skip("TapPosition", self.tap_position),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerLV.General:
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
                failure_frequency=data.get("FailureFrequency", 0),
                type=data.get("SpecialTransformerType", ""),
                switch_state_N_PE=data.get("SwitchState_N_PE", False),
                switch_state_PE_e=data.get("SwitchState_PE_e", False),
                re=data.get("Re", 0),
                tap_position=data.get("TapPosition", 0),
            )

    @dataclass_json
    @dataclass
    class VoltageControl(DataClassJsonMixin):
        """Special Transformer Voltage Control properties."""

        present: bool = False
        status: bool = False
        measure_side: int = 3
        setpoint: float = 0.4
        deadband: float = optional_field(0)
        control_sort: int = optional_field(0)
        Rc: float = optional_field(0)
        Xc: float = optional_field(0)
        compounding_at_generation: bool = True
        pmin1: int = optional_field(0)
        umin1: float = optional_field(0)
        pmax1: int = optional_field(0)
        umax1: float = optional_field(0)

        def serialize(self) -> str:
            """Serialize VoltageControl properties."""
            return serialize_properties(
                write_boolean("Present", value=self.present),
                write_boolean("Status", value=self.status),
                write_integer("MeasureSide", self.measure_side, skip=3),
                write_double("Setpoint", self.setpoint, skip=0.4),
                write_double("Deadband", self.deadband, skip=0),
                write_integer("ControlSort", self.control_sort, skip=0),
                write_double("Rc", self.Rc, skip=0),
                write_double("Xc", self.Xc, skip=0),
                write_boolean("CompoundingAtGeneration", value=self.compounding_at_generation),
                write_integer("Pmin1", self.pmin1, skip=0),
                write_double("Umin1", self.umin1, skip=0),
                write_integer("Pmax1", self.pmax1, skip=0),
                write_double("Umax1", self.umax1, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerLV.VoltageControl:
            """Deserialize VoltageControl properties."""
            return cls(
                present=data.get("Present", False),
                status=data.get("Status", False),
                measure_side=data.get("MeasureSide", 3),
                setpoint=data.get("Setpoint", 0.4),
                deadband=data.get("Deadband", 0),
                control_sort=data.get("ControlSort", 0),
                Rc=data.get("Rc", 0),
                Xc=data.get("Xc", 0),
                compounding_at_generation=data.get("CompoundingAtGeneration", True),
                pmin1=data.get("Pmin1", 0),
                umin1=data.get("Umin1", 0),
                pmax1=data.get("Pmax1", 0),
                umax1=data.get("Umax1", 0),
            )

    @dataclass_json
    @dataclass
    class SpecialTransformerType(DataClassJsonMixin):
        """Special Transformer type properties."""

        sort: SpecialTransformerSort = SpecialTransformerSort.AUTO_YNA0_ASYM
        short_name: str = string_field()
        snom: float | int = 0
        unom1: float | int = optional_field(0)
        unom2: float | int = optional_field(0)
        ukmin: int | float = optional_field(0)
        uknom: int | float = optional_field(0)
        ukmax: int | float = optional_field(0)
        pkmin: float | int = optional_field(0)
        pknom: float | int = optional_field(0)
        pkmax: float | int = optional_field(0)
        po: float = optional_field(0)
        io: float = optional_field(0)
        R0: float | int = optional_field(0)
        Z0: float | int = optional_field(0)
        R0URo_min: int = optional_field(0)
        R0URo_nom: int = optional_field(0)
        R0URo_max: int = optional_field(0)
        Z0URo_min: int = optional_field(0)
        Z0URo_nom: int = optional_field(0)
        Z0URo_max: int = optional_field(0)
        R0URk_min: int = optional_field(0)
        R0URk_nom: int = optional_field(0)
        R0URk_max: int = optional_field(0)
        Z0URk_min: int = optional_field(0)
        Z0URk_nom: int = optional_field(0)
        Z0URk_max: int = optional_field(0)
        R0RUk_min: int = optional_field(0)
        R0RUk_nom: int = optional_field(0)
        R0RUk_max: int = optional_field(0)
        Z0RUk_min: int = optional_field(0)
        Z0RUk_nom: int = optional_field(0)
        Z0RUk_max: int = optional_field(0)
        ik2s: float | int = 0
        tap_side: int = 0
        tap_size: float = 0.25
        tap_min: int = 0
        tap_nom: int = 0
        tap_max: int = 0

        def serialize(self) -> str:
            """Serialize SpecialTransformerType properties."""
            return serialize_properties(
                write_integer("Sort", int(self.sort), skip=4),
                write_quote_string("ShortName", self.short_name),
                write_double_no_skip("Snom", self.snom),
                write_double("Unom1", self.unom1, skip=0),
                write_double("Unom2", self.unom2, skip=0),
                write_double("Ukmin", self.ukmin, skip=0),
                write_double("Uknom", self.uknom, skip=0),
                write_double("Ukmax", self.ukmax, skip=0),
                write_double("Pkmin", self.pkmin, skip=0),
                write_double("Pknom", self.pknom, skip=0),
                write_double("Pkmax", self.pkmax, skip=0),
                write_double("Po", self.po, skip=0),
                write_double("Io", self.io, skip=0),
                write_double("R0", self.R0, skip=0),
                write_double("Z0", self.Z0, skip=0),
                write_integer("R0URomin", self.R0URo_min, skip=0),
                write_integer("R0URonom", self.R0URo_nom, skip=0),
                write_integer("R0URomax", self.R0URo_max, skip=0),
                write_integer("Z0URomin", self.Z0URo_min, skip=0),
                write_integer("Z0URonom", self.Z0URo_nom, skip=0),
                write_integer("Z0URomax", self.Z0URo_max, skip=0),
                write_integer("R0URkmin", self.R0URk_min, skip=0),
                write_integer("R0URknom", self.R0URk_nom, skip=0),
                write_integer("R0URkmax", self.R0URk_max, skip=0),
                write_integer("Z0URkmin", self.Z0URk_min, skip=0),
                write_integer("Z0URknom", self.Z0URk_nom, skip=0),
                write_integer("Z0URkmax", self.Z0URk_max, skip=0),
                write_integer("R0RUkmin", self.R0RUk_min, skip=0),
                write_integer("R0RUknom", self.R0RUk_nom, skip=0),
                write_integer("R0RUkmax", self.R0RUk_max, skip=0),
                write_integer("Z0RUkmin", self.Z0RUk_min, skip=0),
                write_integer("Z0RUknom", self.Z0RUk_nom, skip=0),
                write_integer("Z0RUkmax", self.Z0RUk_max, skip=0),
                write_double_no_skip("Ik2s", self.ik2s),
                write_integer("TapSide", self.tap_side, skip=0),
                write_double_no_skip("TapSize", self.tap_size),
                write_integer("TapMin", self.tap_min, skip=0),
                write_integer("TapNom", self.tap_nom, skip=0),
                write_integer("TapMax", self.tap_max, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SpecialTransformerLV.SpecialTransformerType:
            """Deserialize SpecialTransformerType properties."""
            return cls(
                sort=SpecialTransformerSort(int(data.get("Sort", 4))),
                short_name=data.get("ShortName", ""),
                snom=data.get("Snom", 0),
                unom1=data.get("Unom1", 0),
                unom2=data.get("Unom2", 0),
                ukmin=data.get("Ukmin", 0),
                uknom=data.get("Uknom", 0),
                ukmax=data.get("Ukmax", 0),
                pkmin=data.get("Pkmin", 0),
                pknom=data.get("Pknom", 0),
                pkmax=data.get("Pkmax", 0),
                po=data.get("Po", 0),
                io=data.get("Io", 0),
                R0=data.get("R0", 0),
                Z0=data.get("Z0", 0),
                R0URo_min=data.get("R0URomin", 0),
                R0URo_nom=data.get("R0URonom", 0),
                R0URo_max=data.get("R0URomax", 0),
                Z0URo_min=data.get("Z0URomin", 0),
                Z0URo_nom=data.get("Z0URonom", 0),
                Z0URo_max=data.get("Z0URomax", 0),
                R0URk_min=data.get("R0URkmin", 0),
                R0URk_nom=data.get("R0URknom", 0),
                R0URk_max=data.get("R0URkmax", 0),
                Z0URk_min=data.get("Z0URkmin", 0),
                Z0URk_nom=data.get("Z0URknom", 0),
                Z0URk_max=data.get("Z0URkmax", 0),
                R0RUk_min=data.get("R0RUkmin", 0),
                R0RUk_nom=data.get("R0RUknom", 0),
                R0RUk_max=data.get("R0RUkmax", 0),
                Z0RUk_min=data.get("Z0RUkmin", 0),
                Z0RUk_nom=data.get("Z0RUknom", 0),
                Z0RUk_max=data.get("Z0RUkmax", 0),
                ik2s=data.get("Ik2s", 0),
                tap_side=data.get("TapSide", 0),
                tap_size=data.get("TapSize", 0.25),
                tap_min=data.get("TapMin", 0),
                tap_nom=data.get("TapNom", 0),
                tap_max=data.get("TapMax", 0),
            )

    general: General
    presentations: list[BranchPresentation]
    type: SpecialTransformerType
    voltage_control: VoltageControl | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add special transformer to the network."""
        if self.general.guid in network.special_transformers:
            logger.critical("Special Transformer %s already exists, overwriting", self.general.guid)
        network.special_transformers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the special transformer to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.voltage_control:
            lines.append(f"#VoltageControl {self.voltage_control.serialize()}")

        if self.type:
            lines.append(f"#SpecialTransformerType {self.type.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SpecialTransformerLV:
        """Deserialization of the special transformer from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TSpecialTransformerLS: The deserialized special transformer

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        voltage_control = None
        if data.get("voltageControl"):
            voltage_control = cls.VoltageControl.deserialize(data["voltageControl"][0])

        special_transformertype_data = (
            data.get("specialTransformerType", [{}])[0] if data.get("specialTransformerType") else {}
        )
        special_transformer_type = cls.SpecialTransformerType.deserialize(special_transformertype_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=special_transformer_type,
            voltage_control=voltage_control,
        )
