"""Nodes can appear on multiple sheets.

This is useful for creating overview diagrams or splitting large networks
across multiple sheets while maintaining connections.
"""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.color_utils import CL_BLUE, CL_GRAY, CL_GREEN
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.load import LoadMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.source import SourceMV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkMV()

# Create sheets for different network sections
overview_sheet = SheetMV(SheetMV.General(name="Overview", color=CL_GRAY))
overview_sheet.register(network)
overview_guid = overview_sheet.general.guid

feeder1_sheet = SheetMV(SheetMV.General(name="Feeder 1 Detail", color=CL_BLUE))
feeder1_sheet.register(network)
feeder1_guid = feeder1_sheet.general.guid

feeder2_sheet = SheetMV(SheetMV.General(name="Feeder 2 Detail", color=CL_GREEN))
feeder2_sheet.register(network)
feeder2_guid = feeder2_sheet.general.guid

# Main busbar appears on all sheets
busbar = NodeMV(
    NodeMV.General(name="Main_Busbar", unom=10.0),
    presentations=[
        NodePresentation(sheet=overview_guid, x=200, y=200),
        NodePresentation(sheet=feeder1_guid, x=100, y=150),
        NodePresentation(sheet=feeder2_guid, x=100, y=150),
    ],
)
busbar.register(network)

# Source only on overview
source_node = NodeMV(
    NodeMV.General(name="Source", unom=10.0),
    presentations=[NodePresentation(sheet=overview_guid, x=200, y=100)],
)
source_node.register(network)

source = SourceMV(
    SourceMV.General(node=source_node.general.guid, sk2nom=100.0),
    presentations=[ElementPresentation(sheet=overview_guid, x=200, y=50)],
)
source.register(network)

# Feeder 1 nodes on overview and feeder1 detail
feeder1_load_node = NodeMV(
    NodeMV.General(name="F1_Load", unom=10.0),
    presentations=[
        NodePresentation(sheet=overview_guid, x=350, y=200),
        NodePresentation(sheet=feeder1_guid, x=400, y=150),
    ],
)
feeder1_load_node.register(network)

# Feeder 2 nodes on overview and feeder2 detail
feeder2_load_node = NodeMV(
    NodeMV.General(name="F2_Load", unom=10.0),
    presentations=[
        NodePresentation(sheet=overview_guid, x=50, y=200),
        NodePresentation(sheet=feeder2_guid, x=400, y=150),
    ],
)
feeder2_load_node.register(network)

# Connections use appropriate common sheets
link_source = LinkMV(
    LinkMV.General(node1=source_node.general.guid, node2=busbar.general.guid),
    presentations=[
        BranchPresentation(
            sheet=overview_guid,
            first_corners=[(200, 100), (200, 150)],
            second_corners=[(200, 200)],
        )
    ],
)
link_source.register(network)

link_f1 = LinkMV(
    LinkMV.General(node1=busbar.general.guid, node2=feeder1_load_node.general.guid),
    presentations=[
        BranchPresentation(
            sheet=overview_guid,
            first_corners=[(200, 200), (275, 200)],
            second_corners=[(350, 200)],
        ),
        BranchPresentation(
            sheet=feeder1_guid,
            first_corners=[(100, 150), (250, 150)],
            second_corners=[(400, 150)],
        ),
    ],
)
link_f1.register(network)

link_f2 = LinkMV(
    LinkMV.General(node1=busbar.general.guid, node2=feeder2_load_node.general.guid),
    presentations=[
        BranchPresentation(
            sheet=overview_guid,
            first_corners=[(200, 200), (125, 200)],
            second_corners=[(50, 200)],
        ),
        BranchPresentation(
            sheet=feeder2_guid,
            first_corners=[(100, 150), (250, 150)],
            second_corners=[(400, 150)],
        ),
    ],
)
link_f2.register(network)

load1 = LoadMV(
    LoadMV.General(node=feeder1_load_node.general.guid, P=30.0, Q=15.0),
    presentations=[
        ElementPresentation(sheet=overview_guid, x=350, y=250),
        ElementPresentation(sheet=feeder1_guid, x=400, y=200),
    ],
)
load1.register(network)

load2 = LoadMV(
    LoadMV.General(node=feeder2_load_node.general.guid, P=40.0, Q=20.0),
    presentations=[
        ElementPresentation(sheet=overview_guid, x=50, y=250),
        ElementPresentation(sheet=feeder2_guid, x=400, y=200),
    ],
)
load2.register(network)

network.save("multi_sheet.vnf")
logger.info("Multi-sheet network saved")
