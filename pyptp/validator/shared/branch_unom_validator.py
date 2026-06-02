"""Validator that ensures the endpoints of a Cable, Link, Line or Reactance coil have the same unom."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.element_utils import name_or_guid
from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.elements.lv.cable import CableLV
    from pyptp.elements.lv.link import LinkLV
    from pyptp.elements.lv.reactance_coil import ReactanceCoilLV
    from pyptp.elements.mv.cable import CableMV
    from pyptp.elements.mv.line import LineMV
    from pyptp.elements.mv.link import LinkMV
    from pyptp.elements.mv.reactance_coil import ReactanceCoilMV
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class BranchUnomValidator(Validator):
    """Verifies endpoints of a branch in the network have equal unom.

    In a LV-Network we check branches of type LinkLV, CableLV or ReactanceCoilLV. If a branch is of type Transformer or
    SpecialTransformer it is allowed to have unequal unom at its endpoints. Also if the switch states L1, L2, L3 and h1,
    h2, h3, h4 on both ends of a branch are open, branches are allowed to have unequal unom.
    In a MV-Network we check branches of type LinkMV, LineMV, CableMV or ReactanceCoilMV. If a branch is of type
    Transformer or SpecialTransformer it is allowed to have unequal unom. Also if the switch states on both ends
    of a branch are open, branches are allowed to have unequal unom.
    """

    name = "branch_unom_validator"
    description = (
        "Verifies for all branches in the network that the branch endpoints have equal unom, "
        "unless either all switch states are open or the branch is of type (Special) Transformer."
    )
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Return issues for each branch in the network with unequal unom at its endpoints."""
        issues: list[Issue] = []

        for element_type, collection in _get_equal_unom_branch_collections(network):
            for branch in collection.values():
                issues.extend(self._validate_branch(branch, network, element_type))

        return issues

    def _validate_branch(
        self,
        branch: LinkLV | LinkMV | CableMV | CableLV | ReactanceCoilLV | ReactanceCoilMV | LineMV,
        network: NetworkLV | NetworkMV,
        element_type: str,
    ) -> list[Issue]:
        issues = []
        branch_name = branch.general.name
        branch_guid = branch.general.guid
        node_1 = network.nodes.get(branch.general.node1)
        node_2 = network.nodes.get(branch.general.node2)
        if node_1 is None or node_2 is None:
            # Cannot compare unom when an endpoint is missing.
            return issues
        node_1_name = name_or_guid(node_1.general)
        node_2_name = name_or_guid(node_2.general)

        if node_1.general.unom != node_2.general.unom and not branch.general.switches_open():
            issues.append(
                Issue(
                    code="unequal_unom",
                    message=(
                        f"{element_type} with name '{branch_name}' and guid '{branch_guid}' has unom "
                        f"{node_1.general.unom} at node 1 {node_1_name} and unom {node_2.general.unom} "
                        f"at node 2 {node_2_name}"
                    ),
                    severity=Severity.ERROR,
                    object_type=element_type,
                    object_id=branch.general.guid,
                    validator=self.name,
                    details={
                        "node_1": node_1_name,
                        "unom_node_1": node_1.general.unom,
                        "node_2": node_2_name,
                        "unom_node_2": node_2.general.unom,
                    },
                )
            )
        return issues


def _get_equal_unom_branch_collections(network: NetworkLV | NetworkMV) -> list[tuple[str, dict]]:
    """Retrieve all branch element collections from the network that require matching unom values at their endpoints.

    Returns a list of (element_type_name, collection_dict) tuples for
    branch types that should have equal unom and are present in the network.

    Args:
        network: Network model (LV or MV).

    Returns:
        List of tuples: (human-readable type name, collection dictionary).

    """
    collections: list[tuple[str, dict]] = []

    # Common to both LV and MV
    collections.append(("Link", network.links))
    collections.append(("Cable", network.cables))
    collections.append(("ReactanceCoil", network.reactance_coils))

    # MV only - use getattr to avoid type error for NetworkLV
    lines = getattr(network, "lines", None)
    if lines is not None:
        collections.append(("Line", lines))

    return collections
