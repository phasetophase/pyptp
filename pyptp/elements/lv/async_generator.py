"""Asynchronous generator element for low-voltage networks.

Provides distributed generation capability with asynchronous machine modeling
for LV network power flow analysis and load balancing applications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin

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
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean_no_skip,
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

from .presentations import ElementPresentation


@dataclass
class AsynchronousGeneratorLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Asynchronous generator element for low-voltage network modeling.

    Supports distributed generation with asynchronous machine characteristics
    including multi-point power factor curves and starting current modeling
    for accurate LV network power flow analysis.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical properties for asynchronous generator configuration."""

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
        pref: float = 0
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        type: str = string_field()

        def serialize(self) -> str:
            """Serialize general properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_guid("Node", self.node),
                write_guid_no_skip("GUID", self.guid),
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date, skip=0),
                write_double("RevisionDate", self.revision_date, skip=0.0),
                write_quote_string("Name", self.name),
                write_boolean_no_skip("s_L1", value=self.s_L1),
                write_boolean_no_skip("s_L2", value=self.s_L2),
                write_boolean_no_skip("s_L3", value=self.s_L3),
                write_boolean_no_skip("s_N", value=self.s_N),
                write_quote_string("FieldName", self.field_name),
                write_double("Pref", self.pref),
                write_guid("Profile", self.profile, skip=DEFAULT_PROFILE_GUID),
                write_quote_string("AsynchronousGeneratorType", self.type),
            )

        @classmethod
        def deserialize(cls, data: dict) -> AsynchronousGeneratorLV.General:
            """Parse general properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed properties.

            """
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
                pref=data.get("Pref", 0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                type=data.get("AsynchronousGeneratorType", ""),
            )

    @dataclass
    class AsynchronousGeneratorType(DataClassJsonMixin):
        """Electrical machine parameters for asynchronous generator modeling.

        Defines nominal ratings, impedance characteristics, and multi-point
        power factor curves.
        """

        unom: float = 0.0
        pnom: float = 0.0
        r_x: float = field(default=0.0, metadata=config(field_name="R/X"))
        istart_inom: float = field(default=0.0, metadata=config(field_name="Istart/Inom"))
        poles: int = 0
        rpm_nom: float = 0.0
        critical_torque: float = 0.0
        cos_nom: float = 0.0
        p2: float = 0.0
        cos2: float = 0.0
        p3: float = 0.0
        cos3: float = 0.0
        p4: float = 0.0
        cos4: float = 0.0
        p5: float = 0.0
        cos5: float = 0.0

        def serialize(self) -> str:
            """Serialize generator type properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_double("Unom", self.unom),
                write_double("Pnom", self.pnom),
                write_double("R/X", self.r_x),
                write_double("Istart/Inom", self.istart_inom),
                write_integer("Poles", self.poles),
                write_double("Rpm", self.rpm_nom),
                write_double("CriticalTorque", self.critical_torque),
                write_double("CosNom", self.cos_nom),
                write_double("p2", self.p2),
                write_double("cos2", self.cos2),
                write_double("p3", self.p3),
                write_double("cos3", self.cos3),
                write_double("p4", self.p4),
                write_double("cos4", self.cos4),
                write_double("p5", self.p5),
                write_double("cos5", self.cos5),
            )

        @classmethod
        def deserialize(cls, data: dict) -> AsynchronousGeneratorLV.AsynchronousGeneratorType:
            """Parse generator type properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized AsynchronousGeneratorType instance with parsed machine parameters.

            """
            return cls(
                unom=data.get("Unom", 0.0),
                pnom=data.get("Pnom", 0.0),
                r_x=data.get("R/X", 0.0),
                istart_inom=data.get("Istart/Inom", 0.0),
                poles=data.get("Poles", 0),
                rpm_nom=data.get("Rpm", 0.0),
                critical_torque=data.get("CriticalTorque", 0.0),
                cos_nom=data.get("CosNom", 0.0),
                p2=data.get("p2", 0.0),
                cos2=data.get("cos2", 0.0),
                p3=data.get("p3", 0.0),
                cos3=data.get("cos3", 0.0),
                p4=data.get("p4", 0.0),
                cos4=data.get("cos4", 0.0),
                p5=data.get("p5", 0.0),
                cos5=data.get("cos5", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]
    type: AsynchronousGeneratorType | None = None

    def __post_init__(self) -> None:
        """Initialize mixins for extras, notes, and presentations handling."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Register asynchronous generator in LV network with duplicate detection.

        Args:
            network: Target LV network for generator registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.async_generators:
            logger.critical("Asynchronous Generator %s already exists, overwriting", self.general.guid)
        network.async_generators[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete asynchronous generator to GNF format.

        Returns:
            Multi-line string with all generator sections for GNF file.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#AsynchronousGeneratorType {self.type.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> AsynchronousGeneratorLV:
        """Parse asynchronous generator from GNF format data.

        Args:
            data: Dictionary containing parsed GNF section data with general,
                  type, and presentation information.

        Returns:
            Initialized TASynGeneratorLS instance with all parsed components.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        type_data = data.get("type", [{}])[0] if data.get("type") else None
        async_type = cls.AsynchronousGeneratorType.deserialize(type_data) if type_data else None

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            type=async_type,
        )
