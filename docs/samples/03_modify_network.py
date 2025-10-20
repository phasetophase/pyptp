"""Modify existing network elements."""

from uuid import UUID

from pyptp import NetworkMV, configure_logging
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Note
from pyptp.ptp_log import logger

# Enable logging
configure_logging(level="INFO")

# Load network
network = NetworkMV.from_file("network.vnf")

# Find and modify a node by name
node_guid_str = network.get_node_guid_by_name("Substation_01")
node_guid = Guid(UUID(node_guid_str))
node = network.nodes[node_guid]
node.general.unom = 11.0  # Change voltage
logger.info("Updated {} voltage to {}kV", node.general.name, node.general.unom)

# Modify all loads
for load in network.loads.values():
    load.general.P *= 1.1  # Increase by 10%
    load.general.Q *= 1.1
logger.info("Scaled {} loads by 10%", len(network.loads))

# Add note to specific element
line = next(iter(network.lines.values()))
line.notes.append(Note(text="Verified 2025-01"))

# Delete element
del network.sources[next(iter(network.sources.keys()))]

# Save modified network
network.save("network_modified.vnf")
logger.info("Network modifications saved")
