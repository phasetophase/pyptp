"""Transformer Load (Element)."""

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
    optional_field,
    string_field,
)
from pyptp.elements.lv.shared import HarmonicsType
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
    from pyptp.network_mv import NetworkMV

    from .presentations import ElementPresentation


@dataclass_json
@dataclass
class TransformerLoadMV(ExtrasNotesMixin, HasPresentationsMixin):
    """Represents a transformer load (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a transformer load."""

        node: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        sub_number: int = 0
        creation_time: float | int = 0
        mutation_date: int = optional_field(0)
        revision_date: float | int = optional_field(0.0)
        variant: bool = False
        name: str = string_field()
        switch_state: int = 1
        field_name: str = string_field()
        failure_frequency: float | int = 0
        repair_duration: float | int = 0
        maintenance_frequency: float | int = 0
        maintenance_duration: float | int = 0
        maintenance_cancel_duration: float | int = 0
        not_preferred: bool = False
        load_p: float | int = 0
        load_q: float | int = 0
        load_behaviour: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        load_growth: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        profile: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        generation_p: float = 0
        generation_q: float = 0
        generation_growth: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        generation_profile: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        pv_pnom: float = 0
        pv_growth: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        pv_profile: Guid = field(default=NIL_GUID, metadata=config(encoder=encode_guid, decoder=decode_guid))
        large_consumers: int = 0
        generous_consumers: int = 0
        small_consumers: int = 0
        transformer_type: str = string_field()
        tap_position: int = 0
        harmonics_type: str = string_field()
        loadrate_max: float = 0

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_guid("Node", self.node) if self.node != NIL_GUID else "",
                write_guid_no_skip("GUID", self.guid),
                write_integer("SubNumber", self.sub_number) if self.sub_number != 0 else "",
                write_double_no_skip("CreationTime", self.creation_time),
                write_integer("MutationDate", self.mutation_date) if self.mutation_date != 0 else "",
                write_double("RevisionDate", self.revision_date) if self.revision_date != 0.0 else "",
                write_boolean_no_skip("Variant", value=self.variant),
                write_quote_string_no_skip("Name", self.name),
                write_integer_no_skip("SwitchState", self.switch_state),
                write_quote_string_no_skip("FieldName", self.field_name),
                write_double("FailureFrequency", self.failure_frequency),
                write_double("RepairDuration", self.repair_duration),
                write_double("MaintenanceFrequency", self.maintenance_frequency),
                write_double("MaintenanceDuration", self.maintenance_duration),
                write_double("MaintenanceCancelDuration", self.maintenance_cancel_duration),
                write_boolean("NotPreferred", value=self.not_preferred),
                write_double("LoadP", self.load_p),
                write_double("LoadQ", self.load_q),
                write_guid("LoadBehaviour", self.load_behaviour) if self.load_behaviour != NIL_GUID else "",
                write_guid("LoadGrowth", self.load_growth) if self.load_growth != NIL_GUID else "",
                write_guid("Profile", self.profile) if self.profile != NIL_GUID else "",
                write_double("GenerationP", self.generation_p),
                write_double("GenerationQ", self.generation_q),
                write_guid("GenerationGrowth", self.generation_growth) if self.generation_growth != NIL_GUID else "",
                write_guid("GenerationProfile", self.generation_profile) if self.generation_profile != NIL_GUID else "",
                write_double("PVPnom", self.pv_pnom),
                write_guid("PvGrowth", self.pv_growth) if self.pv_growth != NIL_GUID else "",
                write_guid("PvProfile", self.pv_profile) if self.pv_profile != NIL_GUID else "",
                write_integer("LargeConsumers", self.large_consumers),
                write_integer("GenerousConsumers", self.generous_consumers),
                write_integer("SmallConsumers", self.small_consumers),
                write_quote_string("TransformerType", self.transformer_type),
                write_integer("TapPosition", self.tap_position),
                write_quote_string("HarmonicsType", self.harmonics_type),
                write_double("LoadrateMax", self.loadrate_max),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerLoadMV.General:
            """Deserialize General properties."""
            return cls(
                node=decode_guid(data.get("Node", str(NIL_GUID))),
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                sub_number=data.get("SubNumber", 0),
                creation_time=data.get("CreationTime", 0),
                mutation_date=data.get("MutationDate", 0),
                revision_date=data.get("RevisionDate", 0.0),
                variant=data.get("Variant", False),
                name=data.get("Name", ""),
                switch_state=data.get("SwitchState", 1),
                field_name=data.get("FieldName", ""),
                failure_frequency=data.get("FailureFrequency", 0),
                repair_duration=data.get("RepairDuration", 0),
                maintenance_frequency=data.get("MaintenanceFrequency", 0),
                maintenance_duration=data.get("MaintenanceDuration", 0),
                maintenance_cancel_duration=data.get("MaintenanceCancelDuration", 0),
                not_preferred=data.get("NotPreferred", False),
                load_p=data.get("LoadP", 0),
                load_q=data.get("LoadQ", 0),
                load_behaviour=decode_guid(data.get("LoadBehaviour", str(NIL_GUID))),
                load_growth=decode_guid(data.get("LoadGrowth", str(NIL_GUID))),
                profile=decode_guid(data.get("Profile", str(NIL_GUID))),
                generation_p=data.get("GenerationP", 0),
                generation_q=data.get("GenerationQ", 0),
                generation_growth=decode_guid(data.get("GenerationGrowth", str(NIL_GUID))),
                generation_profile=decode_guid(data.get("GenerationProfile", str(NIL_GUID))),
                pv_pnom=data.get("PVPnom", 0),
                pv_growth=decode_guid(data.get("PvGrowth", str(NIL_GUID))),
                pv_profile=decode_guid(data.get("PvProfile", str(NIL_GUID))),
                large_consumers=data.get("LargeConsumers", 0),
                generous_consumers=data.get("GenerousConsumers", 0),
                small_consumers=data.get("SmallConsumers", 0),
                transformer_type=data.get("TransformerType", ""),
                tap_position=data.get("TapPosition", 0),
                harmonics_type=data.get("HarmonicsType", ""),
                loadrate_max=data.get("LoadrateMax", 0),
            )

    @dataclass_json
    @dataclass
    class TransformerLoadType(DataClassJsonMixin):
        """Electrotechnical properties of the transformer load."""

        short_name: str = string_field()
        snom: float = 0.0
        unom1: float = 0.0
        unom2: float = 0.0
        uk: float = 0.0
        pk: float = 0.0
        po: float = 0.0
        winding_connection1: str = string_field()
        winding_connection2: str = string_field()
        clock_number: int = 0
        tap_side: int = 1
        tap_size: float = 0
        tap_min: int = 0
        tap_nom: int = 0
        tap_max: int = 0

        def serialize(self) -> str:
            """Serialize TransformerLoadType properties."""
            return serialize_properties(
                write_quote_string_no_skip("ShortName", self.short_name),
                write_double_no_skip("Snom", self.snom),
                write_double_no_skip("Unom1", self.unom1),
                write_double_no_skip("Unom2", self.unom2),
                write_double_no_skip("Uk", self.uk),
                write_double_no_skip("Pk", self.pk),
                write_double_no_skip("Po", self.po),
                write_quote_string_no_skip("WindingConnection1", self.winding_connection1),
                write_quote_string_no_skip("WindingConnection2", self.winding_connection2),
                write_integer_no_skip("ClockNumber", self.clock_number),
                write_integer_no_skip("TapSide", self.tap_side),
                write_double_no_skip("TapSize", self.tap_size),
                write_integer_no_skip("TapMin", self.tap_min),
                write_integer_no_skip("TapNom", self.tap_nom),
                write_integer_no_skip("TapMax", self.tap_max),
            )

        @classmethod
        def deserialize(cls, data: dict) -> TransformerLoadMV.TransformerLoadType:
            """Deserialize TransformerLoadType properties."""
            return cls(
                short_name=data.get("ShortName", ""),
                snom=data.get("Snom", 0.0),
                unom1=data.get("Unom1", 0.0),
                unom2=data.get("Unom2", 0.0),
                uk=data.get("Uk", 0.0),
                pk=data.get("Pk", 0.0),
                po=data.get("Po", 0.0),
                winding_connection1=data.get("WindingConnection1", ""),
                winding_connection2=data.get("WindingConnection2", ""),
                clock_number=data.get("ClockNumber", 0),
                tap_side=data.get("TapSide", 1),
                tap_size=data.get("TapSize", 0),
                tap_min=data.get("TapMin", 0),
                tap_nom=data.get("TapNom", 0),
                tap_max=data.get("TapMax", 0),
            )

    general: General
    type: TransformerLoadType
    presentations: list[ElementPresentation]
    harmonics_type: HarmonicsType | None = None
    ceres: dict | None = None

    def __post_init__(self) -> None:
        """Post-initialization to ensure mixins are properly set up."""
        ExtrasNotesMixin.__post_init__(self)
        HasPresentationsMixin.__post_init__(self)

    def register(self, network: NetworkMV) -> None:
        """Will add transformer load to the network."""
        if self.general.guid in network.transformer_loads:
            logger.critical("Transformer Load %s already exists, overwriting", self.general.guid)
        network.transformer_loads[self.general.guid] = self

    def serialize(self) -> str:
        """Serialize the transformer load to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.append(f"#TransformerType {self.type.serialize()}")

        # Add HarmonicsType section if present
        if self.harmonics_type:
            lines.append(f"#HarmonicsType {self.harmonics_type.serialize()}")

        # Add CERES section if present
        if self.ceres:
            ceres_props = []
            for key, value in self.ceres.items():
                ceres_props.append(f"{key}:{value}")
            if ceres_props:
                lines.append(f"#CERES {' '.join(ceres_props)}")

        lines.extend(f"#Presentation {presentation.serialize()}" for presentation in self.presentations)

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> TransformerLoadMV:
        """Deserialization of the transformer load from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TTransformerLoadMS: The deserialized transformer load

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        transformer_type_data = data.get("transformerType", [{}])[0] if data.get("transformerType") else {}
        transformer_type = cls.TransformerLoadType.deserialize(transformer_type_data)

        harmonics_data = data.get("harmonicsType", [{}])[0] if data.get("harmonicsType") else {}
        harmonics_type = None
        if harmonics_data:
            harmonics_type = HarmonicsType.deserialize(harmonics_data)

        ceres_data = data.get("ceres", [{}])[0] if data.get("ceres") else {}
        ceres = None
        if ceres_data:
            ceres = ceres_data

        presentations_data = data.get("presentations", [])
        presentations = []
        for pres_data in presentations_data:
            from .presentations import ElementPresentation

            presentation = ElementPresentation.deserialize(pres_data)
            presentations.append(presentation)

        return cls(
            general=general,
            type=transformer_type,
            presentations=presentations,
            harmonics_type=harmonics_type,
            ceres=ceres,
        )
