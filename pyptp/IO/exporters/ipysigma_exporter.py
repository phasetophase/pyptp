"""Network to ipysigma (force directed graph) exporter."""

from ipysigma import Sigma
from networkx import Graph

from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV


class IPySigmaExporter:
    """Sigma exporter."""

    @classmethod
    def export_ls(cls, network: NetworkLV, output_path: str) -> None:
        """Export a LV network to a ipysigma network (html)."""
        graph = Graph()
        for node in network.nodes.values():
            graph.add_node(node.general.guid, color="red")

        for home in network.homes.values():
            graph.add_node(home.general.guid, color="blue")
            graph.add_edge(home.general.guid, home.general.node)

        for cable in network.cables.values():
            graph.add_edge(
                cable.general.node1,
                cable.general.node2,
                color="green",
                edge_size=cable.cable_part.length,
            )

        for transformer in network.transformers.values():
            graph.add_edge(transformer.general.node1, transformer.general.node2, color="orange")

        sigma = Sigma(graph, start_layout=True, height=1080)

        sigma.to_html(output_path)

    @classmethod
    def export_ms(cls, network: NetworkMV, output_path: str) -> None:
        """Export a MV network to a ipysigma network (html)."""
        graph = Graph()
        for node in network.nodes.values():
            graph.add_node(node.general.guid, color="red")

        for cable in network.cables.values():
            graph.add_edge(
                cable.general.node1,
                cable.general.node2,
                color="green",
                edge_size=sum(part.length for part in cable.cable_parts),
            )

        sigma = Sigma(graph, start_layout=True, height=1080)

        sigma.to_html(output_path)
