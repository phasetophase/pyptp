"""Reusable, type-safe strategies for converting parsed dictionaries into final objects."""

from __future__ import annotations

import re
from typing import Any, Generic, Protocol, TypeVar

from pyptp.elements.lv.profile import ProfileLV
from pyptp.elements.lv.properties import PropertiesLV
from pyptp.elements.lv.shared import FuseType
from pyptp.elements.mixins import Extra, Note

T_co = TypeVar("T_co", covariant=True)


class ValuesInitable(Protocol[T_co]):
    """A protocol for classes whose constructor accepts a 'values' keyword argument."""

    def __init__(self, *, values: list) -> None: ...


T = TypeVar("T")
T_Values = TypeVar("T_Values", bound=ValuesInitable)


class BaseStrategy(Generic[T]):
    """Base class for all parsing strategies."""

    def process(self, dict_list: list[dict] | None) -> T | list[T] | None:
        """Process a list of parsed dictionaries into a final object or list."""
        raise NotImplementedError


class SingleObjectStrategy(BaseStrategy[T]):
    """Create a single object from a dictionary."""

    def __init__(self, cls: type[T], *, required: bool = False) -> None:
        self.cls = cls
        self.required = required

    def process(self, dict_list: list[dict] | None) -> T | None:
        """Process the data for a single object."""
        if not dict_list:
            if self.required:
                msg = "Required GNF section is missing"
                raise ValueError(msg)
            return None
        data = dict_list[0]
        if hasattr(self.cls, "from_dict"):
            return self.cls.from_dict(data)  # type: ignore[attr-defined]
        return self.cls(**data)


class ListOfObjectsStrategy(BaseStrategy[T]):
    """Create a list of objects."""

    def __init__(self, cls: type[T], *, required: bool = False) -> None:
        self.cls = cls
        self.required = required

    def process(self, dict_list: list[dict] | None) -> list[T]:
        """Process the data for a list of objects."""
        if not dict_list:
            if self.required:
                msg = "Required GNF section is missing or empty"
                raise ValueError(msg)
            return []
        if hasattr(self.cls, "from_dict"):
            return [self.cls.from_dict(d) for d in dict_list]  # type: ignore[attr-defined]
        return [self.cls(**d) for d in dict_list]


class SingleTextObjectStrategy(BaseStrategy[T]):
    """Create a single object from a GNF text tag (like #Comment)."""

    def __init__(self, cls: type[T], *, required: bool = False) -> None:
        self.cls = cls
        self.required = required

    def process(self, dict_list: list[dict] | None) -> T | None:
        """Process the data for a single text-based object."""
        if not dict_list:
            if self.required:
                msg = "Required text-based section is missing"
                raise ValueError(msg)
            return None
        return self.cls(text=dict_list[0].get("Text", ""))  # type: ignore[call-arg]


class TextNoteStrategy(BaseStrategy[Note]):
    """Create a list of Note objects."""

    def process(self, dict_list: list[dict] | None) -> list[Note]:
        """Process the data for a list of Note objects."""
        if not dict_list:
            return []
        return [Note(text=d.get("Text", "")) for d in dict_list]


class TextExtraStrategy(BaseStrategy[Extra]):
    """Create a list of Extra objects from 'key=value' text."""

    def process(self, dict_list: list[dict] | None) -> list[Extra]:
        """Process the data for a list of Extra objects."""
        if not dict_list:
            return []
        extras = []
        for d in dict_list:
            text = d.get("Text", "")
            match = re.match(r"([^=]+)=(.*)", text)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                extras.append(Extra(text=key + value))
            elif text:
                # Handle cases where there is only a key and no '='
                extras.append(Extra(text=text))
        return extras


class KeySortedValuesStrategy(BaseStrategy[list[Any]]):
    """A generic strategy to extract values from a dictionary, sorted by their keys.

    Handles keys like 'f1', 'f10', 'User1', 'Text99', etc.
    """

    def __init__(self, key_prefix: str) -> None:
        self.key_prefix = key_prefix

    def process(self, dict_list: list[dict] | None) -> list[Any]:
        """Process the data for a key-sorted values list."""
        if not dict_list:
            return []
        data_dict = dict_list[0]

        prefix_len = len(self.key_prefix)
        numeric_keys = [k for k in data_dict if k.startswith(self.key_prefix) and k[prefix_len:].isdigit()]

        sorted_keys = sorted(numeric_keys, key=lambda k: int(k[prefix_len:]))
        return [data_dict[key] for key in sorted_keys]


class IndexedValuesStrategy(BaseStrategy[T_Values]):
    """Handle tags like '#Fields' by passing a list of values to a constructor."""

    def __init__(self, cls: type[T_Values], *, key_prefix: str) -> None:
        self.cls = cls
        self.key_prefix = key_prefix

    def process(self, dict_list: list[dict] | None) -> T_Values | None:
        """Process the data for an indexed values object."""
        if not dict_list:
            return None
        values = KeySortedValuesStrategy(self.key_prefix).process(dict_list)
        return self.cls(values=values)


class ProfileTypeStrategy(BaseStrategy[ProfileLV.ProfileType]):
    """A custom strategy for the #ProfileType block."""

    def __init__(self, *, required: bool = False) -> None:
        self.required = required

    def process(self, dict_list: list[dict] | None) -> ProfileLV.ProfileType | None:
        """Process the data for a profile type."""
        if not dict_list or "Text" not in dict_list[0]:
            if self.required:
                msg = "Required GNF section '#ProfileType' is missing or malformed"
                raise ValueError(msg)
            return None

        raw_text = dict_list[0]["Text"]

        parsed_dict = {}
        for part in raw_text.split():
            if ":" in part:
                key, val = part.split(":", 1)
                parsed_dict[key.strip()] = val.strip()

        sort_val = parsed_dict.pop("Sort", str(ProfileLV.ProfileType.sort))
        try:
            sort_int = int(sort_val)
        except (ValueError, TypeError):
            sort_int = ProfileLV.ProfileType.sort

        factor_strings = KeySortedValuesStrategy(key_prefix="f").process([parsed_dict])

        factors = []

        for factor_str in factor_strings:
            factor_str_clean = str(factor_str).replace(",", ".")
            try:
                factor_float = float(factor_str_clean)
                factors.append(factor_float)
            except (ValueError, TypeError):
                continue

        return ProfileLV.ProfileType(sort=sort_int, f=factors)


class UsersObjectStrategy(BaseStrategy[PropertiesLV.Users]):
    """Uses KeySortedValuesStrategy to get a list of user strings, then wraps them in a TPropertiesLS.Users object."""

    def process(self, dict_list: list[dict] | None) -> PropertiesLV.Users | None:
        """Process the data for a Users object."""
        if not dict_list:
            return None

        user_list = KeySortedValuesStrategy(key_prefix="User").process(dict_list)
        return PropertiesLV.Users(User=user_list) if user_list else None


class HistoryItemsObjectStrategy(BaseStrategy[PropertiesLV.HistoryItems]):
    """Gets a list of history strings, then wraps them in a TPropertiesLS.HistoryItems."""

    def process(self, dict_list: list[dict] | None) -> PropertiesLV.HistoryItems | None:
        """Process the data for a HistoryItems object."""
        if not dict_list:
            return None

        history_list = KeySortedValuesStrategy(key_prefix="Text").process(dict_list)
        return PropertiesLV.HistoryItems(Text=history_list) if history_list else None


class ComplexFuseTypeStrategy(BaseStrategy[FuseType]):
    """A custom strategy for the #FuseType block, which requires transforming indexed 'I' and 'T' fields into lists."""

    def process(self, dict_list: list[dict] | None) -> FuseType | None:
        """Process the data for a complex fuse type."""
        if not dict_list:
            return None

        ft_data = dict_list[0].copy()

        # maybe seperate branch for T1 but I dont think timeseries appear without I values
        if "I1" in ft_data:
            i_keys = [k for k in ft_data if k.startswith("I") and k[1:].isdigit()]
            t_keys = [k for k in ft_data if k.startswith("T") and k[1:].isdigit()]

            sorted_i_keys = sorted(i_keys, key=lambda k: int(k[1:]))
            sorted_t_keys = sorted(t_keys, key=lambda k: int(k[1:]))

            ft_data["I"] = [ft_data.pop(key) for key in sorted_i_keys]
            ft_data["T"] = [ft_data.pop(key) for key in sorted_t_keys]

        return FuseType.deserialize(ft_data)


class PassThroughStrategy(BaseStrategy[dict]):
    """A simple strategy that passes the first parsed dictionary through, as is."""

    def process(self, dict_list: list[dict] | None) -> dict:
        """Return the first dictionary in the list, or an empty dict."""
        if not dict_list:
            return {}
        return dict_list[0]
