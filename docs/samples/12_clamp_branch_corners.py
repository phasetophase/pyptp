"""Attach a branch to nodes along a route whose points are not exact.

BranchPresentation.between() places both ends on the node symbols, so the
branch connects even when the route's own end points are a few pixels off.
NodePresentation.clamp_point() snaps a single point onto a node symbol.
"""

from pyptp import NetworkLV, configure_logging
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkLV()

sheet = network.add(SheetLV(SheetLV.General(name="Clamp Example")))
sheet_guid = sheet.general.guid

substation = network.add(
    NodeLV(
        NodeLV.General(name="Substation"),
        presentations=[NodePresentation(sheet=sheet_guid, x=100, y=100)],
    )
)
load = network.add(
    NodeLV(
        NodeLV.General(name="Load"),
        presentations=[NodePresentation(sheet=sheet_guid, x=300, y=100)],
    )
)

# ends a few pixels off the nodes
imported_route = [(105, 98), (200, 100), (295, 102)]

via = imported_route[1:-1]

feeder = network.add(
    LinkLV(
        LinkLV.General(name="Feeder", node1=substation.general.guid, node2=load.general.guid),
        presentations=[BranchPresentation.between(substation, load, sheet_guid, via=via)],
    )
)

logger.info("route: %s", feeder.presentations[0].polyline())

# Clamp a single point
logger.info("clamped: %s", substation.presentations[0].clamp_point((105, 98)))

network.save("clamp_corners_example.gnf")
logger.info("Saved clamp_corners_example.gnf")
