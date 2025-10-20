from __future__ import annotations

import unittest

from pyptp.elements.element_utils import NIL_GUID, Guid
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.node import NodeMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.link_node_reference import LinkNodeReferenceValidator
from pyptp.validator.test_helpers import (
    assert_missing_node_reference,
    assert_no_validation_issues,
)


class TestLinkNodeReferenceLV(unittest.TestCase):
    def create_lv_node(self, name: str) -> NodeLV:
        return NodeLV(general=NodeLV.General(name=name), presentations=[])

    def create_lv_link(self, name: str, node1_guid: Guid, node2_guid: Guid) -> LinkLV:
        return LinkLV(
            general=LinkLV.General(name=name, node1=node1_guid, node2=node2_guid),
            presentations=[],
        )

    def test_link_with_valid_nodes_has_no_issues(self) -> None:
        network = NetworkLV()
        node_a = self.create_lv_node("NodeA")
        node_a.register(network)
        node_b = self.create_lv_node("NodeB")
        node_b.register(network)
        link = self.create_lv_link("Link1", node_a.general.guid, node_b.general.guid)
        link.register(network)

        assert_no_validation_issues(self, LinkNodeReferenceValidator(), network)

    def test_missing_node1_reports_issue(self) -> None:
        network = NetworkLV()
        node_b = self.create_lv_node("NodeB")
        node_b.register(network)
        link = self.create_lv_link("Link1", NIL_GUID, node_b.general.guid)
        link.register(network)

        assert_missing_node_reference(
            self, LinkNodeReferenceValidator(), network, "node1", NIL_GUID
        )


class TestLinkNodeReferenceMV(unittest.TestCase):
    def create_mv_node(self, name: str) -> NodeMV:
        return NodeMV(general=NodeMV.General(name=name), presentations=[])

    def create_mv_link(self, name: str, node1_guid: Guid, node2_guid: Guid) -> LinkMV:
        return LinkMV(
            general=LinkMV.General(name=name, node1=node1_guid, node2=node2_guid),
            presentations=[],
        )

    def test_missing_node2_reports_issue(self) -> None:
        network = NetworkMV()
        node_a = self.create_mv_node("NodeA")
        node_a.register(network)
        link = self.create_mv_link("Link1", node_a.general.guid, NIL_GUID)
        link.register(network)

        assert_missing_node_reference(
            self, LinkNodeReferenceValidator(), network, "node2", NIL_GUID
        )


if __name__ == "__main__":
    unittest.main()
