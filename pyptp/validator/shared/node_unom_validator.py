"""Node nominal voltage (Unom) validator.

Ensures that all nodes have a positive nominal voltage, which is required
by Vision and Gaia for network analysis and version migration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class NodeUnomValidator(Validator):
    """Verifies all nodes have a nominal voltage greater than zero."""

    name = "node_unom"
    description = "Verifies all nodes have a nominal voltage greater than zero"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Check that every node has unom > 0.

        Args:
            network: Network model to validate (LV or MV)

        Returns:
            List of validation issues for nodes with invalid Unom.
            Empty list if all nodes are valid.

        """
        issues: list[Issue] = []

        for node in network.nodes.values():
            gen = node.general
            if gen.unom <= 0:
                issues.append(
                    Issue(
                        code="invalid_node_unom",
                        message=(
                            f"Node '{getattr(gen, 'name', str(gen.guid))}' has Unom {gen.unom}, must be greater than 0"
                        ),
                        severity=Severity.ERROR,
                        object_type="Node",
                        object_id=gen.guid,
                        validator=self.name,
                        details={"unom": gen.unom},
                    ),
                )
        return issues
