"""Validators ensuring transformer elements reference nodes that exist."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class TransformerNodeReferenceValidator(Validator):
    """Verifies transformer endpoints reference existing nodes in the network."""

    name = "transformer_node_reference"
    description = "Verifies transformer endpoints reference existing nodes in the network"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Return issues for each transformer node reference that is missing."""
        issues: list[Issue] = []

        transformers = getattr(network, "transformers", {})
        nodes = getattr(network, "nodes", {})
        has_nodes = bool(nodes)

        for transformer in transformers.values():
            general = transformer.general
            transformer_name = getattr(general, "name", str(general.guid))
            for endpoint in ("node1", "node2"):
                node_guid = getattr(general, endpoint)
                if has_nodes and node_guid not in nodes:
                    issues.append(
                        Issue(
                            code="missing_node_reference",
                            message=(f"Transformer '{transformer_name}' references unknown node GUID '{node_guid}'"),
                            severity=Severity.ERROR,
                            object_type="Transformer",
                            object_id=general.guid,
                            validator=self.name,
                            details={"which_end": endpoint, "referenced_guid": node_guid},
                        ),
                    )

        return issues
