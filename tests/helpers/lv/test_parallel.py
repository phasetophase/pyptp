"""Tests for lay_parallel_cable: a new cable beside a chain of old sections."""

from __future__ import annotations

import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pyptp.elements.color_utils import CL_RED
from pyptp.elements.element_utils import Guid
from pyptp.elements.enums import NodePresentationSymbol as Symbol
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.shared import FuseType, GeoCablePart
from pyptp.helpers.lv import lay_parallel_cable, split_cable
from pyptp.network_lv import NetworkLV
from pyptp.type_reader import Types

from ._scene import GX0, GY0, Scene, cable_scene, rich_scene


def _sections(scene: Scene) -> list[CableLV]:
    """Split the scene's cable into four sections of 11, 44, 44 and 11 m."""
    return split_cable(scene.network, scene.cable, [11.0, 55.0, 99.0]).sections


def _map_route(cable: CableLV) -> list[tuple[float, float]] | None:
    if cable.cablepart_geography is None:
        return None
    return cable.cablepart_geography.coordinates


def _turn_round(cable: CableLV) -> None:
    """Store the cable the other way round: node 2 first, drawings and geography reversed."""
    old_node1 = cable.general.node1
    cable.general.node1 = cable.general.node2
    cable.general.node2 = old_node1
    for presentation in cable.presentations:
        old_first_corners = presentation.first_corners
        presentation.first_corners = presentation.second_corners
        presentation.second_corners = old_first_corners
    for geography in (cable.cablepart_geography, cable.geography):
        if geography is not None:
            geography.coordinates = list(reversed(geography.coordinates))


def _degrees_scene() -> Scene:
    """The cable running 111 m north at 52 degrees north, on a map in degrees."""
    scene = cable_scene()
    scene.rail.general.gx = 5.1
    scene.rail.general.gy = 52.0
    scene.end.general.gx = 5.1
    scene.end.general.gy = 52.001
    scene.cable.cablepart_geography = GeoCablePart([(5.1, 52.0), (5.1, 52.001)])
    return scene


def _network_state(
    network: NetworkLV,
) -> tuple[int, int, list[tuple[Guid, Guid, float]]]:
    """Node and cable counts, and every cable's nodes and length."""
    cables = [
        (cable.general.node1, cable.general.node2, cable.cable_part.length)
        for cable in network.cables.values()
    ]
    return (len(network.nodes), len(network.cables), cables)


def _add_node(
    network: NetworkLV,
    sheet: Guid,
    x: int,
    y: int,
    symbol: Symbol = Symbol.CLOSED_CIRCLE,
    size: int = 1,
) -> NodeLV:
    presentation = NodePresentation(sheet=sheet, x=x, y=y, symbol=symbol, size=size)
    return network.add(NodeLV(NodeLV.General(), presentations=[presentation]))


def _add_cable(
    network: NetworkLV,
    sheet: Guid,
    node1: NodeLV,
    node2: NodeLV,
    via: list[tuple[int, int]] | None = None,
) -> CableLV:
    return network.add(
        CableLV(
            CableLV.General(
                node1=node1.general.guid, node2=node2.general.guid, name="Eikenlaan"
            ),
            presentations=[
                BranchPresentation.between(node1, node2, sheet, via=via or [])
            ],
            cable_part=CableLV.CablePart(length=50.0),
        )
    )


def _add_undrawn_cable(
    network: NetworkLV, node1: Guid, node2: Guid, name: str
) -> CableLV:
    return network.add(
        CableLV(
            CableLV.General(node1=node1, node2=node2, name=name),
            presentations=[],
            cable_part=CableLV.CablePart(length=5.0),
        )
    )


class TestChain(unittest.TestCase):
    """The new cable's nodes, length, type and name."""

    def test_one_cable_from_the_outer_nodes(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        node_count = len(scene.network.nodes)
        cable_count = len(scene.network.cables)

        new_cable = lay_parallel_cable(scene.network, sections, offset_px=20)

        self.assertEqual(new_cable.general.node1, scene.rail.general.guid)
        self.assertEqual(new_cable.general.node2, scene.end.general.guid)
        self.assertEqual(new_cable.cable_part.length, 110.0)
        self.assertIs(scene.network.cables[new_cable.general.guid], new_cable)
        self.assertEqual(len(scene.network.cables), cable_count + 1)
        self.assertEqual(len(scene.network.nodes), node_count)

    def test_a_single_cable_is_a_chain_of_one(self) -> None:
        scene = cable_scene()

        new_cable = lay_parallel_cable(scene.network, [scene.cable], offset_px=20)

        self.assertEqual(new_cable.general.node1, scene.rail.general.guid)
        self.assertEqual(new_cable.general.node2, scene.end.general.guid)
        self.assertEqual(new_cable.cable_part.length, 110.0)

    def test_length_is_the_sum_not_the_geography(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        for section, length in zip(sections, [20.0, 30.0, 40.0, 25.004], strict=True):
            section.cable_part.length = length

        new_cable = lay_parallel_cable(scene.network, sections, offset_px=20)

        self.assertEqual(new_cable.cable_part.length, 115.0)

    def test_type_and_name_from_the_first_section(self) -> None:
        types = Types()
        scene = rich_scene(types)
        sections = _sections(scene)
        sections[-1].set_cable_type(types, "4* 50 VMvK/Alk")
        sections[-1].general.name = "Kastanjelaan oud"

        new_cable = lay_parallel_cable(scene.network, sections, offset_px=20)

        self.assertEqual(new_cable.cable_part.type, sections[0].cable_part.type)
        self.assertNotEqual(new_cable.cable_part.type, sections[-1].cable_part.type)
        self.assertEqual(new_cable.cable_type, sections[0].cable_type)
        self.assertIsNot(new_cable.cable_type, sections[0].cable_type)
        self.assertEqual(new_cable.general.name, "Kastanjelaan")

    def test_name_overrides_the_first_sections_name(self) -> None:
        scene = cable_scene()

        new_cable = lay_parallel_cable(
            scene.network, _sections(scene), offset_px=20, name="Kastanjelaan zuid"
        )

        self.assertEqual(new_cable.general.name, "Kastanjelaan zuid")


class TestOtherWayRound(unittest.TestCase):
    """Sections stored or listed the other way round give the same cable."""

    def test_a_section_stored_the_other_way_round(self) -> None:
        expected_scene = rich_scene(Types())
        expected = lay_parallel_cable(
            expected_scene.network,
            _sections(expected_scene),
            offset_px=20,
            offset_m=2,
        )
        scene = rich_scene(Types())
        sections = _sections(scene)
        _turn_round(sections[1])

        new_cable = lay_parallel_cable(
            scene.network, sections, offset_px=20, offset_m=2
        )

        self.assertEqual(
            [drawing.polyline() for drawing in new_cable.presentations],
            [drawing.polyline() for drawing in expected.presentations],
        )
        self.assertEqual(_map_route(new_cable), _map_route(expected))

    def test_first_section_stored_the_other_way_round(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        _turn_round(sections[0])

        new_cable = lay_parallel_cable(scene.network, sections, offset_px=20)

        self.assertEqual(new_cable.general.node1, scene.rail.general.guid)
        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(0, 520), (1000, 520), (1000, 500)],
        )

    def test_sections_listed_from_the_end_to_the_rail(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)

        new_cable = lay_parallel_cable(
            scene.network, sections[::-1], offset_px=20, offset_m=2
        )

        self.assertEqual(new_cable.general.node1, scene.end.general.guid)
        self.assertEqual(new_cable.general.node2, scene.rail.general.guid)
        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(1000, 500), (1000, 480), (0, 480)],
        )
        self.assertEqual(
            _map_route(new_cable),
            [(GX0 + 100, GY0), (GX0 + 100, GY0 + 2), (GX0, GY0 + 2), (GX0, GY0)],
        )


class TestOtherNodes(unittest.TestCase):
    """The new cable connected to other nodes than the old cable's ends."""

    def test_nodes_swapped_run_from_the_end_on_the_same_side(self) -> None:
        scene = cable_scene()

        new_cable = lay_parallel_cable(
            scene.network,
            [scene.cable],
            offset_px=20,
            offset_m=2,
            node1=scene.end,
            node2=scene.rail,
        )

        self.assertEqual(new_cable.general.node1, scene.end.general.guid)
        self.assertEqual(new_cable.general.node2, scene.rail.general.guid)
        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(1000, 500), (1000, 520), (0, 520)],
        )
        self.assertEqual(
            _map_route(new_cable),
            [(GX0 + 100, GY0), (GX0 + 100, GY0 - 2), (GX0, GY0 - 2), (GX0, GY0)],
        )

    def test_other_end_node_joined_in_a_straight_line(self) -> None:
        scene = cable_scene()
        cabinet = _add_node(scene.network, scene.sheet, 1000, 700)
        cabinet.general.gx = GX0 + 100
        cabinet.general.gy = GY0 - 20

        new_cable = lay_parallel_cable(
            scene.network, _sections(scene), offset_px=20, offset_m=2, node2=cabinet
        )

        self.assertEqual(new_cable.general.node1, scene.rail.general.guid)
        self.assertEqual(new_cable.general.node2, cabinet.general.guid)
        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(0, 520), (1000, 520), (1000, 700)],
        )
        self.assertEqual(
            _map_route(new_cable),
            [(GX0, GY0), (GX0, GY0 - 2), (GX0 + 100, GY0 - 2), (GX0 + 100, GY0 - 20)],
        )

    def test_other_start_node_with_the_end_swapped_runs_back(self) -> None:
        scene = cable_scene()
        cabinet = _add_node(scene.network, scene.sheet, 1000, 700)

        new_cable = lay_parallel_cable(
            scene.network,
            _sections(scene),
            offset_px=20,
            node1=cabinet,
            node2=scene.rail,
        )

        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(1000, 700), (1000, 520), (0, 520)],
        )

    def test_from_the_end_to_another_node_runs_back(self) -> None:
        scene = cable_scene()
        cabinet = _add_node(scene.network, scene.sheet, 0, 700)
        cabinet.general.gx = GX0
        cabinet.general.gy = GY0 - 20

        new_cable = lay_parallel_cable(
            scene.network,
            _sections(scene),
            offset_px=20,
            offset_m=2,
            node1=scene.end,
            node2=cabinet,
        )

        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(1000, 500), (1000, 520), (0, 520), (0, 700)],
        )
        self.assertEqual(
            _map_route(new_cable),
            [(GX0 + 100, GY0), (GX0 + 100, GY0 - 2), (GX0, GY0 - 2), (GX0, GY0 - 20)],
        )

    def test_running_back_keeps_the_first_sections_style(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        sections[0].presentations[0].color = CL_RED

        new_cable = lay_parallel_cable(
            scene.network, sections, offset_px=20, node1=scene.end, node2=scene.rail
        )

        self.assertEqual(new_cable.presentations[0].color, CL_RED)

    def test_length_given(self) -> None:
        scene = cable_scene()

        new_cable = lay_parallel_cable(
            scene.network, _sections(scene), offset_px=20, length=135.5
        )

        self.assertEqual(new_cable.cable_part.length, 135.5)

    def test_sheet_the_other_node_is_not_on_is_skipped(self) -> None:
        scene = cable_scene(second_sheet=True)
        cabinet = _add_node(scene.network, scene.sheet, 1000, 700)

        new_cable = lay_parallel_cable(
            scene.network, [scene.cable], offset_px=20, node2=cabinet
        )

        sheets = [drawing.sheet for drawing in new_cable.presentations]
        self.assertEqual(sheets, [scene.sheet])


class TestDrawing(unittest.TestCase):
    """The new cable's drawing beside the old one."""

    def test_to_the_right_of_a_straight_chain(self) -> None:
        scene = cable_scene()

        new_cable = lay_parallel_cable(scene.network, _sections(scene), offset_px=20)

        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(0, 520), (1000, 520), (1000, 500)],
        )

    def test_zig_zag_hugged_with_mitred_corners(self) -> None:
        scene = rich_scene(Types())

        new_cable = lay_parallel_cable(scene.network, _sections(scene), offset_px=20)

        drawing = new_cable.presentations[0]
        self.assertEqual(drawing.sheet, scene.sheet)
        self.assertEqual(
            drawing.polyline(),
            [
                (0, 520),
                (180, 520),
                (180, 820),
                (820, 820),
                (820, 520),
                (1000, 520),
                (1000, 500),
            ],
        )

    def test_step_along_a_joint_drawn_as_a_bar_is_kept(self) -> None:
        network = NetworkLV()
        sheet = network.add(SheetLV(SheetLV.General(name="Eikenlaan"))).general.guid
        start = _add_node(network, sheet, 0, 490)
        cabinet = _add_node(network, sheet, 500, 500, Symbol.VERTICAL_LINE, size=2)
        end = _add_node(network, sheet, 1000, 510)
        sections = [
            _add_cable(network, sheet, start, cabinet),
            _add_cable(network, sheet, cabinet, end),
        ]

        new_cable = lay_parallel_cable(network, sections, offset_px=20)

        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(0, 490), (0, 510), (480, 510), (480, 530), (1000, 530), (1000, 510)],
        )

    def test_u_bend_twice_the_offset_wide_folds_onto_one_line(self) -> None:
        network = NetworkLV()
        sheet = network.add(SheetLV(SheetLV.General(name="Eikenlaan"))).general.guid
        start = _add_node(network, sheet, 0, 500)
        end = _add_node(network, sheet, 0, 540)
        cable = _add_cable(network, sheet, start, end, via=[(500, 500), (500, 540)])

        new_cable = lay_parallel_cable(network, [cable], offset_px=20)

        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(0, 500), (0, 520), (480, 520), (0, 520), (0, 540)],
        )

    def test_drawn_on_top_when_the_offset_is_zero(self) -> None:
        scene = cable_scene()
        scene.cable.presentations = [
            BranchPresentation.between(
                scene.rail,
                scene.end,
                scene.sheet,
                via=[(500, 500), (500, 800), (500, 600)],
            )
        ]

        new_cable = lay_parallel_cable(scene.network, [scene.cable], offset_px=0)

        self.assertEqual(
            new_cable.presentations[0].polyline(),
            [(0, 500), (500, 500), (500, 800), (500, 600), (1000, 500)],
        )

    def test_both_sheets_drawn_each_along_its_own_route(self) -> None:
        scene = rich_scene(Types())

        new_cable = lay_parallel_cable(scene.network, _sections(scene), offset_px=20)

        sheets = [drawing.sheet for drawing in new_cable.presentations]
        self.assertEqual(sheets, [scene.sheet, scene.second_sheet])
        self.assertEqual(
            new_cable.presentations[1].polyline(),
            [(0, 520), (1000, 520), (1000, 500)],
        )

    def test_sheet_the_sections_are_not_on_is_skipped(self) -> None:
        scene = cable_scene()
        msr_sheet = scene.network.add(SheetLV(SheetLV.General(name="MSR"))).general.guid
        scene.rail.presentations.append(NodePresentation(sheet=msr_sheet, x=400, y=400))

        new_cable = lay_parallel_cable(scene.network, _sections(scene), offset_px=20)

        sheets = [drawing.sheet for drawing in new_cable.presentations]
        self.assertEqual(sheets, [scene.sheet])

    def test_sheet_only_some_sections_are_drawn_on_is_skipped(self) -> None:
        scene = cable_scene(second_sheet=True)
        sections = _sections(scene)
        sections[2].presentations = [
            drawing
            for drawing in sections[2].presentations
            if drawing.sheet == scene.sheet
        ]

        new_cable = lay_parallel_cable(scene.network, sections, offset_px=20)

        sheets = [drawing.sheet for drawing in new_cable.presentations]
        self.assertEqual(sheets, [scene.sheet])

    def test_sheet_with_both_nodes_on_one_point_is_skipped(self) -> None:
        scene = cable_scene(second_sheet=True)
        assert scene.second_sheet is not None
        end_on_detail = scene.end.get_presentation_on_sheet(scene.second_sheet)
        assert end_on_detail is not None
        end_on_detail.x = 0
        scene.cable.presentations[1] = BranchPresentation.between(
            scene.rail, scene.end, scene.second_sheet
        )

        new_cable = lay_parallel_cable(scene.network, [scene.cable], offset_px=20)

        sheets = [drawing.sheet for drawing in new_cable.presentations]
        self.assertEqual(sheets, [scene.sheet])

    def test_line_and_text_style_carry_over_without_text_placement(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        old_drawing = sections[0].presentations[0]
        old_drawing.color = CL_RED
        old_drawing.width = 3
        old_drawing.size = 2
        old_drawing.text_color = CL_RED
        old_drawing.text_size = 8
        old_drawing.font = "Courier New"
        old_drawing.text_style = 1
        old_drawing.no_text = True
        old_drawing.upside_down_text = True
        old_drawing.strings1_x = 30
        old_drawing.mid_strings_y = -15
        old_drawing.flag_flipped1 = True

        new_cable = lay_parallel_cable(scene.network, sections, offset_px=20)

        new_drawing = new_cable.presentations[0]
        self.assertEqual(
            replace(new_drawing, first_corners=[], second_corners=[]),
            BranchPresentation(
                sheet=scene.sheet,
                color=CL_RED,
                size=2,
                width=3,
                text_color=CL_RED,
                text_size=8,
                font="Courier New",
                text_style=1,
                no_text=True,
                upside_down_text=True,
            ),
        )


class TestMapRoute(unittest.TestCase):
    """The new cable's route on the map beside the old one."""

    def test_two_metres_to_the_right(self) -> None:
        scene = cable_scene()

        new_cable = lay_parallel_cable(
            scene.network, _sections(scene), offset_px=20, offset_m=2
        )

        self.assertEqual(
            _map_route(new_cable),
            [(GX0, GY0), (GX0, GY0 - 2), (GX0 + 100, GY0 - 2), (GX0 + 100, GY0)],
        )

    def test_same_trench_follows_the_old_route(self) -> None:
        scene = cable_scene()

        new_cable = lay_parallel_cable(scene.network, _sections(scene), offset_px=20)

        self.assertEqual(_map_route(new_cable), [(GX0, GY0), (GX0 + 100, GY0)])
        self.assertIsNone(new_cable.geography)

    def test_same_trench_keeps_a_route_that_turns_back(self) -> None:
        scene = cable_scene()
        turning_back = [(GX0, GY0), (GX0 + 50, GY0), (GX0 + 30, GY0), (GX0 + 100, GY0)]
        scene.cable.cablepart_geography = GeoCablePart(turning_back)

        new_cable = lay_parallel_cable(scene.network, [scene.cable], offset_px=20)

        self.assertEqual(_map_route(new_cable), turning_back)

    def test_rounded_to_the_millimetre(self) -> None:
        scene = cable_scene()
        scene.end.general.gy = GY0 + 100
        scene.cable.cablepart_geography = GeoCablePart(
            [(GX0, GY0), (GX0 + 100, GY0 + 100)]
        )

        new_cable = lay_parallel_cable(
            scene.network, [scene.cable], offset_px=20, offset_m=1
        )

        self.assertEqual(
            _map_route(new_cable),
            [
                (1000.0, 500.0),
                (1000.707, 499.293),
                (1100.707, 599.293),
                (1100.0, 600.0),
            ],
        )

    def test_two_metres_to_the_right_in_degrees(self) -> None:
        scene = _degrees_scene()

        new_cable = lay_parallel_cable(
            scene.network, [scene.cable], offset_px=20, offset_m=2
        )

        # walking north, 2 m to the right is 0.0000292 degrees east at 52 degrees north
        self.assertEqual(
            _map_route(new_cable),
            [(5.1, 52.0), (5.10002921, 52.0), (5.10002921, 52.001), (5.1, 52.001)],
        )

    def test_section_without_geography_follows_the_line_between_its_nodes(
        self,
    ) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        sections[1].cablepart_geography = None

        new_cable = lay_parallel_cable(
            scene.network, sections, offset_px=20, offset_m=2
        )

        self.assertEqual(
            _map_route(new_cable),
            [(GX0, GY0), (GX0, GY0 - 2), (GX0 + 100, GY0 - 2), (GX0 + 100, GY0)],
        )

    def test_no_map_route_without_geography_or_node_positions(self) -> None:
        scene = cable_scene(with_geography=False, node2_has_coordinates=False)

        new_cable = lay_parallel_cable(
            scene.network, _sections(scene), offset_px=20, offset_m=2
        )

        self.assertIsNone(new_cable.cablepart_geography)


class TestEnds(unittest.TestCase):
    """The new cable's ends, and the old sections beside it."""

    def test_ends_are_closed_without_protection_or_fuses(self) -> None:
        scene = rich_scene(Types())
        sections = _sections(scene)
        sections[0].general.field_name1 = "Veld 1"
        sections[0].general.k1_L1 = 8
        sections[0].fuse1_h1 = FuseType(short_name="25 A")

        new_cable = lay_parallel_cable(scene.network, sections, offset_px=20)

        self.assertEqual(
            new_cable.general,
            CableLV.General(
                guid=new_cable.general.guid,
                node1=scene.rail.general.guid,
                node2=scene.end.general.guid,
                name="Kastanjelaan",
            ),
        )
        self.assertIsNone(new_cable.fuse1_h1)
        fuses_on_new_cable = [
            fuse
            for fuse in scene.network.fuses.values()
            if fuse.general.in_object == new_cable.general.guid
        ]
        self.assertEqual(fuses_on_new_cable, [])

    def test_old_sections_are_untouched(self) -> None:
        scene = rich_scene(Types())
        sections = _sections(scene)
        before = deepcopy(sections)

        lay_parallel_cable(scene.network, sections, offset_px=20, offset_m=2)

        self.assertEqual(sections, before)


class TestRaises(unittest.TestCase):
    """Every refusal raises before the network changes."""

    def assert_refused(
        self,
        network: NetworkLV,
        cables: list[CableLV],
        pattern: str,
        **options: Any,
    ) -> None:
        before = _network_state(network)

        with self.assertRaisesRegex(ValueError, pattern):
            lay_parallel_cable(network, cables, offset_px=20, **options)

        self.assertEqual(_network_state(network), before)

    def test_offset_that_is_not_a_finite_number(self) -> None:
        scene = cable_scene()

        for offset_m in [float("nan"), float("inf")]:
            with self.subTest(offset_m=offset_m):
                self.assert_refused(
                    scene.network, [scene.cable], "finite", offset_m=offset_m
                )

    def test_length_below_half_a_metre(self) -> None:
        scene = cable_scene()

        for length in [0.4, -5.0, float("nan"), float("inf")]:
            with self.subTest(length=length):
                self.assert_refused(
                    scene.network, [scene.cable], "Length", length=length
                )

    def test_node_from_another_network(self) -> None:
        scene = cable_scene()
        other_scene = cable_scene()
        other_scene.end.general.name = "Beukenlaan eind"

        self.assert_refused(
            scene.network, [scene.cable], "Beukenlaan eind", node2=other_scene.end
        )

    def test_same_node_at_both_ends(self) -> None:
        scene = cable_scene()

        self.assert_refused(
            scene.network, [scene.cable], "two different nodes", node2=scene.rail
        )

    def test_other_node_on_no_sheet_of_the_sections(self) -> None:
        scene = cable_scene()
        detail_sheet = scene.network.add(
            SheetLV(SheetLV.General(name="Detail"))
        ).general.guid
        cabinet = _add_node(scene.network, detail_sheet, 400, 400)
        cabinet.general.name = "Kast 12"

        self.assert_refused(scene.network, [scene.cable], "Kast 12", node2=cabinet)

    def test_empty_list(self) -> None:
        scene = cable_scene()

        self.assert_refused(scene.network, [], "No cables")

    def test_cable_from_another_network(self) -> None:
        scene = cable_scene()
        other_scene = cable_scene()
        other_scene.cable.general.name = "Beukenlaan"

        self.assert_refused(
            scene.network, [scene.cable, other_scene.cable], "Beukenlaan"
        )

    def test_cable_that_does_not_join_the_previous_one(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        sections[3].general.name = "Kastanjelaan los"

        self.assert_refused(
            scene.network, [sections[0], sections[1], sections[3]], "Kastanjelaan los"
        )

    def test_two_cables_between_the_same_nodes(self) -> None:
        scene = cable_scene()
        second = deepcopy(scene.cable)
        second.general.guid = Guid.random()
        scene.network.add(second)

        self.assert_refused(scene.network, [scene.cable, second], "comes back")

    def test_chain_that_ends_where_it_starts(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        ring = _add_undrawn_cable(
            scene.network,
            sections[1].general.node2,
            scene.rail.general.guid,
            "Kastanjelaan ring",
        )

        self.assert_refused(
            scene.network, [sections[0], sections[1], ring], "Kastanjelaan ring"
        )

    def test_cable_from_a_joint_to_itself(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        joint = sections[0].general.node2
        loop = _add_undrawn_cable(scene.network, joint, joint, "Kastanjelaan lus")

        self.assert_refused(
            scene.network, [sections[0], loop, sections[1]], "Kastanjelaan lus"
        )

    def test_detour_back_to_a_joint(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        joint = sections[0].general.node2
        detour_end = scene.network.add(NodeLV(NodeLV.General(), presentations=[]))
        detour = detour_end.general.guid
        out = _add_undrawn_cable(scene.network, joint, detour, "Kastanjelaan uit")
        back = _add_undrawn_cable(scene.network, detour, joint, "Kastanjelaan terug")

        self.assert_refused(
            scene.network,
            [sections[0], out, back, sections[1]],
            "Kastanjelaan terug",
        )

    def test_section_whose_joint_is_missing_from_the_sheet(self) -> None:
        scene = cable_scene()
        sections = _sections(scene)
        sections[0].general.name = "Kastanjelaan begin"
        joint = scene.network.nodes[sections[0].general.node2]
        joint.presentations = []

        self.assert_refused(scene.network, sections, "Kastanjelaan begin")

    def test_sections_that_share_no_sheet(self) -> None:
        scene = cable_scene(second_sheet=True)
        sections = split_cable(scene.network, scene.cable, [55.0]).sections
        sections[0].presentations = [
            drawing
            for drawing in sections[0].presentations
            if drawing.sheet == scene.second_sheet
        ]
        sections[1].presentations = [
            drawing
            for drawing in sections[1].presentations
            if drawing.sheet == scene.sheet
        ]

        self.assert_refused(scene.network, sections, "'Kastanjelaan'.*one sheet")

    def test_sections_drawn_on_one_point_only(self) -> None:
        scene = cable_scene()
        scene.end.presentations[0].x = 0
        scene.cable.presentations = [
            BranchPresentation.between(scene.rail, scene.end, scene.sheet)
        ]

        self.assert_refused(scene.network, [scene.cable], "'Kastanjelaan'.*one sheet")

    def test_drawing_that_turns_back(self) -> None:
        scene = cable_scene()
        scene.cable.presentations = [
            BranchPresentation.between(
                scene.rail,
                scene.end,
                scene.sheet,
                via=[(500, 500), (500, 800), (500, 600)],
            )
        ]

        self.assert_refused(scene.network, [scene.cable], "'Kastanjelaan'.*turns back")


class TestSaveAndReload(unittest.TestCase):
    """The new cable survives a save and reload through the native loader."""

    def test_save_and_reload(self) -> None:
        scene = rich_scene(Types())
        sections = _sections(scene)

        new_cable = lay_parallel_cable(
            scene.network, sections, offset_px=20, offset_m=2
        )

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "kastanjelaan.gnf"
            scene.network.save(path)
            reloaded = NetworkLV.from_file(path)

        reloaded_cable = reloaded.cables[new_cable.general.guid]
        self.assertEqual(reloaded_cable.cable_part.length, 110.0)
        self.assertEqual(reloaded_cable.general.node1, scene.rail.general.guid)
        self.assertEqual(len(reloaded_cable.presentations), 2)
        self.assertEqual(
            _map_route(reloaded_cable),
            [(GX0, GY0), (GX0, GY0 - 2), (GX0 + 100, GY0 - 2), (GX0 + 100, GY0)],
        )

    def test_save_and_reload_to_another_node(self) -> None:
        scene = rich_scene(Types())
        assert scene.second_sheet is not None
        cabinet = _add_node(scene.network, scene.sheet, 1000, 700)
        cabinet.presentations.append(
            NodePresentation(sheet=scene.second_sheet, x=1000, y=700)
        )

        new_cable = lay_parallel_cable(
            scene.network,
            _sections(scene),
            offset_px=20,
            node1=cabinet,
            node2=scene.rail,
            length=130.0,
        )

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "kastanjelaan.gnf"
            scene.network.save(path)
            reloaded = NetworkLV.from_file(path)

        reloaded_cable = reloaded.cables[new_cable.general.guid]
        self.assertEqual(reloaded_cable.general.node1, cabinet.general.guid)
        self.assertEqual(reloaded_cable.general.node2, scene.rail.general.guid)
        self.assertEqual(reloaded_cable.cable_part.length, 130.0)
        self.assertEqual(
            [drawing.polyline() for drawing in reloaded_cable.presentations],
            [drawing.polyline() for drawing in new_cable.presentations],
        )

    def test_save_and_reload_in_degrees(self) -> None:
        scene = _degrees_scene()

        new_cable = lay_parallel_cable(
            scene.network, [scene.cable], offset_px=20, offset_m=2
        )

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "kastanjelaan.gnf"
            scene.network.save(path)
            reloaded = NetworkLV.from_file(path)

        reloaded_cable = reloaded.cables[new_cable.general.guid]
        self.assertEqual(_map_route(reloaded_cable), _map_route(new_cable))


if __name__ == "__main__":
    unittest.main()
