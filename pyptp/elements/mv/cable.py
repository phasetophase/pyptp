"""Cable (Branch)."""

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
    optional_field,
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
    from pyptp.elements.mv.shared import CableType, GeoCablePart
if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV

    from .presentations import BranchPresentation


@dataclass_json
@dataclass
class CableMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a cable (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a cable."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        subnet_border: bool = False
        field_name1: str = string_field()
        """Name of the connection field on node1 side."""
        field_name2: str = string_field()
        """Name of the connection field on node2 side."""
        source1: str = string_field()
        """Name of the feeding object on node1 side (subnet border case)."""
        source2: str = string_field()
        """Name of the feeding object on node2 side (subnet border case)."""
        name: str = string_field()
        repair_duration: float = 0.0
        failure_frequency: float = 0.0
        maintenance_frequency: float = 0.0
        maintenance_duration: float = 0.0
        maintenance_cancel_duration: float = 0.0
        joint_failure_frequency: float = 0.0
        loadrate_max: float = 0.0
        loadrate_max_emergency: float = 0.0
        switch_state1: int = 1
        switch_state2: int = 1
        rail_connectivity: int = 0
        dyn_model: str = "P"
        dyn_number_of_sections: int = 1
        dyn_neglect_capacitance: bool = False
        node1: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        node2: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date) if self.mutation_date != 0 else "",
                write_double("RevisionDate", self.revision_date) if self.revision_date != 0.0 else "",
                write_boolean("Variant", value=self.variant) if self.variant else "",
                write_guid("Node1", self.node1) if self.node1 != NIL_GUID else "",
                write_guid("Node2", self.node2) if self.node2 != NIL_GUID else "",
                write_quote_string("Name", self.name),
                write_integer_no_skip("SwitchState1", self.switch_state1),
                write_integer_no_skip("SwitchState2", self.switch_state2),
                write_quote_string("FieldName1", self.field_name1),
                write_quote_string("FieldName2", self.field_name2),
                write_boolean("SubnetBorder", value=self.subnet_border) if self.subnet_border else "",
                write_quote_string("Source1", self.source1) if self.source1 else "",
                write_quote_string("Source2", self.source2) if self.source2 else "",
                write_double("RepairDuration", self.repair_duration) if self.repair_duration != 0.0 else "",
                write_double("FailureFrequency", self.failure_frequency) if self.failure_frequency != 0.0 else "",
                (
                    write_double("MaintenanceFrequency", self.maintenance_frequency)
                    if self.maintenance_frequency != 0.0
                    else ""
                ),
                (
                    write_double("MaintenanceDuration", self.maintenance_duration)
                    if self.maintenance_duration != 0.0
                    else ""
                ),
                (
                    write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration)
                    if self.maintenance_cancel_duration != 0.0
                    else ""
                ),
                (
                    write_double("JointFailureFrequency", self.joint_failure_frequency)
                    if self.joint_failure_frequency != 0.0
                    else ""
                ),
                write_double("LoadrateMax", self.loadrate_max) if self.loadrate_max != 0.0 else "",
                write_double("LoadrateMaxmax", self.loadrate_max_emergency)
                if self.loadrate_max_emergency != 0.0
                else "",
                write_integer("RailConnectivity", self.rail_connectivity) if self.rail_connectivity != 0 else "",
                write_quote_string_no_skip("DynModel", self.dyn_model),
                write_integer_no_skip("DynSection", self.dyn_number_of_sections),
                write_boolean("DynNoC", value=self.dyn_neglect_capacitance) if self.dyn_neglect_capacitance else "",
            )

        @classmethod
        def deserialize(cls, data: dict) -> CableMV.General:
            """Deserialize General properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
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
                joint_failure_frequency=data.get("JointFailureFrequency", 0.0),
                loadrate_max=data.get("LoadrateMax", 0.0),
                loadrate_max_emergency=data.get("LoadrateMaxmax", 0.0),
                switch_state1=data.get("SwitchState1", 1),
                switch_state2=data.get("SwitchState2", 1),
                rail_connectivity=data.get("RailConnectivity", 0),
                dyn_model=data.get("DynModel", "P"),
                dyn_number_of_sections=data.get("DynSection", 1),
                dyn_neglect_capacitance=data.get("DynNoC", False),
                node1=decode_guid(data.get("Node1", str(NIL_GUID))),
                node2=decode_guid(data.get("Node2", str(NIL_GUID))),
            )

    @dataclass_json
    @dataclass
    class CablePart(DataClassJsonMixin):
        """Properties for a part of the cable."""

        length: float = 1.0
        cable_type: str = string_field()
        year: str = string_field()
        parallel_cable_count: int = 1
        ground_resistivity_index: int = 1
        ampacity_factor: int = 1

        def serialize(self) -> str:
            """Serialize CablePart properties."""
            return serialize_properties(
                write_double("Length", self.length),
                write_quote_string_no_skip("CableType", self.cable_type),
                write_integer_no_skip("ParallelCableCount", self.parallel_cable_count),
                write_quote_string("Year", self.year) if self.year else "",
                write_integer_no_skip("GroundResistivityIndex", self.ground_resistivity_index),
                write_integer_no_skip("AmpacityFactor", self.ampacity_factor),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CableMV.CablePart:
            """Deserialize CablePart properties."""
            return cls(
                length=data.get("Length", 1.0),
                cable_type=data.get("CableType", ""),
                year=data.get("Year", ""),
                parallel_cable_count=data.get("ParallelCableCount", 1),
                ground_resistivity_index=data.get("GroundResistivityIndex", 1),
                ampacity_factor=data.get("AmpacityFactor", 1),
            )

        def __post_init__(self) -> None:
            """Make sure length is always at least 1."""
            self.length = max(self.length, 1.0)

    @dataclass_json
    @dataclass
    class Joint(DataClassJsonMixin):
        """Cable joint properties."""

        x: float | int = 0.0
        y: float | int = 0.0
        type: str = string_field()
        year: str = string_field()
        failure_frequency: float | int = 0.0

        def serialize(self) -> str:
            """Serialize Joint properties."""
            return serialize_properties(
                write_double("X", self.x),
                write_double("Y", self.y),
                write_quote_string("Type", self.type),
                write_quote_string("Year", self.year),
                write_double("FailureFrequency", self.failure_frequency),
            )

        @classmethod
        def deserialize(cls, data: dict) -> CableMV.Joint:
            """Deserialize Joint properties."""
            return cls(
                x=data.get("X", 0.0),
                y=data.get("Y", 0.0),
                type=data.get("Type", ""),
                year=data.get("Year", ""),
                failure_frequency=data.get("FailureFrequency", 0.0),
            )

    @dataclass_json
    @dataclass
    class Geo(DataClassJsonMixin):
        """Cable Geographical properties."""

        coordinates: FloatCoords = field(
            default_factory=list,
            metadata=config(encoder=encode_float_coords, decoder=decode_float_coords),
        )

        def serialize(self) -> str:
            """Serialize Geo properties."""
            props = []
            if self.coordinates:
                props.append(f"Coordinates:{encode_float_coords(self.coordinates)}")
            return " ".join(props)

        @classmethod
        def deserialize(cls, data: dict) -> CableMV.Geo:
            """Deserialize Geo properties."""
            return cls(
                coordinates=decode_float_coords(data.get("Coordinates", "''")),
            )

    general: General
    cable_parts: list[CablePart]
    cable_types: list[CableType]
    presentations: list[BranchPresentation]
    geo_cable_parts: list[GeoCablePart] = field(default_factory=list)
    joints: list[Joint] = field(default_factory=list)
    geo: Geo | None = None

    def register(self, network: NetworkMV) -> None:
        """Will add cable to the network."""
        if self.general.guid in network.cables:
            logger.critical("Cable %s already exists, overwriting", self.general.guid)
        network.cables[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the cable to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        # Group cable parts with their corresponding types and geo parts
        for i, (cable_part, cable_type) in enumerate(zip(self.cable_parts, self.cable_types, strict=False)):
            lines.append(f"#CablePart {cable_part.serialize()}")
            lines.append(f"#CableType {cable_type.serialize()}")

            # Add corresponding GeoCablePart if available
            if i < len(self.geo_cable_parts):
                lines.append(f"#GeoCablePart {self.geo_cable_parts[i].serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Joint {joint.serialize()}" for joint in self.joints)

        if self.geo:
            lines.append(f"#Geo {self.geo.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> CableMV:
        """Deserialization of the cable from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TCableMS: The deserialized cable

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        # Handle cable parts and types
        cable_parts_data = data.get("cable_parts", [])
        cable_parts = []
        for part_data in cable_parts_data:
            cable_part = cls.CablePart.deserialize(part_data)
            cable_parts.append(cable_part)

        cable_types_data = data.get("cable_types", [])
        cable_types = []
        for type_data in cable_types_data:
            from .shared import CableType

            cable_type = CableType.deserialize(type_data)
            cable_types.append(cable_type)

        # Handle geoCableParts
        geo_cable_parts_data = data.get("geo_cable_parts", [])
        geo_cable_parts = []
        for geo_data in geo_cable_parts_data:
            from .shared import GeoCablePart

            geo_cable_part = GeoCablePart.deserialize(geo_data)
            geo_cable_parts.append(geo_cable_part)

        # Handle presentations
        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import BranchPresentation

            presentation = BranchPresentation.deserialize(pres_data)
            presentations.append(presentation)

        # Handle joints
        joints_data = data.get("joints", [])
        joints = []
        for joint_data in joints_data:
            joint = cls.Joint.deserialize(joint_data)
            joints.append(joint)

        # Handle geo
        geo = None
        if data.get("geo"):
            geo = cls.Geo.deserialize(data["geo"][0])

        return cls(
            general=general,
            cable_parts=cable_parts,
            cable_types=cable_types,
            presentations=presentations,
            geo_cable_parts=geo_cable_parts,
            joints=joints,
            geo=geo,
        )
