"""Line (Branch)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
    NIL_GUID,
    FloatCoords,
    Guid,
    decode_float_coords,
    decode_guid,
    encode_float_coords,
    encode_guid,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_boolean_as_byte_no_skip,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.mv.presentations import BranchPresentation
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class LineMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a line (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a line."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0.0
        mutation_date: int = 0
        revision_date: int = 0
        variant: bool = False
        subnet_border: bool = False
        field_name1: str = string_field()
        field_name2: str = string_field()
        source1: str = string_field()
        source2: str = string_field()
        name: str = string_field()
        repair_duration: float = 0.0
        failure_frequency: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        loadrate_max: float = 0.0
        loadrate_max_emergency: float = 0.0
        switch_state1: int = 1
        switch_state2: int = 1
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        resistance_symbol: bool = False

        def serialize(self) -> str:
            """Serialize General properties following exact Delphi order."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_integer("RevisionDate", self.revision_date, skip=0),
                write_boolean("Variant", value=self.variant),
                write_guid("Node1", self.node1) if self.node1 != NIL_GUID else "",
                write_guid("Node2", self.node2) if self.node2 != NIL_GUID else "",
                write_quote_string("Name", self.name),
                write_boolean_as_byte_no_skip("SwitchState1", value=bool(self.switch_state1)),
                write_boolean_as_byte_no_skip("SwitchState2", value=bool(self.switch_state2)),
                write_quote_string("FieldName1", self.field_name1, skip=""),
                write_quote_string("FieldName2", self.field_name2, skip=""),
                write_boolean("SubnetBorder", value=self.subnet_border),
                write_quote_string("Source1", self.source1, skip=""),
                write_quote_string("Source2", self.source2, skip=""),
                write_double("FailureFrequency", self.failure_frequency, skip=0.0),
                write_double("RepairDuration", self.repair_duration, skip=0.0),
                write_double("MaintenanceFrequency", self.maintenance_frequency, skip=0.0),
                write_double("MaintenanceDuration", self.maintenance_duration, skip=0.0),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration, skip=0.0),
                write_double("LoadrateMax", self.loadrate_max, skip=0.0),
                write_double("LoadrateMaxmax", self.loadrate_max_emergency, skip=0.0),
                write_boolean("ResistanceSymbol", value=self.resistance_symbol),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LineMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0.0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0),
                variant=data.get("Variant", False),
                subnet_border=data.get("SubnetBorder", False),
                field_name1=data.get("FieldName1", ""),
                field_name2=data.get("FieldName2", ""),
                source1=data.get("Source1", ""),
                source2=data.get("Source2", ""),
                name=data.get("Name", ""),
                repair_duration=data.get("RepairDuration", 0.0),
                failure_frequency=data.get("FailureFrequency", 0.0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0.0),
                maintenance_duration=data.get("MaintenanceDuration", 0.0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0.0),
                loadrate_max=data.get("LoadrateMax", 0.0),
                loadrate_max_emergency=data.get("LoadrateMaxmax", 0.0),
                switch_state1=data.get("SwitchState1", 1),
                switch_state2=data.get("SwitchState2", 1),
                node1=decode_guid(data.get("Node1", str(NIL_GUID))),
                node2=decode_guid(data.get("Node2", str(NIL_GUID))),
                resistance_symbol=data.get("ResistanceSymbol", False),
            )

    @dataclass_json
    @dataclass
    class LinePart(DataClassJsonMixin):
        """Electrotechnical properties of a part of the line."""

        R: float = 0
        X: float = 0
        C: float = 0
        R0: float = 0
        X0: float = 0
        C0: float = 0
        inom: float = 0
        inom1: float = 0
        inom2: float = 0
        inom3: float = 0
        ik1s: float = 0
        TR: float = 0
        TI_nom: float = 0
        TIk1s: float = 0
        length: float = 0
        description: str = string_field()

        def __post_init__(self) -> None:
            """Make sure the length of the line is at least 1 meter."""
            self.length = max(self.length, 1)

        def serialize(self) -> str:
            """Serialize LinePart properties following exact Delphi order."""
            return serialize_properties(
                write_double("R", self.R, skip=0.0),
                write_double("X", self.X, skip=0.0),
                write_double("C", self.C, skip=0.0),
                write_double("R0", self.R0, skip=0.0),
                write_double("X0", self.X0, skip=0.0),
                write_double("C0", self.C0, skip=0.0),
                write_double("Inom", self.inom, skip=0.0),
                write_double("Inom1", self.inom1, skip=0.0),
                write_double("Inom2", self.inom2, skip=0.0),
                write_double("Inom3", self.inom3, skip=0.0),
                write_double("Ik1s", self.ik1s, skip=0.0),
                write_double("TR", self.TR, skip=0.0),
                write_double("TInom", self.TI_nom, skip=0.0),
                write_double("TIk1s", self.TIk1s, skip=0.0),
                write_double("Length", self.length, skip=0.0),
                write_quote_string("Description", self.description, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LineMV.LinePart:
            """Deserialize LinePart properties."""
            return cls(
                R=data.get("R", 0),
                X=data.get("X", 0),
                C=data.get("C", 0),
                R0=data.get("R0", 0),
                X0=data.get("X0", 0),
                C0=data.get("C0", 0),
                inom=data.get("Inom", 0),
                inom1=data.get("Inom1", 0),
                inom2=data.get("Inom2", 0),
                inom3=data.get("Inom3", 0),
                ik1s=data.get("Ik1s", 0),
                TR=data.get("TR", 0),
                TI_nom=data.get("TInom", 0),
                TIk1s=data.get("TIk1s", 0),
                length=data.get("Length", 0),
                description=data.get("Description", ""),
            )

    @dataclass_json
    @dataclass
    class Joint(DataClassJsonMixin):
        """Joint (Mof) properties for a line."""

        x: float = 0.0
        y: float = 0.0
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize Joint properties following exact Delphi order."""
            return serialize_properties(
                write_double("X", self.x, skip=0.0),
                write_double("Y", self.y, skip=0.0),
                write_quote_string("Type", self.type, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> LineMV.Joint:
            """Deserialize Joint properties."""
            return cls(
                x=data.get("X", 0.0),
                y=data.get("Y", 0.0),
                type=data.get("Type", ""),
            )

    @dataclass_json
    @dataclass
    class Geo(DataClassJsonMixin):
        """Geographical properties of the line."""

        coordinates: FloatCoords = field(
            default_factory=list,
            metadata=config(encoder=encode_float_coords, decoder=decode_float_coords),
        )

        def serialize(self) -> str:
            """Serialize Geo properties."""
            if self.coordinates:
                return f"Coordinates:{encode_float_coords(self.coordinates)}"
            return ""

        @classmethod
        def deserialize(cls, data: dict) -> LineMV.Geo:
            """Deserialize Geo properties."""
            return cls(
                coordinates=decode_float_coords(data.get("Coordinates", "")),
            )

    general: General
    lineparts: list[LinePart] = field(default_factory=list)
    joints: list[Joint] = field(default_factory=list)
    geo: Geo | None = None
    presentations: list[BranchPresentation] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Will add line to the network."""
        if self.general.guid in network.lines:
            logger.critical("Line %s already exists, overwriting", self.general.guid)
        network.lines[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the line to the VNF format following exact Delphi order.

        Returns:
            str: The serialized representation.

        """
        lines = []

        lines.append(f"#General {self.general.serialize()}")
        lines.extend(f"#LinePart {linepart.serialize()}" for linepart in self.lineparts)
        lines.extend(f"#Joint {joint.serialize()}" for joint in self.joints)

        if self.geo and self.geo.coordinates:
            lines.append(f"#Geo {self.geo.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> LineMV:
        """Deserialization of the line from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            LineMV: The deserialized line

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        lineparts_data = data.get("lineparts", [])
        lineparts = []
        for linepart_data in lineparts_data:
            linepart = cls.LinePart.deserialize(linepart_data)
            lineparts.append(linepart)

        joints_data = data.get("joints", [])
        joints = []
        for joint_data in joints_data:
            joint = cls.Joint.deserialize(joint_data)
            joints.append(joint)

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        # Parse geo section
        geo = None
        geo_data = data.get("geo", [{}])[0] if data.get("geo") else None
        if geo_data:
            geo = cls.Geo.deserialize(geo_data)

        return cls(
            general=general,
            lineparts=lineparts,
            joints=joints,
            geo=geo,
            presentations=presentations,
        )
