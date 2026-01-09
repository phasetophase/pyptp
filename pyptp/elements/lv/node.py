"""Low-voltage network node element for asymmetrical modeling.

Provides connectivity points for LV network elements with comprehensive
support for phase-to-phase and phase-to-neutral configurations required
for unbalanced load flow analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.element_utils import (
    Guid,
    config,
    decode_guid,
    encode_guid,
    encode_string,
    optional_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin, HasPresentationsMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_double,
    write_double_no_skip,
    write_float_no_skip,
    write_guid_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.elements.lv.shared import Fields
    from pyptp.network_lv import NetworkLV

    from .presentations import NodePresentation


@dataclass
class NodeLV(ExtrasNotesMixin, HasPresentationsMixin):
    """Low-voltage network node for asymmetrical modeling.

    Represents a connection point in LV networks supporting up to 9 conductors
    (L1, L2, L3, N, PE, h1-h4) for complex impedance modeling and unbalanced
    load flow analysis.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """Core electrical and operational properties for LV network nodes.

        Encapsulates all essential node characteristics including connection
        configurations, earthing parameters, and conductor support.
        """

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        """The GUID of the node."""

        creation_time: float | int = 0
        """The date of the creation of the node."""

        mutation_date: int = optional_field(0)
        """The date of the last mutation to the node."""

        revision_date: float | int = optional_field(0.0)
        name: str = field(default="", metadata=config(encoder=encode_string, exclude=lambda x: x == ""))
        short_name: str = field(default="", metadata=config(encoder=encode_string, exclude=lambda x: x == ""))
        id: str = field(default="", metadata=config(encoder=encode_string, exclude=lambda x: x == ""))
        unom: float | int = 0.4
        function: str = field(default="", metadata=config(encoder=encode_string, exclude=lambda x: x == ""))
        earthing_configuration: str = field(
            default="",
            metadata=config(encoder=encode_string, exclude=lambda x: x == ""),
        )

        # Connection switch states for earthing configuration
        s_N_PE: bool = False  # noqa: N815
        s_PE_e: bool = False  # noqa: N815
        Re: float | int = optional_field(0)

        # Conductor mapping and switch states
        k_h1: int = optional_field(0)
        """Auxiliary conductor h1 to main conductor mapping"""

        k_h2: int = optional_field(0)
        """Auxiliary conductor h2 to main conductor mapping"""

        k_h3: int = optional_field(0)
        """Auxiliary conductor h3 to main conductor mapping"""

        k_h4: int = optional_field(0)
        """Auxiliary conductor h4 to main conductor mapping"""

        s_h1: bool = False
        s_h2: bool = False
        s_h3: bool = False
        s_h4: bool = False

        # Geographic coordinates and reliability analysis
        gx: float | int = optional_field(0)
        gy: float | int = optional_field(0)
        failure_frequency: float = optional_field(0.0)
        risk: bool = False

        def serialize(self) -> str:
            """Serialize node properties to GNF format.

            Returns:
                Space-separated property string for GNF file section.

            """
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_float_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date),
                write_double("RevisionDate", self.revision_date),
                write_quote_string("Name", self.name),
                write_quote_string("ShortName", self.short_name),
                write_quote_string("ID", self.id),
                write_double_no_skip("Unom", self.unom),
                write_quote_string("Function", self.function),
                write_quote_string("EarthingConfiguration", self.earthing_configuration),
                write_boolean("s_N_PE", value=self.s_N_PE),
                write_boolean("s_PE_e", value=self.s_PE_e),
                write_double("Re", self.Re),
                write_integer("k_h1", self.k_h1),
                write_integer("k_h2", self.k_h2),
                write_integer("k_h3", self.k_h3),
                write_integer("k_h4", self.k_h4),
                write_boolean("s_h1", value=self.s_h1),
                write_boolean("s_h2", value=self.s_h2),
                write_boolean("s_h3", value=self.s_h3),
                write_boolean("s_h4", value=self.s_h4),
                write_double("GX", self.gx),
                write_double("GY", self.gy),
                write_double("FailureFrequency", self.failure_frequency),
                write_boolean("Risk", value=self.risk),
            )

        @classmethod
        def deserialize(cls, data: dict) -> NodeLV.General:
            """Parse node properties from GNF section data.

            Args:
                data: Dictionary of property key-value pairs from GNF parsing.

            Returns:
                Initialized General instance with parsed node properties.

            """
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                name=data.get("Name", ""),
                short_name=data.get("ShortName", ""),
                id=data.get("ID", ""),
                unom=data.get("Unom", 0.4),
                function=data.get("Function", ""),
                earthing_configuration=data.get("EarthingConfiguration", ""),
                s_N_PE=data.get("s_N_PE", False),
                s_PE_e=data.get("s_PE_e", False),
                Re=data.get("Re", 0),
                k_h1=data.get("k_h1", 0),
                k_h2=data.get("k_h2", 0),
                k_h3=data.get("k_h3", 0),
                k_h4=data.get("k_h4", 0),
                s_h1=data.get("s_h1", False),
                s_h2=data.get("s_h2", False),
                s_h3=data.get("s_h3", False),
                s_h4=data.get("s_h4", False),
                gx=data.get("GX", 0),
                gy=data.get("GY", 0),
                failure_frequency=data.get("FailureFrequency", 0.0),
                risk=data.get("Risk", False),
            )

    general: General
    presentations: list[NodePresentation]
    fields: Fields | None = None

    def __post_init__(self) -> None:
        """Initialize mixins and ensure presentation list format.

        Validates that presentations is a proper list for consistent handling
        across the element hierarchy.
        """
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)
        if not isinstance(self.presentations, list):
            self.presentations = [self.presentations]

    def register(self, network: NetworkLV) -> None:
        """Register node in LV network with GUID-based indexing.

        Args:
            network: Target LV network for node registration.

        Warns:
            Logs critical warning if GUID collision detected during registration.

        """
        if self.general.guid in network.nodes:
            logger.critical("Node %s already exists, overwriting", self.general.guid)
        network.nodes[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize complete node to GNF format.

        Returns:
            Multi-line string with all node sections for GNF file output.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()} ")

        if self.fields:
            lines.append(f"#Fields {self.fields.serialize()}")

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.safe_extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.safe_notes)
        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> NodeLV:
        """Create node instance from parsed GNF data.

        Args:
            data: Dictionary containing parsed GNF sections for node element.

        Returns:
            Fully initialized TNodeLS instance with all properties and
            sub-components properly deserialized.

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        fields = None
        if data.get("fields"):
            from .shared import Fields

            fields = Fields.deserialize(data["fields"][0])

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import NodePresentation

            presentation = NodePresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            presentations=presentations,
            fields=fields,
        )
