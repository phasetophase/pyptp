"""Understanding branch corner coordinates and polyline construction.

CRITICAL: FirstCorners start FROM Node1 traveling outward.
          SecondCorners start FROM Node2 traveling outward.
          A connection line joins the last point of each.

Common mistake: SecondCorners must start at Node2, not end at it.

BranchPresentation.between() builds both lists from the two nodes, the sheet
GUID and the points the route passes through.
"""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.color_utils import CL_GRAY
from pyptp.elements.enums import SymbolSegment
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkMV()

sheet = network.add(SheetMV(SheetMV.General(name="Corner Examples", color=CL_GRAY)))
sheet_guid = sheet.general.guid


def node(name: str, x: int, y: int) -> NodeMV:
    """Add a node to the sheet."""
    return network.add(
        NodeMV(
            NodeMV.General(name=name, unom=10.0),
            presentations=[NodePresentation(sheet=sheet_guid, x=x, y=y)],
        )
    )


def link(
    name: str,
    node1: NodeMV,
    node2: NodeMV,
    via: list[tuple[int, int]],
    symbol_segment: SymbolSegment | int = SymbolSegment.MIDDLE,
) -> LinkMV:
    """Add a link between two nodes."""
    return network.add(
        LinkMV(
            LinkMV.General(name=name, node1=node1.general.guid, node2=node2.general.guid),
            presentations=[
                BranchPresentation.between(node1, node2, sheet_guid, via=via, symbol_segment=symbol_segment)
            ],
        )
    )


def show(label: str, presentation: BranchPresentation) -> None:
    """Log the route and both corner lists."""
    logger.info("%s: %s", label, presentation.polyline())
    logger.info("%s corners: %s and %s", label, presentation.first_corners, presentation.second_corners)


# Example 1: straight line
straight = link("straight", node("A", 100, 100), node("B", 300, 100), via=[])
show("straight", straight.presentations[0])

# Example 2: a Z with two bends
bend = link("bend", node("C", 100, 200), node("D", 300, 300), via=[(100, 250), (300, 250)])
show("bend", bend.presentations[0])

# Example 3: zig-zag
start = node("E", 100, 400)
end = node("F", 450, 450)
zigzag_via = [(150, 400), (200, 350), (250, 350), (300, 400), (350, 400), (375, 410), (400, 420)]
zigzag = link("zigzag", start, end, via=zigzag_via)
show("zigzag", zigzag.presentations[0])

# Example 4: same zig-zag, with its text on the longest segment
on_longest = BranchPresentation.between(start, end, sheet_guid, via=zigzag_via, symbol_segment=SymbolSegment.LONGEST)
show("zigzag on longest", on_longest)

# Example 1 with the corner lists written by hand
by_hand = BranchPresentation(
    sheet=sheet_guid,
    first_corners=[(100, 100)],
    second_corners=[(300, 100)],
)
logger.info("by hand: %s", by_hand.polyline())

network.save("branch_corners.vnf")
logger.info("Branch corner examples saved")
