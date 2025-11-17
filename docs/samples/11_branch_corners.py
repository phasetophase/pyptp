"""Understanding branch corner coordinates and polyline construction.

CRITICAL: FirstCorners start FROM Node1 traveling outward.
          SecondCorners start FROM Node2 traveling outward.
          A connection line joins the last point of each.

Common mistake: SecondCorners must start at Node2, not end at it.
"""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.color_utils import CL_GRAY
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkMV()

sheet = SheetMV(SheetMV.General(name="Corner Examples", color=CL_GRAY))
sheet.register(network)
sheet_guid = sheet.general.guid

# Example 1: Simple straight line
node1 = NodeMV(
    NodeMV.General(name="A", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=100)],
)
node1.register(network)

node2 = NodeMV(
    NodeMV.General(name="B", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=100)],
)
node2.register(network)

# FirstCorners: from Node1 at (100,100) going right to (200,100)
# SecondCorners: from Node2 at (300,100) - single point on the node
# Connection line drawn between (200,100) and (300,100)
link1 = LinkMV(
    LinkMV.General(node1=node1.general.guid, node2=node2.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(100, 100), (200, 100)],
            second_corners=[(300, 100)],
        )
    ],
)
link1.register(network)

# Example 2: Right-angle bend
node3 = NodeMV(
    NodeMV.General(name="C", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=200)],
)
node3.register(network)

node4 = NodeMV(
    NodeMV.General(name="D", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=300)],
)
node4.register(network)

# Polyline path: (100,200) -> (100,250) -> connection -> (300,250) -> (300,300)
# FirstCorners from C: down to (100,250)
# SecondCorners from D: up to (300,250)
# Connection drawn between (100,250) and (300,250)
link2 = LinkMV(
    LinkMV.General(node1=node3.general.guid, node2=node4.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(100, 200), (100, 250)],
            second_corners=[(300, 300), (300, 250)],
        )
    ],
)
link2.register(network)

# Example 3: Complex zig-zag path with diagonals
node5 = NodeMV(
    NodeMV.General(name="E", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=400)],
)
node5.register(network)

node6 = NodeMV(
    NodeMV.General(name="F", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=450, y=450)],
)
node6.register(network)

# Zig-zag with diagonals from both ends meeting in middle
# From E (Node1): right, diagonal up, right, diagonal down to (300,400)
# From F (Node2): diagonal left-up, left, more left to (350,400)
# Connection line between (300,400) and (350,400)
link3 = LinkMV(
    LinkMV.General(node1=node5.general.guid, node2=node6.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(100, 400), (150, 400), (200, 350), (250, 350), (300, 400)],
            second_corners=[(450, 450), (400, 420), (375, 410), (350, 400)],
        )
    ],
)
link3.register(network)

# Example 4: Minimal specification
node7 = NodeMV(
    NodeMV.General(name="G", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=550)],
)
node7.register(network)

node8 = NodeMV(
    NodeMV.General(name="H", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=550)],
)
node8.register(network)

# Minimal: just the starting points on each node
# FirstCorners: start on Node7, SecondCorners: start on Node8
# Direct connection line drawn between them
link4 = LinkMV(
    LinkMV.General(node1=node7.general.guid, node2=node8.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(100, 550)],
            second_corners=[(300, 550)],
        )
    ],
)
link4.register(network)

network.save("branch_corners.vnf")
logger.info("Branch corner examples saved")
