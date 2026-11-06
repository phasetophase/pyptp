"""Validator ensuring no two objects in a network share a GUID."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.element_utils import Guid
from pyptp.validator import Issue, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp._network_objects import NetworkObject
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


def _describe(element: NetworkObject) -> str:
    """Return the element kind and, when it has one, its name."""
    kind = type(element).__name__.removesuffix("LV").removesuffix("MV")
    name = getattr(element.general, "name", "")
    if not name:
        return kind
    return f"{kind} '{name}'"


class UniqueGuidValidator(Validator):
    """Verifies every object GUID is used by one object only."""

    name = "unique_guid"
    description = "Verifies no two objects in the network share a GUID"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Return one issue per object whose GUID is also used by another object."""
        owners: dict[Guid, list[NetworkObject]] = {}
        for collection in vars(network).values():
            if not isinstance(collection, dict):
                continue
            for guid, element in collection.items():
                if not isinstance(guid, Guid):
                    continue
                owners.setdefault(guid, []).append(element)

        issues: list[Issue] = []
        for guid, elements in owners.items():
            if len(elements) == 1:
                continue
            for element in elements:
                others = [_describe(other) for other in elements if other is not element]
                message = f"{_describe(element)} has GUID '{guid}', also used by {', '.join(others)}"
                issues.append(self.issue(element, "duplicate_guid", message, also_used_by=others))
        return issues
