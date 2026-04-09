from __future__ import annotations

import unittest

from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.node import NodeMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.node_unom_validator import NodeUnomValidator
from pyptp.validator.test_helpers import assert_issue_count, assert_no_validation_issues


class TestNodeUnomLV(unittest.TestCase):
    """LV node Unom validation."""

    def _create_lv_node(self, name: str, unom: float) -> NodeLV:
        return NodeLV(general=NodeLV.General(name=name, unom=unom), presentations=[])

    def test_valid_unom_no_issues(self) -> None:
        network = NetworkLV()
        self._create_lv_node("GoodNode", unom=0.4).register(network)

        assert_no_validation_issues(self, NodeUnomValidator(), network)

    def test_zero_unom_reports_error(self) -> None:
        network = NetworkLV()
        self._create_lv_node("BadNode", unom=0).register(network)

        assert_issue_count(self, NodeUnomValidator(), network, 1)

    def test_negative_unom_reports_error(self) -> None:
        network = NetworkLV()
        self._create_lv_node("BadNode", unom=-5).register(network)

        assert_issue_count(self, NodeUnomValidator(), network, 1)

    def test_multiple_bad_nodes(self) -> None:
        network = NetworkLV()
        self._create_lv_node("Bad1", unom=0).register(network)
        self._create_lv_node("Bad2", unom=-1).register(network)
        self._create_lv_node("Good", unom=10).register(network)

        assert_issue_count(self, NodeUnomValidator(), network, 2)

    def test_issue_details(self) -> None:
        network = NetworkLV()
        self._create_lv_node("ZeroNode", unom=0).register(network)

        issues = NodeUnomValidator().validate(network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "invalid_node_unom")
        self.assertEqual(issues[0].object_type, "Node")
        self.assertEqual(issues[0].details["unom"], 0)


class TestNodeUnomMV(unittest.TestCase):
    """MV node Unom validation."""

    def _create_mv_node(self, name: str, unom: float) -> NodeMV:
        return NodeMV(general=NodeMV.General(name=name, unom=unom), presentations=[])

    def test_valid_unom_no_issues(self) -> None:
        network = NetworkMV()
        self._create_mv_node("GoodNode", unom=10.5).register(network)

        assert_no_validation_issues(self, NodeUnomValidator(), network)

    def test_zero_unom_reports_error(self) -> None:
        network = NetworkMV()
        self._create_mv_node("BadNode", unom=0).register(network)

        assert_issue_count(self, NodeUnomValidator(), network, 1)

    def test_negative_unom_reports_error(self) -> None:
        network = NetworkMV()
        self._create_mv_node("BadNode", unom=-10).register(network)

        assert_issue_count(self, NodeUnomValidator(), network, 1)

    def test_multiple_bad_nodes(self) -> None:
        network = NetworkMV()
        self._create_mv_node("Bad1", unom=0).register(network)
        self._create_mv_node("Bad2", unom=-1).register(network)
        self._create_mv_node("Good", unom=10).register(network)

        assert_issue_count(self, NodeUnomValidator(), network, 2)


if __name__ == "__main__":
    unittest.main()
