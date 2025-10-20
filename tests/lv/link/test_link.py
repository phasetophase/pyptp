"""Unit-tests for TLinkLS behaviour using the new registration system."""

import unittest
from typing import cast
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.shared import CurrentType, FuseType
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestLinkRegistration(unittest.TestCase):
    """Test link registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh in-memory network with one sheet and two nodes."""
        self.network = NetworkLV()

        # Create and register sheet
        sheet = SheetLV(SheetLV.General(name="Sheet-1"))
        sheet.register(self.network)
        self.sheet_guid = cast("Guid", sheet.general.guid)

        # Create and register nodes
        n1 = NodeLV(
            NodeLV.General(name="N1"), [NodePresentation(sheet=self.sheet_guid)]
        )
        n1.register(self.network)
        self.n1_guid = cast("Guid", n1.general.guid)

        n2 = NodeLV(
            NodeLV.General(name="N2"), [NodePresentation(sheet=self.sheet_guid, x=100)]
        )
        n2.register(self.network)
        self.n2_guid = cast("Guid", n2.general.guid)

    def test_link_registration_works(self) -> None:
        """Test that links can register themselves with the network."""
        link = LinkLV(
            LinkLV.General(node1=self.n1_guid, node2=self.n2_guid, name="TestLink"),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.register(self.network)

        # Verify link is in network
        self.assertIn(link.general.guid, self.network.links)
        self.assertIs(self.network.links[link.general.guid], link)

        # Verify lookup works
        found_link = self.network.get_link(link.general.guid)
        self.assertIs(found_link, link)

    def test_link_with_fuse_and_current_protection_serializes_correctly(self) -> None:
        """Test that links with FuseType and CurrentType serialize correctly."""
        fuse_i = [1.0] * 16
        fuse_t = [2.0] * 16
        fuse = FuseType(short_name="F1", unom=230, inom=10, I=fuse_i, T=fuse_t)
        current_i = [i + 10 for i in range(12)]
        current_t = [i + 20 for i in range(12)]
        current = CurrentType(
            short_name="C1",
            inom=5,
            setting_sort=1,
            I=current_i,
            T=current_t,
            I_great=6,
            T_great=7,
            I_greater=8,
            T_greater=9,
            I_greatest=10,
            T_greatest=11,
            M=0.5,
            Id=0.6,
            alpha=1,
            beta=2,
            c=3,
            d=4,
            e=5,
            ilt=6,
            ist=7,
        )

        link = LinkLV(
            LinkLV.General(
                node1=self.n1_guid,
                node2=self.n2_guid,
                name="L-FuseCurrent",
            ),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.fuse1_h1 = fuse
        link.current_protection1_h1 = current
        link.notes.append(Note(text="nc"))
        link.extras.append(Extra(text="ec=ev"))
        link.register(self.network)

        # Verify properties are set
        self.assertIs(link.fuse1_h1, fuse)
        self.assertIs(link.current_protection1_h1, current)

        # Test serialization
        serialized = link.serialize()

        self.assertIn("#FuseType1_h1", serialized)
        self.assertIn("ShortName:'F1'", serialized)
        self.assertIn("Unom:230", serialized)
        self.assertIn("Inom:10", serialized)
        self.assertIn("I1:1", serialized)
        self.assertIn("T1:2", serialized)
        self.assertIn("#CurrentType1_h1", serialized)
        self.assertIn("#Extra Text:ec=ev", serialized)
        self.assertIn("#Note Text:nc", serialized)

    def test_link_with_multiple_fuse_positions_serializes_correctly(self) -> None:
        """Test that links with multiple fuse positions serialize correctly."""
        f1 = FuseType(short_name="F1", unom=100, inom=5, I=[1.0] * 16, T=[2.0] * 16)
        f2 = FuseType(short_name="F2", unom=200, inom=6, I=[3.0] * 16, T=[4.0] * 16)
        f3 = FuseType(short_name="F3", unom=300, inom=7, I=[5.0] * 16, T=[6.0] * 16)
        f4 = FuseType(short_name="F4", unom=400, inom=8, I=[7.0] * 16, T=[8.0] * 16)

        link = LinkLV(
            LinkLV.General(
                node1=self.n1_guid,
                node2=self.n2_guid,
                name="L-AllFuses",
            ),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.fuse1_h1 = f1
        link.fuse1_h2 = f2
        link.fuse1_h3 = f3
        link.fuse1_h4 = f4
        link.fuse2_h1 = f1
        link.fuse2_h2 = f2
        link.fuse2_h3 = f3
        link.fuse2_h4 = f4
        link.register(self.network)

        serialized = link.serialize()

        # Verify all fuse positions are serialized
        for side, ftype in zip(
            ["1", "1", "1", "1", "2", "2", "2", "2"],
            [f1, f2, f3, f4, f1, f2, f3, f4],
            strict=False,
        ):
            idx = [f1, f2, f3, f4].index(ftype) + 1
            label = f"#FuseType{side}_h{idx}"
            self.assertIn(label, serialized)
            self.assertIn(f"ShortName:'{ftype.short_name}'", serialized)

    def test_link_fuse_assignment_overwrites_correctly(self) -> None:
        """Test that assigning a new fuse to the same position overwrites correctly."""
        f_old = FuseType(short_name="F-O", unom=10, inom=1, I=[0.0] * 16, T=[0.0] * 16)
        f_new = FuseType(
            short_name="F-N",
            unom=20,
            inom=2,
            I=[float(i) for i in range(16)],
            T=[float(i + 1) for i in range(16)],
        )

        link = LinkLV(
            LinkLV.General(
                node1=self.n1_guid,
                node2=self.n2_guid,
                name="L-DupFuse",
            ),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.fuse1_h1 = f_old
        link.register(self.network)

        # Overwrite the fuse
        link.fuse1_h1 = f_new

        serialized = link.serialize()

        self.assertIn("#FuseType1_h1", serialized)
        self.assertIn("ShortName:'F-N'", serialized)
        self.assertNotIn("ShortName:'F-O'", serialized)

    def test_minimal_link_serialization(self) -> None:
        """Test that minimal links serialize correctly with only required fields."""
        link = LinkLV(
            LinkLV.General(node1=self.n1_guid, node2=self.n2_guid, name="L-Min"),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.register(self.network)

        serialized = link.serialize()

        # Should have General and Presentation, but no fuse/current types
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)
        self.assertNotIn("#FuseType", serialized)
        self.assertNotIn("#CurrentType", serialized)

    def test_duplicate_link_registration_overwrites(self) -> None:
        """Test that registering a link with the same GUID overwrites the existing one."""
        link1 = LinkLV(
            LinkLV.General(node1=self.n1_guid, node2=self.n2_guid, name="L-First"),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link1.register(self.network)

        common_guid = cast("Guid", link1.general.guid)
        link2 = LinkLV(
            LinkLV.General(
                guid=common_guid,
                node1=self.n1_guid,
                node2=self.n2_guid,
                name="L-Second",
            ),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link2.register(self.network)

        # Should only have one link
        self.assertEqual(len(self.network.links), 1)
        # Should be the second link
        self.assertEqual(self.network.links[common_guid].general.name, "L-Second")

    def test_link_lookup_works(self) -> None:
        """Test that links can be looked up by GUID."""
        link = LinkLV(
            LinkLV.General(node1=self.n1_guid, node2=self.n2_guid, name="L-Exists"),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.register(self.network)

        # Verify lookup works
        retrieved = self.network.get_link(link.general.guid)
        self.assertIs(retrieved, link)

    def test_link_lookup_missing_returns_none(self) -> None:
        """Test that looking up a nonexistent link returns None."""
        fake_guid = Guid(UUID("00000000-0000-0000-0000-000000000000"))

        missing = self.network.get_link(fake_guid)

        self.assertIsNone(missing)

    def test_link_with_switch_states_serializes_correctly(self) -> None:
        """Test that links with switch states serialize correctly."""
        link = LinkLV(
            LinkLV.General(
                node1=self.n1_guid,
                node2=self.n2_guid,
                name="L-Switches",
                switch_state1_L1=False,
                switch_state1_L2=True,
                switch_state1_L3=False,
                switch_state1_N=True,
                switch_state1_PE=False,
                switch_state2_L1=True,
                switch_state2_L2=False,
                switch_state2_L3=True,
                switch_state2_N=False,
                switch_state2_PE=True,
                switch_state1_h1=False,
                switch_state1_h2=True,
                switch_state1_h3=False,
                switch_state1_h4=True,
                switch_state2_h1=True,
                switch_state2_h2=False,
                switch_state2_h3=True,
                switch_state2_h4=False,
            ),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.register(self.network)

        serialized = link.serialize()

        # Verify switch states are serialized
        self.assertIn("SwitchState1_L1:False", serialized)
        self.assertIn("SwitchState1_L2:True", serialized)
        self.assertIn("SwitchState1_L3:False", serialized)
        self.assertIn("SwitchState1_N:True", serialized)
        self.assertIn("SwitchState1_PE:False", serialized)
        self.assertIn("SwitchState2_L1:True", serialized)
        self.assertIn("SwitchState2_L2:False", serialized)
        self.assertIn("SwitchState2_L3:True", serialized)
        self.assertIn("SwitchState2_N:False", serialized)
        self.assertIn("SwitchState2_PE:True", serialized)
        self.assertIn("SwitchState1_h1:False", serialized)
        self.assertIn("SwitchState1_h2:True", serialized)
        self.assertIn("SwitchState1_h3:False", serialized)
        self.assertIn("SwitchState1_h4:True", serialized)
        self.assertIn("SwitchState2_h1:True", serialized)
        self.assertIn("SwitchState2_h2:False", serialized)
        self.assertIn("SwitchState2_h3:True", serialized)
        self.assertIn("SwitchState2_h4:False", serialized)

    def test_link_with_protection_types_serializes_correctly(self) -> None:
        """Test that links with protection types serialize correctly."""
        link = LinkLV(
            LinkLV.General(
                node1=self.n1_guid,
                node2=self.n2_guid,
                name="L-Protection",
                protection_type1_h1="Fuse",
                protection_type1_h2="CircuitBreaker",
                protection_type1_h3="LoadSwitch",
                protection_type1_h4="None",
                protection_type2_h1="Fuse",
                protection_type2_h2="CircuitBreaker",
                protection_type2_h3="LoadSwitch",
                protection_type2_h4="None",
            ),
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        link.register(self.network)

        serialized = link.serialize()

        # Verify protection types are serialized
        self.assertIn("ProtectionType1_h1:'Fuse'", serialized)
        self.assertIn("ProtectionType1_h2:'CircuitBreaker'", serialized)
        self.assertIn("ProtectionType1_h3:'LoadSwitch'", serialized)
        self.assertIn("ProtectionType1_h4:'None'", serialized)
        self.assertIn("ProtectionType2_h1:'Fuse'", serialized)
        self.assertIn("ProtectionType2_h2:'CircuitBreaker'", serialized)
        self.assertIn("ProtectionType2_h3:'LoadSwitch'", serialized)
        self.assertIn("ProtectionType2_h4:'None'", serialized)

    def test_link_with_multiple_presentations_serializes_correctly(self) -> None:
        """Test that links with multiple presentations serialize correctly."""
        pres1 = BranchPresentation(
            sheet=self.sheet_guid, strings1_x=100, strings1_y=100
        )
        pres2 = BranchPresentation(
            sheet=self.sheet_guid, strings1_x=200, strings1_y=200
        )

        link = LinkLV(
            LinkLV.General(node1=self.n1_guid, node2=self.n2_guid, name="L-MultiPres"),
            [pres1, pres2],
        )
        link.register(self.network)

        serialized = link.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Strings1X:100", serialized)
        self.assertIn("Strings1X:200", serialized)
        self.assertIn("Strings1Y:100", serialized)
        self.assertIn("Strings1Y:200", serialized)


if __name__ == "__main__":
    unittest.main()
