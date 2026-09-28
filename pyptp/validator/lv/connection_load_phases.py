"""Validator that checks a connection's load and generation are set in the fields its phase setting uses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.element_utils import name_or_guid
from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.elements.lv.connection import ConnectionLV
    from pyptp.network_lv import NetworkLV

_THREE_PHASE = 4

_SINGLE_PHASE_FIELDS = ("p1", "q1")

_THREE_PHASE_FIELDS = ("pa", "qa", "pb", "qb", "pc", "qc", "pab", "qab", "pac", "qac", "pbc", "qbc")


class ConnectionLoadPhasesValidator(Validator):
    """Checks that a connection's load and generation are set in the fields its phase setting uses.

    A three-phase connection uses the per-phase fields, any other connection uses p1 and q1.
    Power set in the other fields is ignored.
    """

    name = "connection_load_phases"
    description = "Verifies every connection states its load and generation in the fields matching its phase setting"
    applies_to = ("LV",)
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV) -> list[Issue]:
        """Return an issue per load or generation of a connection that is set in ignored fields."""
        issues: list[Issue] = []
        for connection in network.homes.values():
            phases = connection.general.phases
            if phases == _THREE_PHASE:
                ignored = _SINGLE_PHASE_FIELDS
                phase_text = "three-phase"
            else:
                ignored = _THREE_PHASE_FIELDS
                phase_text = "single-phase"

            parts = {"load": connection.load, "generation": connection.generation}
            for part_name, part in parts.items():
                set_but_ignored = _set_fields(part, ignored)
                if not set_but_ignored:
                    continue

                message = (
                    f"Connection '{name_or_guid(connection.general)}' is {phase_text}, "
                    f"so its {part_name} in {', '.join(set_but_ignored)} is ignored"
                )
                issues.append(
                    self.issue(
                        connection,
                        "load_ignored_for_phases",
                        message,
                        severity=Severity.WARNING,
                        part=part_name,
                        phases=phases,
                        ignored_fields=set_but_ignored,
                    )
                )
        return issues


def _set_fields(part: ConnectionLV.Load | ConnectionLV.Generation | None, names: tuple[str, ...]) -> list[str]:
    if part is None:
        return []
    return [name for name in names if getattr(part, name)]
