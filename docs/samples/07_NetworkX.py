"""NetworkX Usage Examples.

Shows different ways to generate NetworkX graphs from a network
"""

from ipysigma import Sigma

from pyptp.graph.networkx_converter import NetworkxConverter
from pyptp.IO.importers.vnf_importer import VnfImporter

importer = VnfImporter()

network = importer.import_vnf("PATH_TO_VNF")
graph = NetworkxConverter.graph_mv(network)
sigma = Sigma(graph, start_layout=True, height=1080, node_label="type", node_color="type")
sigma.to_html("PATH_TO_GRAPH")
