"""General Network Properties."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, dataclass_json

from pyptp.elements.element_utils import (
    Guid,
    config,
    decode_guid,
    encode_guid,
    encode_guid_optional,
    optional_field,
    string_field,
)
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_double,
    write_guid,
    write_guid_no_skip,
    write_quote_string,
)

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass_json
@dataclass
class PropertiesLV:
    """LV Network Properties."""

    @dataclass_json
    @dataclass
    class System(DataClassJsonMixin):
        """System."""

        currency: str = "EUR"

        def serialize(self) -> str:
            """Serialize System properties."""
            return serialize_properties(write_quote_string("Currency", self.currency))

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesLV.System:
            """Deserialize System properties."""
            return cls(
                currency=data.get("Currency", "EUR"),
            )

    @dataclass_json
    @dataclass
    class Network(DataClassJsonMixin):
        """Network."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        previous_state: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        state: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        save_datetime: float | int = 0

        def serialize(self) -> str:
            """Serialize Network properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_guid("PreviousState", self.previous_state) if self.previous_state is not None else "",
                write_guid_no_skip("State", self.state),
                write_double("SaveDateTime", self.save_datetime, skip=0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesLV.Network:
            """Deserialize Network properties."""
            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                previous_state=decode_guid(data["PreviousState"]) if data.get("PreviousState") is not None else None,
                state=decode_guid(data.get("State", str(uuid4()))),
                save_datetime=data.get("SaveDateTime", 0),
            )

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General."""

        customer: str = string_field()
        place: str = string_field()
        region: str = string_field()
        country: str = string_field()
        date: float | int = optional_field(0)
        project: str = string_field()
        description: str = string_field()
        version: str = string_field()
        state: str = string_field()
        by: str = string_field()

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_quote_string("Customer", self.customer),
                write_quote_string("Place", self.place),
                write_quote_string("Region", self.region),
                write_quote_string("Country", self.country),
                write_double("Date", self.date, skip=0),
                write_quote_string("Project", self.project),
                write_quote_string("Description", self.description),
                write_quote_string("Version", self.version),
                write_quote_string("State", self.state),
                write_quote_string("By", self.by),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesLV.General:
            """Deserialize General properties."""
            return cls(
                customer=data.get("Customer", ""),
                place=data.get("Place", ""),
                region=data.get("Region", ""),
                country=data.get("Country", ""),
                date=data.get("Date", 0),
                project=data.get("Project", ""),
                description=data.get("Description", ""),
                version=data.get("Version", ""),
                state=data.get("State", ""),
                by=data.get("By", ""),
            )

    @dataclass_json
    @dataclass
    class Invisible(DataClassJsonMixin):
        """Invisible."""

        Property: list[str] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize Invisible properties."""
            return serialize_properties(
                *[write_quote_string(f"Property{i}", prop) for i, prop in enumerate(self.Property)],
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesLV.Invisible:
            """Deserialize Invisible properties."""
            properties = []
            i = 0
            while f"Property{i}" in data:
                properties.append(data[f"Property{i}"])
                i += 1
            return cls(Property=properties)

    @dataclass_json
    @dataclass
    class History(DataClassJsonMixin):
        """History."""

        ask: bool = False
        always: bool = False

        def serialize(self) -> str:
            """Serialize History properties."""
            return serialize_properties(
                write_boolean("Ask", value=self.ask),
                write_boolean("Always", value=self.always),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesLV.History:
            """Deserialize History properties."""
            return cls(
                ask=data.get("Ask", False),
                always=data.get("Always", False),
            )

    @dataclass_json
    @dataclass
    class HistoryItems(DataClassJsonMixin):
        """History Items."""

        Text: list[str] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize HistoryItems properties."""
            return serialize_properties(*[write_quote_string(f"Text{i}", text) for i, text in enumerate(self.Text)])

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesLV.HistoryItems:
            """Deserialize HistoryItems properties."""
            texts = []
            i = 0
            while f"Text{i}" in data:
                texts.append(data[f"Text{i}"])
                i += 1
            return cls(Text=texts)

    @dataclass_json
    @dataclass
    class Users(DataClassJsonMixin):
        """Users."""

        User: list[str] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize Users properties."""
            return serialize_properties(*[write_quote_string(f"User{i}", user) for i, user in enumerate(self.User)])

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesLV.Users:
            """Deserialize Users properties."""
            users = []
            i = 0
            while f"User{i}" in data:
                users.append(data[f"User{i}"])
                i += 1
            return cls(User=users)

    system: System
    network: Network | None = None
    general: General | None = None
    invisible: Invisible | None = None
    history: History | None = None
    history_items: HistoryItems | None = None
    users: Users | None = None

    def register(self, network: NetworkLV) -> None:
        """Will set the network properties."""
        network.properties = self

    def serialize(self) -> str:
        """Serialize the network properties to a string."""
        lines = []

        if self.system:
            lines.append(f"#System {self.system.serialize()}")
        else:
            lines.append(f"#System {self.System().serialize()}")

        network_serialize = self.network.serialize() if self.network else ""
        lines.append(f"#Network {network_serialize}")

        general_serialize = self.general.serialize() if self.general else ""
        lines.append(f"#General {general_serialize}")

        invisible_serialize = self.invisible.serialize() if self.invisible else ""
        lines.append(f"#Invisible {invisible_serialize}")

        history_serialize = self.history.serialize() if self.history else ""
        lines.append(f"#History {history_serialize}")

        history_items_serialize = self.history_items.serialize() if self.history_items else ""
        lines.append(f"#HistoryItems {history_items_serialize}")

        users_serialize = self.users.serialize() if self.users else ""
        lines.append(f"#Users {users_serialize}")

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> PropertiesLV:
        """Deserialization of the network properties from GNF format.

        Args:
            data: Dictionary containing the parsed GNF data

        Returns:
            TPropertiesLS: The deserialized network properties

        """
        system_data = data.get("system", [{}])[0] if data.get("system") else {}
        system = cls.System.deserialize(system_data)

        network = None
        if data.get("network"):
            network = cls.Network.deserialize(data["network"][0])

        general = None
        if data.get("general"):
            general = cls.General.deserialize(data["general"][0])

        invisible = None
        if data.get("invisible"):
            invisible = cls.Invisible.deserialize(data["invisible"][0])

        history = None
        if data.get("history"):
            history = cls.History.deserialize(data["history"][0])

        history_items = None
        if data.get("historyItems"):
            history_items = cls.HistoryItems.deserialize(data["historyItems"][0])

        users = None
        if data.get("users"):
            users = cls.Users.deserialize(data["users"][0])

        return cls(
            system=system,
            network=network,
            general=general,
            invisible=invisible,
            history=history,
            history_items=history_items,
            users=users,
        )
