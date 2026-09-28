"""Shared scene for the LV helper tests."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyptp.elements.element_utils import Guid
from pyptp.elements.enums import NodePresentationSymbol as Symbol
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.shared import GeoCablePart
from pyptp.network_lv import NetworkLV

if TYPE_CHECKING:
    from pyptp.type_reader import Types

# the cable is recorded longer than its geography, so positions and lengths differ
GX0 = 1000.0
GY0 = 500.0
GEO_LENGTH = 100.0
RECORDED_LENGTH = 110.0
PX_PER_M = 10

# a street at 52 degrees north, 100 m east to the corner and then 100 m north
START_IN_DEGREES = (5.1, 52.0)
CORNER_IN_DEGREES = (5.10146184, 52.0)
END_IN_DEGREES = (5.10146184, 52.0009)

EARTH_RADIUS_M = 6_371_008.8


@dataclass
class Scene:
    """A network with one sheet, a rail and an end node, and the cable between them."""

    network: NetworkLV
    sheet: Guid
    rail: NodeLV
    end: NodeLV
    cable: CableLV
    second_sheet: Guid | None = None


def cable_scene(
    *,
    reverse_geography: bool = False,
    node1_has_coordinates: bool = True,
    node2_has_coordinates: bool = True,
    with_geography: bool = True,
    second_sheet: bool = False,
) -> Scene:
    """A rail and an end node 100 m apart, joined by the cable."""
    network = NetworkLV()
    sheet = network.add(SheetLV(SheetLV.General(name="Kastanjelaan"))).general.guid

    rail = network.add(
        NodeLV(
            NodeLV.General(
                name="MSR Kastanjelaan",
                gx=GX0 if node1_has_coordinates else 0,
                gy=GY0 if node1_has_coordinates else 0,
            ),
            presentations=[
                NodePresentation(
                    sheet=sheet, x=0, y=500, symbol=Symbol.VERTICAL_LINE, size=4
                )
            ],
        )
    )
    end = network.add(
        NodeLV(
            NodeLV.General(
                name="Kastanjelaan eind",
                gx=GX0 + GEO_LENGTH if node2_has_coordinates else 0,
                gy=GY0 if node2_has_coordinates else 0,
            ),
            presentations=[
                NodePresentation(sheet=sheet, x=int(GEO_LENGTH * PX_PER_M), y=500)
            ],
        )
    )
    presentations = [BranchPresentation.between(rail, end, sheet)]

    second_sheet_guid = None
    if second_sheet:
        second_sheet_guid = network.add(
            SheetLV(SheetLV.General(name="Detail"))
        ).general.guid
        rail.presentations.append(
            NodePresentation(
                sheet=second_sheet_guid, x=0, y=500, symbol=Symbol.VERTICAL_LINE, size=4
            )
        )
        end.presentations.append(
            NodePresentation(
                sheet=second_sheet_guid, x=int(GEO_LENGTH * PX_PER_M), y=500
            )
        )
        presentations.append(BranchPresentation.between(rail, end, second_sheet_guid))

    cablepart_geography = None
    if with_geography:
        coordinates = [(GX0, GY0), (GX0 + GEO_LENGTH, GY0)]
        if reverse_geography:
            coordinates = list(reversed(coordinates))
        cablepart_geography = GeoCablePart(coordinates=coordinates)

    cable = network.add(
        CableLV(
            CableLV.General(
                node1=rail.general.guid,
                node2=end.general.guid,
                name="Kastanjelaan",
            ),
            presentations=presentations,
            cable_part=CableLV.CablePart(length=RECORDED_LENGTH),
            cablepart_geography=cablepart_geography,
        )
    )
    return Scene(
        network=network,
        sheet=sheet,
        rail=rail,
        end=end,
        cable=cable,
        second_sheet=second_sheet_guid,
    )


def rich_scene(types: Types) -> Scene:
    """The cable drawn on two sheets and on the map, each along a different route.

    Node 1's end has an open switch, and both ends have a fuse.
    """
    scene = cable_scene(second_sheet=True)
    cable = scene.cable
    cable.set_cable_type(types, "4*150 VVMvKsas/Alk")
    cable.geography = GeoCablePart(
        coordinates=[(GX0, GY0), (GX0 + 50, GY0 + 20), (GX0 + GEO_LENGTH, GY0)]
    )
    cable.presentations[0] = BranchPresentation.between(
        scene.rail,
        scene.end,
        scene.sheet,
        via=[(200, 500), (200, 800), (800, 800), (800, 500)],
    )
    cable.general.switch_state1_L1 = False
    for side in (1, 2):
        scene.network.add(
            FuseLV(
                FuseLV.General(
                    name=f"Kastanjelaan {side}",
                    in_object=cable.general.guid,
                    side=side,
                )
            )
        )
    return scene


def degrees_scene() -> Scene:
    """The cable round the corner on a map in degrees, recorded as 200 m."""
    scene = cable_scene()
    start_longitude, start_latitude = START_IN_DEGREES
    end_longitude, end_latitude = END_IN_DEGREES
    scene.rail.general.gx = start_longitude
    scene.rail.general.gy = start_latitude
    scene.end.general.gx = end_longitude
    scene.end.general.gy = end_latitude
    scene.cable.cable_part.length = 200.0
    scene.cable.cablepart_geography = GeoCablePart(
        [START_IN_DEGREES, CORNER_IN_DEGREES, END_IN_DEGREES]
    )
    return scene


def metres_between(start: tuple[float, float], end: tuple[float, float]) -> float:
    """Great-circle distance between two (longitude, latitude) points."""
    start_lon, start_lat = map(math.radians, start)
    end_lon, end_lat = map(math.radians, end)
    haversine = (
        math.sin((end_lat - start_lat) / 2) ** 2
        + math.cos(start_lat)
        * math.cos(end_lat)
        * math.sin((end_lon - start_lon) / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(haversine))


def ordered_sections(network: NetworkLV, cable: CableLV) -> list[CableLV]:
    """The cable's sections in order, found by chaining node 1 to node 2 by name."""
    by_node1 = {
        c.general.node1: c
        for c in network.cables.values()
        if c.general.name == cable.general.name and c is not cable
    }
    chain = [cable]
    while chain[-1].general.node2 in by_node1:
        chain.append(by_node1[chain[-1].general.node2])
    return chain
