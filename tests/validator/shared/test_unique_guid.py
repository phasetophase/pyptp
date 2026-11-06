from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.text import TextMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.unique_guid import UniqueGuidValidator
from pyptp.validator.test_helpers import assert_no_validation_issues


def _lv_network_with_sheet_and_node_sharing_a_guid() -> NetworkLV:
    network = NetworkLV()
    sheet = SheetLV(general=SheetLV.General(name="Street"))
    sheet.register(network)
    node = NodeLV(
        general=NodeLV.General(guid=sheet.general.guid, name="Joint"), presentations=[]
    )
    node.register(network)
    other = NodeLV(general=NodeLV.General(name="Cabinet"), presentations=[])
    other.register(network)
    link = LinkLV(
        general=LinkLV.General(
            name="Bridge", node1=other.general.guid, node2=node.general.guid
        ),
        presentations=[],
    )
    link.register(network)
    return network


class TestUniqueGuidLV(unittest.TestCase):
    def test_distinct_guids_have_no_issues(self) -> None:
        network = NetworkLV()
        SheetLV(general=SheetLV.General(name="Street")).register(network)
        NodeLV(general=NodeLV.General(name="Joint"), presentations=[]).register(network)

        assert_no_validation_issues(self, UniqueGuidValidator(), network)

    def test_sheet_and_node_sharing_a_guid_are_both_reported(self) -> None:
        network = _lv_network_with_sheet_and_node_sharing_a_guid()
        shared_guid = next(iter(network.sheets))

        issues = UniqueGuidValidator().validate(network)

        self.assertEqual([issue.object_type for issue in issues], ["Sheet", "Node"])
        self.assertEqual({issue.object_id for issue in issues}, {shared_guid})
        self.assertEqual(issues[0].details, {"also_used_by": ["Node 'Joint'"]})
        self.assertEqual(issues[1].details, {"also_used_by": ["Sheet 'Street'"]})

    def test_loader_rejection_is_raised_instead_of_a_locked_temp_file(self) -> None:
        network = _lv_network_with_sheet_and_node_sharing_a_guid()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "shared_guid.gnf"
            network.save(path, native_check=False)

            with self.assertRaises(RuntimeError):
                NetworkLV.from_file(path)


class TestUniqueGuidMV(unittest.TestCase):
    def test_three_objects_sharing_a_guid_each_name_the_other_two(self) -> None:
        network = NetworkMV()
        sheet = SheetMV(general=SheetMV.General(name="Station"))
        sheet.register(network)
        node = NodeMV(
            general=NodeMV.General(guid=sheet.general.guid, name="Busbar"),
            presentations=[],
        )
        node.register(network)
        text = TextMV(general=TextMV.General(guid=sheet.general.guid), presentations=[])
        text.register(network)

        issues = UniqueGuidValidator().validate(network)

        details_by_type = {issue.object_type: issue.details for issue in issues}
        self.assertEqual(
            details_by_type,
            {
                "Sheet": {"also_used_by": ["Node 'Busbar'", "Text"]},
                "Node": {"also_used_by": ["Sheet 'Station'", "Text"]},
                "Text": {"also_used_by": ["Node 'Busbar'", "Sheet 'Station'"]},
            },
        )


if __name__ == "__main__":
    unittest.main()
