"""Cable node reference integrity validator for network topology validation.

Ensures that all cable endpoints reference valid nodes that exist in the network,
preventing broken topology references that could cause analysis failures in
electrical modeling software.

Applies to both LV (Gaia/GNF) and MV (Vision/VNF) networks as topology integrity
is fundamental to all electrical network analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class CableNodeReferenceValidator(Validator):
    """Verifies cable endpoints reference existing nodes in the network."""

    name = "cable_node_reference"
    description = "Verifies cable endpoints reference existing nodes in the network"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Verify that all cable node references point to existing network nodes.

        Args:
            network: Network model to validate (LV or MV)

        Returns:
            List of validation issues for cables with invalid node references.
            Empty list if all cable references are valid.

        """
        issues: list[Issue] = []

        for cable in network.cables.values():
            gen = cable.general
            for end in ("node1", "node2"):
                node_guid = getattr(gen, end)
                if node_guid not in network.nodes:
                    issues.append(
                        Issue(
                            code="missing_node_reference",
                            message=(
                                f"Cable '{getattr(gen, 'name', str(gen.guid))}' "
                                f"references unknown node GUID '{node_guid}'"
                            ),
                            severity=Severity.ERROR,
                            object_type="Cable",
                            object_id=gen.guid,
                            validator=self.name,
                            details={"which_end": end, "referenced_guid": node_guid},
                        ),
                    )
        return issues
