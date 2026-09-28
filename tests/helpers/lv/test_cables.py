"""Tests for split_cable: cutting a cable into sections at new joints."""

from __future__ import annotations

import unittest
from dataclasses import fields
from pathlib import Path
from tempfile import TemporaryDirectory

from pyptp.elements.element_utils import Guid
from pyptp.elements.enums import NodePresentationSymbol as Symbol
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.presentations import BranchPresentation
from pyptp.elements.lv.shared import FuseType, GeoCablePart
from pyptp.helpers.lv import CableSections, split_cable
from pyptp.network_lv import NetworkLV
from pyptp.type_reader import Types

from ._scene import (
    CORNER_IN_DEGREES,
    GEO_LENGTH,
    GX0,
    GY0,
    RECORDED_LENGTH,
    Scene,
    cable_scene,
    degrees_scene,
    metres_between,
    ordered_sections,
    rich_scene,
)


def _equip_node1_end(cable: CableLV) -> None:
    """Give node 1's end a field name, protection type, conductor mapping and open switch."""
    cable.general.switch_state1_L1 = False
    cable.general.field_name1 = "Veld 1"
    cable.general.protection_type1_h1 = "gG 25 A"
    cable.general.k1_L1 = 8
    cable.fuse1_h1 = FuseType(short_name="25 A")


def _equip_node2_end(network: NetworkLV, cable: CableLV) -> FuseLV:
    """Give node 2's end a fuse, field name, protection type, conductor mapping and open switch."""
    cable.general.switch_state2_L1 = False
    cable.general.field_name2 = "Veld 2"
    cable.general.protection_type2_h1 = "gG 25 A"
    cable.general.k2_L1 = 9
    cable.fuse2_h1 = FuseType(short_name="25 A")
    return network.add(
        FuseLV(
            FuseLV.General(name="Kastanjelaan 2", in_object=cable.general.guid, side=2)
        )
    )


def _end_fields(side: int) -> list[str]:
    """Every field of one cable end, read from CableLV.General itself."""
    prefixes = (
        f"switch_state{side}",
        f"field_name{side}",
        f"protection_type{side}",
        f"k{side}_",
    )
    return [f.name for f in fields(CableLV.General) if f.name.startswith(prefixes)]


def _network_state(scene: Scene) -> tuple[int, int, Guid, float]:
    """Node count, cable count, and the cable's node 2 and length, unchanged after a failed split."""
    return (
        len(scene.network.nodes),
        len(scene.network.cables),
        scene.cable.general.node2,
        scene.cable.cable_part.length,
    )


class TestSections(unittest.TestCase):
    """Cable sections after a split."""

    def test_lengths_share_out_the_recorded_length_and_sum_to_it(self) -> None:
        scene = cable_scene()
        split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0])

        chain = ordered_sections(scene.network, scene.cable)
        self.assertEqual([c.cable_part.length for c in chain], [11.0, 44.0, 44.0, 11.0])
        self.assertEqual(sum(c.cable_part.length for c in chain), RECORDED_LENGTH)

    def test_section_geography_ends_at_its_joint(self) -> None:
        scene = cable_scene()
        joints = split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0]).joints

        self.assertAlmostEqual(joints[0].general.gx, GX0 + 10.0)
        self.assertAlmostEqual(joints[1].general.gx, GX0 + 50.0)
        self.assertAlmostEqual(joints[2].general.gx, GX0 + 90.0)
        for joint in joints:
            self.assertAlmostEqual(joint.general.gy, GY0)

    def test_each_sections_drawing_starts_on_its_nodes(self) -> None:
        scene = cable_scene()
        joints = split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0]).joints

        chain_nodes = [scene.rail, *joints, scene.end]
        chain_cables = ordered_sections(scene.network, scene.cable)
        for start, stop, section in zip(
            chain_nodes[:-1], chain_nodes[1:], chain_cables, strict=True
        ):
            polyline = section.presentations[0].polyline()
            self.assertEqual(
                polyline[0], (start.presentations[0].x, start.presentations[0].y)
            )
            self.assertEqual(
                polyline[-1], (stop.presentations[0].x, stop.presentations[0].y)
            )

    def test_cable_drawn_on_two_sheets_gets_a_joint_drawing_on_both(self) -> None:
        scene = cable_scene(second_sheet=True)

        joints = split_cable(scene.network, scene.cable, [55.0]).joints

        joint_sheets = {presentation.sheet for presentation in joints[0].presentations}
        self.assertEqual(joint_sheets, {scene.sheet, scene.second_sheet})

    def test_cable_drawn_twice_on_a_sheet_gets_one_joint_drawing_there(self) -> None:
        scene = cable_scene()
        scene.cable.presentations.append(
            BranchPresentation.between(
                scene.rail, scene.end, scene.sheet, via=[(0, 900), (1000, 900)]
            )
        )

        result = split_cable(scene.network, scene.cable, [55.0])

        joint_drawings = result.joints[0].presentations
        self.assertEqual(len(joint_drawings), 1)
        joint_point = (joint_drawings[0].x, joint_drawings[0].y)
        for drawing in result.sections[0].presentations:
            self.assertEqual(drawing.polyline()[-1], joint_point)

    def test_empty_positions_leave_the_cable_whole(self) -> None:
        scene = cable_scene()

        result = split_cable(scene.network, scene.cable, [])

        self.assertEqual(result, CableSections([scene.cable], []))

    def test_result_lists_sections_and_joints_from_node1_to_node2(self) -> None:
        scene = cable_scene()

        result = split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0])

        self.assertEqual(result.sections, ordered_sections(scene.network, scene.cable))
        self.assertIs(result.sections[0], scene.cable)
        self.assertEqual(len(result.joints), 3)
        for section, joint in zip(result.sections, result.joints, strict=False):
            self.assertEqual(section.general.node2, joint.general.guid)


class TestRounding(unittest.TestCase):
    """Positions are rounded to centimetres and the sections add up to the cable."""

    def test_three_cuts_with_three_decimals(self) -> None:
        scene = cable_scene()

        result = split_cable(scene.network, scene.cable, [10.005, 55.555, 99.995])

        lengths = [section.cable_part.length for section in result.sections]
        self.assertEqual(lengths, [10.01, 45.54, 44.45, 10.0])
        self.assertEqual(sum(lengths), RECORDED_LENGTH)

    def test_the_last_section_takes_the_rest_unrounded(self) -> None:
        scene = cable_scene()
        scene.cable.cable_part.length = 37.483

        result = split_cable(scene.network, scene.cable, [10.0])

        lengths = [section.cable_part.length for section in result.sections]
        self.assertEqual(lengths, [10.0, 27.483])


class TestGeography(unittest.TestCase):
    """The cable's route on the map, and its drawing, cut along with it."""

    def test_cable_geography_is_cut_at_the_joints(self) -> None:
        scene = cable_scene(with_geography=False)
        scene.cable.geography = GeoCablePart(
            coordinates=[(GX0, GY0), (GX0 + GEO_LENGTH, GY0)]
        )

        result = split_cable(scene.network, scene.cable, [55.0])

        first, last = result.sections
        assert first.geography is not None
        assert last.geography is not None
        self.assertEqual(first.geography.coordinates[0], (GX0, GY0))
        self.assertAlmostEqual(first.geography.coordinates[-1][0], GX0 + 50.0)
        self.assertAlmostEqual(last.geography.coordinates[0][0], GX0 + 50.0)
        self.assertEqual(last.geography.coordinates[-1], (GX0 + GEO_LENGTH, GY0))
        self.assertAlmostEqual(result.joints[0].general.gx, GX0 + 50.0)

    def test_without_geography_joints_go_on_the_line_between_the_nodes(self) -> None:
        scene = cable_scene(with_geography=False)
        scene.end.general.gy = GY0 + 40.0

        result = split_cable(scene.network, scene.cable, [27.5])

        joint = result.joints[0]
        self.assertAlmostEqual(joint.general.gx, GX0 + 25.0)
        self.assertAlmostEqual(joint.general.gy, GY0 + 10.0)
        for section in result.sections:
            self.assertIsNone(section.cablepart_geography)
            self.assertIsNone(section.geography)

    def test_without_geography_or_node_positions_joints_stay_off_the_map(self) -> None:
        scene = cable_scene(with_geography=False, node2_has_coordinates=False)

        joints = split_cable(scene.network, scene.cable, [55.0]).joints

        self.assertEqual((joints[0].general.gx, joints[0].general.gy), (0, 0))

    def test_one_point_geography_is_dropped_from_every_section(self) -> None:
        scene = cable_scene(with_geography=False)
        scene.cable.geography = GeoCablePart(coordinates=[(GX0, GY0)])

        result = split_cable(scene.network, scene.cable, [55.0])

        for section in result.sections:
            self.assertIsNone(section.geography)

    def test_half_way_along_a_route_in_degrees_is_the_corner(self) -> None:
        scene = degrees_scene()

        joint = split_cable(scene.network, scene.cable, [100.0]).joints[0]

        joint_position = (joint.general.gx, joint.general.gy)
        self.assertLess(metres_between(joint_position, CORNER_IN_DEGREES), 0.05)

    def test_drawing_with_corners_keeps_its_corners(self) -> None:
        scene = cable_scene()
        scene.cable.presentations = [
            BranchPresentation.between(
                scene.rail,
                scene.end,
                scene.sheet,
                via=[(200, 500), (200, 800), (800, 800), (800, 500)],
            )
        ]

        result = split_cable(scene.network, scene.cable, [55.0])

        first, last = result.sections
        self.assertEqual(
            first.presentations[0].polyline(),
            [(0, 500), (200, 500), (200, 800), (500, 800)],
        )
        self.assertEqual(
            last.presentations[0].polyline(),
            [(500, 800), (800, 800), (800, 500), (1000, 500)],
        )


class TestEnds(unittest.TestCase):
    """What happens at the outer and inner ends of the sections."""

    def test_outer_ends_keep_their_values(self) -> None:
        scene = cable_scene()
        _equip_node1_end(scene.cable)
        _equip_node2_end(scene.network, scene.cable)

        result = split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0])

        first = result.sections[0]
        self.assertFalse(first.general.switch_state1_L1)
        self.assertEqual(first.general.field_name1, "Veld 1")
        self.assertEqual(first.general.k1_L1, 8)
        self.assertEqual(first.fuse1_h1, FuseType(short_name="25 A"))
        last = result.sections[-1]
        self.assertFalse(last.general.switch_state2_L1)
        self.assertEqual(last.general.field_name2, "Veld 2")
        self.assertEqual(last.general.k2_L1, 9)
        self.assertEqual(last.fuse2_h1, FuseType(short_name="25 A"))

    def test_inner_ends_reset_every_matching_field(self) -> None:
        scene = cable_scene()
        _equip_node1_end(scene.cable)
        _equip_node2_end(scene.network, scene.cable)

        result = split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0])

        blank = CableLV.General()
        for section in result.sections[1:]:
            self.assertIsNone(section.fuse1_h1)
            for name in _end_fields(1):
                self.assertEqual(
                    getattr(section.general, name), getattr(blank, name), name
                )
        for section in result.sections[:-1]:
            self.assertIsNone(section.fuse2_h1)
            for name in _end_fields(2):
                self.assertEqual(
                    getattr(section.general, name), getattr(blank, name), name
                )

    def test_side2_fuse_moves_to_the_last_section_side1_fuse_stays(self) -> None:
        scene = cable_scene()
        fuse1 = scene.network.add(
            FuseLV(
                FuseLV.General(
                    name="Kastanjelaan 1",
                    in_object=scene.cable.general.guid,
                    side=1,
                )
            )
        )
        fuse2 = _equip_node2_end(scene.network, scene.cable)
        original_guid = scene.cable.general.guid

        result = split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0])

        last = result.sections[-1]
        self.assertEqual(fuse1.general.in_object, original_guid)
        self.assertEqual(fuse2.general.in_object, last.general.guid)
        self.assertNotEqual(last.general.guid, original_guid)


class TestOrientation(unittest.TestCase):
    """Orienting a cable's geography from node 1 to node 2."""

    def test_reversed_geography_gives_the_same_joints(self) -> None:
        scene = cable_scene(reverse_geography=True)

        joints = split_cable(scene.network, scene.cable, [55.0]).joints

        self.assertAlmostEqual(joints[0].general.gx, GX0 + 50.0)

    def test_orientation_from_node2_coordinates_alone(self) -> None:
        scene = cable_scene(reverse_geography=True, node1_has_coordinates=False)

        joints = split_cable(scene.network, scene.cable, [55.0]).joints

        self.assertAlmostEqual(joints[0].general.gx, GX0 + 50.0)

    def test_neither_end_node_has_coordinates_raises(self) -> None:
        scene = cable_scene(node1_has_coordinates=False, node2_has_coordinates=False)
        cable_count = len(scene.network.cables)

        with self.assertRaisesRegex(ValueError, "cannot be oriented"):
            split_cable(scene.network, scene.cable, [55.0])

        self.assertEqual(len(scene.network.cables), cable_count)


class TestJoints(unittest.TestCase):
    """Symbol, N-PE connection and unom of the new joints."""

    def test_symbol_override(self) -> None:
        scene = cable_scene()

        joints = split_cable(
            scene.network, scene.cable, [55.0], symbol=Symbol.OPEN_TRIANGLE
        ).joints

        self.assertEqual(joints[0].presentations[0].symbol, Symbol.OPEN_TRIANGLE)

    def test_joints_are_plain_at_node1_voltage(self) -> None:
        scene = cable_scene()
        scene.rail.general.unom = 0.42

        joints = split_cable(scene.network, scene.cable, [55.0]).joints

        self.assertFalse(joints[0].general.s_N_PE)
        self.assertEqual(joints[0].general.unom, 0.42)


class TestRaises(unittest.TestCase):
    """Every failure raises before anything is mutated."""

    def test_unregistered_cable_raises(self) -> None:
        scene = cable_scene()
        other_scene = cable_scene()
        cable_count = len(scene.network.cables)

        with self.assertRaisesRegex(ValueError, "not registered"):
            split_cable(scene.network, other_scene.cable, [55.0])

        self.assertEqual(len(scene.network.cables), cable_count)

    def test_cable_with_its_own_connections_raises(self) -> None:
        scene = cable_scene()
        scene.cable.cable_connection.append(CableLV.CableConnection(name="Aftakking"))
        scene.cable.cable_connections.append(CableLV.CableConnections())
        before = _network_state(scene)

        with self.assertRaisesRegex(ValueError, "connections on the cable itself"):
            split_cable(scene.network, scene.cable, [55.0])

        self.assertEqual(_network_state(scene), before)

    def test_positions_not_ascending_or_outside_raise(self) -> None:
        scene = cable_scene()
        before = _network_state(scene)

        for at in ([55.0, 11.0], [11.0, 11.0], [11.0, 11.001]):
            with self.subTest(at=at), self.assertRaisesRegex(ValueError, "ascending"):
                split_cable(scene.network, scene.cable, at)
        for at in ([0.0], [110.0], [-5.0], [120.0]):
            with self.subTest(at=at), self.assertRaisesRegex(ValueError, "between 0"):
                split_cable(scene.network, scene.cable, at)

        self.assertEqual(_network_state(scene), before)

    def test_section_shorter_than_half_a_metre_raises(self) -> None:
        scene = cable_scene()
        before = _network_state(scene)

        for at in ([11.0, 11.3], [0.3], [109.8]):
            with (
                self.subTest(at=at),
                self.assertRaisesRegex(ValueError, "at least 0.5"),
            ):
                split_cable(scene.network, scene.cable, at)

        self.assertEqual(_network_state(scene), before)


class TestSaveAndReload(unittest.TestCase):
    """The split survives a save and reload through Gaia's own loader."""

    def test_save_and_reload(self) -> None:
        scene = rich_scene(Types())

        split_cable(scene.network, scene.cable, [0.5, 55.0, 109.5])

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "kastanjelaan.gnf"
            scene.network.save(path)
            reloaded = NetworkLV.from_file(path)

        first = reloaded.cables[scene.cable.general.guid]
        sections = ordered_sections(reloaded, first)
        self.assertEqual(
            [section.cable_part.length for section in sections],
            [0.5, 54.5, 54.5, 0.5],
        )

    def test_save_and_reload_in_degrees(self) -> None:
        scene = degrees_scene()

        result = split_cable(scene.network, scene.cable, [50.0, 100.0])

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "kastanjelaan.gnf"
            scene.network.save(path)
            reloaded = NetworkLV.from_file(path)

        first = reloaded.cables[scene.cable.general.guid]
        sections = ordered_sections(reloaded, first)
        self.assertEqual(
            [section.cable_part.length for section in sections], [50.0, 50.0, 100.0]
        )
        self.assertEqual(
            [section.cablepart_geography for section in sections],
            [section.cablepart_geography for section in result.sections],
        )
        corner_joint = reloaded.nodes[sections[1].general.node2]
        corner_position = (corner_joint.general.gx, corner_joint.general.gy)
        self.assertLess(metres_between(corner_position, CORNER_IN_DEGREES), 0.05)


if __name__ == "__main__":
    unittest.main()
