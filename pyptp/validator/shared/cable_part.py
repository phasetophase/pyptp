"""Validator that checks the parts a cable is built from."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyptp.elements.element_utils import name_or_guid
from pyptp.elements.lv.cable import MIN_PART_LENGTH_M as MIN_PART_LENGTH_LV_M
from pyptp.elements.mv.cable import MIN_PART_LENGTH_M as MIN_PART_LENGTH_MV_M
from pyptp.validator import Issue, Validator, ValidatorCategory
from pyptp.validator.base import _LIMIT_TOLERANCE

if TYPE_CHECKING:
    from pyptp.elements.lv.cable import CableLV
    from pyptp.elements.mv.cable import CableMV
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


@dataclass
class _Part:
    cable: CableLV | CableMV
    label: str
    """How messages name the part, for example ``Cable 'A' part 2``."""
    number: int
    length: float
    minimum: float
    has_type: bool


class CablePartValidator(Validator):
    """Checks every cable part for a minimum length and for cable type data.

    A part without cable type data is not saved for a balanced network,
    and is saved without impedance data for an unbalanced one.
    """

    name = "cable_part"
    description = "Verifies every cable part reaches the minimum length and has cable type data"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Return an issue per cable part that is too short or has no type data."""
        issues: list[Issue] = []
        for part in _parts(network):
            if part.length < part.minimum * (1 - _LIMIT_TOLERANCE):
                issues.append(self._too_short_issue(part))
            if not part.has_type:
                issues.append(self._without_type_issue(part))
        return issues

    def _too_short_issue(self, part: _Part) -> Issue:
        message = f"{part.label} is {part.length} m, minimum is {part.minimum} m"
        return self.issue(
            part.cable,
            "cable_part_too_short",
            message,
            part=part.number,
            length=part.length,
            minimum=part.minimum,
        )

    def _without_type_issue(self, part: _Part) -> Issue:
        message = f"{part.label} has no cable type data"
        return self.issue(part.cable, "cable_part_without_type", message, part=part.number)


def _parts(network: NetworkLV | NetworkMV) -> list[_Part]:
    from pyptp.network_lv import NetworkLV

    if isinstance(network, NetworkLV):
        return _lv_parts(network)
    return _mv_parts(network)


def _lv_parts(network: NetworkLV) -> list[_Part]:
    parts: list[_Part] = []
    for cable in network.cables.values():
        label = f"Cable '{name_or_guid(cable.general)}'"
        length = cable.cable_part.length
        has_type = cable.cable_type is not None
        parts.append(_Part(cable, label, 1, length, MIN_PART_LENGTH_LV_M, has_type))
    return parts


def _mv_parts(network: NetworkMV) -> list[_Part]:
    parts: list[_Part] = []
    for cable in network.cables.values():
        type_count = len(cable.cable_types)
        for number, part in enumerate(cable.cable_parts, start=1):
            label = f"Cable '{name_or_guid(cable.general)}' part {number}"
            has_type = number <= type_count
            parts.append(_Part(cable, label, number, part.length, MIN_PART_LENGTH_MV_M, has_type))
    return parts
