"""Build a simple network from scratch."""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.color_utils import CL_GRAY
from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.load import LoadMV
from pyptp.elements.mv.node import NodeMV   
from pyptp.elements.mv.presentations import BranchPresentation, ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.source import SourceMV
from pyptp.ptp_log import logger

# Enable logging
configure_logging(level="INFO")

# Create network
network = NetworkMV()

# Create sheet
sheet = SheetMV(SheetMV.General(name="Main", color=CL_GRAY))
sheet.register(network)
sheet_guid: Guid = sheet.general.guid

# Create source node
source_node = NodeMV(
    NodeMV.General(name="Source", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=150, y=250)],
)
source_node.register(network)

# Create source
source = SourceMV(
    SourceMV.General(node=source_node.general.guid, sk2nom=100.0),
    presentations=[ElementPresentation(sheet=sheet_guid, x=150, y=100)],
)
source.general.sk2nom=900.0
source.register(network)

# Create load node
load_node = NodeMV(
    NodeMV.General(name="Load", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=450, y=250)],
)
load_node.register(network)

# Connect with line
link = LinkMV(
    LinkMV.General(node1=source_node.general.guid, node2=load_node.general.guid),
    presentations=[BranchPresentation(sheet=sheet_guid, first_corners=[(150, 250), (300, 250)], second_corners=[(450, 250)])],
)
link.general.switch_state1 = 1
link.general.switch_state2 = 1
link.register(network)

load = LoadMV(
    LoadMV.General(node=load_node.general.guid, P=100.0, Q=50.0),
    presentations=[ElementPresentation(sheet=sheet_guid, x=450, y=350)],
)
load.register(network)

# Save
network.save("simple_network.vnf")
logger.info("Network created with {} nodes and {} line", len(network.nodes), len(network.lines))
