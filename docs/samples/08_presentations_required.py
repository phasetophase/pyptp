"""Presentations are required for all elements.

Networks must be valid both topologically and schematically to open in Gaia/Vision.
Presentations don't affect calculations but are mandatory for file validity.
"""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.color_utils import CL_GRAY
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.load import LoadMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.source import SourceMV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkMV()

# Every network needs at least one sheet
sheet = SheetMV(SheetMV.General(name="Main", color=CL_GRAY))
sheet.register(network)
sheet_guid = sheet.general.guid

# Nodes require NodePresentation
node1 = NodeMV(
    NodeMV.General(name="Node1", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=100)],
)
node1.register(network)

node2 = NodeMV(
    NodeMV.General(name="Node2", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=100)],
)
node2.register(network)

# Branches require BranchPresentation
link = LinkMV(
    LinkMV.General(node1=node1.general.guid, node2=node2.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(100, 100), (200, 100)],
            second_corners=[(300, 100)],
        )
    ],
)
link.register(network)

# Elements require ElementPresentation
source = SourceMV(
    SourceMV.General(node=node1.general.guid, sk2nom=100.0),
    presentations=[ElementPresentation(sheet=sheet_guid, x=100, y=50)],
)
source.register(network)

load = LoadMV(
    LoadMV.General(node=node2.general.guid, P=50.0, Q=25.0),
    presentations=[ElementPresentation(sheet=sheet_guid, x=300, y=50)],
)
load.register(network)

network.save("with_presentations.vnf")
logger.info("Valid network saved")
