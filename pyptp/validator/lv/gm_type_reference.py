"""Validator that checks the GM type references of connections."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.element_utils import name_or_guid
from pyptp.validator import Issue, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


class GMTypeReferenceValidator(Validator):
    """Checks that every GM on a connection refers to a GM type in the network."""

    name = "gm_type_reference"
    description = "Verifies every GM on a connection refers to a GM type registered in the same network"
    applies_to = ("LV",)
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV) -> list[Issue]:
        """Return an issue per GM whose GM type is missing from the network."""
        issues: list[Issue] = []
        known = set(network.gmtypes)

        for connection in network.homes.values():
            for index, gm in enumerate(connection.gms, start=1):
                if gm.gm_type_number in known:
                    continue
                message = (
                    f"Connection '{name_or_guid(connection.general)}' GM {index} "
                    f"refers to GM type {gm.gm_type_number}, which the network does not contain"
                )
                issues.append(
                    self.issue(connection, "unknown_gm_type", message, gm=index, gm_type_number=gm.gm_type_number)
                )
        return issues
