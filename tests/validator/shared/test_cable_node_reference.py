from __future__ import annotations

import unittest

from pyptp.elements.element_utils import NIL_GUID, Guid
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.node import NodeMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.cable_node_reference import CableNodeReferenceValidator
from pyptp.validator.test_helpers import (
    assert_issue_count,
    assert_missing_node_reference,
    assert_no_validation_issues,
)


class TestCableNodeReferenceLV(unittest.TestCase):
    """LV-specific fixture builder and assertions for the cable-node validator."""

    def create_lv_node(self, name: str) -> NodeLV:
        return NodeLV(general=NodeLV.General(name=name), presentations=[])

    def create_lv_cable(self, name: str, node1_guid: Guid, node2_guid: Guid) -> CableLV:
        return CableLV(
            general=CableLV.General(name=name, node1=node1_guid, node2=node2_guid),
            presentations=[],
            cable_part=CableLV.CablePart(),
        )

    def test_both_present_no_issues(self) -> None:
        lv_network = NetworkLV()
        node_one = self.create_lv_node("NodeOne")
        node_one.register(lv_network)
        node_two = self.create_lv_node("NodeTwo")
        node_two.register(lv_network)
        cable = self.create_lv_cable(
            "CableA", node_one.general.guid, node_two.general.guid
        )
        cable.register(lv_network)

        assert_no_validation_issues(self, CableNodeReferenceValidator(), lv_network)

    def test_node1_missing_reports(self) -> None:
        lv_network = NetworkLV()
        node_two = self.create_lv_node("NodeTwo")
        node_two.register(lv_network)
        cable = self.create_lv_cable("CableA", NIL_GUID, node_two.general.guid)
        cable.register(lv_network)

        assert_missing_node_reference(
            self, CableNodeReferenceValidator(), lv_network, "node1", NIL_GUID
        )

    def test_node2_missing_reports(self) -> None:
        lv_network = NetworkLV()
        node_one = self.create_lv_node("NodeOne")
        node_one.register(lv_network)
        cable = self.create_lv_cable("CableA", node_one.general.guid, NIL_GUID)
        cable.register(lv_network)

        assert_missing_node_reference(
            self, CableNodeReferenceValidator(), lv_network, "node2", NIL_GUID
        )

    def test_both_missing_two_issues(self) -> None:
        lv_network = NetworkLV()
        cable = self.create_lv_cable("CableA", NIL_GUID, NIL_GUID)
        cable.register(lv_network)

        assert_issue_count(self, CableNodeReferenceValidator(), lv_network, 2)


class TestCableNodeReferenceMV(unittest.TestCase):
    """MV fixture helper exercising the same validator contract."""

    def create_mv_node(self, name: str) -> NodeMV:
        return NodeMV(general=NodeMV.General(name=name), presentations=[])

    def create_mv_cable(self, name: str, node1_guid: Guid, node2_guid: Guid) -> CableMV:
        return CableMV(
            general=CableMV.General(name=name, node1=node1_guid, node2=node2_guid),
            cable_parts=[CableMV.CablePart(cable_type="TestType")],
            cable_types=[],
            presentations=[],
        )

    def test_missing_node1_mv(self) -> None:
        mv_network = NetworkMV()
        node_two = self.create_mv_node("NodeTwo")
        node_two.register(mv_network)
        cable = self.create_mv_cable("CableA", NIL_GUID, node_two.general.guid)
        cable.register(mv_network)

        assert_missing_node_reference(
            self, CableNodeReferenceValidator(), mv_network, "node1", NIL_GUID
        )


if __name__ == "__main__":
    unittest.main()
