"""Medium-voltage load element for Vision integration.

Provides MV load representation with symmetrical modeling
for balanced three-phase power system analysis and control.
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
    encode_guid_optional,
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
    from pyptp.elements.mv.shared import PControl, QControl
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class LoadMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Medium-voltage load element for symmetrical modeling.

    Supports balanced three-phase load modeling with power control,
    unbalanced loading capabilities, and comprehensive load behavior
    configuration for MV distribution system analysis.
    """

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for MV loads."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        switch_state: int = 1
        field_name: str = string_field()
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        not_preferred: bool = False
        P: float = 0.0
        Q: float = 0.0
        unbalanced: bool = False
        delta: bool = False
        fp1: float = 0.0
        fq1: float = 0.0
        fp2: float = 0.0
        fq2: float = 0.0
        fp3: float = 0.0
        fq3: float = 0.0
        earthing: int = 0
        re: float = 0.0
        xe: float = 0.0
        load_behaviour: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        load_growth: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        profile: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        harmonics_type: str = string_field()
        large_consumers: int = 0
        generous_consumers: int = 0
        small_consumers: int = 0
        harmonic_impedance: bool = True

        def serialize(self) -> str:
            """Serialize load properties to VNF format.

            Returns:
                Space-separated property string for VNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("Node", self.node),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string_no_skip("Name", self.name),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string("FieldName", self.field_name, skip=""),
                write_double("FailureFrequency", self.failure_frequency, skip=0.0),
                write_double("RepairDuration", self.repair_duration, skip=0.0),
                write_double("MaintenanceFrequency", self.maintenance_frequency, skip=0.0),
                write_double("MaintenanceDuration", self.maintenance_duration, skip=0.0),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration, skip=0.0),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_double("P", self.P, skip=0.0),
                write_double("Q", self.Q, skip=0.0),
                write_boolean("Unbalanced", value=self.unbalanced),
                write_boolean("Delta", value=self.delta),
                write_double_no_skip("Fp1", self.fp1),
                write_double_no_skip("Fq1", self.fq1),
                write_double_no_skip("Fp2", self.fp2),
                write_double_no_skip("Fq2", self.fq2),
                write_double_no_skip("Fp3", self.fp3),
                write_double_no_skip("Fq3", self.fq3),
                write_integer_no_skip("Earthing", self.earthing),
                write_double("Re", self.re, skip=0.0),
                write_double("Xe", self.xe, skip=0.0),
                write_guid("LoadBehaviour", self.load_behaviour) if self.load_behaviour is not None else "",
                write_guid("LoadGrowth", self.load_growth) if self.load_growth is not None else "",
                write_guid("Profile", self.profile) if self.profile is not None else "",
                write_quote_string("HarmonicsType", self.harmonics_type, skip=""),
                write_integer("LargeConsumers", self.large_consumers, skip=0),
                write_integer("GenerousConsumers", self.generous_consumers, skip=0),
                write_integer("SmallConsumers", self.small_consumers, skip=0),
                write_boolean_no_skip("HarmonicImpedance", value=self.harmonic_impedance),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LoadMV.General:
            """Parse load properties from VNF section data.

            Args:
                data: Dictionary of property key-value pairs from VNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
            guid = data.get("GUID")
            node = data.get("Node")
            load_behaviour = data.get("LoadBehaviour")
            load_growth = data.get("LoadGrowth")
            profile = data.get("Profile")
            mutation_date = data.get("MutationDate")
            revision_date = data.get("RevisionDate")

            return cls(
                node=decode_guid(node) if node else Guid(uuid4()),
                guid=decode_guid(guid) if guid else Guid(uuid4()),
                creation_time=data.get("CreationTime", 0),
                mutation_date=mutation_date if mutation_date is not None else 0,
                revision_date=revision_date if revision_date is not None else 0.0,
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                switch_state=data.get("SwitchState", 1),
                field_name=data.get("FieldName", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                not_preferred=data.get("NotPreferred", False),
                P=data.get("P", 0.0),
                Q=data.get("Q", 0.0),
                unbalanced=data.get("Unbalanced", False),
                delta=data.get("Delta", False),
                fp1=data.get("Fp1", 0.0),
                fq1=data.get("Fq1", 0.0),
                fp2=data.get("Fp2", 0.0),
                fq2=data.get("Fq2", 0.0),
                fp3=data.get("Fp3", 0.0),
                fq3=data.get("Fq3", 0.0),
                earthing=data.get("Earthing", 0),
                re=data.get("Re", 0.0),
                xe=data.get("Xe", 0.0),
                load_behaviour=decode_guid(load_behaviour) if load_behaviour else None,
                load_growth=decode_guid(load_growth) if load_growth else None,
                profile=decode_guid(profile) if profile else None,
                harmonics_type=data.get("HarmonicsType", ""),
                large_consumers=data.get("LargeConsumers", 0),
                generous_consumers=data.get("GenerousConsumers", 0),
                small_consumers=data.get("SmallConsumers", 0),
                harmonic_impedance=data.get("HarmonicImpedance", True),
            )

    @dataclass_json
    @dataclass
    class PIControl(DataClassJsonMixin):
        """Power-current control characteristics for load response."""

        input1: float = 1.0
        output1: float = 0.0
        input2: float = 0.0
        output2: float = 0.0
        input3: float = 0.0
        output3: float = 0.0
        input4: float = 0.0
        output4: float = 0.0
        input5: float = 0.0
        output5: float = 0.0
        measure_field1: str = string_field()
        measure_field2: str = string_field()
        measure_field3: str = string_field()

        def serialize(self) -> str:
            """Serialize PI control properties to VNF format."""
            props = []
            props.append(f"Input1:{self.input1}")
            props.append(f"Output1:{self.output1}")
            props.append(f"Input2:{self.input2}")
            props.append(f"Output2:{self.output2}")
            props.append(f"Input3:{self.input3}")
            props.append(f"Output3:{self.output3}")
            props.append(f"Input4:{self.input4}")
            props.append(f"Output4:{self.output4}")
            props.append(f"Input5:{self.input5}")
            props.append(f"Output5:{self.output5}")
            props.append(f"MeasureField1:'{self.measure_field1}'")
            props.append(f"MeasureField2:'{self.measure_field2}'")
            props.append(f"MeasureField3:'{self.measure_field3}'")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> LoadMV.PIControl:
            """Parse PI control properties from VNF data."""
            return cls(
                input1=data.get("Input1", 1.0),
                output1=data.get("Output1", 0.0),
                input2=data.get("Input2", 0.0),
                output2=data.get("Output2", 0.0),
                input3=data.get("Input3", 0.0),
                output3=data.get("Output3", 0.0),
                input4=data.get("Input4", 0.0),
                output4=data.get("Output4", 0.0),
                input5=data.get("Input5", 0.0),
                output5=data.get("Output5", 0.0),
                measure_field1=data.get("MeasureField1", ""),
                measure_field2=data.get("MeasureField2", ""),
                measure_field3=data.get("MeasureField3", ""),
            )

    @dataclass_json
    @dataclass
    class Capacity(DataClassJsonMixin):
        """Load capacity restrictions and time-based limitations."""

        sort: str = string_field()
        begin_date: int = 0
        end_date: int = 0
        begin_time: float = 0.0
        end_time: float = 0.0
        p_max: float = 0.0

        def serialize(self) -> str:
            """Serialize capacity properties to VNF format."""
            props = []
            props.append(f"Sort:'{self.sort}'")
            props.append(f"BeginDate:{self.begin_date}")
            props.append(f"EndDate:{self.end_date}")
            props.append(f"BeginTime:{self.begin_time}")
            props.append(f"EndTime:{self.end_time}")
            props.append(f"Pmax:{self.p_max}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> LoadMV.Capacity:
            """Parse capacity properties from VNF data."""
            return cls(
                sort=data.get("Sort", ""),
                begin_date=data.get("BeginDate", 0),
                end_date=data.get("EndDate", 0),
                begin_time=data.get("BeginTime", 0.0),
                end_time=data.get("EndTime", 0.0),
                p_max=data.get("Pmax", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]
    p_control: PControl | None = None
    q_control: QControl | None = None
    pi_control: PIControl | None = None
    ceres: dict | None = None
    restrictions: Capacity | None = None

    def register(self, network: NetworkMV) -> None:
        """Register load in MV network with GUID-based indexing.

        Args:
            network: Target MV network for load registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.loads:
            logger.critical("Load %s already exists, overwriting", self.general.guid)
        network.loads[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the load to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.p_control:
            lines.append(f"#P(U)Control {self.p_control.serialize()}")

        if self.q_control:
            lines.append(f"#QControl {self.q_control.serialize()}")

        if self.pi_control:
            lines.append(f"#P(I)Control {self.pi_control.serialize()}")

        if self.ceres:
            lines.append(f"#CERES {self.ceres}")

        if self.restrictions:
            lines.append(f"#Restriction {self.restrictions.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> LoadMV:
        """Parse load from VNF format data.

        Args:
            data: Dictionary containing parsed VNF section data.

        Returns:
            Initialized TLoadMS instance with parsed properties.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        pcontrol_data = data.get("pControl", [{}])[0] if data.get("pControl") else {}
        pcontrol = None
        if pcontrol_data:
            from .shared import PControl

            pcontrol = PControl.deserialize(pcontrol_data)

        qcontrol_data = data.get("qControl", [{}])[0] if data.get("qControl") else {}
        qcontrol = None
        if qcontrol_data:
            from .shared import QControl

            qcontrol = QControl.deserialize(qcontrol_data)

        picontrol_data = data.get("piControl", [{}])[0] if data.get("piControl") else {}
        picontrol = None
        if picontrol_data:
            picontrol = cls.PIControl.deserialize(picontrol_data)

        ceres_data = data.get("ceres", [{}])[0] if data.get("ceres") else {}
        ceres = None
        if ceres_data:
            ceres = ceres_data

        restrictions_data = data.get("restrictions", [{}])[0] if data.get("restrictions") else {}
        restrictions = None
        if restrictions_data:
            restrictions = cls.Capacity.deserialize(restrictions_data)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            p_control=pcontrol,
            q_control=qcontrol,
            pi_control=picontrol,
            ceres=ceres,
            restrictions=restrictions,
        )
