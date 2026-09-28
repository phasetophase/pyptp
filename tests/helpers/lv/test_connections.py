"""Tests for move_connections_to_cable: connecting connections to a cable at new joints."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pyptp.elements.element_utils import Guid
from pyptp.elements.enums import NodePresentationSymbol as Symbol
from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import (
    BranchPresentation,
    ElementPresentation,
    NodePresentation,
)
from pyptp.elements.lv.sheet import SheetLV
from pyptp.helpers.lv import CableSections, move_connections_to_cable
from pyptp.network_lv import NetworkLV
from pyptp.type_reader import Types

from ._scene import (
    CORNER_IN_DEGREES,
    GX0,
    GY0,
    PX_PER_M,
    Scene,
    cable_scene,
    degrees_scene,
    metres_between,
    ordered_sections,
    rich_scene,
)


def _connection(
    network: NetworkLV,
    sheet: Guid,
    name: str,
    metres: float,
    *,
    on_geography: bool = True,
    on_sheet: bool = False,
    extra_sheet: Guid | None = None,
) -> ConnectionLV:
    """A connection at ``metres`` along the cable, positioned by geography, sheet, or both."""
    general = ConnectionLV.General(name=name, length=10.0)
    if on_geography:
        general.geo_x_coord = GX0 + metres
        general.geo_y_coord = GY0
    presentations = []
    if on_sheet:
        presentations.append(
            ElementPresentation(sheet=sheet, x=int(metres * PX_PER_M), y=580)
        )
    if extra_sheet is not None:
        presentations.append(ElementPresentation(sheet=extra_sheet, x=0, y=0))
    return network.add(ConnectionLV(general, presentations=presentations, gms=[]))


def _street() -> tuple[Scene, list[ConnectionLV]]:
    """The cable, with connections 10, 50 and 90 m along, each on its own old joint."""
    scene = cable_scene()
    connections = []
    for index, metres in enumerate((10.0, 50.0, 90.0), start=1):
        old_joint = scene.network.add(
            NodeLV(
                NodeLV.General(name=f"Kastanjelaan oud {index}"),
                presentations=[
                    NodePresentation(
                        sheet=scene.sheet,
                        x=int(metres * PX_PER_M),
                        y=560,
                        symbol=Symbol.OPEN_TRIANGLE,
                    )
                ],
            )
        )
        connection = _connection(
            scene.network, scene.sheet, f"Kastanjelaan {2 * index - 1}", metres
        )
        connection.general.node = old_joint.general.guid
        connections.append(connection)
    return scene, connections


class TestPlacement(unittest.TestCase):
    """Where joints land and which connections connect to them."""

    def test_joints_land_nearest_each_connection_in_order(self) -> None:
        scene, connections = _street()

        # out of order on purpose
        result = move_connections_to_cable(
            scene.network, scene.cable, [connections[2], connections[0], connections[1]]
        )

        self.assertEqual(
            [joint.general.gx for joint in result.joints],
            [GX0 + 10.0, GX0 + 50.0, GX0 + 90.0],
        )
        self.assertEqual(
            [section.cable_part.length for section in result.sections],
            [11.0, 44.0, 44.0, 11.0],
        )

    def test_connections_connected_to_their_joints(self) -> None:
        scene, connections = _street()
        joints = move_connections_to_cable(
            scene.network, scene.cable, connections
        ).joints

        for connection, joint in zip(connections, joints, strict=True):
            self.assertEqual(connection.general.node, joint.general.guid)

    def test_connections_less_than_half_a_metre_apart_share_a_joint(self) -> None:
        scene = cable_scene()
        close_a = _connection(scene.network, scene.sheet, "Kastanjelaan 1", 10.0)
        close_b = _connection(scene.network, scene.sheet, "Kastanjelaan 3", 10.3)

        joints = move_connections_to_cable(
            scene.network, scene.cable, [close_a, close_b]
        ).joints

        self.assertEqual(len(joints), 1)
        self.assertEqual(close_a.general.node, joints[0].general.guid)
        self.assertEqual(close_b.general.node, joints[0].general.guid)

    def test_connection_near_an_end_is_clamped_not_snapped_onto_the_node(self) -> None:
        scene = cable_scene()
        connection = _connection(scene.network, scene.sheet, "Kastanjelaan 1", 0.1)

        joints = move_connections_to_cable(
            scene.network, scene.cable, [connection]
        ).joints

        self.assertEqual(len(joints), 1)
        self.assertEqual(scene.cable.cable_part.length, 0.5)

    def test_connection_at_node_2_of_a_cable_measured_in_millimetres_keeps_half_a_metre(
        self,
    ) -> None:
        scene = cable_scene()
        scene.cable.cable_part.length = 37.487
        connection = _connection(scene.network, scene.sheet, "Kastanjelaan 1", 99.99)

        result = move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertEqual(
            [section.cable_part.length for section in result.sections], [36.98, 0.507]
        )

    def test_cable_running_from_the_far_end_gives_each_connection_its_nearest_joint(
        self,
    ) -> None:
        scene, connections = _street()
        cable = scene.cable
        cable.general.node1 = scene.end.general.guid
        cable.general.node2 = scene.rail.general.guid
        cable.presentations = [
            BranchPresentation.between(scene.end, scene.rail, scene.sheet)
        ]

        move_connections_to_cable(scene.network, cable, connections)

        for connection in connections:
            joint = scene.network.nodes[connection.general.node]
            metres = connection.general.geo_x_coord - GX0
            self.assertAlmostEqual(joint.general.gx, connection.general.geo_x_coord)
            self.assertEqual(joint.presentations[0].x, metres * PX_PER_M)

    def test_house_at_the_corner_of_a_route_in_degrees_joins_at_the_corner(
        self,
    ) -> None:
        scene = degrees_scene()
        corner_longitude, corner_latitude = CORNER_IN_DEGREES
        # 5 m south-east of the corner, outside the bend
        general = ConnectionLV.General(
            name="Kastanjelaan 1",
            length=10.0,
            geo_x_coord=corner_longitude + 0.00005,
            geo_y_coord=corner_latitude - 0.00003,
        )
        connection = scene.network.add(ConnectionLV(general, presentations=[], gms=[]))

        result = move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertEqual(
            [section.cable_part.length for section in result.sections], [100.0, 100.0]
        )
        joint = result.joints[0]
        joint_position = (joint.general.gx, joint.general.gy)
        self.assertLess(metres_between(joint_position, CORNER_IN_DEGREES), 0.05)

    def test_empty_connections_leave_the_cable_whole(self) -> None:
        scene = cable_scene()

        result = move_connections_to_cable(scene.network, scene.cable, [])

        self.assertEqual(result, CableSections([scene.cable], []))


class TestFallbackAndConnectionGeography(unittest.TestCase):
    """Positioning from the drawing when there is no usable geography, and the connection's geography."""

    def test_sheet_fallback_off_the_map_leaves_the_joint_off_the_map(self) -> None:
        scene = cable_scene(
            with_geography=False,
            node1_has_coordinates=False,
            node2_has_coordinates=False,
        )
        connection = _connection(
            scene.network,
            scene.sheet,
            "Kastanjelaan 1",
            50.0,
            on_geography=False,
            on_sheet=True,
        )

        joints = move_connections_to_cable(
            scene.network, scene.cable, [connection]
        ).joints

        self.assertEqual(joints[0].general.gx, 0)
        self.assertEqual(joints[0].presentations[0].x, 500)

    def test_without_geography_the_line_between_the_nodes_places_the_joint(
        self,
    ) -> None:
        scene = cable_scene(with_geography=False)
        connection = _connection(scene.network, scene.sheet, "Kastanjelaan 1", 30.0)
        connection.connection_geography = ConnectionLV.Geography(
            coordinates=[(0.0, 0.0), (0.0, 0.0)]
        )

        result = move_connections_to_cable(scene.network, scene.cable, [connection])

        joint = result.joints[0]
        self.assertEqual(scene.cable.cable_part.length, 33.0)
        self.assertAlmostEqual(joint.general.gx, GX0 + 30.0)
        assert connection.connection_geography is not None
        self.assertEqual(
            connection.connection_geography.coordinates,
            [(joint.general.gx, joint.general.gy), (GX0 + 30.0, GY0)],
        )

    def test_without_geography_a_shared_sheet_comes_before_the_line_between_the_nodes(
        self,
    ) -> None:
        scene = cable_scene(with_geography=False)
        connection = _connection(
            scene.network, scene.sheet, "Kastanjelaan 1", 30.0, on_sheet=True
        )
        connection.presentations[0].x = 80 * PX_PER_M

        move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertEqual(scene.cable.cable_part.length, 88.0)

    def test_connection_geography_dropped_off_the_map(self) -> None:
        scene = cable_scene(
            with_geography=False,
            node1_has_coordinates=False,
            node2_has_coordinates=False,
        )
        connection = _connection(
            scene.network,
            scene.sheet,
            "Kastanjelaan 1",
            50.0,
            on_geography=False,
            on_sheet=True,
        )
        connection.connection_geography = ConnectionLV.Geography(
            coordinates=[(0.0, 0.0), (0.0, 0.0)]
        )

        move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertIsNone(connection.connection_geography)


class TestJoints(unittest.TestCase):
    """Properties of the new joints."""

    def test_joints_connect_n_and_pe(self) -> None:
        scene, connections = _street()
        joints = move_connections_to_cable(
            scene.network, scene.cable, connections
        ).joints

        for joint in joints:
            self.assertTrue(joint.general.s_N_PE)

    def test_symbol_override(self) -> None:
        scene, connections = _street()
        joints = move_connections_to_cable(
            scene.network, scene.cable, connections, symbol=Symbol.OPEN_TRIANGLE
        ).joints

        for joint in joints:
            self.assertEqual(joint.presentations[0].symbol, Symbol.OPEN_TRIANGLE)

    def test_joints_drawn_as_closed_triangles(self) -> None:
        scene, connections = _street()
        joints = move_connections_to_cable(
            scene.network, scene.cable, connections
        ).joints

        for joint in joints:
            self.assertEqual(joint.presentations[0].symbol, Symbol.CLOSED_TRIANGLE)


class TestRaises(unittest.TestCase):
    """Every failure raises before anything is mutated."""

    def test_unregistered_cable_raises(self) -> None:
        scene = cable_scene()
        other_scene, other_connections = _street()
        cable_count = len(scene.network.cables)

        with self.assertRaisesRegex(ValueError, "Cable .*not registered"):
            move_connections_to_cable(
                scene.network, other_scene.cable, other_connections
            )

        self.assertEqual(len(scene.network.cables), cable_count)

    def test_cable_too_short_raises(self) -> None:
        scene = cable_scene()
        scene.cable.cable_part.length = 0.9
        connection = _connection(scene.network, scene.sheet, "Kastanjelaan 1", 50.0)
        cable_count = len(scene.network.cables)

        with self.assertRaisesRegex(ValueError, "at least 1.0 m"):
            move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertEqual(len(scene.network.cables), cable_count)
        self.assertEqual(connection.general.node, Guid(0))

    def test_connection_with_no_position_raises(self) -> None:
        scene = cable_scene(with_geography=False)
        connection = scene.network.add(
            ConnectionLV(
                ConnectionLV.General(name="Kastanjelaan 1", length=10.0),
                presentations=[],
                gms=[],
            )
        )
        cable_count = len(scene.network.cables)

        with self.assertRaisesRegex(ValueError, "no map position and is not drawn"):
            move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertEqual(len(scene.network.cables), cable_count)
        self.assertEqual(connection.general.node, Guid(0))

    def test_connection_on_the_map_beside_a_cable_without_map_position_raises(
        self,
    ) -> None:
        scene = cable_scene(with_geography=False, node2_has_coordinates=False)
        connection = _connection(scene.network, scene.sheet, "Kastanjelaan 1", 50.0)

        with self.assertRaisesRegex(ValueError, "has no map position"):
            move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertEqual(connection.general.node, Guid(0))

    def test_connection_from_another_network_raises(self) -> None:
        scene = cable_scene()
        own = _connection(scene.network, scene.sheet, "Kastanjelaan 1", 30.0)
        other_scene = cable_scene()
        foreign = _connection(
            other_scene.network, other_scene.sheet, "Kastanjelaan 3", 60.0
        )
        node_count = len(scene.network.nodes)
        cable_count = len(scene.network.cables)

        with self.assertRaisesRegex(ValueError, "Kastanjelaan 3"):
            move_connections_to_cable(scene.network, scene.cable, [own, foreign])

        self.assertEqual(len(scene.network.nodes), node_count)
        self.assertEqual(len(scene.network.cables), cable_count)
        self.assertEqual(scene.cable.cable_part.length, 110.0)
        self.assertEqual(own.general.node, Guid(0))
        self.assertEqual(foreign.general.node, Guid(0))

    def test_connection_drawn_on_a_sheet_the_cable_is_not_drawn_on_raises(self) -> None:
        scene = cable_scene()
        other_sheet = scene.network.add(
            SheetLV(SheetLV.General(name="Ander blad"))
        ).general.guid
        connection = _connection(
            scene.network, scene.sheet, "Kastanjelaan 1", 50.0, extra_sheet=other_sheet
        )
        cable_count = len(scene.network.cables)

        with self.assertRaisesRegex(ValueError, "drawn on a sheet without"):
            move_connections_to_cable(scene.network, scene.cable, [connection])

        self.assertEqual(len(scene.network.cables), cable_count)
        self.assertEqual(connection.general.node, Guid(0))


class TestSaveAndReload(unittest.TestCase):
    """The move survives a save and reload through Gaia's own loader."""

    def test_save_and_reload(self) -> None:
        types = Types()
        scene = rich_scene(types)
        connections = []
        for name, metres in (
            ("Kastanjelaan 1", 0.2),
            ("Kastanjelaan 3", 50.0),
            ("Kastanjelaan 5", 99.9),
        ):
            connection = _connection(
                scene.network,
                scene.sheet,
                name,
                metres,
                on_sheet=True,
                extra_sheet=scene.second_sheet,
            )
            connection.set_cable_type(types, "Vulto 4x10 Cu")
            connection.connection_geography = ConnectionLV.Geography(
                coordinates=[(0.0, 0.0), (0.0, 0.0)]
            )
            connections.append(connection)

        move_connections_to_cable(scene.network, scene.cable, connections)

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
        for connection, section in zip(connections, sections[:-1], strict=True):
            moved = reloaded.homes[connection.general.guid]
            joint = reloaded.nodes[section.general.node2]
            self.assertEqual(moved.general.node, joint.general.guid)
            self.assertTrue(joint.general.s_N_PE)
            assert moved.connection_geography is not None
            start, end = moved.connection_geography.coordinates
            self.assertAlmostEqual(start[0], joint.general.gx)
            self.assertAlmostEqual(start[1], joint.general.gy)
            self.assertEqual(
                end, (connection.general.geo_x_coord, connection.general.geo_y_coord)
            )


if __name__ == "__main__":
    unittest.main()
