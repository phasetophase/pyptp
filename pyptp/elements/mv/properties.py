"""Network Properties (Other)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from pyptp.elements.element_utils import (
    Guid,
    decode_guid,
    encode_guid,
    encode_guid_optional,
    encode_string,
    string_field,
)
from pyptp.elements.mixins import ExtrasNotesMixin
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_boolean,
    write_double,
    write_double_no_skip,
    write_guid,
    write_guid_no_skip,
    write_quote_string,
    write_quote_string_no_skip,
)

if TYPE_CHECKING:
    from pyptp.network_mv import NetworkMV


@dataclass_json
@dataclass
class PropertiesMV(ExtrasNotesMixin):
    """Network Properties."""

    @dataclass_json
    @dataclass
    class System(DataClassJsonMixin):
        """System properties for a network."""

        currency: str = field(default="EUR", metadata=config(encoder=encode_string))

        def serialize(self) -> str:
            """Serialize System properties."""
            return serialize_properties(write_quote_string_no_skip("Currency", self.currency))

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesMV.System:
            """Deserialize System properties."""
            return cls(
                currency=data.get("Currency", "EUR"),
            )

    @dataclass_json
    @dataclass
    class Network(DataClassJsonMixin):
        """Properties of the network instance."""

        guid: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        state: Guid = field(
            default_factory=lambda: Guid(uuid4()),
            metadata=config(encoder=encode_guid, decoder=decode_guid),
        )
        previous_state: Guid | None = field(
            default=None,
            metadata=config(encoder=encode_guid_optional, exclude=lambda x: x is None),
        )
        last_saved_datetime: float | int = 0

        def serialize(self) -> str:
            """Serialize Network properties."""
            return serialize_properties(
                write_guid_no_skip("GUID", self.guid),
                write_guid_no_skip("State", self.state),
                write_guid("PreviousState", self.previous_state) if self.previous_state is not None else "",
                write_double_no_skip("SaveDateTime", self.last_saved_datetime),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesMV.Network:
            """Deserialize Network properties."""
            previous_state = data.get("PreviousState")

            # Handle European decimal format (comma instead of dot) in SaveDateTime
            save_datetime = data.get("SaveDateTime", 0)
            if isinstance(save_datetime, str):
                save_datetime = float(save_datetime.replace(",", "."))
            elif save_datetime is None:
                save_datetime = 0

            return cls(
                guid=decode_guid(data.get("GUID", str(uuid4()))),
                state=decode_guid(data.get("State", str(uuid4()))),
                previous_state=decode_guid(previous_state) if previous_state else None,
                last_saved_datetime=save_datetime,
            )

    @dataclass_json
    @dataclass
    class General(DataClassJsonMixin):
        """General properties of the network."""

        customer: str = string_field()
        place: str = string_field()
        region: str = string_field()
        country: str = string_field()
        date: float | int = 0.0
        project: str = string_field()
        description: str = string_field()
        version: str = string_field()
        state: str = string_field()
        by: str = "PyPtP"

        def serialize(self) -> str:
            """Serialize General properties."""
            return serialize_properties(
                write_quote_string("Customer", self.customer),
                write_quote_string("Place", self.place),
                write_quote_string("Region", self.region),
                write_quote_string("Country", self.country),
                write_double("Date", self.date, skip=0.0),
                write_quote_string("Project", self.project),
                write_quote_string("Description", self.description),
                write_quote_string("Version", self.version),
                write_quote_string("State", self.state),
                write_quote_string("By", self.by, skip="PyPtP"),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesMV.General:
            """Deserialize General properties."""
            return cls(
                customer=data.get("Customer", ""),
                place=data.get("Place", ""),
                region=data.get("Region", ""),
                country=data.get("Country", ""),
                date=data.get("Date", 0.0),
                project=data.get("Project", ""),
                description=data.get("Description", ""),
                version=data.get("Version", ""),
                state=data.get("State", ""),
                by=data.get("By", "PyPtP"),
            )

    @dataclass_json
    @dataclass
    class Invisible(DataClassJsonMixin):
        """Invisible."""

        property: list[str] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize Invisible properties."""
            return serialize_properties(
                *[write_quote_string_no_skip(f"Property{i}", prop) for i, prop in enumerate(self.property)],
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesMV.Invisible:
            """Deserialize Invisible properties."""
            properties = []
            i = 0
            while f"Property{i}" in data:
                properties.append(data[f"Property{i}"])
                i += 1

            return cls(property=properties)

    @dataclass_json
    @dataclass
    class History(DataClassJsonMixin):
        """Network History."""

        ask: bool = False
        always: bool = False

        def serialize(self) -> str:
            """Serialize History properties."""
            return serialize_properties(
                write_boolean("Ask", value=self.ask),
                write_boolean("Always", value=self.always),
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesMV.History:
            """Deserialize History properties."""
            return cls(
                ask=data.get("Ask", False),
                always=data.get("Always", False),
            )

    @dataclass_json
    @dataclass
    class HistoryItems(DataClassJsonMixin):
        """History Items."""

        text: list[str] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize HistoryItems properties."""
            return serialize_properties(
                *[write_quote_string_no_skip(f"Text{i}", text) for i, text in enumerate(self.text)],
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesMV.HistoryItems:
            """Deserialize HistoryItems properties."""
            texts = []
            i = 0
            while f"Text{i}" in data:
                texts.append(data[f"Text{i}"])
                i += 1
            return cls(text=texts)

    @dataclass_json
    @dataclass
    class Users(DataClassJsonMixin):
        """Users."""

        user: list[str] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize Users properties."""
            return serialize_properties(
                *[write_quote_string_no_skip(f"User{i}", user) for i, user in enumerate(self.user)],
            )

        @classmethod
        def deserialize(cls, data: dict) -> PropertiesMV.Users:
            """Deserialize Users properties."""
            users = []
            i = 0
            while f"User{i}" in data:
                users.append(data[f"User{i}"])
                i += 1
            return cls(user=users)

    system: System
    network: Network | None = None
    general: General | None = None
    invisible: Invisible | None = None
    history: History | None = None
    history_items: HistoryItems | None = None
    users: Users | None = None

    def register(self, network: NetworkMV) -> None:
        """Will set the network properties."""
        network.properties = self

    def serialize(self) -> str:
        """Serialize the network properties to a string."""
        lines = []

        if self.system:
            lines.append(f"#System {self.system.serialize()}")
        else:
            # Fallback to default system if somehow None
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

        lines.extend(f"#Extra Text:{extra.text}" for extra in self.extras)
        lines.extend(f"#Note Text:{note.text}" for note in self.notes)

        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> PropertiesMV:
        """Deserialization of the properties from VNF format.

        Args:
            data: Dictionary containing the parsed VNF data

        Returns:
            TPropertiesMS: The deserialized properties

        """
        system_data = data.get("system", [{}])[0] if data.get("system") else {}
        system = cls.System.deserialize(system_data)

        network_data = data.get("network", [{}])[0] if data.get("network") else {}
        network = cls.Network.deserialize(network_data) if network_data else None

        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data) if general_data else None

        invisible_data = data.get("invisible", [{}])[0] if data.get("invisible") else {}
        invisible = cls.Invisible.deserialize(invisible_data) if invisible_data else None

        history_data = data.get("history", [{}])[0] if data.get("history") else {}
        history = cls.History.deserialize(history_data) if history_data else None

        history_items_data = data.get("historyItems", [{}])[0] if data.get("historyItems") else {}
        history_items = cls.HistoryItems.deserialize(history_items_data) if history_items_data else None

        users_data = data.get("users", [{}])[0] if data.get("users") else {}
        users = cls.Users.deserialize(users_data) if users_data else None

        return cls(
            system=system,
            network=network,
            general=general,
            invisible=invisible,
            history=history,
            history_items=history_items,
            users=users,
        )
