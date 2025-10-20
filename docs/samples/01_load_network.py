"""Load and inspect existing network files."""

from pyptp import NetworkLV, NetworkMV, configure_logging
from pyptp.ptp_log import logger

# Enable logging to see output
configure_logging(level="INFO")

# Load low-voltage network (Gaia/GNF format)
lv_network = NetworkLV.from_file("path/to/network.gnf")
logger.info("LV Network: {} nodes, {} cables", len(lv_network.nodes), len(lv_network.cables))

# Load medium-voltage network (Vision/VNF format)
mv_network = NetworkMV.from_file("path/to/network.vnf")
logger.info("MV Network: {} nodes, {} lines", len(mv_network.nodes), len(mv_network.lines))

# Access network elements
for node in list(mv_network.nodes.values())[:5]:
    logger.info("Node: {} at {}kV", node.general.name, node.general.unom)

# Save modified network
lv_network.save("output.gnf")
mv_network.save("output.vnf")
