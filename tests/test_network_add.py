"""Tests for NetworkLV.add and NetworkMV.add."""

from __future__ import annotations

import unittest

from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.node import NodeMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV


class TestNetworkAdd(unittest.TestCase):
    """add() registers an element and returns it."""

    def test_lv_add_returns_the_same_element(self) -> None:
        network = NetworkLV()
        node = NodeLV(general=NodeLV.General(name="Rail"), presentations=[])

        returned = network.add(node)

        self.assertIs(returned, node)
        self.assertIs(network.nodes[node.general.guid], node)

    def test_mv_add_returns_the_same_element(self) -> None:
        network = NetworkMV()
        node = NodeMV(general=NodeMV.General(name="Rail"), presentations=[])

        returned = network.add(node)

        self.assertIs(returned, node)
        self.assertIs(network.nodes[node.general.guid], node)


if __name__ == "__main__":
    unittest.main()
