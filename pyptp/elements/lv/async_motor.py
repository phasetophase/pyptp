"""Asynchronous motor element for low-voltage networks.

Provides motor load modeling with starting characteristics, efficiency curves
and harmonic content.
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
    write_boolean,
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
    from pyptp.elements.lv.shared import HarmonicsType
    from pyptp.network_lv import NetworkLV

    from .presentations import ElementPresentation


@dataclass
class AsynchronousMotorLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Asynchronous motor element for low-voltage network modeling.

    Models three-phase induction motors with starting transients, power factor
    characteristics, and harmonic generation for comprehensive LV network
    analysis including motor starting studies and efficiency assessments.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """General properties for an asynchronous motor."""

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
        """Name of the connection field."""
        phase: int = 0
        p_mechanic: float = 0
        """Actual mechanical power per motor in MW."""
        istart_inom: int = field(default=0, metadata=config(field_name="Istart/Inom"))
        """Quotient of starting current and nominal current."""
        ta: int = optional_field(0)
        """Motor starting acceleration time in seconds."""
        profile: Guid = field(default=DEFAULT_PROFILE_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        type: str = string_field()
        harmonics_type: str = string_field()
        switch_on_frequency: int = optional_field(0)
        """Motor switch-on frequency in times per day."""

        def serialize(self) -> str:
            """Serialize General properties."""
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
                write_integer_no_skip("Phase", self.phase),
                write_double("Pmechanic", self.p_mechanic),
                write_integer("Istart/Inom", self.istart_inom),
                write_integer("ta", self.ta, skip=0),
                write_guid("Profile", self.profile),
                write_quote_string("AsynchronousMotorType", self.type),
                write_quote_string("HarmonicsType", self.harmonics_type),
                write_integer("SwitchOnFrequency", self.switch_on_frequency, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> AsynchronousMotorLV.General:
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
                phase=data.get("Phase", 0),
                p_mechanic=data.get("Pmechanic", 0),
                istart_inom=data.get("Istart/Inom", 0),
                ta=data.get("ta", 0),
                profile=decode_guid(data.get("Profile", str(DEFAULT_PROFILE_GUID))),
                type=data.get("AsynchronousMotorType", ""),
                harmonics_type=data.get("HarmonicsType", ""),
                switch_on_frequency=data.get("SwitchOnFrequency", 0),
            )

    @dataclass
    class AsynchronousMotorType(DataClassJsonMixin):
        """Asynchronous Motor type properties."""

        single_phase: bool = False
        unom: float = 0.0
        """Nominal voltage in kV."""
        pm_nom: float = 0.0
        """Rated mechanical power per motor in MW."""
        r_x: float = field(default=0.0, metadata=config(field_name="R/X"))
        """R/X ratio for short-circuit studies."""
        istart_inom: int = field(default=0, metadata=config(field_name="Istart/Inom"))
        """Quotient of starting current and nominal current."""
        poles: int = 0
        """Number of poles."""
        rpm_nom: float = 0.0
        """Nominal speed in rpm."""
        critical_torque: float = 0.0
        """Critical torque in %."""
        cos_nom: float = 0.0
        """Power factor at nominal power."""
        efficiency: float = 0.0
        """Efficiency at nominal power in %."""
        p2: float = 0.0
        """Power curve point 2 in pu."""
        cos2: float = 0.0
        """Power factor at curve point 2."""
        n2: float = 0.0
        """Efficiency at curve point 2 in %."""
        p3: float = 0.0
        """Power curve point 3 in pu."""
        cos3: float = 0.0
        """Power factor at curve point 3."""
        n3: float = 0.0
        """Efficiency at curve point 3 in %."""
        p4: float = 0.0
        """Power curve point 4 in pu."""
        cos4: float = 0.0
        """Power factor at curve point 4."""
        n4: float = 0.0
        """Efficiency at curve point 4 in %."""
        p5: float = 0.0
        """Power curve point 5 in pu."""
        cos5: float = 0.0
        """Power factor at curve point 5."""
        n5: float = 0.0
        """Efficiency at curve point 5 in %."""

        def serialize(self) -> str:
            """Serialize AsynchronousMotorType properties."""
            return serialize_properties(
                write_boolean("OnePhase", value=self.single_phase),
                write_double("Unom", self.unom),
                write_double("Pmnom", self.pm_nom),
                write_double("R/X", self.r_x),
                write_integer("Istart/Inom", self.istart_inom),
                write_integer("Poles", self.poles),
                write_double("Rpm", self.rpm_nom),
                write_double("CriticalTorque", self.critical_torque),
                write_double("Cosnom", self.cos_nom),
                write_double("Efficiency", self.efficiency),
                write_double("p2", self.p2),
                write_double("cos2", self.cos2),
                write_double("n2", self.n2),
                write_double("p3", self.p3),
                write_double("cos3", self.cos3),
                write_double("n3", self.n3),
                write_double("p4", self.p4),
                write_double("cos4", self.cos4),
                write_double("n4", self.n4),
                write_double("p5", self.p5),
                write_double("cos5", self.cos5),
                write_double("n5", self.n5),
            )

        @classmethod
        def deserialize(cls, data: dict) -> AsynchronousMotorLV.AsynchronousMotorType:
            """Deserialize AsynchronousMotorType properties."""
            return cls(
                single_phase=data.get("OnePhase", False),
                unom=data.get("Unom", 0.0),
                pm_nom=data.get("Pmnom", 0.0),
                r_x=data.get("R/X", 0.0),
                istart_inom=data.get("Istart/Inom", 0),
                poles=data.get("Poles", 0),
                rpm_nom=data.get("Rpm", 0.0),
                critical_torque=data.get("CriticalTorque", 0.0),
                cos_nom=data.get("Cosnom", 0.0),
                efficiency=data.get("Efficiency", 0.0),
                p2=data.get("p2", 0.0),
                cos2=data.get("cos2", 0.0),
                n2=data.get("n2", 0.0),
                p3=data.get("p3", 0.0),
                cos3=data.get("cos3", 0.0),
                n3=data.get("n3", 0.0),
                p4=data.get("p4", 0.0),
                cos4=data.get("cos4", 0.0),
                n4=data.get("n4", 0.0),
                p5=data.get("p5", 0.0),
                cos5=data.get("cos5", 0.0),
                n5=data.get("n5", 0.0),
            )

    general: General
    presentations: list[ElementPresentation]
    type: AsynchronousMotorType
    harmonics: HarmonicsType | None = None

    def __post_init__(self) -> None:
        """Initialize element after dataclass creation."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkLV) -> None:
        """Will add asynchronous motor to the network."""
        if self.general.guid in network.async_motors:
            logger.critical("Asynchronous Motor %s already exists, overwriting", self.general.guid)
        network.async_motors[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the asynchronous motor to the GNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")

        if self.type:
            lines.append(f"#AsynchronousMotorType {self.type.serialize()}")

        if self.harmonics:
            lines.append(f"#HarmonicsType {self.harmonics.serialize()}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> AsynchronousMotorLV:
        """Deserialization of the asynchronous motor from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TAsyncMotorLS: The deserialized asynchronous motor

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        type_data = data.get("type", [{}])[0] if data.get("type") else {}
        motor_type = cls.AsynchronousMotorType.deserialize(type_data)

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
            harmonics=harmonics,
            type=motor_type,
        )
