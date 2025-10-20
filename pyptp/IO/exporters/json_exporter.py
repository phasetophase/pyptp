"""Exports Network to JSON."""

import json
from pathlib import Path

from pyptp.network_lv import NetworkLV


class JsonExporter:
    """Network to JSON Exporter."""

    @classmethod
    def export(cls, network: NetworkLV, output_path: str) -> None:
        """Will take a network and output a JSON file to output_path."""
        out_json = []

        config = {
            "NodeLS": ["GUID"],
            "CableLS": ["GUID", "Node1", "Node2", "CableType"],
            "FuseLS": ["InObject", "FuseType"],
        }

        nodes = []
        for node in network.nodes.values():
            node_object = node.general.to_dict()
            node_object = {k: node_object[k] for k in config["NodeLS"] if k in node_object}
            nodes.append(node_object)
        out_json.append({"Nodes": nodes})

        cables = []
        for cable in network.cables.values():
            cable_object = cable.general.to_dict()
            cable_object = {k: cable_object[k] for k in config["CableLS"] if k in cable_object}
            cable_object["CableType"] = cable.cable_type.short_name if cable.cable_type else ""
            cables.append(cable_object)
        out_json.append({"Cables": cables})

        fuses = []
        for fuse in network.fuses.values():
            fuse_object = fuse.general.to_dict()
            fuse_object = {k: fuse_object[k] for k in config["FuseLS"] if k in fuse_object}
            fuses.append(fuse_object)
        out_json.append({"Fuses": fuses})

        path = Path(output_path)
        with path.open("w") as f:
            json.dump(out_json, f, default=lambda o: o.__dict__, indent=4)
