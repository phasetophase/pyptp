"""Clamp branch corners to line symbol nodes.

Line symbols (VERTICAL_LINE, HORIZONTAL_LINE) have extent based on their size.
clamp_point() finds the nearest point on the line segment, not just the center.
"""

from pyptp import NetworkLV, configure_logging
from pyptp.elements.enums import NodePresentationSymbol
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkLV()

sheet = SheetLV(SheetLV.General(name="Line Symbol Examples"))
sheet.register(network)
sheet_guid = sheet.general.guid

# Example 1: Vertical line node
# Busbar at (100, 300) with size=3 → line from (100, 270) to (100, 330)
busbar = NodeLV(
    NodeLV.General(name="VerticalBusbar"),
    presentations=[
        NodePresentation(
            sheet=sheet_guid,
            x=100,
            y=300,
            symbol=NodePresentationSymbol.VERTICAL_LINE,
            size=3,
        )
    ],
)
busbar.register(network)

load = NodeLV(
    NodeLV.General(name="VerticalLoad"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=350)],
)
load.register(network)

busbar_pres = busbar.presentations[0]
load_pres = load.presentations[0]

# Point (100, 340) is below the line, clamps to bottom edge (100, 330)
feeder = LinkLV(
    LinkLV.General(name="VerticalFeeder", node1=busbar.general.guid, node2=load.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[busbar_pres.clamp_point((100, 340)), (150, 340), (200, 350)],
            second_corners=[load_pres.clamp_point((300, 350))],
        )
    ],
)
feeder.register(network)

# Example 2: Horizontal line node
# Busbar at (100, 500) with size=2 → line from (80, 500) to (120, 500)
busbar = NodeLV(
    NodeLV.General(name="HorizontalBusbar"),
    presentations=[
        NodePresentation(
            sheet=sheet_guid,
            x=100,
            y=500,
            symbol=NodePresentationSymbol.HORIZONTAL_LINE,
            size=2,
        )
    ],
)
busbar.register(network)

load = NodeLV(
    NodeLV.General(name="HorizontalLoad"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=500)],
)
load.register(network)

busbar_pres = busbar.presentations[0]
load_pres = load.presentations[0]

# Point (150, 500) is beyond the line, clamps to right edge (120, 500)
feeder = LinkLV(
    LinkLV.General(name="HorizontalFeeder", node1=busbar.general.guid, node2=load.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[busbar_pres.clamp_point((150, 500)), (200, 500)],
            second_corners=[load_pres.clamp_point((300, 500))],
        )
    ],
)
feeder.register(network)

network.save("clamp_line_symbols_example.gnf")
logger.info("Saved clamp_line_symbols_example.gnf")
