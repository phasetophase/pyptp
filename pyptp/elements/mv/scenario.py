"""Scenario (Other)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
    Guid,
    decode_guid,
    encode_guid_optional,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double_no_skip,
    write_guid,
    write_integer,
    write_integer_no_skip,
    write_quote_string,
    write_quote_string_no_skip,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class ScenarioMV:
    """Represents a scenario (MV)."""

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties for a scenario."""

        name: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_quote_string_no_skip("Name", self.name),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ScenarioMV.General:
            """Deserialize General properties."""
            return cls(
                name=data.get("Name", ""),
            )

    @dataclass_json
    @dataclass
    class ScenarioItem:
        """Scenario Item."""

        date: int = 0
        vision_object: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        attribute: int = 0
        value: float = 0.0
        comment: str = string_field()

        def serialize(self) -> str:
            """Serialize ScenarioItem properties."""
            return serialize_properties(
                write_integer("Date", self.date, skip=0),
                write_guid("VisionObject", self.vision_object) if self.vision_object is not None else "",
                write_integer_no_skip("Attribute", self.attribute),
                write_double_no_skip("Value", self.value),
                write_quote_string("Comment", self.comment, skip=""),
            )

        @classmethod
        def deserialize(cls, data: dict) -> ScenarioMV.ScenarioItem:
            """Deserialize ScenarioItem properties."""
            vision_object = data.get("VisionObject")

            return cls(
                date=data.get("Date", 0),
                vision_object=decode_guid(vision_object) if vision_object else None,
                attribute=data.get("Attribute", 0),
                value=data.get("Value", 0.0),
                comment=data.get("Comment", ""),
            )

    general: General
    scenario_items: list[ScenarioItem] = field(default_factory=list)

    def register(self, network: NetworkMV) -> None:
        """Will add scenario to the network."""
        if self.general.name in network.scenarios:
            logger.critical("Scenario %s already exists, overwriting", self.general.name)
        network.scenarios[self.general.name] = self

    def serialize(self) -> str:
        """Serialize the scenario to the VNF format.

        Returns:
            str: The serialized representation.

        """
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        lines.extend(f"#ScenarioItem {item.serialize()}" for item in self.scenario_items)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> ScenarioMV:
        """Deserialization of the scenario from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TScenarioMS: The deserialized scenario

        """
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        scenario_items = []
        scenario_items_data = data.get("scenarioItem", [])
        for item_data in scenario_items_data:
            scenario_item = cls.ScenarioItem.deserialize(item_data)
            scenario_items.append(scenario_item)

        return cls(
            general=general,
            scenario_items=scenario_items,
        )
