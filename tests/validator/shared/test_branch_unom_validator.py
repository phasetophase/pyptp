from __future__ import annotations

import unittest


from pyptp.elements.lv.transformer import TransformerLV
from pyptp.elements.lv.special_transformer import SpecialTransformerLV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.reactance_coil import ReactanceCoilLV
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.shared import CableType
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.line import LineMV
from pyptp.elements.mv.transformer import TransformerMV
from pyptp.elements.mv.special_transformer import SpecialTransformerMV
from pyptp.elements.mv.reactance_coil import ReactanceCoilMV
from pyptp.validator.shared.branch_unom_validator import BranchUnomValidator
from pyptp.validator.test_helpers import assert_issue_count, assert_no_validation_issues


class TestBranchUnomLV(unittest.TestCase):
    """Test LV branch Unom validator."""

    def setUp(self) -> None:
        """Set up validator"""
        self.validator = BranchUnomValidator()

    def _create_lv_node(
        self,
        name: str,
        network: NetworkLV,
        unom: float | int = 0.4,
    ) -> NodeLV:
        """Create a node with specified unom."""
        node = NodeLV(
            general=NodeLV.General(name=name, unom=unom),
            presentations=[],
        )
        node.register(network)
        return node

    def _create_lv_link(
        self, name: str, node1: NodeLV, node2: NodeLV, network: NetworkLV
    ) -> LinkLV:
        link = LinkLV(
            general=LinkLV.General(
                name=name,
                node1=node1.general.guid,
                node2=node2.general.guid,
            ),
            presentations=[],
        )
        link.register(network)
        return link

    def _create_lv_cable(
        self, name: str, node1: NodeLV, node2: NodeLV, network: NetworkLV
    ) -> CableLV:
        cable = CableLV(
            general=CableLV.General(
                name=name, node1=node1.general.guid, node2=node2.general.guid
            ),
            presentations=[],
            cable_part=CableLV.CablePart(),
        )
        cable.register(network)
        return cable

    def _create_lv_reactancecoil(
        self, name: str, node1: NodeLV, node2: NodeLV, network: NetworkLV
    ) -> ReactanceCoilLV:
        reactance_coil = ReactanceCoilLV(
            general=ReactanceCoilLV.General(
                name=name,
                node1=node1.general.guid,
                node2=node2.general.guid,
            ),
            presentations=[],
            type=ReactanceCoilLV.ReactanceCoilType(short_name="300 A"),
        )
        reactance_coil.register(network)
        return reactance_coil

    def _create_lv_transformer(
        self, name: str, node1: NodeLV, node2: NodeLV, network: NetworkLV
    ) -> TransformerLV:
        transformer = TransformerLV(
            general=TransformerLV.General(
                name=name, node1=node1.general.guid, node2=node2.general.guid
            ),
            presentations=[],
            type=TransformerLV.TransformerType(short_name="50 kVA"),
        )
        transformer.register(network)
        return transformer

    def _create_lv_special_transformer(
        self, name: str, node1: NodeLV, node2: NodeLV, network: NetworkLV
    ) -> SpecialTransformerLV:
        special_transformer = SpecialTransformerLV(
            general=SpecialTransformerLV.General(
                name=name, node1=node1.general.guid, node2=node2.general.guid
            ),
            presentations=[],
            type=SpecialTransformerLV.SpecialTransformerType(
                short_name="40/26 kV 40 MVA Yd11"
            ),
        )
        special_transformer.register(network)
        return special_transformer

    def _open_all_switch_states_link_or_cable(
        self, branch: LinkLV | CableLV
    ) -> LinkLV | CableLV:
        branch.general.switch_state1_L1 = False
        branch.general.switch_state1_L2 = False
        branch.general.switch_state1_L3 = False
        branch.general.switch_state1_h1 = False
        branch.general.switch_state1_h2 = False
        branch.general.switch_state1_h3 = False
        branch.general.switch_state1_h4 = False
        branch.general.switch_state2_L1 = False
        branch.general.switch_state2_L2 = False
        branch.general.switch_state2_L3 = False
        branch.general.switch_state2_h1 = False
        branch.general.switch_state2_h2 = False
        branch.general.switch_state2_h3 = False
        branch.general.switch_state2_h4 = False
        return branch

    def _open_all_switch_states_reactance_coil(
        self, reactance_coil: ReactanceCoilLV
    ) -> ReactanceCoilLV:
        reactance_coil.general.switch_state1_L1 = False
        reactance_coil.general.switch_state1_L2 = False
        reactance_coil.general.switch_state1_L3 = False
        reactance_coil.general.switch_state2_L1 = False
        reactance_coil.general.switch_state2_L2 = False
        reactance_coil.general.switch_state2_L3 = False
        return reactance_coil

    def _assert_unequal_unom(
        self,
        network: NetworkLV | NetworkMV,
        expected_element_type: str,
    ) -> None:
        """Assert that validator reports exactly one missing unequal unom issue.

        Verifies:
        - Exactly 1 issue is reported
        - Issue has details dictionary
        - Issue has the right code: unequal_unom
        - Issue reports the correct objecttype
        - Issue message starts with the element type

        Args:
            network: Network to validate
            expected_elementtype: Expected type of the failing object (Cable, Link, etc.)
        """
        issues = self.validator.validate(network)
        self.assertEqual(len(issues), 1)
        self.assertIsNotNone(issues[0].details)
        self.assertEqual(issues[0].code, "unequal_unom")
        self.assertEqual(issues[0].object_type, expected_element_type)
        self.assertTrue(issues[0].message.startswith(expected_element_type))

    def test_link_equal_unom_no_issues(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=0.4)
        self._create_lv_link("link", node_1, node_2, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_cable_equal_unom_no_issues(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=0.4)
        self._create_lv_cable("cable", node_1, node_2, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_reactance_coil_equal_unom_no_issues(self) -> None:
        # The reactancecoil actually is not allowed in the LV network since its voltage should at least be 10 KV!
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=0.4)
        self._create_lv_reactancecoil("reactancecoil", node_1, node_2, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_link_unequal_unom_reports_issue(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        self._create_lv_link("link", node_1, node_2, network)
        self._assert_unequal_unom(network, "Link")

    def test_cable_unequal_unom_reports_issue(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        self._create_lv_cable("cable", node_1, node_2, network)
        self._assert_unequal_unom(
            network,
            "Cable",
        )

    def test_reactance_coil_unequal_unom_reports_issue(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        self._create_lv_reactancecoil("reactancecoil", node_1, node_2, network)
        self._assert_unequal_unom(
            network,
            "ReactanceCoil",
        )

    def test_transformer_unequal_unom_reports_no_issues(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=5)
        self._create_lv_transformer("transformer", node_1, node_2, network)
        self.assertNotEqual(node_1.general.unom, node_2.general.unom)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_special_transformer_unequal_unom_reports_no_issues(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=5)
        self._create_lv_special_transformer(
            "special_transformer", node_1, node_2, network
        )
        self.assertNotEqual(node_1.general.unom, node_2.general.unom)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_link_all_switches_open_unequal_unom_no_issues(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        link = self._create_lv_link("link", node_1, node_2, network)
        link = self._open_all_switch_states_link_or_cable(link)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_cable_all_switches_open_unequal_unom_no_issues(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        cable = self._create_lv_cable("cable", node_1, node_2, network)
        cable = self._open_all_switch_states_link_or_cable(cable)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_reactance_coil_all_switches_open_unequal_unom_no_issues(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        reactance_coil = self._create_lv_reactancecoil(
            "reactance_coil", node_1, node_2, network
        )
        reactance_coil = self._open_all_switch_states_reactance_coil(reactance_coil)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_multiple_unequal_unom(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1)
        node_3 = self._create_lv_node("node3", network, unom=1.4)
        self._create_lv_cable("reactance_coil", node_1, node_2, network)
        self._create_lv_link("link1", node_2, node_3, network)
        self._create_lv_link("link2", node_1, node_3, network)
        assert_issue_count(self, BranchUnomValidator(), network, 3)

    def test_link_switches_partly_open(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        link = self._create_lv_link("link", node_1, node_2, network)
        link.general.switch_state1_h1 = False
        link.general.switch_state2_L1 = False
        self._assert_unequal_unom(network, "Link")

    def test_cable_switches_partly_open(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        cable = self._create_lv_cable("cable", node_1, node_2, network)
        cable.general.switch_state1_h2 = False
        cable.general.switch_state2_L3 = False
        self._assert_unequal_unom(network, "Cable")

    def test_reactance_coil_switches_partly_open(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        node_2 = self._create_lv_node("node2", network, unom=1.4)
        reactance_coil = self._create_lv_reactancecoil(
            "reactance_coil", node_1, node_2, network
        )
        reactance_coil.general.switch_state1_L2 = False
        reactance_coil.general.switch_state2_L3 = False
        self._assert_unequal_unom(network, "ReactanceCoil")

    def test_missing_endpoint_node_no_crash(self) -> None:
        network = NetworkLV()
        node_1 = self._create_lv_node("node1", network, unom=0.4)
        unregistered = NodeLV(
            general=NodeLV.General(name="ghost", unom=1.4), presentations=[]
        )
        self._create_lv_link("link", node_1, unregistered, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)


class TestBranchUnomMV(unittest.TestCase):
    """Test MV branch Unom validation."""

    def setUp(self) -> None:
        """Set up test network with a sheet."""
        self.validator = BranchUnomValidator()

    def _create_mv_node(
        self,
        name: str,
        network: NetworkMV,
        unom: float | int = 10,
    ) -> NodeMV:
        """Create a node with specified unom."""
        node = NodeMV(
            general=NodeMV.General(name=name, unom=unom),
            presentations=[],
        )
        node.register(network)
        return node

    def _create_mv_link(
        self, name: str, node1: NodeMV, node2: NodeMV, network: NetworkMV
    ) -> LinkMV:
        link = LinkMV(
            general=LinkMV.General(
                name=name,
                node1=node1.general.guid,
                node2=node2.general.guid,
            ),
            presentations=[],
        )
        link.register(network)
        return link

    def _create_mv_line(
        self, name: str, node1: NodeMV, node2: NodeMV, network: NetworkMV
    ) -> LineMV:
        line = LineMV(
            general=LineMV.General(
                name=name,
                node1=node1.general.guid,
                node2=node2.general.guid,
            ),
            presentations=[],
        )
        line.register(network)
        return line

    def _create_mv_cable(
        self, name: str, node1: NodeMV, node2: NodeMV, network: NetworkMV
    ) -> CableMV:
        cable = CableMV(
            general=CableMV.General(
                name=name, node1=node1.general.guid, node2=node2.general.guid
            ),
            presentations=[],
            cable_parts=[CableMV.CablePart()],
            cable_types=[CableType("50 Al")],
        )
        cable.register(network)
        return cable

    def _create_mv_reactancecoil(
        self, name: str, node1: NodeMV, node2: NodeMV, network: NetworkMV
    ) -> ReactanceCoilMV:
        reactance_coil = ReactanceCoilMV(
            general=ReactanceCoilMV.General(
                name=name,
                node1=node1.general.guid,
                node2=node2.general.guid,
            ),
            presentations=[],
            type=ReactanceCoilMV.ReactanceCoilType(short_name="300 A"),
        )
        reactance_coil.register(network)
        return reactance_coil

    def _create_mv_transformer(
        self, name: str, node1: NodeMV, node2: NodeMV, network: NetworkMV
    ) -> TransformerMV:
        transformer = TransformerMV(
            general=TransformerMV.General(
                name=name, node1=node1.general.guid, node2=node2.general.guid
            ),
            presentations=[],
            type=TransformerMV.TransformerType(short_name="50 kVA"),
        )
        transformer.register(network)
        return transformer

    def _create_mv_special_transformer(
        self, name: str, node1: NodeMV, node2: NodeMV, network: NetworkMV
    ) -> SpecialTransformerMV:
        special_transformer = SpecialTransformerMV(
            general=SpecialTransformerMV.General(
                name=name, node1=node1.general.guid, node2=node2.general.guid
            ),
            presentations=[],
            type=SpecialTransformerMV.SpecialTransformerType(
                short_name="40/26 kV 40 MVA Yd11"
            ),
        )
        special_transformer.register(network)
        return special_transformer

    def _open_all_switch_states_branch(
        self, branch: LinkMV | CableMV | LineMV | ReactanceCoilMV
    ) -> LinkMV | CableMV | LineMV | ReactanceCoilMV:
        branch.general.switch_state1 = False
        branch.general.switch_state2 = False
        return branch

    def _assert_unequal_unom(
        self,
        network: NetworkMV | NetworkMV,
        expected_element_type: str,
    ) -> None:
        """Assert that validator reports exactly one missing unequal unom issue.

        Verifies:
        - Exactly 1 issue is reported
        - Issue has details dictionary
        - Issue has the right code: unequal_unom
        - Issue reports the correct objecttype
        - Issue message starts with the element type

        Args:
            network: Network to validate
            expected_elementtype: Expected type of the failing object (Cable, Link, etc.)
        """
        issues = self.validator.validate(network)
        self.assertEqual(len(issues), 1)
        self.assertIsNotNone(issues[0].details)
        self.assertEqual(issues[0].code, "unequal_unom")
        self.assertEqual(issues[0].object_type, expected_element_type)
        self.assertTrue(issues[0].message.startswith(expected_element_type))

    def test_link_equal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=10)
        self._create_mv_link("link", node_1, node_2, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_line_equal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=10)
        self._create_mv_line("line", node_1, node_2, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_cable_equal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=10)
        self._create_mv_cable("cable", node_1, node_2, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_reactance_coil_equal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=10)
        self._create_mv_reactancecoil("reactancecoil", node_1, node_2, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_link_unequal_unom_reports_issue(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        self._create_mv_link("link", node_1, node_2, network)
        self._assert_unequal_unom(network, "Link")

    def test_line_unequal_unom_reports_issue(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        self._create_mv_line("line", node_1, node_2, network)
        self._assert_unequal_unom(network, "Line")

    def test_cable_unequal_unom_reports_issue(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        self._create_mv_cable("cable", node_1, node_2, network)
        self._assert_unequal_unom(
            network,
            "Cable",
        )

    def test_reactance_coil_unequal_unom_reports_issue(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        self._create_mv_reactancecoil("reactancecoil", node_1, node_2, network)
        self._assert_unequal_unom(
            network,
            "ReactanceCoil",
        )

    def test_transformer_unequal_unom_reports_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        self._create_mv_transformer("transformer", node_1, node_2, network)
        self.assertNotEqual(node_1.general.unom, node_2.general.unom)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_special_transformer_unequal_unom_reports_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        self._create_mv_special_transformer(
            "special_transformer", node_1, node_2, network
        )
        self.assertNotEqual(node_1.general.unom, node_2.general.unom)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_link_all_switches_open_unequal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        link = self._create_mv_link("link", node_1, node_2, network)
        link = self._open_all_switch_states_branch(link)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_line_all_switches_open_unequal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        line = self._create_mv_line("line", node_1, node_2, network)
        line = self._open_all_switch_states_branch(line)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_cable_all_switches_open_unequal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        cable = self._create_mv_cable("cable", node_1, node_2, network)
        cable = self._open_all_switch_states_branch(cable)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_reactance_coil_all_switches_open_unequal_unom_no_issues(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        reactance_coil = self._create_mv_reactancecoil(
            "reactance_coil", node_1, node_2, network
        )
        reactance_coil = self._open_all_switch_states_branch(reactance_coil)
        assert_no_validation_issues(self, BranchUnomValidator(), network)

    def test_multiple_unequal_unom(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        node_3 = self._create_mv_node("node3", network, unom=25)
        self._create_mv_cable("reactance_coil", node_1, node_2, network)
        self._create_mv_link("link1", node_2, node_3, network)
        self._create_mv_link("link2", node_1, node_3, network)
        assert_issue_count(self, BranchUnomValidator(), network, 3)

    def test_link_switches_partly_open(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        link = self._create_mv_link("link", node_1, node_2, network)
        link.general.switch_state1 = False
        self._assert_unequal_unom(network, "Link")

    def test_line_switches_partly_open(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        line = self._create_mv_line("line", node_1, node_2, network)
        line.general.switch_state1 = False
        self._assert_unequal_unom(network, "Line")

    def test_cable_switches_partly_open(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        cable = self._create_mv_cable("cable", node_1, node_2, network)
        cable.general.switch_state1 = False
        self._assert_unequal_unom(network, "Cable")

    def test_reactance_coil_switches_partly_open(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        node_2 = self._create_mv_node("node2", network, unom=20)
        reactance_coil = self._create_mv_reactancecoil(
            "reactance_coil", node_1, node_2, network
        )
        reactance_coil.general.switch_state1 = False
        self._assert_unequal_unom(network, "ReactanceCoil")

    def test_missing_endpoint_node_no_crash(self) -> None:
        network = NetworkMV()
        node_1 = self._create_mv_node("node1", network, unom=10)
        unregistered = NodeMV(
            general=NodeMV.General(name="ghost", unom=20), presentations=[]
        )
        self._create_mv_link("link", node_1, unregistered, network)
        assert_no_validation_issues(self, BranchUnomValidator(), network)
