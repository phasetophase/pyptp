"""Validator that checks a source's voltage limits against the nominal voltage of its node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.element_utils import name_or_guid
from pyptp.validator import Issue, Severity, Validator, ValidatorCategory
from pyptp.validator.base import _LIMIT_TOLERANCE

if TYPE_CHECKING:
    from pyptp.elements.lv.source import SourceLV
    from pyptp.network_lv import NetworkLV

_UMIN_FACTOR = 0.5

_UMAX_FACTOR = 1.5


class SourceVoltageValidator(Validator):
    """Checks a source's Umin and Umax against the nominal voltage of its node.

    Umin must lie between 0.5 and 1.5 times the nominal voltage, and Umax between Umin
    and 1.5 times the nominal voltage. A source outside these limits does not load.
    """

    name = "source_voltage"
    description = (
        "Verifies every source's Umin lies between 0.5 and 1.5 times the nominal voltage of its node, "
        "and its Umax between Umin and 1.5 times that voltage"
    )
    applies_to = ("LV",)
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV) -> list[Issue]:
        """Return an issue per source whose Umin or Umax is out of range."""
        issues: list[Issue] = []
        for source in network.sources.values():
            node = network.nodes.get(source.general.node)
            if node is None:
                continue
            issue = self._voltage_issue(source, node.general.unom)
            if issue is not None:
                issues.append(issue)
        return issues

    def _voltage_issue(self, source: SourceLV, unom: float) -> Issue | None:
        umin = source.general.umin
        umax = source.general.umax
        umin_lower = _UMIN_FACTOR * unom
        upper = _UMAX_FACTOR * unom
        if _outside(umin, umin_lower, upper):
            return self._out_of_range(source, "umin", umin, umin_lower, upper, unom)
        if _outside(umax, umin, upper):
            return self._out_of_range(source, "umax", umax, umin, upper, unom)
        return None

    def _out_of_range(
        self, source: SourceLV, field: str, value: float, lower: float, upper: float, unom: float
    ) -> Issue:
        name = name_or_guid(source.general)
        message = f"Source '{name}' has {field} {value} kV, outside {lower:g} to {upper:g} kV for its {unom} kV node"
        code = f"source_{field}_out_of_range"
        details = {field: value, "unom": unom, "lower": lower, "upper": upper}
        return self.issue(source, code, message, severity=Severity.ERROR, **details)


def _outside(value: float, lower: float, upper: float) -> bool:
    too_low = value < lower * (1 - _LIMIT_TOLERANCE)
    too_high = value > upper * (1 + _LIMIT_TOLERANCE)
    return too_low or too_high
