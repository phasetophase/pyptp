"""Validator that checks the side a fuse, switch or measure field sits on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp._network_objects import NetworkObject, SecondaryParent, all_secondaries, secondary_parents
from pyptp.elements.element_utils import name_or_guid
from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.elements.mv.transformer_load import TransformerLoadMV
from pyptp.validator import Issue, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.elements.element_utils import Guid
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class SecondarySideValidator(Validator):
    """Checks that every fuse, switch, measure field and indicator sits on a side its object has.

    Placed on any other side, it does not load.
    """

    name = "secondary_side"
    description = "Verifies every fuse, switch, measure field and indicator sits on a side its object has"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Return an issue per secondary on a side the object it sits in does not have."""
        from pyptp.network_mv import NetworkMV

        parents = secondary_parents(network)
        secondaries = all_secondaries(network)
        if isinstance(network, NetworkMV):
            secondaries.extend(network.indicators.values())

        issues: list[Issue] = []
        for secondary in secondaries:
            issue = self._side_issue(secondary, parents)
            if issue is not None:
                issues.append(issue)
        return issues

    def _side_issue(self, secondary: NetworkObject, parents: dict[Guid, SecondaryParent]) -> Issue | None:
        parent = parents.get(secondary.general.in_object)
        if parent is None:
            return None
        allowed = _allowed_sides(secondary, parent)
        side = secondary.general.side
        if side in allowed:
            return None

        allowed_text = ", ".join(str(allowed_side) for allowed_side in allowed)
        text = (
            f"{_kind(secondary)} '{name_or_guid(secondary.general)}' is on side {side} of "
            f"{_kind(parent.obj)} '{name_or_guid(parent.obj.general)}', allowed sides: {allowed_text}"
        )
        return self.issue(secondary, "secondary_side_invalid", text, side=side, allowed_sides=allowed)


def _allowed_sides(secondary: NetworkObject, parent: SecondaryParent) -> list[int]:
    if isinstance(secondary, MeasureFieldMV) and isinstance(parent.obj, TransformerLoadMV):
        return [1, 2]
    return parent.sides


def _kind(obj: NetworkObject) -> str:
    return type(obj).__name__.removesuffix("LV").removesuffix("MV")
