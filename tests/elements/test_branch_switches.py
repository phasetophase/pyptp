from __future__ import annotations

import unittest

from pyptp.elements.element_utils import SIDE_NODE1, SIDE_NODE2
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.reactance_coil import ReactanceCoilLV
from pyptp.elements.lv.special_transformer import SpecialTransformerLV
from pyptp.elements.lv.transformer import TransformerLV
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.line import LineMV
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.reactance_coil import ReactanceCoilMV
from pyptp.elements.mv.special_transformer import SpecialTransformerMV
from pyptp.elements.mv.transformer import TransformerMV

BRANCH_GENERALS = (
    CableLV.General,
    LinkLV.General,
    ReactanceCoilLV.General,
    SpecialTransformerLV.General,
    TransformerLV.General,
    CableMV.General,
    LineMV.General,
    LinkMV.General,
    ReactanceCoilMV.General,
    SpecialTransformerMV.General,
    TransformerMV.General,
)


class TestBranchSwitches(unittest.TestCase):
    def test_every_branch_opens_and_closes_per_side(self) -> None:
        for general_class in BRANCH_GENERALS:
            with self.subTest(general=general_class.__qualname__):
                general = general_class()

                general.set_switches(SIDE_NODE1, closed=False)
                general.set_switches(SIDE_NODE2, closed=False)
                self.assertTrue(general.switches_open())

                general.set_switches(SIDE_NODE1, closed=True)
                self.assertTrue(general.side_closed(SIDE_NODE1))
                self.assertFalse(general.side_closed(SIDE_NODE2))

    def test_neutral_and_pe_stay_closed(self) -> None:
        for general_class in BRANCH_GENERALS:
            general = general_class()
            if not hasattr(general, "switch_state1_N"):
                continue
            with self.subTest(general=general_class.__qualname__):
                general.set_switches(SIDE_NODE1, closed=False)
                general.set_switches(SIDE_NODE2, closed=False)

                self.assertTrue(getattr(general, "switch_state1_N"))
                self.assertTrue(getattr(general, "switch_state1_PE"))
                self.assertTrue(getattr(general, "switch_state2_N"))
                self.assertTrue(getattr(general, "switch_state2_PE"))

    def test_opening_one_side_is_not_enough(self) -> None:
        general = CableLV.General()
        general.set_switches(SIDE_NODE1, closed=False)

        self.assertFalse(general.switches_open())

    def test_link_covers_the_auxiliary_conductors(self) -> None:
        general = LinkLV.General()
        general.set_switches(SIDE_NODE2, closed=False)

        self.assertFalse(general.switch_state2_h1)

    def test_one_closed_auxiliary_conductor_keeps_a_side_closed(self) -> None:
        general = LinkLV.General()
        general.set_switches(SIDE_NODE1, closed=False)
        general.switch_state1_h2 = True

        self.assertTrue(general.side_closed(SIDE_NODE1))

    def test_side_closed_reads_one_side(self) -> None:
        general = CableLV.General()
        general.set_switches(SIDE_NODE1, closed=False)

        self.assertFalse(general.side_closed(SIDE_NODE1))
        self.assertTrue(general.side_closed(SIDE_NODE2))

    def test_an_unknown_side_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "side"):
            CableLV.General().set_switches(3, closed=False)

    def test_side_closed_on_an_unknown_side_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "side"):
            CableLV.General().side_closed(3)


if __name__ == "__main__":
    unittest.main()
