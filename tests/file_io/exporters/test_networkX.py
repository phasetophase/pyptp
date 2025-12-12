"""Unit tests for NetworkxConverter for LV and MV networks."""

from __future__ import annotations

import unittest
from networkx import Graph
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pathlib import Path
from pyptp.graph.networkx_converter import NetworkxConverter


def graph_as_text(graph: Graph, filepath=None) -> str:
    lines = []

    lines.append("NODES:")
    for node in sorted(graph.nodes()):
        attrs = graph.nodes[node]
        attr_str = ", ".join(f"{k}={v}" for k, v in sorted(attrs.items()))
        lines.append(f"  {node} [{attr_str}]")

    lines.append("EDGES:")
    for u, v in sorted(graph.edges()):
        lines.append(f"  {u} -- {v}")

    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return "\n".join(lines)


class TestNetworkxConverterLV(unittest.TestCase):
    """Test NetworkX graph exporter"""

    def setUp(self):
        self.root = Path(__file__).parent.parent.parent
        self.network_lv = NetworkLV.from_file(
            self.root / "input_files" / "AllComponents.gnf"
        )
        self.network_mv = NetworkMV.from_file(
            self.root / "input_files" / "AllComponents.vnf"
        )

        self.truth_lv = open(
            self.root / "output_files" / "network_x" / "truth_lv_graph.txt", "r"
        ).read()

        self.truth_mv = open(
            self.root / "output_files" / "network_x" / "truth_mv_graph.txt", "r"
        ).read()

    def test_networkX_lv_graph(self):
        """NetworkX graph LV test"""
        graph = NetworkxConverter.graph_lv(self.network_lv)
        graph_text = graph_as_text(graph)
        self.assertEqual(graph_text, self.truth_lv)

    def test_networkX_mv_graph(self):
        """NetworkX graph MV test"""
        graph = NetworkxConverter.graph_mv(self.network_mv)
        graph_text = graph_as_text(graph)
        self.assertEqual(graph_text, self.truth_mv)


if __name__ == "__main__":
    unittest.main()
