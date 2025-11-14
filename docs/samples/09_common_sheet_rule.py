"""Branch presentations must reference a common sheet between both nodes.

When nodes appear on multiple sheets, the branch connecting them must use
a sheet where both nodes are visible.
"""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.color_utils import CL_BLUE, CL_GRAY, CL_GREEN
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkMV()

# Create three sheets
sheet_a = SheetMV(SheetMV.General(name="Sheet A", color=CL_GRAY))
sheet_a.register(network)
sheet_a_guid = sheet_a.general.guid

sheet_b = SheetMV(SheetMV.General(name="Sheet B", color=CL_BLUE))
sheet_b.register(network)
sheet_b_guid = sheet_b.general.guid

sheet_c = SheetMV(SheetMV.General(name="Sheet C", color=CL_GREEN))
sheet_c.register(network)
sheet_c_guid = sheet_c.general.guid

# Node1 appears on sheets A and B
node1 = NodeMV(
    NodeMV.General(name="Node1", unom=10.0),
    presentations=[
        NodePresentation(sheet=sheet_a_guid, x=400, y=100),
        NodePresentation(sheet=sheet_b_guid, x=100, y=100),
    ],
)
node1.register(network)

# Node2 appears on sheets B and C
node2 = NodeMV(
    NodeMV.General(name="Node2", unom=10.0),
    presentations=[
        NodePresentation(sheet=sheet_b_guid, x=400, y=100),
        NodePresentation(sheet=sheet_c_guid, x=100, y=100),
    ],
)
node2.register(network)

# Branch must use Sheet B - the only common sheet
link = LinkMV(
    LinkMV.General(node1=node1.general.guid, node2=node2.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_b_guid,
            first_corners=[(100, 100), (250, 100)],
            second_corners=[(400, 100)],
        )
    ],
)
link.register(network)

network.save("common_sheet.vnf")
logger.info("Network with common sheet rule saved")
