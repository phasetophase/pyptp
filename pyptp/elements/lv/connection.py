"""Home / Connection (Element)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.element_utils import (
    DEFAULT_PROFILE_GUID,
    NIL_GUID,
    FloatCoords,
    Guid,
    config,
    decode_float_coords,
    decode_guid,
    encode_float_coords,
    encode_guid,
    encode_string,
    optional_field,
    string_field,
)
from pyptp.elements.lv.shared import CableType
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
    from pyptp.elements.lv.shared import CurrentType, EfficiencyType, FuseType
if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV

    from .presentations import ElementPresentation


@dataclass
class ConnectionLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a home / connection (LV)."""

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a home."""

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
        s_PE: bool = True  # noqa: N815
        k_L1: int = 1  # noqa: N815
        k_L2: int = 2  # noqa: N815
        k_L3: int = 3  # noqa: N815
        length: float | int = optional_field(0.0)
        cable_type: str = string_field()
        earthing_configuration: str = string_field()
        s_Nh_PEh: bool = False  # noqa: N815
        s_PEh_PEh: bool = True  # noqa: N815
        s_PEh_e: bool = False  # noqa: N815
        re: float | int = optional_field(0.0)
        s_Hh: bool = True  # noqa: N815
        protection_type: str = string_field()
        s_h1_h3: bool = False
        s_h2_h4: bool = False
        phases: int = 4
        sort: str = string_field()
        connection_value: str = string_field()
        i_earthleak: int | float = optional_field(0.0)
        risk: bool = False
        geo_x_coord: float | int = optional_field(0.0)
        geo_y_coord: float | int = optional_field(0.0)
        address: str = string_field()
        postal_code: str = string_field()
        city: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties to a string."""
            return serialize_properties(
                write_guid("Node", self.node),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_quote_string("Name", self.name),
                write_boolean("s_L1", value=self.s_L1),
                write_boolean("s_L2", value=self.s_L2),
                write_boolean("s_L3", value=self.s_L3),
                write_boolean("s_N", value=self.s_N),
                write_quote_string("FieldName", self.field_name),
                write_boolean("s_PE", value=self.s_PE),
                write_integer("k_L1", self.k_L1),
                write_integer("k_L2", self.k_L2),
                write_integer("k_L3", self.k_L3),
                write_double_no_skip("Length", self.length),
                write_quote_string("CableType", self.cable_type),
                write_quote_string("EarthingConfiguration", self.earthing_configuration),
                write_boolean("s_Nh_PEh", value=self.s_Nh_PEh),
                write_boolean("s_PEh_PEh", value=self.s_PEh_PEh),
                write_boolean("s_PEh_e", value=self.s_PEh_e),
                write_double("Re", self.re, skip=0.0),
                write_boolean("s_Hh", value=self.s_Hh),
                write_quote_string("ProtectionType", value=self.protection_type),
                write_boolean("s_h1_h3", value=self.s_h1_h3),
                write_boolean("s_h2_h4", value=self.s_h2_h4),
                write_integer("Phases", self.phases),
                write_quote_string("Sort", self.sort),
                write_quote_string("ConnectionValue", self.connection_value),
                write_double("Iearthleak", self.i_earthleak, skip=0.0),
                write_boolean("Risk", value=self.risk),
                write_double("GX", self.geo_x_coord, skip=0.0),
                write_double("GY", self.geo_y_coord, skip=0.0),
                write_quote_string("Address", self.address),
                write_quote_string("PostalCode", self.postal_code),
                write_quote_string("City", self.city),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.General:
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
                s_PE=data.get("s_PE", True),
                k_L1=data.get("k_L1", 1),
                k_L2=data.get("k_L2", 2),
                k_L3=data.get("k_L3", 3),
                length=data.get("Length", 0.0),
                cable_type=data.get("CableType", ""),
                earthing_configuration=data.get("EarthingConfiguration", ""),
                s_Nh_PEh=data.get("s_Nh_PEh", False),
                s_PEh_PEh=data.get("s_PEh_PEh", True),
                s_PEh_e=data.get("s_PEh_e", False),
                re=data.get("Re", 0.0),
                s_Hh=data.get("s_Hh", True),
                protection_type=data.get("ProtectionType", ""),
                s_h1_h3=data.get("s_h1_h3", False),
                s_h2_h4=data.get("s_h2_h4", False),
                phases=data.get("Phases", 4),
                sort=data.get("Sort", ""),
                connection_value=data.get("ConnectionValue", ""),
                i_earthleak=data.get("Iearthleak", 0.0),
                risk=data.get("Risk", False),
                geo_x_coord=data.get("GX", 0.0),
                geo_y_coord=data.get("GY", 0.0),
                address=data.get("Address", ""),
                postal_code=data.get("PostalCode", ""),
                city=data.get("City", ""),
            )

    @dataclass
    class Load(DataClassJsonMixin):
        """Load of a home/connection."""

        p1: float = 0.0
        q1: float = 0.0
        pa: float = 0.0
        qa: float = 0.0
        pb: float = 0.0
        qb: float = 0.0
        pc: float = 0.0
        qc: float = 0.0
        pab: float = 0.0
        qab: float = 0.0
        pac: float = 0.0
        qac: float = 0.0
        pbc: float = 0.0
        qbc: float = 0.0
        behaviour_sort: str = string_field()
        switch_on_frequency: float = 0.0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize Load properties to a string."""
            return serialize_properties(
                write_double("P1", self.p1),
                write_double("Q1", self.q1),
                write_double("Pa", self.pa),
                write_double("Qa", self.qa),
                write_double("Pb", self.pb),
                write_double("Qb", self.qb),
                write_double("Pc", self.pc),
                write_double("Qc", self.qc),
                write_double("Pab", self.pab),
                write_double("Qab", self.qab),
                write_double("Pac", self.pac),
                write_double("Qac", self.qac),
                write_double("Pbc", self.pbc),
                write_double("Qbc", self.qbc),
                write_quote_string("BehaviourSort", self.behaviour_sort),
                write_double("SwitchOnFrequency", self.switch_on_frequency),
                write_guid("Profile", self.profile),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.Load:
            """Deserialize Load properties."""
            return cls(
                p1=data.get("P1", 0.0),
                q1=data.get("Q1", 0.0),
                pa=data.get("Pa", 0.0),
                qa=data.get("Qa", 0.0),
                pb=data.get("Pb", 0.0),
                qb=data.get("Qb", 0.0),
                pc=data.get("Pc", 0.0),
                qc=data.get("Qc", 0.0),
                pab=data.get("Pab", 0.0),
                qab=data.get("Qab", 0.0),
                pac=data.get("Pac", 0.0),
                qac=data.get("Qac", 0.0),
                pbc=data.get("Pbc", 0.0),
                qbc=data.get("Qbc", 0.0),
                behaviour_sort=data.get("BehaviourSort", ""),
                switch_on_frequency=data.get("SwitchOnFrequency", 0.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
            )

    @dataclass
    class Geography(DataClassJsonMixin):
        """Connection geographical information."""

        coordinates: FloatCoords = field(
            default_factory=list,
            metadata=config(encoder=encode_float_coords, decoder=decode_float_coords),
        )

        def serialize(self) -> str:
            """Serialize Geography properties to a string."""
            props = []
            if self.coordinates:
                props.append(f"Coordinates:{encode_float_coords(self.coordinates)}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.Geography:
            """Deserialize Geography properties."""
            return cls(
                coordinates=decode_float_coords(data.get("Coordinates", "''")),
            )

    @dataclass
    class GM(DataClassJsonMixin):
        """Gaussian Mixture properties."""

        gm_type_number: int = 1
        p: float = 0.0
        cos: float = 1.0
        small_appliance_phases: int = 1
        net_aware_charging: bool = False
        adjustable: bool = False

        def serialize(self) -> str:
            """Serialize GM properties to a string."""
            return serialize_properties(
                write_integer("GMTypeNumber", self.gm_type_number),
                write_double("P", self.p),
                write_double("Cos", self.cos),
                write_integer("SmallAppliancePhases", self.small_appliance_phases, skip=1),
                write_boolean("NetawareCharging", value=self.net_aware_charging),
                write_boolean("DownTuning", value=self.adjustable),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.GM:
            """Deserialize GM properties."""
            return cls(
                gm_type_number=data.get("GMTypeNumber", 1),
                p=data.get("P", 0.0),
                cos=data.get("Cos", 1.0),
                small_appliance_phases=data.get("SmallAppliancePhases", 1),
                net_aware_charging=data.get("NetawareCharging", False),
                adjustable=data.get("DownTuning", False),
            )

    @dataclass
    class PL(DataClassJsonMixin):
        """PL."""

        number_of: int = 0
        phases: int = 1
        pl_type: str = string_field()

        def serialize(self) -> str:
            """Serialize PL properties to a string."""
            return (
                serialize_properties(
                    write_integer("NumberOf", self.number_of, skip=0),
                    write_integer("Phases", self.phases, skip=1),
                    write_quote_string("PLType", self.pl_type),
                )
                + " "
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.PL:
            """Deserialize PL properties."""
            return cls(
                number_of=data.get("NumberOf", 0),
                phases=data.get("Phases", 1),
                pl_type=data.get("PLType", ""),
            )

    @dataclass
    class PLType(DataClassJsonMixin):
        """PL type."""

        unom: float = 0.0
        inom: float = 0.0
        cosnom: float = 0.0

        def serialize(self) -> str:
            """Serialize PLType properties to a string."""
            return serialize_properties(
                write_double("Unom", self.unom),
                write_double("Inom", self.inom),
                write_double("CosNom", self.cosnom),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.PLType:
            """Deserialize PLType properties."""
            return cls(
                unom=data.get("Unom", 0.0),
                inom=data.get("Inom", 0.0),
                cosnom=data.get("CosNom", 0.0),
            )

    @dataclass
    class Heatpump(DataClassJsonMixin):
        """Heatpump properties of a home/connection."""

        number_of: int = 0
        sort: str = "Air"
        house_type: str = "Apartment"
        house_area: float = 0.0
        cosnom: float = 0.0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize Heatpump properties to a string."""
            return serialize_properties(
                write_integer("NumberOf", self.number_of, skip=0),
                write_quote_string("Sort", self.sort),
                write_quote_string("HouseType", self.house_type, skip="Apartment"),
                write_double("HouseArea", self.house_area),
                write_double("Cosnom", self.cosnom),
                write_guid("Profile", self.profile),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.Heatpump:
            """Deserialize Heatpump properties from GNF format."""
            return cls(
                number_of=data.get("NumberOf", 0),
                sort=data.get("Sort", "Air"),
                house_type=data.get("HouseType", "Apartment"),
                house_area=data.get("HouseArea", 0.0),
                cosnom=data.get("Cosnom", 0.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
            )

    @dataclass
    class PV(DataClassJsonMixin):
        """PV properties of a home/connection."""

        scaling: float = 0
        panel1_pnom: float = 0
        panel1_orientation: float = 0
        panel1_slope: float = 0
        panel2_pnom: float = 0
        panel2_orientation: float = 0
        panel2_slope: float = 0
        panel3_pnom: float = 0
        panel3_orientation: float = 0
        panel3_slope: float = 0
        inverter_snom: float = 0
        efficiency_type: str = string_field()
        phases: int = 1
        u_out: float = 0
        p_controlsort: int = 0
        p_control_input1: float = 0.0
        p_control_output1: float = 0.0
        q_control_input1: float = 0.0
        q_control_output1: float = 0.0
        p_control_input2: float = 0.0
        p_control_output2: float = 0.0
        q_control_input2: float = 0.0
        q_control_output2: float = 0.0
        p_control_input3: float = 0.0
        p_control_output3: float = 0.0
        q_control_input3: float = 0.0
        q_control_output3: float = 0.0
        p_control_input4: float = 0.0
        p_control_output4: float = 0.0
        q_control_input4: float = 0.0
        q_control_output4: float = 0.0
        p_control_input5: float = 0.0
        p_control_output5: float = 0.0
        q_control_input5: float = 0.0
        q_control_output5: float = 0.0
        q_controlsort: int = 0
        q_control_cosref: float = 0.0
        q_control_no_p_no_q: bool = False
        intersection: float = 0.0
        length: float = 0.0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize PV properties to a string."""
            return serialize_properties(
                write_double_no_skip("Scaling", self.scaling),
                write_guid("Profile", self.profile),
                write_double_no_skip("Panel1Pnom", self.panel1_pnom),
                write_double_no_skip("Panel1Orientation", self.panel1_orientation),
                write_double_no_skip("Panel1Slope", self.panel1_slope),
                write_double_no_skip("Panel2Pnom", self.panel2_pnom),
                write_double_no_skip("Panel2Orientation", self.panel2_orientation),
                write_double_no_skip("Panel2Slope", self.panel2_slope),
                write_double_no_skip("Panel3Pnom", self.panel3_pnom),
                write_double_no_skip("Panel3Orientation", self.panel3_orientation),
                write_double_no_skip("Panel3Slope", self.panel3_slope),
                write_double("InverterSnom", self.inverter_snom),
                write_quote_string("EfficiencyType", self.efficiency_type),
                write_integer("Phases", self.phases, skip=1),
                write_double("Uout", self.u_out),
                write_integer("PcontrolSort", self.p_controlsort),
                write_double_no_skip("PControlInput1", self.p_control_input1),
                write_double_no_skip("PControlOutput1", self.p_control_output1),
                write_double_no_skip("PControlInput2", self.p_control_input2),
                write_double_no_skip("PControlOutput2", self.p_control_output2),
                write_double_no_skip("PControlInput3", self.p_control_input3),
                write_double_no_skip("PControlOutput3", self.p_control_output3),
                write_double_no_skip("PControlInput4", self.p_control_input4),
                write_double_no_skip("PControlOutput4", self.p_control_output4),
                write_double_no_skip("PControlInput5", self.p_control_input5),
                write_double_no_skip("PControlOutput5", self.p_control_output5),
                write_double_no_skip("QControlCosRef", self.q_control_cosref),
                write_boolean("QControlNoPnoQ", value=self.q_control_no_p_no_q),
                write_double_no_skip("QControlInput1", self.q_control_input1),
                write_double_no_skip("QControlOutput1", self.q_control_output1),
                write_double_no_skip("QControlInput2", self.q_control_input2),
                write_double_no_skip("QControlOutput2", self.q_control_output2),
                write_double_no_skip("QControlInput3", self.q_control_input3),
                write_double_no_skip("QControlOutput3", self.q_control_output3),
                write_double_no_skip("QControlInput4", self.q_control_input4),
                write_double_no_skip("QControlOutput4", self.q_control_output4),
                write_double_no_skip("QControlInput5", self.q_control_input5),
                write_double_no_skip("QControlOutput5", self.q_control_output5),
                write_integer("QControlSort", self.q_controlsort, skip=0),
                write_double("Intersection", self.intersection),
                write_double_no_skip("Length", self.length),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.PV:
            """Deserialize PV properties from GNF format."""
            return cls(
                scaling=data.get("Scaling", 0),
                panel1_pnom=data.get("Panel1Pnom", 0),
                panel1_orientation=data.get("Panel1Orientation", 0),
                panel1_slope=data.get("Panel1Slope", 0),
                panel2_pnom=data.get("Panel2Pnom", 0),
                panel2_orientation=data.get("Panel2Orientation", 0),
                panel2_slope=data.get("Panel2Slope", 0),
                panel3_pnom=data.get("Panel3Pnom", 0),
                panel3_orientation=data.get("Panel3Orientation", 0),
                panel3_slope=data.get("Panel3Slope", 0),
                inverter_snom=data.get("InverterSnom", 0),
                efficiency_type=data.get("EfficiencyType", ""),
                phases=data.get("Phases", 1),
                u_out=data.get("Uout", 0),
                p_controlsort=data.get("PcontrolSort", 0),
                p_control_input1=data.get("PControlInput1", 0.0),
                p_control_output1=data.get("PControlOutput1", 0.0),
                q_control_input1=data.get("QControlInput1", 0.0),
                q_control_output1=data.get("QControlOutput1", 0.0),
                p_control_input2=data.get("PControlInput2", 0.0),
                p_control_output2=data.get("PControlOutput2", 0.0),
                q_control_input2=data.get("QControlInput2", 0.0),
                q_control_output2=data.get("QControlOutput2", 0.0),
                p_control_input3=data.get("PControlInput3", 0.0),
                p_control_output3=data.get("PControlOutput3", 0.0),
                q_control_input3=data.get("QControlInput3", 0.0),
                q_control_output3=data.get("QControlOutput3", 0.0),
                p_control_input4=data.get("PControlInput4", 0.0),
                p_control_output4=data.get("PControlOutput4", 0.0),
                q_control_input4=data.get("QControlInput4", 0.0),
                q_control_output4=data.get("QControlOutput4", 0.0),
                p_control_input5=data.get("PControlInput5", 0.0),
                p_control_output5=data.get("PControlOutput5", 0.0),
                q_control_input5=data.get("QControlInput5", 0.0),
                q_control_output5=data.get("QControlOutput5", 0.0),
                q_controlsort=data.get("QControlSort", 0),
                q_control_cosref=data.get("QControlCosRef", 0.0),
                q_control_no_p_no_q=data.get("QControlNoPnoQ", False),
                intersection=data.get("Intersection", 0.0),
                length=data.get("Length", 0.0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
            )

    @dataclass
    class Generation(DataClassJsonMixin):
        """Generating properties of a home/connection."""

        p1: float = 0.0
        q1: float = 0.0
        pa: float = 0.0
        qa: float = 0.0
        pb: float = 0.0
        qb: float = 0.0
        pc: float = 0.0
        qc: float = 0.0
        pab: float = 0.0
        qab: float = 0.0
        pac: float = 0.0
        qac: float = 0.0
        pbc: float = 0.0
        qbc: float = 0.0
        behaviour_sort: str = string_field()
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize Generation properties to a string."""
            return serialize_properties(
                write_double("P1", self.p1),
                write_double("Q1", self.q1),
                write_double("Pa", self.pa),
                write_double("Qa", self.qa),
                write_double("Pb", self.pb),
                write_double("Qb", self.qb),
                write_double("Pc", self.pc),
                write_double("Qc", self.qc),
                write_double("Pab", self.pab),
                write_double("Qab", self.qab),
                write_double("Pac", self.pac),
                write_double("Qac", self.qac),
                write_double("Pbc", self.pbc),
                write_double("Qbc", self.qbc),
                write_quote_string("BehaviourSort", self.behaviour_sort),
                write_guid("Profile", self.profile),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.Generation:
            """Deserialize Generation properties from GNF format."""
            return cls(
                p1=data.get("P1", 0.0),
                q1=data.get("Q1", 0.0),
                pa=data.get("Pa", 0.0),
                qa=data.get("Qa", 0.0),
                pb=data.get("Pb", 0.0),
                qb=data.get("Qb", 0.0),
                pc=data.get("Pc", 0.0),
                qc=data.get("Qc", 0.0),
                pab=data.get("Pab", 0.0),
                qab=data.get("Qab", 0.0),
                pac=data.get("Pac", 0.0),
                qac=data.get("Qac", 0.0),
                pbc=data.get("Pbc", 0.0),
                qbc=data.get("Qbc", 0.0),
                behaviour_sort=data.get("BehaviourSort", ""),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
            )

    @dataclass
    class WindTurbine(DataClassJsonMixin):
        """Windturbine of a home/connection."""

        windspeed: float = 11
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        pnom: float = 0.0
        sort: int = 0
        inverter_snom: float = 0.0
        efficiency_type: str = string_field()
        phases: int = 0
        u_out: float = 0.0
        q_controlsort: int = 0
        q_control_cosref: float = 0
        q_control_no_p_no_q: bool = False
        q_control_input1: float = 0.0
        q_control_output1: float = 0.0
        q_control_input2: float = 0.0
        q_control_output2: float = 0.0
        q_control_input3: float = 0.0
        q_control_output3: float = 0.0
        q_control_input4: float = 0.0
        q_control_output4: float = 0.0
        q_control_input5: float = 0.0
        q_control_output5: float = 0.0
        intersection: float = 0.0
        length: float = 0.0

        def serialize(self) -> str:
            """Serialize WindTurbine properties to a string."""
            return serialize_properties(
                write_double("WindSpeed", self.windspeed),
                write_guid("Profile", self.profile),
                write_double("Pnom", self.pnom),
                write_integer("Sort", self.sort, skip=0),
                write_double("InverterSnom", self.inverter_snom),
                write_quote_string("EfficiencyType", self.efficiency_type),
                write_integer("Phases", self.phases, skip=0),
                write_double("Uout", self.u_out),
                write_integer("QControlSort", self.q_controlsort, skip=0),
                write_double("QControlCosRef", self.q_control_cosref),
                write_boolean("QControlNoPnoQ", value=self.q_control_no_p_no_q),
                write_double_no_skip("QControlInput1", self.q_control_input1),
                write_double_no_skip("QControlOutput1", self.q_control_output1),
                write_double_no_skip("QControlInput2", self.q_control_input2),
                write_double_no_skip("QControlOutput2", self.q_control_output2),
                write_double_no_skip("QControlInput3", self.q_control_input3),
                write_double_no_skip("QControlOutput3", self.q_control_output3),
                write_double_no_skip("QControlInput4", self.q_control_input4),
                write_double_no_skip("QControlOutput4", self.q_control_output4),
                write_double_no_skip("QControlInput5", self.q_control_input5),
                write_double_no_skip("QControlOutput5", self.q_control_output5),
                write_double("Intersection", self.intersection),
                write_double_no_skip("Length", self.length),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.WindTurbine:
            """Deserialize WindTurbine properties from GNF format."""
            return cls(
                windspeed=data.get("WindSpeed", 11),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                pnom=data.get("Pnom", 0.0),
                sort=data.get("Sort", 0),
                inverter_snom=data.get("InverterSnom", 0.0),
                efficiency_type=data.get("EfficiencyType", ""),
                phases=data.get("Phases", 0),
                u_out=data.get("Uout", 0.0),
                q_controlsort=data.get("QControlSort", 0),
                q_control_cosref=data.get("QControlCosRef", 0),
                q_control_no_p_no_q=data.get("QControlNoPnoQ", False),
                q_control_input1=data.get("QControlInput1", 0.0),
                q_control_output1=data.get("QControlOutput1", 0.0),
                q_control_input2=data.get("QControlInput2", 0.0),
                q_control_output2=data.get("QControlOutput2", 0.0),
                q_control_input3=data.get("QControlInput3", 0.0),
                q_control_output3=data.get("QControlOutput3", 0.0),
                q_control_input4=data.get("QControlInput4", 0.0),
                q_control_output4=data.get("QControlOutput4", 0.0),
                q_control_input5=data.get("QControlInput5", 0.0),
                q_control_output5=data.get("QControlOutput5", 0.0),
                intersection=data.get("Intersection", 0.0),
                length=data.get("Length", 0.0),
            )

    @dataclass
    class Battery(DataClassJsonMixin):
        """Battery of a home/connections."""

        pref: float = 0.0
        state_of_charge: float = 50
        capacity: float = 0
        crate: float = 0.5
        sort: int = 0
        inverter_snom: float = 0
        charge_efficiency_type: str = field(default="", metadata=config(encoder=encode_string))
        discharge_efficiency_type: str = field(default="", metadata=config(encoder=encode_string))
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        inverter_cosref: float = 0.0

        def serialize(self) -> str:
            """Serialize Battery properties to a string."""
            return serialize_properties(
                write_double("Pref", self.pref),
                write_double("StateOfCharge", self.state_of_charge),
                write_guid("Profile", self.profile),
                write_double("Capacity", self.capacity),
                write_double("Crate", self.crate, skip=0.5),
                write_integer("Sort", self.sort, skip=0),
                write_double("InverterSnom", self.inverter_snom),
                write_quote_string("ChargeEfficiencyType", self.charge_efficiency_type),
                write_quote_string("DischargeEfficiencyType", self.discharge_efficiency_type),
                write_double("InverterCosRef", self.inverter_cosref),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.Battery:
            """Deserialize Battery properties from GNF format."""
            return cls(
                pref=data.get("Pref", 0.0),
                state_of_charge=data.get("StateOfCharge", 50),
                capacity=data.get("Capacity", 0),
                crate=data.get("Crate", 0.5),
                sort=data.get("Sort", 0),
                inverter_snom=data.get("InverterSnom", 0),
                charge_efficiency_type=data.get("ChargeEfficiencyType", ""),
                discharge_efficiency_type=data.get("DischargeEfficiencyType", ""),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                inverter_cosref=data.get("InverterCosRef", 0.0),
            )

    @dataclass
    class HEMS(DataClassJsonMixin):
        """Home Energy Management System."""

        regime: str = string_field()
        parameter1: float = 0.0
        parameter2: float = 0.0
        parameter3: float = 0.0

        def serialize(self) -> str:
            """Serialize HEMS properties to a string."""
            return (
                serialize_properties(
                    write_quote_string("Regime", self.regime),
                    write_double("Parameter1", self.parameter1),
                    write_double("Parameter2", self.parameter2),
                    write_double("Parameter3", self.parameter3),
                )
                + " "
            )

        @classmethod
        def deserialize(cls, data: dict) -> ConnectionLV.HEMS:
            """Deserialize HEMS properties from GNF format."""
            return cls(
                regime=data.get("Regime", ""),
                parameter1=data.get("Parameter1", 0.0),
                parameter2=data.get("Parameter2", 0.0),
                parameter3=data.get("Parameter3", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]
    gms: list[GM]
    connection_cable: CableType | None = None
    connection_geography: Geography | None = None
    fuse_type: FuseType | None = None
    current_protection: CurrentType | None = None
    load: Load | None = None
    public_lighting: PL | None = None
    public_lighting_type: PLType | None = None
    heat_pump: Heatpump | None = None
    generation: Generation | None = None
    pv: PV | None = None
    pv_efficiency: EfficiencyType | None = None
    windturbine: WindTurbine | None = None
    windturbine_efficiency: EfficiencyType | None = None
    battery: Battery | None = None
    battery_charge_efficiency: EfficiencyType | None = None
    battery_discharge_efficiency: EfficiencyType | None = None
    hems: HEMS | None = None

    def __post_init__(self) -> None:
        """Initialize mixins for extras, notes, and presentations."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Register this home/connection in the given network, overwriting if GUID already exists."""
        if self.general.guid in network.homes:
            logger.critical("Connection/Home %s already exists, overwriting", self.general.guid)
        network.homes[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the home/connection and all its subcomponents to a string."""
        lines = []

        # Add ProtectionType to General serialization if available
        general_line = f"#General {self.general.serialize()}"
        lines.append(general_line)

        if self.connection_cable:
            lines.append(f"#ConnectionCableType {self.connection_cable.serialize()}")
        if self.fuse_type:
            lines.append(f"#FuseType {self.fuse_type.serialize()}")
        lines.extend(f"#GM {gm.serialize()} " for gm in self.gms)
        if self.current_protection:
            lines.append(f"#CurrentType {self.current_protection.serialize()}")
        if self.load:
            lines.append(f"#Load {self.load.serialize()}")
        if self.public_lighting:
            lines.append(f"#PL {self.public_lighting.serialize()}")
        if self.public_lighting_type:
            lines.append(f"#PLType {self.public_lighting_type.serialize()}")
        if self.heat_pump:
            lines.append(f"#Heatpump {self.heat_pump.serialize()}")
        if self.generation:
            lines.append(f"#Generation {self.generation.serialize()}")
        if self.connection_geography:
            lines.append(f"#ConnectionGeo {self.connection_geography.serialize()}")
        if self.pv:
            lines.append(f"#PV {self.pv.serialize()}")
        if self.pv_efficiency:
            lines.append(f"#PVInverterEfficiencyType {self.pv_efficiency.serialize()}")
        if self.windturbine:
            lines.append(f"#WindTurbine {self.windturbine.serialize()} ")
        if self.windturbine_efficiency:
            lines.append(f"#WindTurbineInverterEfficiencyType {self.windturbine_efficiency.serialize()}")
        if self.battery:
            lines.append(f"#Battery {self.battery.serialize()}")
        if self.battery_charge_efficiency:
            lines.append(f"#BatteryChargeEfficiency {self.battery_charge_efficiency.serialize()}")
        if self.battery_discharge_efficiency:
            lines.append(f"#BatteryDischargeEfficiency {self.battery_discharge_efficiency.serialize()}")
        if self.hems:
            lines.append(f"#Hems {self.hems.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)
        lines.extend(f"#Presentation {p.serialize()}" for p in self.presentations)
        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ConnectionLV:
        """Deserialize a home/connection and all its subcomponents from a dictionary."""
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)
        # For all optional/nested fields, check and use their deserialize if present
        connection_cable = None
        if data.get("connection_cable"):
            connection_cable = CableType.deserialize(data["connection_cable"])
        fuse_type = None
        if data.get("fuse_type"):
            from pyptp.elements.lv.shared import FuseType

            fuse_type = FuseType.deserialize(data["fuse_type"])
        current_protection = None
        if data.get("current_protection"):
            from pyptp.elements.lv.shared import CurrentType

            current_protection = CurrentType.deserialize(data["current_protection"])
        load = cls.Load.deserialize(data["load"]) if data.get("load") else None
        public_lighting = cls.PL.deserialize(data["public_lighting"]) if data.get("public_lighting") else None
        public_lighting_type = (
            cls.PLType.deserialize(data["public_lighting_type"]) if data.get("public_lighting_type") else None
        )
        heat_pump = cls.Heatpump.deserialize(data["heat_pump"]) if data.get("heat_pump") else None
        generation = cls.Generation.deserialize(data["generation"]) if data.get("generation") else None
        connection_geography = (
            cls.Geography.deserialize(data["connection_geography"]) if data.get("connection_geography") else None
        )
        pv = cls.PV.deserialize(data["pv"]) if data.get("pv") else None
        pv_efficiency = None
        if data.get("pv_efficiency"):
            from pyptp.elements.lv.shared import EfficiencyType

            pv_efficiency = EfficiencyType.deserialize(data["pv_efficiency"])
        windturbine = cls.WindTurbine.deserialize(data["windturbine"]) if data.get("windturbine") else None
        windturbine_efficiency = None
        if data.get("windturbine_efficiency"):
            from pyptp.elements.lv.shared import EfficiencyType

            windturbine_efficiency = EfficiencyType.deserialize(data["windturbine_efficiency"])
        battery = cls.Battery.deserialize(data["battery"]) if data.get("battery") else None
        battery_charge_efficiency = None
        if data.get("battery_charge_efficiency"):
            from pyptp.elements.lv.shared import EfficiencyType

            battery_charge_efficiency = EfficiencyType.deserialize(data["battery_charge_efficiency"])
        battery_discharge_efficiency = None
        if data.get("battery_discharge_efficiency"):
            from pyptp.elements.lv.shared import EfficiencyType

            battery_discharge_efficiency = EfficiencyType.deserialize(data["battery_discharge_efficiency"])
        hems = cls.HEMS.deserialize(data["hems"]) if data.get("hems") else None
        gms = [cls.GM.deserialize(gm) for gm in data.get("gms", [])]
        presentations = []
        for pres_data in data.get("presentations", []):
            from .presentations import ElementPresentation

            presentations.append(ElementPresentation.deserialize(pres_data))
        return cls(
            general=general,
            presentations=presentations,
            gms=gms,
            connection_cable=connection_cable,
            connection_geography=connection_geography,
            fuse_type=fuse_type,
            current_protection=current_protection,
            load=load,
            public_lighting=public_lighting,
            public_lighting_type=public_lighting_type,
            heat_pump=heat_pump,
            generation=generation,
            pv=pv,
            pv_efficiency=pv_efficiency,
            windturbine=windturbine,
            windturbine_efficiency=windturbine_efficiency,
            battery=battery,
            battery_charge_efficiency=battery_charge_efficiency,
            battery_discharge_efficiency=battery_discharge_efficiency,
            hems=hems,
        )
