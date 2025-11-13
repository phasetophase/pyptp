"""Low-voltage transformer element for asymmetrical network modeling.

Provides complex transformer modeling with detailed impedance characteristics,
voltage control capabilities, and multiple winding configurations required
for accurate unbalanced load flow analysis in LV networks.
"""

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
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean_no_skip,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import BranchPresentation


@dataclass_json
@dataclass
class TransformerLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Low-voltage transformer element with advanced modeling capabilities.

    Supports complex impedance modeling, tap changing, voltage control,
    and detailed electrical parameter specifications for accurate
    asymmetrical analysis in LV distribution networks.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for LV transformers.

        Encompasses all essential transformer characteristics including
        connection nodes, switch states, tap position, and control parameters.
        """

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
        clock_number: int = optional_field(0)
        loadrate_max: float = optional_field(0)

        def serialize(self) -> str:
            """Serialize transformer general properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
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
                write_quote_string("TransformerType", self.type),
                write_boolean_no_skip("SwitchState_N_PE", value=self.switch_state_N_PE),
                write_boolean_no_skip("SwitchState_PE_e", value=self.switch_state_PE_e),
                write_double("Re", self.re),
                write_double_no_skip("TapPosition", self.tap_position),
                write_integer("ClockNumber", self.clock_number),
                write_double("LoadrateMax", self.loadrate_max),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerLV.General:
            """Parse transformer general properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed transformer properties.

            """
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
                type=data.get("TransformerType", ""),
                switch_state_N_PE=data.get("SwitchState_N_PE", False),
                switch_state_PE_e=data.get("SwitchState_PE_e", False),
                re=data.get("Re", 0),
                tap_position=data.get("TapPosition", 0),
                clock_number=data.get("ClockNumber", 0),
                loadrate_max=data.get("LoadrateMax", 0),
            )

    @dataclass_json
    @dataclass
    class VoltageControl(DataClassJsonMixin):
        """Automatic voltage control configuration for transformer operation.

        Defines control parameters for tap-changing transformers including
        setpoints, deadbands, and compounding settings for voltage regulation.
        """

        own_control: bool = False
        control_status: int = optional_field(0)
        measure_side: int = 3
        control_node: str = string_field()
        setpoint: float = optional_field(0)
        deadband: float = optional_field(0)
        control_sort: int = optional_field(0)
        Rc: float = optional_field(0)
        Xc: float = optional_field(0)
        compounding_at_generation: bool = True
        p_min1: int = optional_field(0)
        u_min1: float = optional_field(0)
        p_max1: int = optional_field(0)
        u_max1: float = optional_field(0)

        def serialize(self) -> str:
            """Serialize voltage control properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_boolean_no_skip("OwnControl", value=self.own_control),
                write_integer("ControlStatus", self.control_status),
                write_integer_no_skip("MeasureSide", self.measure_side),
                write_quote_string("ControlNode", self.control_node),
                write_double("Setpoint", self.setpoint),
                write_double("Deadband", self.deadband),
                write_integer("ControlSort", self.control_sort),
                write_double("Rc", self.Rc),
                write_double("Xc", self.Xc),
                write_boolean_no_skip("CompoundingAtGeneration", value=self.compounding_at_generation),
                write_integer("Pmin1", self.p_min1),
                write_double("Umin1", self.u_min1),
                write_integer("Pmax1", self.p_max1),
                write_double("Umax1", self.u_max1),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerLV.VoltageControl:
            """Parse voltage control properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized VoltageControl instance with parsed control parameters.

            """
            return cls(
                own_control=data.get("OwnControl", False),
                control_status=data.get("ControlStatus", 0),
                measure_side=data.get("MeasureSide", 3),
                control_node=data.get("ControlNode", ""),
                setpoint=data.get("Setpoint", 0),
                deadband=data.get("Deadband", 0),
                control_sort=data.get("ControlSort", 0),
                Rc=data.get("Rc", 0),
                Xc=data.get("Xc", 0),
                compounding_at_generation=data.get("CompoundingAtGeneration", True),
                p_min1=data.get("Pmin1", 0),
                u_min1=data.get("Umin1", 0),
                p_max1=data.get("Pmax1", 0),
                u_max1=data.get("Umax1", 0),
            )

    @dataclass_json
    @dataclass
    class TransformerType(DataClassJsonMixin):
        """Electrical specifications and parameters for transformer modeling.

        Defines comprehensive transformer characteristics including impedances,
        losses, winding configurations, and tap changer specifications required
        for accurate power flow and short-circuit analysis.
        """

        short_name: str = string_field()
        snom: float | int = 0.0
        unom1: float | int = 0.0
        unom2: float | int = 0.0
        Uk: int | float = 0.0
        Pk: float | int = 0.0
        Po: float = 0.0
        Io: float = optional_field(0)
        R0: float | int = optional_field(0)
        Z0: float | int = optional_field(0)
        ik2s: float | int = optional_field(0)
        winding_connection1: str = field(default="D", metadata=config(encoder=encode_string))
        winding_connection2: str = field(default="YN", metadata=config(encoder=encode_string))
        clock_number: int = 5
        tap_side: int = 1
        tap_size: float = 0.25
        tap_min: int = 0
        tap_nom: int = 0
        tap_max: int = 0
        ki: int | float = 0
        tau: int | float = 0
        controllable: bool = False

        def serialize(self) -> str:
            """Serialize transformer type properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_quote_string("ShortName", self.short_name),
                write_double_no_skip("Snom", self.snom),
                write_double_no_skip("Unom1", self.unom1),
                write_double_no_skip("Unom2", self.unom2),
                write_double_no_skip("Uk", self.Uk),
                write_double_no_skip("Pk", self.Pk),
                write_double_no_skip("Po", self.Po),
                write_double("Io", self.Io),
                write_double("R0", self.R0),
                write_double("Z0", self.Z0),
                write_double("Ik2s", self.ik2s),
                write_quote_string("WindingConnection1", self.winding_connection1),
                write_quote_string("WindingConnection2", self.winding_connection2),
                write_integer_no_skip("ClockNumber", self.clock_number),
                write_integer_no_skip("TapSide", self.tap_side),
                write_double_no_skip("TapSize", self.tap_size),
                write_integer_no_skip("TapMin", self.tap_min),
                write_integer_no_skip("TapNom", self.tap_nom),
                write_integer_no_skip("TapMax", self.tap_max),
                write_double_no_skip("Ki", self.ki),
                write_double_no_skip("Tau", self.tau),
                write_boolean_no_skip("Controllable", value=self.controllable),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerLV.TransformerType:
            """Parse transformer type properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized TransformerType instance with parsed specifications.

            """
            return cls(
                short_name=data.get("ShortName", ""),
                snom=data.get("Snom", 0.0),
                unom1=data.get("Unom1", 0.0),
                unom2=data.get("Unom2", 0.0),
                Uk=data.get("Uk", 0.0),
                Pk=data.get("Pk", 0.0),
                Po=data.get("Po", 0.0),
                Io=data.get("Io", 0),
                R0=data.get("R0", 0),
                Z0=data.get("Z0", 0),
                ik2s=data.get("Ik2s", 0),
                winding_connection1=data.get("WindingConnection1", "D"),
                winding_connection2=data.get("WindingConnection2", "YN"),
                clock_number=data.get("ClockNumber", 5),
                tap_side=data.get("TapSide", 1),
                tap_size=data.get("TapSize", 0.25),
                tap_min=data.get("TapMin", 0),
                tap_nom=data.get("TapNom", 0),
                tap_max=data.get("TapMax", 0),
                ki=data.get("Ki", 0),
                tau=data.get("Tau", 0),
                controllable=data.get("Controllable", False),
            )

    general: General
    presentations: list[BranchPresentation]
    type: TransformerType
    voltage_control: VoltageControl | None = None

    def __post_init__(self) -> None:
        """Initialize mixins after dataclass instantiation.

        Ensures proper initialization of ExtrasNotesMixin and
        HasPresentationsMixin for consistent element behavior.
        """
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Register transformer in LV network with GUID-based indexing.

        Args:
            network: Target LV network for transformer registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.transformers:
            logger.critical("Transformer %s already exists, overwriting", self.general.guid)
        network.transformers[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete transformer to GNF format.

        Returns:
            Multi-line string with all transformer sections for GNF file output.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.voltage_control:
            lines.append(f"#VoltageControl {self.voltage_control.serialize()}")

        if self.type:
            lines.append(f"#TransformerType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        # Serialize extras and notes using safe accessors
        lines.extend(f"#Extra Text:{extra.text}" for extra in self.safe_extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.safe_notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> TransformerLV:
        """Create transformer instance from parsed GNF data.

        Args:
            data: Dictionary containing parsed GNF sections for transformer element.

        Returns:
            Fully initialized TTransformerLS instance with all properties and
            sub-components properly deserialized.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        voltage_control = None
        if data.get("voltageControl"):
            voltage_control = cls.VoltageControl.deserialize(data["voltageControl"][0])

        transformer_type_data = data.get("transformerType", [{}])[0] if data.get("transformerType") else {}
        transformer_type = cls.TransformerType.deserialize(transformer_type_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=transformer_type,
            voltage_control=voltage_control,
        )
