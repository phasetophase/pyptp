"""Validators ensuring link elements reference nodes that exist in the network."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class LinkNodeReferenceValidator(Validator):
    """Verifies link endpoints reference existing nodes in the network."""

    name = "link_node_reference"
    description = "Verifies link endpoints reference existing nodes in the network"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Return issues for each link node reference that is missing."""
        issues: list[Issue] = []

        link_lookup = getattr(network, "links", {})
        nodes = getattr(network, "nodes", {})
        has_nodes = bool(nodes)

        for link in link_lookup.values():
            general = link.general
            link_name = getattr(general, "name", str(general.guid))
            for endpoint in ("node1", "node2"):
                node_guid = getattr(general, endpoint)
                if has_nodes and node_guid not in nodes:
                    issues.append(
                        Issue(
                            code="missing_node_reference",
                            message=(f"Link '{link_name}' references unknown node GUID '{node_guid}'"),
                            severity=Severity.ERROR,
                            object_type="Link",
                            object_id=general.guid,
                            validator=self.name,
                            details={"which_end": endpoint, "referenced_guid": node_guid},
                        ),
                    )
        return issues
