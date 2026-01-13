"""Photovoltaics / Solar Panels / Solar Field (Element)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import (
    DEFAULT_PROFILE_GUID,
    NIL_GUID,
    Guid,
    config,
    decode_guid,
    encode_guid,
    optional_field,
    string_field,
)
from pyptp.elements.lv.shared import EfficiencyType
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_double,
    write_double_no_skip,
    write_guid,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.lv.shared import EfficiencyType, HarmonicsType
if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class PVLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a pv (LV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a pv."""

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
        single_phase: bool = False
        phase: int = 0
        scaling: float = 1000.0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        longitude: float = 0.0
        latitude: float = 0.0
        panel1_pnom: float = 0.0
        panel1_orientation: float = 0.0
        panel1_slope: float = 0.0
        panel2_pnom: float = 0.0
        panel2_orientation: float = 0.0
        panel2_slope: float = 0.0
        panel3_pnom: float = 0.0
        panel3_orientation: float = 0.0
        panel3_slope: float = 0.0
        harmonics_type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node),
                write_guid("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date),
                write_double("RevisionDate", self.revision_date),
                write_quote_string("Name", self.name),
                write_boolean("s_L1", self.s_L1),
                write_boolean("s_L2", self.s_L2),
                write_boolean("s_L3", self.s_L3),
                write_boolean("s_N", self.s_N),
                write_boolean("OnePhase", self.single_phase),
                write_quote_string("FieldName", self.field_name),
                write_integer("Phase", self.phase),
                write_double("Scaling", self.scaling),
                write_guid("Profile", self.profile),
                write_double("Longitude", self.longitude),
                write_double("Latitude", self.latitude),
                write_double("Panel1Pnom", self.panel1_pnom),
                write_double_no_skip("Panel1Orientation", self.panel1_orientation),
                write_double_no_skip("Panel1Slope", self.panel1_slope),
                write_double("Panel2Pnom", self.panel2_pnom),
                write_double_no_skip("Panel2Orientation", self.panel2_orientation),
                write_double_no_skip("Panel2Slope", self.panel2_slope),
                write_double("Panel3Pnom", self.panel3_pnom),
                write_double_no_skip("Panel3Orientation", self.panel3_orientation),
                write_double_no_skip("Panel3Slope", self.panel3_slope),
                write_quote_string("HarmonicsType", self.harmonics_type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVLV.General:
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
                single_phase=data.get("OnePhase", False),
                phase=data.get("Phase", 0),
                scaling=data.get("Scaling", 1000.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                longitude=data.get("Longitude", 0.0),
                latitude=data.get("Latitude", 0.0),
                panel1_pnom=data.get("Panel1Pnom", 0.0),
                panel1_orientation=data.get("Panel1Orientation", 0.0),
                panel1_slope=data.get("Panel1Slope", 0.0),
                panel2_pnom=data.get("Panel2Pnom", 0.0),
                panel2_orientation=data.get("Panel2Orientation", 0.0),
                panel2_slope=data.get("Panel2Slope", 0.0),
                panel3_pnom=data.get("Panel3Pnom", 0.0),
                panel3_orientation=data.get("Panel3Orientation", 0.0),
                panel3_slope=data.get("Panel3Slope", 0.0),
                harmonics_type=data.get("HarmonicsType", ""),
            )

    @dataclass_json
    @dataclass
    class Inverter(DataClassJsonMixin):
        """Inverter."""

        snom: float = 12.5
        efficiency_type: str = string_field()
        u_off: float = 0.0

        def serialize(self) -> str:
            """Serialize Inverter properties."""
            return serialize_properties(
                write_double_no_skip("Snom", self.snom),
                write_quote_string("EfficiencyType", self.efficiency_type),
                write_double("Uoff", self.u_off),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVLV.Inverter:
            """Deserialize Inverter properties."""
            return cls(
                snom=data.get("Snom", 12.5),
                efficiency_type=data.get("EfficiencyType", ""),
                u_off=data.get("Uoff", 0.0),
            )

    @dataclass_json
    @dataclass
    class QControl(DataClassJsonMixin):
        """Q control."""

        sort: int = optional_field(0)
        cos_ref: float = 0.0
        no_p_no_q: bool = False
        input1: float = 0.0
        output1: float = 0.0
        input2: float = 0.0
        output2: float = 0.0
        input3: float = 0.0
        output3: float = 0.0
        input4: float = 0.0
        output4: float = 0.0
        input5: float = 0.0
        output5: float = 0.0

        def serialize(self) -> str:
            """Serialize QControl properties."""
            return serialize_properties(
                write_integer("Sort", self.sort),
                write_double_no_skip("CosRef", self.cos_ref),
                write_double_no_skip("NoPNoQ", self.no_p_no_q),
                write_double_no_skip("Input1", self.input1),
                write_double_no_skip("Output1", self.output1),
                write_double_no_skip("Input2", self.input2),
                write_double_no_skip("Output2", self.output2),
                write_double_no_skip("Input3", self.input3),
                write_double_no_skip("Output3", self.output3),
                write_double_no_skip("Input4", self.input4),
                write_double_no_skip("Output4", self.output4),
                write_double_no_skip("Input5", self.input5),
                write_double_no_skip("Output5", self.output5),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVLV.QControl:
            """Deserialize QControl properties."""
            return cls(
                sort=data.get("Sort", 0),
                cos_ref=data.get("CosRef", 0.0),
                no_p_no_q=data.get("NoPNoQ", False),
                input1=data.get("Input1", 0.0),
                output1=data.get("Output1", 0.0),
                input2=data.get("Input2", 0.0),
                output2=data.get("Output2", 0.0),
                input3=data.get("Input3", 0.0),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
            )

    @dataclass_json
    @dataclass
    class PUControl(DataClassJsonMixin):
        """PU Control."""

        input1: float = 0.0
        output1: float = 0.0
        input2: float = 0.0
        output2: float = 0.0
        input3: float = 0.0
        output3: float = 0.0
        input4: float = 0.0
        output4: float = 0.0
        input5: float = 0.0
        output5: float = 0.0

        def serialize(self) -> str:
            """Serialize PUControl properties."""
            return serialize_properties(
                write_double_no_skip("Input1", self.input1),
                write_double_no_skip("Output1", self.output1),
                write_double_no_skip("Input2", self.input2),
                write_double_no_skip("Output2", self.output2),
                write_double_no_skip("Input3", self.input3),
                write_double_no_skip("Output3", self.output3),
                write_double_no_skip("Input4", self.input4),
                write_double_no_skip("Output4", self.output4),
                write_double_no_skip("Input5", self.input5),
                write_double_no_skip("Output5", self.output5),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PVLV.PUControl:
            """Deserialize PUControl properties."""
            return cls(
                input1=data.get("Input1", 0.0),
                output1=data.get("Output1", 0.0),
                input2=data.get("Input2", 0.0),
                output2=data.get("Output2", 0.0),
                input3=data.get("Input3", 0.0),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]
    inverter: Inverter
    efficiency_type: EfficiencyType | None = None
    q_control: QControl | None = None
    pu_control: PUControl | None = None
    harmonics: HarmonicsType | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add photovoltaics / solar energy generation to the network."""
        if self.general.guid in network.pvs:
            logger.critical("Pv %s already exists, overwriting", self.general.guid)
        network.pvs[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the pv to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.inverter:
            lines.append(f"#Inverter {self.inverter.serialize()}")

        if self.q_control:
            lines.append(f"#QControl {self.q_control.serialize()}")

        if self.pu_control:
            lines.append(f"#P(U)Control {self.pu_control.serialize()}")

        if self.efficiency_type:
            lines.append(f"#EfficiencyType {self.efficiency_type.serialize()}")

        if self.harmonics:
            lines.append(f"#HarmonicsType {self.harmonics.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> PVLV:
        """Deserialization of the pv from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TPvLS: The deserialized pv

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        inverter_data = data.get("inverter", [{}])[0] if data.get("inverter") else {}
        inverter = cls.Inverter.deserialize(inverter_data)

        efficiency_type = None
        if data.get("efficiency_type"):
            from .shared import EfficiencyType

            efficiency_type = EfficiencyType.deserialize(data["efficiency_type"][0])

        q_control = None
        if data.get("Qcontrol"):
            q_control = cls.QControl.deserialize(data["Qcontrol"][0])

        pu_control = None
        if data.get("PUcontrol"):
            pu_control = cls.PUControl.deserialize(data["PUcontrol"][0])

        harmonics = None
        if data.get("harmonics"):
            from .shared import HarmonicsType

            harmonics = HarmonicsType.deserialize(data["harmonics"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            inverter=inverter,
            efficiency_type=efficiency_type,
            q_control=q_control,
            pu_control=pu_control,
            harmonics=harmonics,
        )
