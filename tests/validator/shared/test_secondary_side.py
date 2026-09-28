"""Tests for the secondary side validator."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.load import LoadLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.mv.fuse import FuseMV
from pyptp.elements.mv.indicator import IndicatorMV
from pyptp.elements.mv.load import LoadMV
from pyptp.elements.mv.load_switch import LoadSwitchMV
from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV
from pyptp.elements.mv.transformer_load import TransformerLoadMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.secondary_side import SecondarySideValidator
from pyptp.validator.test_helpers import assert_no_validation_issues


class TestSecondarySideLV(unittest.TestCase):
    """Unbalanced network: a street cable with fuses and a load."""

    def setUp(self) -> None:
        self.network = NetworkLV()
        self.station = NodeLV(
            general=NodeLV.General(name="MSR Dorpsstraat"), presentations=[]
        )
        self.station.register(self.network)
        self.joint = NodeLV(general=NodeLV.General(name="Mof 1"), presentations=[])
        self.joint.register(self.network)

    def _cable(self) -> CableLV:
        cable = CableLV(
            general=CableLV.General(
                name="Kabel 1",
                node1=self.station.general.guid,
                node2=self.joint.general.guid,
            ),
            presentations=[],
            cable_part=CableLV.CablePart(length=40.0, type="4x150 Al"),
        )
        cable.register(self.network)
        return cable

    def _fuse(self, in_object: Guid, side: int) -> FuseLV:
        fuse = FuseLV(
            general=FuseLV.General(name="Groep 3", in_object=in_object, side=side)
        )
        fuse.register(self.network)
        return fuse

    def test_fuses_on_both_ends_of_a_cable_and_on_a_load_give_no_issues(self) -> None:
        cable = self._cable()
        load = LoadLV(
            general=LoadLV.General(name="Bakkerij", node=self.joint.general.guid),
            presentations=[],
        )
        load.register(self.network)
        self._fuse(cable.general.guid, side=1)
        self._fuse(cable.general.guid, side=2)
        self._fuse(load.general.guid, side=1)

        assert_no_validation_issues(self, SecondarySideValidator(), self.network)

    def test_fuse_on_side_3_of_a_cable_is_reported(self) -> None:
        cable = self._cable()
        fuse = self._fuse(cable.general.guid, side=3)

        issues = SecondarySideValidator().validate(self.network)

        self.assertEqual(len(issues), 1)
        issue = issues[0]
        self.assertEqual(issue.code, "secondary_side_invalid")
        self.assertEqual(issue.object_id, fuse.general.guid)
        self.assertEqual(issue.details, {"side": 3, "allowed_sides": [1, 2]})
        self.assertIn("Kabel 1", issue.message)

    def test_fuse_in_an_object_missing_from_the_network_is_skipped(self) -> None:
        self._fuse(Guid.deterministic("removed cable"), side=3)

        assert_no_validation_issues(self, SecondarySideValidator(), self.network)

    def test_saving_a_fuse_on_side_3_fails_to_load(self) -> None:
        link = LinkLV(
            general=LinkLV.General(
                name="Link 1",
                node1=self.station.general.guid,
                node2=self.joint.general.guid,
            ),
            presentations=[],
        )
        link.register(self.network)
        self._fuse(link.general.guid, side=3)

        with (
            tempfile.TemporaryDirectory() as folder,
            self.assertRaises(RuntimeError) as raised,
        ):
            self.network.save(Path(folder) / "dorpsstraat.gnf")

        self.assertIn("Zijde te groot: 3", str(raised.exception))


class TestSecondarySideMV(unittest.TestCase):
    """Balanced network: sides of nodes, elements and three-winding transformers."""

    def setUp(self) -> None:
        self.network = NetworkMV()
        self.node = NodeMV(
            general=NodeMV.General(name="OS Zuid 10 kV"), presentations=[]
        )
        self.node.register(self.network)

    def test_switch_on_side_3_of_a_threewinding_transformer_is_accepted(self) -> None:
        node2 = NodeMV(general=NodeMV.General(name="OS Zuid 20 kV"), presentations=[])
        node2.register(self.network)
        node3 = NodeMV(general=NodeMV.General(name="OS Zuid 3 kV"), presentations=[])
        node3.register(self.network)
        transformer = ThreewindingTransformerMV(
            general=ThreewindingTransformerMV.General(
                name="TR3",
                node1=self.node.general.guid,
                node2=node2.general.guid,
                node3=node3.general.guid,
            ),
            type=ThreewindingTransformerMV.ThreewindingTransformerType(),
            presentations=[],
        )
        transformer.register(self.network)
        switch = LoadSwitchMV(
            general=LoadSwitchMV.General(
                name="LS3", in_object=transformer.general.guid, side=3
            )
        )
        switch.register(self.network)

        assert_no_validation_issues(self, SecondarySideValidator(), self.network)

    def test_measure_field_on_side_2_of_a_transformer_load_is_accepted(self) -> None:
        transformer_load = TransformerLoadMV(
            general=TransformerLoadMV.General(
                name="Wijkstation", node=self.node.general.guid
            ),
            type=TransformerLoadMV.TransformerLoadType(),
            presentations=[],
        )
        transformer_load.register(self.network)
        measure_field = MeasureFieldMV(
            general=MeasureFieldMV.General(
                name="MV1", in_object=transformer_load.general.guid, side=2
            ),
            presentations=[],
        )
        measure_field.register(self.network)

        assert_no_validation_issues(self, SecondarySideValidator(), self.network)

    def test_fuse_and_indicator_on_side_2_of_a_load_are_reported(self) -> None:
        load = LoadMV(
            general=LoadMV.General(name="Fabriek", node=self.node.general.guid),
            presentations=[],
        )
        load.register(self.network)
        fuse = FuseMV(
            general=FuseMV.General(name="Z1", in_object=load.general.guid, side=2),
            type=FuseMV.FuseType(),
            presentations=[],
        )
        fuse.register(self.network)
        indicator = IndicatorMV(
            IndicatorMV.General(name="KV1", in_object=load.general.guid, side=2), []
        )
        indicator.register(self.network)

        issues = SecondarySideValidator().validate(self.network)

        self.assertEqual(
            [issue.object_id for issue in issues],
            [fuse.general.guid, indicator.general.guid],
        )
        self.assertEqual(issues[0].details, {"side": 2, "allowed_sides": [1]})

    def test_measure_field_in_a_node_on_side_1_is_reported(self) -> None:
        measure_field = MeasureFieldMV(
            general=MeasureFieldMV.General(
                name="MV1", in_object=self.node.general.guid, side=1
            ),
            presentations=[],
        )
        measure_field.register(self.network)

        issues = SecondarySideValidator().validate(self.network)

        self.assertEqual(
            [issue.object_id for issue in issues], [measure_field.general.guid]
        )
        self.assertEqual(issues[0].details, {"side": 1, "allowed_sides": [0]})


if __name__ == "__main__":
    unittest.main()
