"""Tests for the node and edge rules of NetworkxConverter."""

from __future__ import annotations

import unittest

from networkx import Graph

from pyptp.elements.element_utils import NIL_GUID, Guid
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.load import LoadLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.fuse import FuseMV
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.load import LoadMV
from pyptp.elements.mv.load_switch import LoadSwitchMV
from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV
from pyptp.graph.networkx_converter import NetworkxConverter
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV


def edges(graph: Graph) -> set[frozenset[str]]:
    return {frozenset(edge) for edge in graph.edges}


def edge(*guids: Guid) -> frozenset[str]:
    return frozenset(str(guid) for guid in guids)


class TestNetworkxConverterMV(unittest.TestCase):
    """Balanced network: the scenario from issue #81 and its variations."""

    def setUp(self) -> None:
        self.network = NetworkMV()
        self.node1 = NodeMV(
            general=NodeMV.General(guid=Guid.deterministic("node1")), presentations=[]
        )
        self.node1.register(self.network)
        self.node2 = NodeMV(
            general=NodeMV.General(guid=Guid.deterministic("node2")), presentations=[]
        )
        self.node2.register(self.network)

    def _link(
        self, *, switch_state1: bool = True, switch_state2: bool = True
    ) -> LinkMV:
        link = LinkMV(
            general=LinkMV.General(
                guid=Guid.deterministic("link"),
                node1=self.node1.general.guid,
                node2=self.node2.general.guid,
                switch_state1=switch_state1,
                switch_state2=switch_state2,
            ),
            presentations=[],
        )
        link.register(self.network)
        return link

    def _load(self, *, switch_state: bool = True) -> LoadMV:
        load = LoadMV(
            general=LoadMV.General(
                guid=Guid.deterministic("load"),
                node=self.node2.general.guid,
                switch_state=switch_state,
            ),
            presentations=[],
        )
        load.register(self.network)
        return load

    def _switch(self, name: str, in_object: Guid, side: int = 1) -> LoadSwitchMV:
        switch = LoadSwitchMV(
            general=LoadSwitchMV.General(
                guid=Guid.deterministic(name), in_object=in_object, side=side
            )
        )
        switch.register(self.network)
        return switch

    def test_issue_81_scenario(self) -> None:
        """A half-open link, an open load, and a switch on every side."""
        link = self._link(switch_state1=True, switch_state2=False)
        load = self._load(switch_state=False)
        switch1 = self._switch("switch1", link.general.guid, side=1)
        switch2 = self._switch("switch2", link.general.guid, side=2)
        switch3 = self._switch("switch3", load.general.guid)

        graph = NetworkxConverter.graph_mv(self.network)

        expected_nodes = [self.node1, self.node2, link, load, switch1, switch2, switch3]
        self.assertEqual(
            set(graph.nodes), {str(obj.general.guid) for obj in expected_nodes}
        )
        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, switch1.general.guid),
                edge(switch1.general.guid, link.general.guid),
                edge(link.general.guid, switch2.general.guid),
                edge(switch3.general.guid, load.general.guid),
            },
        )

    def test_issue_81_scenario_ignoring_switch_states(self) -> None:
        """With respect_switch_states=False every side is connected to its node."""
        link = self._link(switch_state1=True, switch_state2=False)
        load = self._load(switch_state=False)
        switch1 = self._switch("switch1", link.general.guid, side=1)
        switch2 = self._switch("switch2", link.general.guid, side=2)
        switch3 = self._switch("switch3", load.general.guid)

        graph = NetworkxConverter.graph_mv(self.network, respect_switch_states=False)

        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, switch1.general.guid),
                edge(switch1.general.guid, link.general.guid),
                edge(link.general.guid, switch2.general.guid),
                edge(switch2.general.guid, self.node2.general.guid),
                edge(self.node2.general.guid, switch3.general.guid),
                edge(switch3.general.guid, load.general.guid),
            },
        )

    def test_graph_type_attribute(self) -> None:
        link = self._link()
        switch = self._switch("switch", link.general.guid)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(graph.nodes[str(self.node1.general.guid)]["type"], "NodeMV")
        self.assertEqual(graph.nodes[str(link.general.guid)]["type"], "LinkMV")
        self.assertEqual(graph.nodes[str(switch.general.guid)]["type"], "LoadSwitchMV")

    def test_branch_with_both_sides_open_is_an_isolated_node(self) -> None:
        link = self._link(switch_state1=False, switch_state2=False)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertIn(str(link.general.guid), graph.nodes)
        self.assertEqual(graph.degree(str(link.general.guid)), 0)

    def test_branch_without_secondaries_connects_directly(self) -> None:
        link = self._link()

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, link.general.guid),
                edge(link.general.guid, self.node2.general.guid),
            },
        )

    def test_secondaries_on_one_side_are_chained_in_series(self) -> None:
        """A fuse and a measure field on the same side sit in series between node and branch."""
        link = self._link()
        fuse = FuseMV(
            general=FuseMV.General(
                guid=Guid.deterministic("fuse"), in_object=link.general.guid, side=1
            ),
            type=FuseMV.FuseType(),
            presentations=[],
        )
        fuse.register(self.network)
        measure_field = MeasureFieldMV(
            general=MeasureFieldMV.General(
                guid=Guid.deterministic("mf"), in_object=link.general.guid, side=1
            ),
            presentations=[],
        )
        measure_field.register(self.network)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, fuse.general.guid),
                edge(fuse.general.guid, measure_field.general.guid),
                edge(measure_field.general.guid, link.general.guid),
                edge(link.general.guid, self.node2.general.guid),
            },
        )

    def test_secondaries_are_chained_by_kind_then_in_the_order_they_were_added(
        self,
    ) -> None:
        """Fuses come before load switches, whatever order they were added in."""
        link = self._link()
        switch1 = self._switch("switch1", link.general.guid)
        switch2 = self._switch("switch2", link.general.guid)
        fuse = FuseMV(
            general=FuseMV.General(
                guid=Guid.deterministic("fuse"), in_object=link.general.guid, side=1
            ),
            type=FuseMV.FuseType(),
            presentations=[],
        )
        fuse.register(self.network)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, fuse.general.guid),
                edge(fuse.general.guid, switch1.general.guid),
                edge(switch1.general.guid, switch2.general.guid),
                edge(switch2.general.guid, link.general.guid),
                edge(link.general.guid, self.node2.general.guid),
            },
        )

    def test_open_side_with_chained_secondaries_only_drops_node_edge(self) -> None:
        link = self._link(switch_state1=False)
        first = self._switch("first", link.general.guid, side=1)
        second = self._switch("second", link.general.guid, side=1)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(first.general.guid, second.general.guid),
                edge(second.general.guid, link.general.guid),
                edge(link.general.guid, self.node2.general.guid),
            },
        )

    def test_element_secondary_on_closed_element(self) -> None:
        load = self._load()
        switch = self._switch("switch", load.general.guid)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(self.node2.general.guid, switch.general.guid),
                edge(switch.general.guid, load.general.guid),
            },
        )

    def test_secondary_without_in_object_is_an_isolated_node(self) -> None:
        switch = self._switch("orphan", NIL_GUID)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertIn(str(switch.general.guid), graph.nodes)
        self.assertEqual(graph.degree(str(switch.general.guid)), 0)

    def test_secondary_in_a_missing_object_is_isolated_with_a_warning(self) -> None:
        switch = self._switch("stray", Guid.deterministic("removed link"))

        with self.assertLogs("pyptp", level="WARNING") as logs:
            graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(graph.degree(str(switch.general.guid)), 0)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("belongs to", logs.output[0])

    def test_secondary_in_a_node_is_isolated_without_a_warning(self) -> None:
        link = self._link()
        measure_field = MeasureFieldMV(
            general=MeasureFieldMV.General(
                guid=Guid.deterministic("mf"),
                in_object=self.node1.general.guid,
                side=0,
            ),
            presentations=[],
        )
        measure_field.register(self.network)

        with self.assertNoLogs("pyptp", level="WARNING"):
            graph = NetworkxConverter.graph_mv(self.network)

        self.assertIn(str(measure_field.general.guid), graph.nodes)
        self.assertEqual(graph.degree(str(measure_field.general.guid)), 0)
        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, link.general.guid),
                edge(link.general.guid, self.node2.general.guid),
            },
        )

    def test_secondary_on_a_side_the_branch_lacks_is_isolated(self) -> None:
        link = self._link()
        switch = self._switch("switch3", link.general.guid, side=3)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertIn(str(switch.general.guid), graph.nodes)
        self.assertEqual(graph.degree(str(switch.general.guid)), 0)

    def test_side_to_a_missing_node_has_no_edge_and_a_warning(self) -> None:
        link = LinkMV(
            general=LinkMV.General(
                guid=Guid.deterministic("link"),
                node1=self.node1.general.guid,
                node2=Guid.deterministic("removed node"),
            ),
            presentations=[],
        )
        link.register(self.network)

        with self.assertLogs("pyptp", level="WARNING") as logs:
            graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(
            edges(graph), {edge(self.node1.general.guid, link.general.guid)}
        )
        self.assertNotIn(str(Guid.deterministic("removed node")), graph.nodes)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("has no edge to node", logs.output[0])

    def test_threewinding_transformer_third_side(self) -> None:
        node3 = NodeMV(
            general=NodeMV.General(guid=Guid.deterministic("node3")), presentations=[]
        )
        node3.register(self.network)
        transformer = ThreewindingTransformerMV(
            general=ThreewindingTransformerMV.General(
                guid=Guid.deterministic("3w"),
                node1=self.node1.general.guid,
                node2=self.node2.general.guid,
                node3=node3.general.guid,
                switch_state2=False,
            ),
            type=ThreewindingTransformerMV.ThreewindingTransformerType(),
            presentations=[],
        )
        transformer.register(self.network)
        switch = self._switch("switch3", transformer.general.guid, side=3)

        graph = NetworkxConverter.graph_mv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, transformer.general.guid),
                edge(node3.general.guid, switch.general.guid),
                edge(switch.general.guid, transformer.general.guid),
            },
        )

    def test_instance_call_still_works(self) -> None:
        link = self._link()

        graph = NetworkxConverter().graph_mv(self.network)

        self.assertIn(str(link.general.guid), graph.nodes)


class TestNetworkxConverterLV(unittest.TestCase):
    """Unbalanced network: per-core switches decide whether a side is closed."""

    def setUp(self) -> None:
        self.network = NetworkLV()
        self.node1 = NodeLV(
            general=NodeLV.General(guid=Guid.deterministic("node1")), presentations=[]
        )
        self.node1.register(self.network)
        self.node2 = NodeLV(
            general=NodeLV.General(guid=Guid.deterministic("node2")), presentations=[]
        )
        self.node2.register(self.network)
        self.link = LinkLV(
            general=LinkLV.General(
                guid=Guid.deterministic("link"),
                node1=self.node1.general.guid,
                node2=self.node2.general.guid,
            ),
            presentations=[],
        )
        self.link.register(self.network)

    def _open_side1_phases(self) -> None:
        self.link.general.switch_state1_L1 = False
        self.link.general.switch_state1_L2 = False
        self.link.general.switch_state1_L3 = False

    def _open_side1_auxiliary(self) -> None:
        self.link.general.switch_state1_h1 = False
        self.link.general.switch_state1_h2 = False
        self.link.general.switch_state1_h3 = False
        self.link.general.switch_state1_h4 = False

    def _fuse(self, name: str, in_object: Guid, side: int = 1) -> FuseLV:
        fuse = FuseLV(
            general=FuseLV.General(
                guid=Guid.deterministic(name), in_object=in_object, side=side
            )
        )
        fuse.register(self.network)
        return fuse

    def test_closed_link(self) -> None:
        graph = NetworkxConverter.graph_lv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(self.node1.general.guid, self.link.general.guid),
                edge(self.link.general.guid, self.node2.general.guid),
            },
        )

    def test_side_stays_closed_while_one_phase_is_closed(self) -> None:
        self.link.general.switch_state1_L1 = False
        self.link.general.switch_state1_L2 = False
        self._open_side1_auxiliary()

        graph = NetworkxConverter.graph_lv(self.network)

        self.assertIn(
            edge(self.node1.general.guid, self.link.general.guid), edges(graph)
        )

    def test_side_stays_closed_while_an_auxiliary_core_is_closed(self) -> None:
        self._open_side1_phases()

        graph = NetworkxConverter.graph_lv(self.network)

        self.assertIn(
            edge(self.node1.general.guid, self.link.general.guid), edges(graph)
        )

    def test_side_open_when_all_phase_and_auxiliary_cores_are_open(self) -> None:
        self._open_side1_phases()
        self._open_side1_auxiliary()

        graph = NetworkxConverter.graph_lv(self.network)

        self.assertEqual(
            edges(graph), {edge(self.link.general.guid, self.node2.general.guid)}
        )

    def test_neutral_and_pe_do_not_close_a_side(self) -> None:
        self._open_side1_phases()
        self._open_side1_auxiliary()
        self.link.general.switch_state1_N = True
        self.link.general.switch_state1_PE = True

        graph = NetworkxConverter.graph_lv(self.network)

        self.assertNotIn(
            edge(self.node1.general.guid, self.link.general.guid), edges(graph)
        )

    def test_open_side_ignored_on_request(self) -> None:
        self._open_side1_phases()
        self._open_side1_auxiliary()

        graph = NetworkxConverter.graph_lv(self.network, respect_switch_states=False)

        self.assertIn(
            edge(self.node1.general.guid, self.link.general.guid), edges(graph)
        )

    def test_fuse_on_open_side_keeps_edge_to_branch(self) -> None:
        self._open_side1_phases()
        self._open_side1_auxiliary()
        fuse = self._fuse("fuse", self.link.general.guid, side=1)

        graph = NetworkxConverter.graph_lv(self.network)

        self.assertEqual(
            edges(graph),
            {
                edge(fuse.general.guid, self.link.general.guid),
                edge(self.link.general.guid, self.node2.general.guid),
            },
        )

    def test_open_element_keeps_secondary_but_loses_node(self) -> None:
        load = LoadLV(
            general=LoadLV.General(
                guid=Guid.deterministic("load"),
                node=self.node2.general.guid,
                s_L1=False,
                s_L2=False,
                s_L3=False,
            ),
            presentations=[],
        )
        load.register(self.network)
        fuse = self._fuse("fuse", load.general.guid)

        graph = NetworkxConverter.graph_lv(self.network)

        self.assertIn(edge(fuse.general.guid, load.general.guid), edges(graph))
        self.assertNotIn(edge(self.node2.general.guid, fuse.general.guid), edges(graph))
        self.assertNotIn(edge(self.node2.general.guid, load.general.guid), edges(graph))

    def test_single_phase_element_is_connected(self) -> None:
        load = LoadLV(
            general=LoadLV.General(
                guid=Guid.deterministic("load"),
                node=self.node2.general.guid,
                s_L2=False,
                s_L3=False,
            ),
            presentations=[],
        )
        load.register(self.network)

        graph = NetworkxConverter.graph_lv(self.network)

        self.assertIn(edge(self.node2.general.guid, load.general.guid), edges(graph))


if __name__ == "__main__":
    unittest.main()
