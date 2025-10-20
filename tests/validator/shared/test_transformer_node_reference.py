from __future__ import annotations

import unittest

from pyptp.elements.element_utils import NIL_GUID, Guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.transformer import TransformerLV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.transformer import TransformerMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.transformer_node_reference import (
    TransformerNodeReferenceValidator,
)
from pyptp.validator.test_helpers import assert_missing_node_reference


class TestTransformerNodeReferenceLV(unittest.TestCase):
    def create_lv_node(self, name: str) -> NodeLV:
        return NodeLV(general=NodeLV.General(name=name), presentations=[])

    def create_lv_transformer(
        self, name: str, node1_guid: Guid, node2_guid: Guid
    ) -> TransformerLV:
        general = TransformerLV.General(
            name=name, node1=node1_guid, node2=node2_guid, type="TestLV"
        )
        transformer_type = TransformerLV.TransformerType(short_name="TestLV")
        return TransformerLV(general=general, presentations=[], type=transformer_type)

    def test_transformer_with_missing_node1_reports_issue(self) -> None:
        network = NetworkLV()
        node_b = self.create_lv_node("NodeB")
        node_b.register(network)
        transformer = self.create_lv_transformer("T1", NIL_GUID, node_b.general.guid)
        transformer.register(network)

        assert_missing_node_reference(
            self, TransformerNodeReferenceValidator(), network, "node1", NIL_GUID
        )


class TestTransformerNodeReferenceMV(unittest.TestCase):
    def create_mv_node(self, name: str) -> NodeMV:
        return NodeMV(general=NodeMV.General(name=name), presentations=[])

    def create_mv_transformer(
        self, name: str, node1_guid: Guid, node2_guid: Guid
    ) -> TransformerMV:
        general = TransformerMV.General(
            name=name, node1=node1_guid, node2=node2_guid, type="TestMV"
        )
        transformer_type = TransformerMV.TransformerType(short_name="TestMV")
        return TransformerMV(general=general, presentations=[], type=transformer_type)

    def test_transformer_with_missing_node2_reports_issue(self) -> None:
        network = NetworkMV()
        node_a = self.create_mv_node("NodeA")
        node_a.register(network)
        transformer = self.create_mv_transformer("T1", node_a.general.guid, NIL_GUID)
        transformer.register(network)

        assert_missing_node_reference(
            self, TransformerNodeReferenceValidator(), network, "node2", NIL_GUID
        )


if __name__ == "__main__":
    unittest.main()
