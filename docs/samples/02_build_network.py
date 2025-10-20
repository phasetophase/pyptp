"""Build a simple network from scratch."""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.line import LineMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.source import SourceMV
from pyptp.ptp_log import logger

# Enable logging
configure_logging(level="INFO")

# Create network
network = NetworkMV()

# Create sheet
sheet = SheetMV(SheetMV.General(name="Main"))
sheet.register(network)
sheet_guid: Guid = sheet.general.guid

# Create source node
source_node = NodeMV(
    NodeMV.General(name="Source", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=100)],
)
source_node.register(network)

# Create source
source = SourceMV(
    SourceMV.General(node=source_node.general.guid, sk2nom=100.0),
    presentations=[ElementPresentation(sheet=sheet_guid, x=100, y=100)],
)
source.register(network)

# Create load node
load_node = NodeMV(
    NodeMV.General(name="Load", unom=10.0),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=100)],
)
load_node.register(network)

# Connect with line
line = LineMV(
    LineMV.General(node1=source_node.general.guid, node2=load_node.general.guid),
    presentations=[],
)
line.register(network)

# Save
network.save("simple_network.vnf")
logger.info("Network created with {} nodes and {} line", len(network.nodes), len(network.lines))
