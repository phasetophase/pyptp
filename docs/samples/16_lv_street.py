"""Build a small LV street: a substation and two feeders with connections.

A cable joins the far ends of the two feeders. It is switched open, so the feeders
run separately until someone closes it.
"""

import math
from collections.abc import Sequence
from itertools import pairwise

from pyptp import NetworkLV, configure_logging
from pyptp.elements.color_utils import CL_BLACK, CL_BLUE, CL_ORANGE, DelphiColor
from pyptp.elements.element_utils import SIDE_NODE2
from pyptp.elements.enums import NodePresentationSymbol as Symbol
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import (
    BranchPresentation,
    ElementPresentation,
    NodePresentation,
    SecundairPresentation,
)
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.source import SourceLV
from pyptp.elements.lv.transformer import TransformerLV
from pyptp.ptp_log import logger
from pyptp.type_reader import Types

configure_logging(level="INFO")

PIXELS_PER_METER = 20
STREET_Y = 600
CONNECTIONS_PER_SIDE = 3

network = NetworkLV()
types = Types()
sheet = network.add(SheetLV(SheetLV.General(name="Molenstraat"))).general.guid


def add_cable(
    name: str, color: DelphiColor, node1: NodeLV, node2: NodeLV, via: Sequence[tuple[int, int]] = ()
) -> CableLV:
    """Add a cable between two nodes, its length follows the drawing."""
    presentation = BranchPresentation.between(node1, node2, sheet, via=via)
    presentation.color = color
    drawn = sum(math.dist(a, b) for a, b in pairwise(presentation.polyline()))
    cable = CableLV(
        CableLV.General(node1=node1.general.guid, node2=node2.general.guid, name=name),
        presentations=[presentation],
        cable_part=CableLV.CablePart(length=round(drawn / PIXELS_PER_METER, 1)),
    )
    cable.set_cable_type(types, "4*150 VVMvKsas/Alk")
    return network.add(cable)


def add_joint(x: int, y: int, color: DelphiColor) -> NodeLV:
    presentation = NodePresentation(sheet=sheet, x=x, y=y, symbol=Symbol.OPEN_TRIANGLE, color=color)
    return network.add(NodeLV(NodeLV.General(), presentations=[presentation]))


def add_fuse(name: str, color: DelphiColor, cable: CableLV) -> None:
    """Add a fuse at the start of ``cable``."""
    fuse = FuseLV(
        FuseLV.General(name=name, in_object=cable.general.guid, side=1),
        presentations=[SecundairPresentation(sheet=sheet, distance=40, color=color)],
    )
    fuse.set_type(types, "Jean Muller 200 A gL/gG")
    network.add(fuse)


def add_connection(joint: NodeLV, number: int, x: int, y: int, gm_type: int) -> None:
    """Add Molenstraat ``number`` on ``joint``, drawn at ``(x, y)``."""
    connection = ConnectionLV(
        ConnectionLV.General(node=joint.general.guid, name=f"Molenstraat {number}", length=10),
        presentations=[ElementPresentation(sheet=sheet, x=x, y=y)],
        gms=[ConnectionLV.GM(gm_type_number=gm_type)],
    )
    connection.set_cable_type(types, "Vulto 4x10 Cu")
    connection.set_fuse_type(types, "Jean Muller 25 A gL/gG")
    network.add(connection)


def add_feeder(name: str, color: DelphiColor, rail: NodeLV, gm_type: int, *, above: bool) -> NodeLV:
    """Add a feeder from ``rail`` with a connection at every joint and return the last joint."""
    side = -1 if above else 1
    cable_y = STREET_Y + side * 60
    connection_y = cable_y + side * 200
    first_number = 1 if above else 2
    previous = rail
    for index in range(CONNECTIONS_PER_SIDE):
        x = 800 + 160 * index
        joint = add_joint(x, cable_y, color)
        section = add_cable(name, color, previous, joint)
        if index == 0:
            add_fuse(name, color, section)
        add_connection(joint, first_number + 2 * index, x + 80, connection_y, gm_type)
        previous = joint
    return previous


mv_rail = network.add(
    NodeLV(
        NodeLV.General(name="MS-rail", unom=10),
        presentations=[NodePresentation(sheet=sheet, x=200, y=STREET_Y, symbol=Symbol.VERTICAL_LINE, size=4)],
    )
)
lv_rail = network.add(
    NodeLV(
        NodeLV.General(name="MSR Molenstraat"),
        presentations=[NodePresentation(sheet=sheet, x=600, y=STREET_Y, symbol=Symbol.VERTICAL_LINE, size=8)],
    )
)

network.add(
    SourceLV(
        SourceLV.General(node=mv_rail.general.guid, name="Net", umin=10, umax=10, uref=10, sk2nom=1000),
        presentations=[ElementPresentation(sheet=sheet, x=100, y=STREET_Y)],
    )
)

transformer = TransformerLV(
    TransformerLV.General(node1=mv_rail.general.guid, node2=lv_rail.general.guid, name="Trafo 1"),
    presentations=[BranchPresentation.between(mv_rail, lv_rail, sheet)],
    type=TransformerLV.TransformerType(),
)
transformer.set_type(types, "10250/400 V  630 kVA")
network.add(transformer)

household_gm = network.add(types.get_lv_gm_type("sjv2500"))
household = household_gm.general.number

odd_end = add_feeder("Molenstraat oneven", CL_BLUE, lv_rail, household, above=True)
even_end = add_feeder("Molenstraat even", CL_ORANGE, lv_rail, household, above=False)

normally_open = add_cable("Molenstraat kop", CL_BLACK, odd_end, even_end, via=[(1240, 540), (1240, 660)])
normally_open.general.set_switches(SIDE_NODE2, closed=False)

network.save("lv_street.gnf")
logger.info("Saved lv_street.gnf")
