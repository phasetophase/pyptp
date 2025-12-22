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
    encode_guid_optional,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
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
    from pyptp.network_mv import NetworkMV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class SynchronousGeneratorMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a synchronous generator (MV)."""

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
        mutation_date: int = 0
        revision_date: float | int = 0
        variant: bool = False
        name: str = string_field()
        switch_state: int = 0
        field_name: str = string_field()
        failure_frequency: float = 0.0
        repair_duration: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        not_preferred: bool = False
        pref: float | int = 0
        fp_droop: float | int = 0
        isochronous_control: bool = False
        control_sort: str = "C"
        q_ref: float | int = 0
        cos_ref: float = 0.95
        absorbs_q: bool = False
        uref: float = 1.0
        uq_droop: float = 1.0
        q_limiting_type: int = 1
        control_node: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        control_measure_field: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        earthing: int = 0
        re: float | int = 0
        xe: float | int = 0
        earthing_node: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        emergency_generator: bool = False
        pnom: float | int = 0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties in exact Delphi order."""
            return serialize_properties(
                write_guid("Node", self.node) if self.node != NIL_GUID else "",
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_boolean("Variant", value=self.variant),
                write_quote_string("Name", self.name, skip=""),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string("FieldName", self.field_name, skip=""),
                write_double("FailureFrequency", self.failure_frequency, skip=0.0),
                write_double("RepairDuration", self.repair_duration, skip=0.0),
                write_double("MaintenanceFrequency", self.maintenance_frequency, skip=0.0),
                write_double("MaintenanceDuration", self.maintenance_duration, skip=0.0),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration, skip=0.0),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_double("Pref", self.pref, skip=0),
                write_double("fpDroop", self.fp_droop, skip=0),
                write_boolean("IsochronousControl", value=self.isochronous_control),
                write_quote_string_no_skip("ControlSort", self.control_sort),
                write_double_no_skip("Qref", self.q_ref),
                write_double_no_skip("CosRef", self.cos_ref),
                write_boolean("AbsorbsQ", value=self.absorbs_q),
                write_double_no_skip("Uref", self.uref),
                write_double_no_skip("UQDroop", self.uq_droop),
                write_integer_no_skip("QlimitingType", self.q_limiting_type),
                write_guid("ControlNode", self.control_node) if self.control_node else "",
                write_guid("ControlMeasureField", self.control_measure_field) if self.control_measure_field else "",
                write_integer_no_skip("Earthing", self.earthing),
                write_double("Re", self.re, skip=0),
                write_double("Xe", self.xe, skip=0),
                write_guid("EarthingNode", self.earthing_node) if self.earthing_node else "",
                write_boolean("EmergencyGenerator", value=self.emergency_generator),
                write_double("Pnom", self.pnom, skip=0),
                write_guid("Profile", self.profile) if self.profile != DEFAULT_PROFILE_GUID else "",
                write_quote_string("SynchronousGeneratorType", self.type, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousGeneratorMV.General:
            """Deserialize General properties."""
            control_node = data.get("ControlNode")
            control_measure_field = data.get("ControlMeasureField")
            earthing_node = data.get("EarthingNode")

            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                switch_state=data.get("SwitchState", 0),
                field_name=data.get("FieldName", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
                repair_duration=data.get("RepairDuration", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                not_preferred=data.get("NotPreferred", False),
                pref=data.get("Pref", 0),
                fp_droop=data.get("fpDroop", 0),
                isochronous_control=data.get("IsochronousControl", False),
                control_sort=data.get("ControlSort", "C"),
                q_ref=data.get("Qref", 0),
                cos_ref=data.get("CosRef", 0.95),
                absorbs_q=data.get("AbsorbsQ", False),
                uref=data.get("Uref", 1.0),
                uq_droop=data.get("UQDroop", 1.0),
                q_limiting_type=data.get("QlimitingType", 1),
                control_node=decode_guid(control_node) if control_node else None,
                control_measure_field=decode_guid(control_measure_field) if control_measure_field else None,
                earthing=data.get("Earthing", 0),
                re=data.get("Re", 0),
                xe=data.get("Xe", 0),
                earthing_node=decode_guid(earthing_node) if earthing_node else None,
                emergency_generator=data.get("EmergencyGenerator", False),
                pnom=data.get("Pnom", 0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                type=data.get("SynchronousGeneratorType", ""),
            )

    @dataclass_json
    @dataclass
    class SynchronousGeneratorType(DataClassJsonMixin):
        """Electrotechnical properties of a synchronous generator."""

        unom: float | int = 0
        snom: float | int = 0
        cos_nom: float = 0.95
        qmin: float | int = 0
        qmax: float | int = 0
        rg: float | int = 0
        xd2sat: float = 0.2
        excitation_type: int = 0
        rotor: int = 0
        ikp: float | int = 0
        uf_max: float = 1.3
        xd_sat: float = 1.6
        Xl: float | int = 0
        Xd: float | int = 0
        Xq: float | int = 0
        X0: float | int = 0
        Xds: float | int = 0
        Xqs: float | int = 0
        Xdss: float | int = 0
        Xqss: float | int = 0
        open_circuit_time_constants: bool = False
        Tds: float | int = 0
        Tqs: float | int = 0
        Tdss: float | int = 0
        Tqss: float | int = 0
        inertia: bool = False
        h: float | int = 0
        J: float | int = 0
        KD: float | int = 0
        Nnom: float = 3000.0
        tdc: float | int = 0
        tdc_unknown: bool = False
        ikd: float | int = 0

        def serialize(self) -> str:
            """Serialize SynchronousGeneratorType properties in exact Delphi order."""
            return serialize_properties(
                write_double("Unom", self.unom, skip=0),
                write_double("Snom", self.snom, skip=0),
                write_double("CosNom", self.cos_nom, skip=0),
                write_double("Qmin", self.qmin, skip=0),
                write_double("Qmax", self.qmax, skip=0),
                write_double("rg", self.rg, skip=0),
                write_double("Xd2sat", self.xd2sat, skip=0),
                write_integer("ExcitationType", self.excitation_type, skip=0),
                write_integer("Rotor", self.rotor, skip=0),
                write_double("IkP", self.ikp, skip=0),
                write_double("UfMax", self.uf_max, skip=0),
                write_double("Xdsat", self.xd_sat, skip=0),
                write_double("Xl", self.Xl, skip=0),
                write_double("Xd", self.Xd, skip=0),
                write_double("Xq", self.Xq, skip=0),
                write_double("X0", self.X0, skip=0),
                write_double("Xds", self.Xds, skip=0),
                write_double("Xqs", self.Xqs, skip=0),
                write_double("Xdss", self.Xdss, skip=0),
                write_double("Xqss", self.Xqss, skip=0),
                write_boolean("OpenCircuitTimeConstants", value=self.open_circuit_time_constants),
                write_double("Tds", self.Tds, skip=0),
                write_double("Tqs", self.Tqs, skip=0),
                write_double("Tdss", self.Tdss, skip=0),
                write_double("Tqss", self.Tqss, skip=0),
                write_boolean("Inertia", value=self.inertia),
                write_double("h", self.h, skip=0),
                write_double("J", self.J, skip=0),
                write_double("KD", self.KD, skip=0),
                write_double("Nnom", self.Nnom, skip=0),
                write_double("Tdc", self.tdc, skip=0),
                write_boolean("TdcUnknown", value=self.tdc_unknown),
                write_double("Ikd", self.ikd, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousGeneratorMV.SynchronousGeneratorType:
            """Deserialize SynchronousGeneratorType properties."""
            return cls(
                unom=data.get("Unom", 0),
                snom=data.get("Snom", 0),
                cos_nom=data.get("CosNom", 0.95),
                qmin=data.get("Qmin", 0),
                qmax=data.get("Qmax", 0),
                rg=data.get("Rg", 0),
                xd2sat=data.get("Xd2sat", 0.2),
                excitation_type=data.get("ExcitationType", 0),
                rotor=data.get("Rotor", 0),
                ikp=data.get("IkP", 0),
                uf_max=data.get("UfMax", 1.3),
                xd_sat=data.get("Xdsat", 1.6),
                Xl=data.get("Xl", 0),
                Xd=data.get("Xd", 0),
                Xq=data.get("Xq", 0),
                X0=data.get("X0", 0),
                Xds=data.get("Xds", 0),
                Xqs=data.get("Xqs", 0),
                Xdss=data.get("Xdss", 0),
                Xqss=data.get("Xqss", 0),
                open_circuit_time_constants=data.get("OpenCircuitTimeConstants", False),
                Tds=data.get("Tds", 0),
                Tqs=data.get("Tqs", 0),
                Tdss=data.get("Tdss", 0),
                Tqss=data.get("Tqss", 0),
                inertia=data.get("Inertia", False),
                h=data.get("h", 0),
                J=data.get("J", 0),
                KD=data.get("KD", 0),
                Nnom=data.get("Nnom", 3000.0),
                tdc=data.get("Tdc", 0),
                tdc_unknown=data.get("TdcUnknown", False),
                ikd=data.get("Ikd", 0),
            )

    @dataclass_json
    @dataclass
    class HarmonicsType(DataClassJsonMixin):
        """Harmonics properties."""

        h2: float = 0.0
        h3: float = 0.0
        h4: float = 0.0
        h5: float = 0.0
        h6: float = 0.0
        h7: float = 0.0
        h8: float = 0.0
        h9: float = 0.0
        h10: float = 0.0
        h11: float = 0.0
        h12: float = 0.0
        h13: float = 0.0
        h14: float = 0.0
        h15: float = 0.0
        h16: float = 0.0
        h17: float = 0.0
        h18: float = 0.0
        h19: float = 0.0
        h20: float = 0.0
        h21: float = 0.0
        h22: float = 0.0
        h23: float = 0.0
        h24: float = 0.0
        h25: float = 0.0

        angle2: float = 0.0
        angle3: float = 0.0
        angle4: float = 0.0
        angle5: float = 0.0
        angle6: float = 0.0
        angle7: float = 0.0
        angle8: float = 0.0
        angle9: float = 0.0
        angle10: float = 0.0
        angle11: float = 0.0
        angle12: float = 0.0
        angle13: float = 0.0
        angle14: float = 0.0
        angle15: float = 0.0
        angle16: float = 0.0
        angle17: float = 0.0
        angle18: float = 0.0
        angle19: float = 0.0
        angle20: float = 0.0
        angle21: float = 0.0
        angle22: float = 0.0
        angle23: float = 0.0
        angle24: float = 0.0
        angle25: float = 0.0

        def has_harmonics(self) -> bool:
            """Check if any harmonic values are non-zero."""
            return any(getattr(self, f"h{i}", 0) != 0 or getattr(self, f"Angle{i}", 0) != 0 for i in range(2, 26))

        def serialize(self) -> str:
            """Serialize HarmonicsType properties."""
            props = []
            for i in range(2, 26):
                h_val = getattr(self, f"h{i}", 0)
                if h_val != 0:
                    props.append(write_double(f"h{i}", h_val, skip=0))
            for i in range(2, 26):
                angle_val = getattr(self, f"Angle{i}", 0)
                if angle_val != 0:
                    props.append(write_double(f"Angle{i}", angle_val, skip=0))
            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousGeneratorMV.HarmonicsType:
            """Deserialize HarmonicsType properties."""
            kwargs = {}
            for i in range(2, 26):
                kwargs[f"h{i}"] = data.get(f"h{i}", 0.0)
                kwargs[f"angle{i}"] = data.get(f"Angle{i}", 0.0)
            return cls(**kwargs)

    @dataclass_json
    @dataclass
    class Restriction(DataClassJsonMixin):
        """Restriction."""

        sort: str = string_field()
        begin_date: int = 0
        end_date: int = 0
        begin_time: float | int = 0
        end_time: float | int = 0
        p_max: float | int = 0

        def serialize(self) -> str:
            """Serialize Restriction properties."""
            return serialize_properties(
                write_quote_string_no_skip("Sort", self.sort),
                write_integer_no_skip("BeginDate", self.begin_date),
                write_integer_no_skip("EndDate", self.end_date),
                write_double_no_skip("BeginTime", self.begin_time),
                write_double_no_skip("EndTime", self.end_time),
                write_double_no_skip("Pmax", self.p_max),
            )

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousGeneratorMV.Restriction:
            """Deserialize Restriction properties."""
            return cls(
                sort=data.get("Sort", ""),
                begin_date=data.get("BeginDate", 0),
                end_date=data.get("EndDate", 0),
                begin_time=data.get("BeginTime", 0),
                end_time=data.get("EndTime", 0),
                p_max=data.get("Pmax", 0),
            )

    @dataclass_json
    @dataclass
    class PQDiagram(DataClassJsonMixin):
        """Diagram."""

        p_limit: list[float] | None = field(default_factory=lambda: [0] * 10)
        q_limit: list[float] | None = field(default_factory=lambda: [0] * 10)

        def serialize(self) -> str:
            """Serialize PQDiagram properties."""
            props = []
            if self.p_limit:
                props.extend([write_double_no_skip(f"PLimit{i + 1}", p) for i, p in enumerate(self.p_limit)])
            if self.q_limit:
                props.extend([write_double_no_skip(f"QLimit{i + 1}", q) for i, q in enumerate(self.q_limit)])
            return serialize_properties(*props)

        @classmethod
        def deserialize(cls, data: dict) -> SynchronousGeneratorMV.PQDiagram:
            """Deserialize PQDiagram properties."""
            p_limit = []
            q_limit = []

            i = 1
            while f"PLimit{i}" in data:
                p_limit.append(data[f"PLimit{i}"])
                i += 1

            i = 1
            while f"QLimit{i}" in data:
                q_limit.append(data[f"QLimit{i}"])
                i += 1

            return cls(
                p_limit=p_limit if p_limit else [0.0] * 10,
                q_limit=q_limit if q_limit else [0.0] * 10,
            )

    general: General
    presentations: list[ElementPresentation]
    type: SynchronousGeneratorType
    harmonics_type: HarmonicsType = field(default_factory=lambda: SynchronousGeneratorMV.HarmonicsType())
    pq_diagram: PQDiagram | None = None
    restrictions: list[Restriction] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def apply_node_defaults(self, network: NetworkMV) -> None:
        """Apply defaults based on the connected node's Unom, matching Delphi behavior."""
        if self.general.node != NIL_GUID and self.general.node in network.nodes:
            node = network.nodes[self.general.node]
            unom = node.general.unom

            if self.type.unom == 0:
                self.type.unom = unom

            if self.type.rg == 0:
                if unom <= 1:
                    self.type.rg = 0.15 * self.type.xd2sat
                else:
                    self.type.rg = 0.07 * self.type.xd2sat

    def register(self, network: NetworkMV) -> None:
        """Will add synchronous generator to the network."""
        if self.general.guid in network.synchronous_generators:
            logger.critical("Synchronous Generator %s already exists, overwriting", self.general.guid)

        self.apply_node_defaults(network)

        network.synchronous_generators[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the synchronous generator to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.append(f"#SynchronousGeneratorType {self.type.serialize()}")

        q_limiting_pq_diagram = 2  # Magic value defined for readability
        if self.general.q_limiting_type == q_limiting_pq_diagram and self.pq_diagram:
            lines.append(f"#PQDiagram {self.pq_diagram.serialize()}")

        if self.harmonics_type.has_harmonics():
            lines.append(f"#HarmonicsType {self.harmonics_type.serialize()}")

        lines.extend(f"#Restriction {restriction.serialize()}" for restriction in self.restrictions)

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)

        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> SynchronousGeneratorMV:
        """Deserialization of the synchronous generator from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TSynchronousGeneratorMS: The deserialized synchronous generator

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        generator_type_data = (
            data.get("synchronousGeneratorType", [{}])[0] if data.get("synchronousGeneratorType") else {}
        )
        generator_type = cls.SynchronousGeneratorType.deserialize(generator_type_data)

        harmonics_data = data.get("harmonicsType", [{}])[0] if data.get("harmonicsType") else {}
        harmonics_type = cls.HarmonicsType.deserialize(harmonics_data)

        pq_diagram_data = data.get("pqDiagram", [{}])[0] if data.get("pqDiagram") else None
        pq_diagram = cls.PQDiagram.deserialize(pq_diagram_data) if pq_diagram_data else None

        restrictions_data = data.get("restrictions", [])
        restrictions = []
        for restriction_data in restrictions_data:
            restriction = cls.Restriction.deserialize(restriction_data)
            restrictions.append(restriction)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=generator_type,
            harmonics_type=harmonics_type,
            pq_diagram=pq_diagram,
            restrictions=restrictions,
            presentations=presentations,
        )
