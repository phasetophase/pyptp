"""Low-voltage cable element for unbalanced network modeling.

Provides complex cable modeling with support for up to 9 conductors,
advanced impedance matrices, and nested connection modeling required
for accurate unbalanced load flow analysis in LV networks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast
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
    write_boolean,
    write_boolean_no_skip,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
    write_quote_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.lv.connection import ConnectionLV
    from pyptp.network_lv import NetworkLV
    from pyptp.type_reader import Types

    from .presentations import BranchPresentation
    from .shared import CableType, CurrentType, EfficiencyType, Fields, FuseType, GeoCablePart


@dataclass
class CableLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Low-voltage cable element with advanced conductor modeling.

    Supports complex impedance modeling for up to 9 conductors per cable
    (L1, L2, L3, N, PE, h1-h4) enabling accurate asymmetrical analysis
    and harmonic studies in LV distribution networks.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for LV cables.

        Encompasses all essential cable characteristics including connection
        nodes, switch states for all conductors, protection settings, and
        harmonic conductor configurations.
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
        failure_frequency: float = optional_field(0)
        new: bool = False
        loadrate_max: float = optional_field(0.0)
        k1_L1: int = 1  # noqa: N815
        k1_L2: int = 2  # noqa: N815
        k1_L3: int = 3  # noqa: N815
        k1_h1: int = 6
        k1_h2: int = 7
        k1_h3: int = 8
        k1_h4: int = 9
        k2_L1: int = 1  # noqa: N815
        k2_L2: int = 2  # noqa: N815
        k2_L3: int = 3  # noqa: N815
        k2_h1: int = 6
        k2_h2: int = 7
        k2_h3: int = 8
        k2_h4: int = 9

        switch_state1_h1: bool = True
        switch_state1_h2: bool = True
        switch_state1_h3: bool = True
        switch_state1_h4: bool = True
        switch_state2_h1: bool = True
        switch_state2_h2: bool = True
        switch_state2_h3: bool = True
        switch_state2_h4: bool = True

        protection_type1_h1: str = string_field()
        protection_type1_h2: str = string_field()
        protection_type1_h3: str = string_field()
        protection_type1_h4: str = string_field()

        protection_type2_h1: str = string_field()
        protection_type2_h2: str = string_field()
        protection_type2_h3: str = string_field()
        protection_type2_h4: str = string_field()

        def serialize(self) -> str:
            """Serialize cable general properties to GNF format.

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
                write_boolean("New", value=self.new),
                write_double("LoadrateMax", self.loadrate_max),
                write_integer_no_skip("k1_L1", self.k1_L1),
                write_integer_no_skip("k1_L2", self.k1_L2),
                write_integer_no_skip("k1_L3", self.k1_L3),
                write_integer_no_skip("k1_h1", self.k1_h1),
                write_integer_no_skip("k1_h2", self.k1_h2),
                write_integer_no_skip("k1_h3", self.k1_h3),
                write_integer_no_skip("k1_h4", self.k1_h4),
                write_integer_no_skip("k2_L1", self.k2_L1),
                write_integer_no_skip("k2_L2", self.k2_L2),
                write_integer_no_skip("k2_L3", self.k2_L3),
                write_integer_no_skip("k2_h1", self.k2_h1),
                write_integer_no_skip("k2_h2", self.k2_h2),
                write_integer_no_skip("k2_h3", self.k2_h3),
                write_integer_no_skip("k2_h4", self.k2_h4),
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
        def deserialize(cls, data: dict) -> CableLV.General:
            """Parse cable general properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed cable properties.

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
                new=data.get("New", False),
                loadrate_max=data.get("LoadrateMax", 0.0),
                k1_L1=data.get("k1_L1", 1),
                k1_L2=data.get("k1_L2", 2),
                k1_L3=data.get("k1_L3", 3),
                k1_h1=data.get("k1_h1", 6),
                k1_h2=data.get("k1_h2", 7),
                k1_h3=data.get("k1_h3", 8),
                k1_h4=data.get("k1_h4", 9),
                k2_L1=data.get("k2_L1", 1),
                k2_L2=data.get("k2_L2", 2),
                k2_L3=data.get("k2_L3", 3),
                k2_h1=data.get("k2_h1", 6),
                k2_h2=data.get("k2_h2", 7),
                k2_h3=data.get("k2_h3", 8),
                k2_h4=data.get("k2_h4", 9),
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

    @dataclass
    class CablePart(DataClassJsonMixin):
        """Physical cable segment properties.

        Defines the physical characteristics of a cable segment including
        length and cable type for impedance calculations.
        """

        length: float | int = 0.5
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize cable part properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return (
                serialize_properties(
                    write_double_no_skip("Length", self.length),
                    write_quote_string("CableType", self.type),
                )
                + " "
            )

        @classmethod
        def deserialize(cls, data: dict) -> CableLV.CablePart:
            """Parse cable part properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized CablePart instance with parsed segment properties.

            """
            return cls(
                length=data.get("Length", 0.5),
                type=data.get("CableType", ""),
            )

    @dataclass
    class CableConnections(DataClassJsonMixin):
        """Configuration for nested connections along cable segments.

        Defines spacing and quantity parameters for service connections
        distributed along the cable route in typical residential applications.
        """

        first_distance: int = 0
        between_distance: int = 0
        remaining_distance: int = 0
        number_of: int = 0

        def serialize(self) -> str:
            """Serialize cable connections properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return (
                serialize_properties(
                    write_integer_no_skip("FirstDistance", self.first_distance),
                    write_integer_no_skip("BetweenDistance", self.between_distance),
                    write_integer_no_skip("RemainingDistance", self.remaining_distance),
                    write_integer_no_skip("NumberOf", self.number_of),
                )
                + " "
            )

        @classmethod
        def deserialize(cls, data: dict) -> CableLV.CableConnections:
            """Parse cable connections properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized CableConnections instance with parsed configuration.

            """
            return cls(
                first_distance=data.get("FirstDistance", 0),
                between_distance=data.get("BetweenDistance", 0),
                remaining_distance=data.get("RemainingDistance", 0),
                number_of=data.get("NumberOf", 0),
            )

    @dataclass
    class CableConnection(DataClassJsonMixin):
        """Individual service connection nested within cable segment.

        Represents a single customer connection point along the cable route
        with detailed conductor configurations and earthing parameters.
        """

        name: str = string_field()
        s_L1: bool = True  # noqa: N815
        s_L2: bool = True  # noqa: N815
        s_L3: bool = True  # noqa: N815
        s_N: bool = True  # noqa: N815
        field_name: str = string_field()
        s_PE: bool = True  # noqa: N815
        k_L1: int = 1  # noqa: N815
        k_L2: int = 2  # noqa: N815
        k_L3: int = 3  # noqa: N815
        length: int | float = 0
        cable_type: str = string_field()

        earthing_configuration: str = string_field()
        s_Nh_PEh: bool = False  # noqa: N815
        s_PEh_PEh: bool = True  # noqa: N815
        s_PEh_e: bool = True  # noqa: N815
        re: int | float = 0
        s_Hh: bool = True  # noqa: N815
        s_h1_h3: bool = True
        s_h2_h4: bool = True
        phases: int = 0
        sort: str = string_field()

        protection_type: str = string_field()
        connection_value: str = string_field()
        iearthleak: int = 0
        risk: bool = False
        address: str = string_field()
        postal_code: str = string_field()
        city: str = string_field()

        def serialize(self) -> str:
            """Serialize cable connection properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_quote_string_no_skip("Name", self.name),
                write_boolean_no_skip("s_L1", value=self.s_L1),
                write_boolean_no_skip("s_L2", value=self.s_L2),
                write_boolean_no_skip("s_L3", value=self.s_L3),
                write_boolean_no_skip("s_N", value=self.s_N),
                write_quote_string("FieldName", self.field_name),
                write_boolean_no_skip("s_PE", value=self.s_PE),
                write_integer_no_skip("k_L1", self.k_L1),
                write_integer_no_skip("k_L2", self.k_L2),
                write_integer_no_skip("k_L3", self.k_L3),
                write_double_no_skip("Length", self.length),
                write_quote_string("CableType", self.cable_type),
                write_quote_string("EarthingConfiguration", self.earthing_configuration),
                write_boolean("s_Nh_PEh", value=self.s_Nh_PEh),
                write_boolean("s_PEh_PEh", value=self.s_PEh_PEh),
                write_boolean("s_PEh_e", value=self.s_PEh_e),
                write_double("Re", self.re),
                write_boolean("s_Hh", value=self.s_Hh),
                write_quote_string("ProtectionType", value=self.protection_type),
                write_boolean("s_h1_h3", value=self.s_h1_h3),
                write_boolean("s_h2_h4", value=self.s_h2_h4),
                write_integer_no_skip("Phases", self.phases),
                write_quote_string("Sort", self.sort),
                write_quote_string("ConnectionValue", value=self.connection_value),
                write_integer("Iearthleak", value=self.iearthleak),
                write_boolean("Risk", value=self.risk),
                write_quote_string("Address", self.address),
                write_quote_string("PostalCode", self.postal_code),
                write_quote_string("City", self.city),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CableLV.CableConnection:
            """Parse cable connection properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized CableConnection instance with parsed connection data.

            """
            return cls(
                name=data.get("Name", ""),
                s_L1=data.get("s_L1", True),
                s_L2=data.get("s_L2", True),
                s_L3=data.get("s_L3", True),
                s_N=data.get("s_N", True),
                field_name=data.get("FieldName", ""),
                s_PE=data.get("s_PE", True),
                k_L1=data.get("k_L1", 1),
                k_L2=data.get("k_L2", 2),
                k_L3=data.get("k_L3", 3),
                length=data.get("Length", 0),
                cable_type=data.get("CableType", ""),
                earthing_configuration=data.get("EarthingConfiguration", ""),
                s_Nh_PEh=data.get("s_Nh_PEh", False),
                s_PEh_PEh=data.get("s_PEh_PEh", True),
                s_PEh_e=data.get("s_PEh_e", False),
                re=data.get("Re", 0),
                s_Hh=data.get("s_Hh", True),
                s_h1_h3=data.get("s_h1_h3", False),
                s_h2_h4=data.get("s_h2_h4", False),
                phases=data.get("Phases", 0),
                sort=data.get("Sort", ""),
                address=data.get("Address", ""),
                postal_code=data.get("PostalCode", ""),
                city=data.get("City", ""),
                protection_type=data.get("ProtectionType", ""),
                connection_value=data.get("ConnectionValue", ""),
                iearthleak=data.get("Iearthleak", 0),
                risk=data.get("Risk", False),
            )

    general: General
    presentations: list[BranchPresentation]

    cable_part: CablePart
    cable_type: CableType | None = None

    geography: GeoCablePart | None = None
    cablepart_geography: GeoCablePart | None = None

    fuse_type: FuseType | None = None

    fuse1_h1: FuseType | None = None
    fuse1_h2: FuseType | None = None
    fuse1_h3: FuseType | None = None
    fuse1_h4: FuseType | None = None

    fuse2_h1: FuseType | None = None
    fuse2_h2: FuseType | None = None
    fuse2_h3: FuseType | None = None
    fuse2_h4: FuseType | None = None

    current1_h1: CurrentType | None = None
    current1_h2: CurrentType | None = None
    current1_h3: CurrentType | None = None
    current1_h4: CurrentType | None = None

    current2_h1: CurrentType | None = None
    current2_h2: CurrentType | None = None
    current2_h3: CurrentType | None = None
    current2_h4: CurrentType | None = None

    cable_connections: list[CableConnections] = field(default_factory=list)
    cable_connection: list[CableConnection] = field(default_factory=list)
    connection_cable_type: list[CableType] = field(default_factory=list)

    load: ConnectionLV.Load | None = None
    pl: ConnectionLV.PL | None = None
    pl_type: ConnectionLV.PLType | None = None
    heatpump: ConnectionLV.Heatpump | None = None
    generation: ConnectionLV.Generation | None = None

    pv: ConnectionLV.PV | None = None
    pv_efficiency: EfficiencyType | None = None
    wind_turbine: ConnectionLV.WindTurbine | None = None
    wind_turbine_efficiency: EfficiencyType | None = None

    battery: ConnectionLV.Battery | None = None
    battery_charge_efficiency: EfficiencyType | None = None
    battery_discharge_efficiency: EfficiencyType | None = None

    fields: Fields | None = None

    def __post_init__(self) -> None:
        """Initialize mixins after dataclass instantiation.

        Ensures proper initialization of ExtrasNotesMixin and
        HasPresentationsMixin for consistent element behavior.
        """
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def set_cable(self, default_types: Types, cable_type: str) -> None:
        """Set `cable_type` from the Excel-backed types provider by name.

        Args:
            default_types: Type library containing cable specifications.
            cable_type: Cable type identifier to apply to this cable.

        Warns:
            Logs critical warning if specified cable type not found in library.

        """
        obj = default_types.get_lv_cable(cable_type)
        if obj is None:
            logger.critical("Cabletype %s not found", cable_type)
            return

        typed = cast("CableType", obj)
        self.cable_part.type = typed.short_name or cable_type
        self.cable_type = typed

    def register(self, network: NetworkLV) -> None:
        """Register cable in LV network with GUID-based indexing.

        Args:
            network: Target LV network for cable registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.cables:
            logger.critical("Cable %s already exists, overwriting", self.general.guid)
        network.cables[self.general.guid] = self

    def serialize(self) -> str:  # noqa: C901, PLR0912
        """Serialize complete cable to GNF format.

        Returns:
            Multi-line string with all cable sections for GNF file output.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.append(f"#CablePart {self.cable_part.serialize()}")

        if self.cable_type:
            lines.append(f"#CableType {self.cable_type.serialize()}")

        if self.cablepart_geography:
            lines.append(f"#GeoCablePart {self.cablepart_geography.serialize()}")

        if self.geography:
            lines.append(f"#Geo {self.geography.serialize()}")

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

        if self.current1_h1 is not None:
            lines.append(f"#CurrentType1_h1 {self.current1_h1.serialize()}")

        if self.current1_h2 is not None:
            lines.append(f"#CurrentType1_h2 {self.current1_h2.serialize()}")

        if self.current1_h3 is not None:
            lines.append(f"#CurrentType1_h3 {self.current1_h3.serialize()}")

        if self.current1_h4 is not None:
            lines.append(f"#CurrentType1_h4 {self.current1_h4.serialize()}")

        if self.current2_h1 is not None:
            lines.append(f"#CurrentType2_h1 {self.current2_h1.serialize()}")

        if self.current2_h2 is not None:
            lines.append(f"#CurrentType2_h2 {self.current2_h2.serialize()}")

        if self.current2_h3 is not None:
            lines.append(f"#CurrentType2_h3 {self.current2_h3.serialize()}")

        if self.current2_h4 is not None:
            lines.append(f"#CurrentType2_h4 {self.current2_h4.serialize()}")

        for _, (cable_connections, cable_connection, connection_cable_type) in enumerate(
            zip(self.cable_connections, self.cable_connection, self.connection_cable_type, strict=False)
        ):
            lines.append(f"#CableConnections {cable_connections.serialize()}")
            lines.append(f"#CableConnection {cable_connection.serialize()}")
            lines.append(f"#ConnectionCableType {connection_cable_type.serialize()}")

        if self.fields is not None:
            lines.append(f"#Fields {self.fields.serialize()}")

        if self.fuse_type:
            lines.append(f"#FuseType {self.fuse_type.serialize()}")

        if self.load:
            lines.append(f"#Load {self.load.serialize()}")

        if self.pl:
            lines.append(f"#PL {self.pl.serialize()}")

        if self.pl_type:
            lines.append(f"#PLType {self.pl_type.serialize()}")

        if self.heatpump:
            lines.append(f"#Heatpump {self.heatpump.serialize()}")

        if self.generation:
            lines.append(f"#Generation {self.generation.serialize()}")

        if self.pv:
            lines.append(f"#PV {self.pv.serialize()}")

        if self.pv_efficiency:
            lines.append(f"#PVInverterEfficiencyType {self.pv_efficiency.serialize()}")

        if self.wind_turbine:
            lines.append(f"#WindTurbine {self.wind_turbine.serialize()}")

        if self.wind_turbine_efficiency:
            lines.append(f"#WindTurbineInverterEfficiencyType {self.wind_turbine_efficiency.serialize()}")

        if self.battery:
            lines.append(f"#Battery {self.battery.serialize()}")

        if self.battery_charge_efficiency:
            lines.append(f"#BatteryChargeEfficiency {self.battery_charge_efficiency.serialize()}")

        if self.battery_discharge_efficiency:
            lines.append(f"#BatteryDischargeEfficiency {self.battery_discharge_efficiency.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.safe_extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.safe_notes)
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> CableLV:
        """Create cable instance from parsed GNF data.

        Args:
            data: Dictionary containing parsed GNF sections for cable element.

        Returns:
            Fully initialized TCableLS instance with all properties and
            sub-components properly deserialized.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        cable_part_data = data.get("cable_part", [{}])[0] if data.get("cable_part") else {}
        cable_part = cls.CablePart.deserialize(cable_part_data)

        cable_type_data = data.get("cable_type", [{}])[0] if data.get("cable_type") else {}
        cable_type = None
        if cable_type_data:
            from .shared import CableType

            cable_type = CableType.deserialize(cable_type_data)
        else:
            # Create default CableType if none provided
            from .shared import CableType

            cable_type = CableType(short_name="")

        cablepart_geography_data = data.get("cablepart_geography", [{}])[0] if data.get("cablepart_geography") else None
        cablepart_geography = None
        if cablepart_geography_data:
            from .shared import GeoCablePart

            cablepart_geography = GeoCablePart.deserialize(cablepart_geography_data)

        # Deserialize harmonic conductor fuse and current types
        from .shared import CurrentType, FuseType

        def deserialize_optional_type(type_cls: type[Any], field_names: list[str]) -> dict[str, Any | None]:
            """Deserialize optional type instances for harmonic conductor components.

            Args:
                type_cls: Type class to instantiate for non-empty data.
                field_names: List of field names to process from parsed data.

            Returns:
                Dictionary mapping field names to deserialized instances or None.

            """
            result: dict[str, Any | None] = {}
            for field_name in field_names:
                if data.get(field_name):
                    # type: ignore[assignment]
                    result[field_name] = type_cls.deserialize(data[field_name][0])
                else:
                    result[field_name] = None
            return result

        fuse_fields = [
            "fuse1_h1",
            "fuse1_h2",
            "fuse1_h3",
            "fuse1_h4",
            "fuse2_h1",
            "fuse2_h2",
            "fuse2_h3",
            "fuse2_h4",
        ]
        fuse_types = deserialize_optional_type(FuseType, fuse_fields)

        current_fields = [
            "current1_h1",
            "current1_h2",
            "current1_h3",
            "current1_h4",
            "current2_h1",
            "current2_h2",
            "current2_h3",
            "current2_h4",
        ]
        current_types = deserialize_optional_type(CurrentType, current_fields)

        # Deserialize optional fields section
        fields = None
        if data.get("fields"):
            from .shared import Fields

            fields = Fields.deserialize(data["fields"][0])

        cable_connection = data.get("cable_connection", [])
        cable_connections = data.get("cable_connections", [])
        connection_cable_type = data.get("connection_cable_type", [])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            cable_part=cable_part,
            cable_type=cable_type,
            cablepart_geography=cablepart_geography,
            cable_connection=cable_connection,
            cable_connections=cable_connections,
            connection_cable_type=connection_cable_type,
            fields=fields,
            fuse1_h1=fuse_types["fuse1_h1"],
            fuse1_h2=fuse_types["fuse1_h2"],
            fuse1_h3=fuse_types["fuse1_h3"],
            fuse1_h4=fuse_types["fuse1_h4"],
            fuse2_h1=fuse_types["fuse2_h1"],
            fuse2_h2=fuse_types["fuse2_h2"],
            fuse2_h3=fuse_types["fuse2_h3"],
            fuse2_h4=fuse_types["fuse2_h4"],
            current1_h1=current_types["current1_h1"],
            current1_h2=current_types["current1_h2"],
            current1_h3=current_types["current1_h3"],
            current1_h4=current_types["current1_h4"],
            current2_h1=current_types["current2_h1"],
            current2_h2=current_types["current2_h2"],
            current2_h3=current_types["current2_h3"],
            current2_h4=current_types["current2_h4"],
        )
