"""Network to NetworkX (force directed graph) exporter."""

from networkx import Graph

from pyptp.elements.element_utils import NIL_GUID, SIDE_NODE1, SIDE_NODE2
from pyptp.elements.lv.async_generator import AsynchronousGeneratorLV
from pyptp.elements.lv.async_motor import AsynchronousMotorLV
from pyptp.elements.lv.battery import BatteryLV
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV
from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.earthing_transformer import EarthingTransformerLV
from pyptp.elements.lv.fuse import FuseLV
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.load import LoadLV
from pyptp.elements.lv.load_switch import LoadSwitchLV
from pyptp.elements.lv.measure_field import MeasureFieldLV
from pyptp.elements.lv.pv import PVLV
from pyptp.elements.lv.reactance_coil import ReactanceCoilLV
from pyptp.elements.lv.shunt_capacitor import ShuntCapacitorLV
from pyptp.elements.lv.source import SourceLV
from pyptp.elements.lv.special_transformer import SpecialTransformerLV
from pyptp.elements.lv.syn_generator import SynchronousGeneratorLV
from pyptp.elements.lv.transformer import TransformerLV
from pyptp.elements.mv.async_generator import AsynchronousGeneratorMV
from pyptp.elements.mv.async_motor import AsynchronousMotorMV
from pyptp.elements.mv.battery import BatteryMV
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.circuit_breaker import CircuitBreakerMV
from pyptp.elements.mv.earthing_transformer import EarthingTransformerMV
from pyptp.elements.mv.fuse import FuseMV
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.load import LoadMV
from pyptp.elements.mv.load_switch import LoadSwitchMV
from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.elements.mv.pv import PVMV
from pyptp.elements.mv.reactance_coil import ReactanceCoilMV
from pyptp.elements.mv.shunt_capacitor import ShuntCapacitorMV
from pyptp.elements.mv.shunt_coil import ShuntCoilMV
from pyptp.elements.mv.source import SourceMV
from pyptp.elements.mv.special_transformer import SpecialTransformerMV
from pyptp.elements.mv.synchronous_generator import SynchronousGeneratorMV
from pyptp.elements.mv.synchronous_motor import SynchronousMotorMV
from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV
from pyptp.elements.mv.transformer import TransformerMV
from pyptp.elements.mv.transformer_load import TransformerLoadMV
from pyptp.elements.mv.windturbine import WindTurbineMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV


class NetworkxConverter:
    """Sigma exporter."""

    @classmethod
    def __inject_branch_lv(
        cls,
        graph: Graph,
        branch: (CableLV | LinkLV | TransformerLV | SpecialTransformerLV | ReactanceCoilLV),
    ) -> None:
        graph.add_node(str(branch.general.guid), type=type(branch).__name__)
        graph.add_edge(str(branch.general.node1), str(branch.general.guid))
        graph.add_edge(str(branch.general.node2), str(branch.general.guid))

    @classmethod
    def __inject_branch_mv(
        cls,
        graph: Graph,
        branch: (CableMV | LinkMV | TransformerMV | SpecialTransformerMV | ReactanceCoilMV | ThreewindingTransformerMV),
    ) -> None:
        if type(branch) is ThreewindingTransformerMV:
            transformer: ThreewindingTransformerMV = branch
            if (
                transformer.general.switch_state1 == 0
                or transformer.general.switch_state2 == 0
                or transformer.general.switch_state3 == 0
            ):
                return
            graph.add_node(str(branch.general.guid), type=type(branch).__name__)
            graph.add_edge(str(transformer.general.node1), str(transformer.general.guid))
            graph.add_edge(str(transformer.general.node2), str(transformer.general.guid))
            graph.add_edge(str(transformer.general.node3), str(transformer.general.guid))
        else:
            if branch.general.switch_state1 == 0 or branch.general.switch_state2 == 0:
                return
            graph.add_node(str(branch.general.guid), type=type(branch).__name__)
            graph.add_edge(str(branch.general.node1), str(branch.general.guid))
            graph.add_edge(str(branch.general.node2), str(branch.general.guid))

    @classmethod
    def __inject_element(
        cls,
        graph: Graph,
        element: (
            ConnectionLV
            | SourceLV
            | SynchronousGeneratorLV
            | AsynchronousGeneratorLV
            | AsynchronousMotorLV
            | EarthingTransformerLV
            | ShuntCapacitorLV
            | BatteryLV
            | LoadLV
            | PVLV
            | LoadMV
            | EarthingTransformerMV
            | AsynchronousGeneratorMV
            | AsynchronousMotorMV
            | BatteryMV
            | SourceMV
            | ShuntCapacitorMV
            | SynchronousGeneratorMV
            | SynchronousMotorMV
            | PVMV
            | TransformerLoadMV
            | WindTurbineMV
            | ShuntCoilMV
        ),
    ) -> None:
        graph.add_node(str(element.general.guid), type=type(element).__name__)
        graph.add_edge(str(element.general.guid), str(element.general.node))

    @classmethod
    def __inject_secundair(
        cls,
        graph: Graph,
        network: NetworkLV | NetworkMV,
        secundair: (
            FuseLV
            | LoadSwitchLV
            | CircuitBreakerLV
            | MeasureFieldLV
            | FuseMV
            | LoadSwitchMV
            | CircuitBreakerMV
            | MeasureFieldMV
        ),
    ) -> None:
        u = str(secundair.general.guid)
        in_guid = secundair.general.in_object
        if in_guid == NIL_GUID:
            return

        branch = None
        if in_guid in network.cables:
            branch = network.cables[in_guid]
        elif in_guid in network.links:
            branch = network.links[in_guid]
        elif in_guid in network.transformers:
            branch = network.transformers[in_guid]
        elif in_guid in network.special_transformers:
            branch = network.special_transformers[in_guid]
        elif in_guid in network.reactance_coils:
            branch = network.reactance_coils[in_guid]
        else:
            return

        side = secundair.general.side
        if side == SIDE_NODE1:
            v = str(branch.general.node1)
        elif side == SIDE_NODE2:
            v = str(branch.general.node2)
        else:
            return

        graph.add_node(u, type=type(secundair).__name__)

        through_neighbor = None

        if graph.has_edge(v, str(in_guid)):
            through_neighbor = str(in_guid)
        else:
            for n in graph.neighbors(v):
                if n == in_guid:
                    through_neighbor = n
                    break

        if through_neighbor is None:
            return

        if graph.has_edge(v, through_neighbor):
            graph.remove_edge(v, through_neighbor)
        graph.add_edge(v, u)
        graph.add_edge(u, through_neighbor)

    @classmethod
    def graph_lv(cls, network: NetworkLV) -> Graph:
        """Export a Low Voltage (LV) network to a NetworkX Graph.

        In the resulting graph:
        - Nodes represent **nodes**, **cables**, and **elements**.
        - Edges represent relationships between Nodes
        """
        graph = Graph()
        for node in network.nodes.values():
            graph.add_node(str(node.general.guid), type=type(node).__name__)

        for cable in network.cables.values():
            cls.__inject_branch_lv(graph, cable)
        for link in network.links.values():
            cls.__inject_branch_lv(graph, link)
        for tranformer in network.transformers.values():
            cls.__inject_branch_lv(graph, tranformer)
        for special_transformer in network.special_transformers.values():
            cls.__inject_branch_lv(graph, special_transformer)
        for reactance_coils in network.reactance_coils.values():
            cls.__inject_branch_lv(graph, reactance_coils)

        for home in network.homes.values():
            cls.__inject_element(graph, home)
        for source in network.sources.values():
            cls.__inject_element(graph, source)
        for syn_generators in network.syn_generators.values():
            cls.__inject_element(graph, syn_generators)
        for async_generators in network.async_generators.values():
            cls.__inject_element(graph, async_generators)
        for async_motors in network.async_motors.values():
            cls.__inject_element(graph, async_motors)
        for earthing_transformers in network.earthing_transformers.values():
            cls.__inject_element(graph, earthing_transformers)
        for shunt_capacitors in network.shunt_capacitors.values():
            cls.__inject_element(graph, shunt_capacitors)
        for batteries in network.batteries.values():
            cls.__inject_element(graph, batteries)
        for loads in network.loads.values():
            cls.__inject_element(graph, loads)
        for pvs in network.pvs.values():
            cls.__inject_element(graph, pvs)

        for fuse in network.fuses.values():
            cls.__inject_secundair(graph, network, fuse)
        for load_switch in network.load_switches.values():
            cls.__inject_secundair(graph, network, load_switch)
        for circuit_breaker in network.circuit_breakers.values():
            cls.__inject_secundair(graph, network, circuit_breaker)
        for measure_field in network.measure_fields.values():
            cls.__inject_secundair(graph, network, measure_field)

        return graph

    @classmethod
    def __add_mv_branches(cls, graph: Graph, network: NetworkMV) -> None:
        """Add all branch elements to the graph."""
        for cable in network.cables.values():
            cls.__inject_branch_mv(graph, cable)
        for link in network.links.values():
            cls.__inject_branch_mv(graph, link)
        for tranformer in network.transformers.values():
            cls.__inject_branch_mv(graph, tranformer)
        for special_transformer in network.special_transformers.values():
            cls.__inject_branch_mv(graph, special_transformer)
        for reactance_coils in network.reactance_coils.values():
            cls.__inject_branch_mv(graph, reactance_coils)
        for threewinding_transformer in network.threewinding_transformers.values():
            cls.__inject_branch_mv(graph, threewinding_transformer)

    @classmethod
    def __add_mv_elements(cls, graph: Graph, network: NetworkMV) -> None:
        """Add all node-connected elements to the graph."""
        for load in network.loads.values():
            cls.__inject_element(graph, load)
        for earthing_transformer in network.earthing_transformers.values():
            cls.__inject_element(graph, earthing_transformer)
        for asynchronous_generator in network.asynchronous_generators.values():
            cls.__inject_element(graph, asynchronous_generator)
        for asynchronous_motor in network.asynchronous_motors.values():
            cls.__inject_element(graph, asynchronous_motor)
        for synchronous_generator in network.synchronous_generators.values():
            cls.__inject_element(graph, synchronous_generator)
        for synchronous_motor in network.synchronous_motors.values():
            cls.__inject_element(graph, synchronous_motor)
        for battery in network.batteries.values():
            cls.__inject_element(graph, battery)
        for pv in network.pvs.values():
            cls.__inject_element(graph, pv)
        for source in network.sources.values():
            cls.__inject_element(graph, source)
        for windturbine in network.windturbines.values():
            cls.__inject_element(graph, windturbine)
        for shunt_coil in network.shunt_coils.values():
            cls.__inject_element(graph, shunt_coil)
        for shunt_capacitor in network.shunt_capacitors.values():
            cls.__inject_element(graph, shunt_capacitor)
        for transformer_load in network.transformer_loads.values():
            cls.__inject_element(graph, transformer_load)

    @classmethod
    def __add_mv_secundair(cls, graph: Graph, network: NetworkMV) -> None:
        """Add all secundair elements to the graph."""
        for fuse in network.fuses.values():
            cls.__inject_secundair(graph, network, fuse)
        for load_switch in network.load_switches.values():
            cls.__inject_secundair(graph, network, load_switch)
        for circuit_breaker in network.circuit_breakers.values():
            cls.__inject_secundair(graph, network, circuit_breaker)
        for measure_field in network.measure_fields.values():
            cls.__inject_secundair(graph, network, measure_field)

    @classmethod
    def graph_mv(cls, network: NetworkMV) -> Graph:
        """Export a Medium Voltage (MV) network to a NetworkX Graph.

        In the resulting graph:
        - Nodes represent **nodes**, **cables**, and **elements**.
        - Edges represent relationships between Nodes
        """
        graph = Graph()
        for node in network.nodes.values():
            graph.add_node(str(node.general.guid), type=type(node).__name__)

        cls.__add_mv_branches(graph, network)
        cls.__add_mv_elements(graph, network)
        cls.__add_mv_secundair(graph, network)

        return graph
