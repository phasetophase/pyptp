"""NetworkX Usage Examples.

Demonstrates how to convert electrical networks to NetworkX graphs
for analysis and visualization.
"""

from pyptp.graph.networkx_converter import NetworkxConverter
from pyptp.IO.importers.gnf_importer import GnfImporter
from pyptp.IO.importers.vnf_importer import VnfImporter

# Convert MV network to NetworkX graph
vnf_importer = VnfImporter()
mv_network = vnf_importer.import_vnf("PATH_TO_VNF")
mv_graph = NetworkxConverter.graph_mv(mv_network)

# Convert LV network to NetworkX graph
gnf_importer = GnfImporter()
lv_network = gnf_importer.import_gnf("PATH_TO_GNF")
lv_graph = NetworkxConverter.graph_lv(lv_network)

# Now you can use NetworkX for analysis
print(f"MV Network: {mv_graph.number_of_nodes()} nodes, {mv_graph.number_of_edges()} edges")
print(f"LV Network: {lv_graph.number_of_nodes()} nodes, {lv_graph.number_of_edges()} edges")

# Example: Use NetworkX algorithms
import networkx as nx

# Check if network is connected
is_connected = nx.is_connected(mv_graph)
print(f"Network is connected: {is_connected}")

# Find shortest path between nodes
# path = nx.shortest_path(mv_graph, source_node, target_node)

# Export to various NetworkX formats
# nx.write_gexf(mv_graph, "network.gexf")
# nx.write_graphml(mv_graph, "network.graphml")
