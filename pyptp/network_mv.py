"""Medium-voltage network model for symmetrical electrical system analysis.

Supports VNF format networks with balanced three-phase modeling,
positive/negative/zero sequence analysis, and traditional power system calculations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.mv.properties import PropertiesMV
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pathlib import Path

    from pyptp.elements.element_utils import Guid
    from pyptp.elements.mv.async_generator import AsynchronousGeneratorMV
    from pyptp.elements.mv.async_motor import AsynchronousMotorMV
    from pyptp.elements.mv.battery import BatteryMV
    from pyptp.elements.mv.cable import CableMV
    from pyptp.elements.mv.calc_case import CalculationCaseMV
    from pyptp.elements.mv.circuit_breaker import CircuitBreakerMV
    from pyptp.elements.mv.comment import CommentMV
    from pyptp.elements.mv.earthing_transformer import EarthingTransformerMV
    from pyptp.elements.mv.frame import FrameMV
    from pyptp.elements.mv.fuse import FuseMV
    from pyptp.elements.mv.growth import GrowthMV
    from pyptp.elements.mv.hyperlink import HyperlinkMV
    from pyptp.elements.mv.indicator import IndicatorMV
    from pyptp.elements.mv.legend import LegendMV
    from pyptp.elements.mv.line import LineMV
    from pyptp.elements.mv.link import LinkMV
    from pyptp.elements.mv.load import LoadMV
    from pyptp.elements.mv.load_behaviour import LoadBehaviourMV
    from pyptp.elements.mv.load_switch import LoadSwitchMV
    from pyptp.elements.mv.measure_field import MeasureFieldMV
    from pyptp.elements.mv.mutual import MutualMV
    from pyptp.elements.mv.node import NodeMV
    from pyptp.elements.mv.profile import ProfileMV
    from pyptp.elements.mv.pv import PVMV
    from pyptp.elements.mv.rails import RailSystemMV
    from pyptp.elements.mv.reactance_coil import ReactanceCoilMV
    from pyptp.elements.mv.scenario import ScenarioMV
    from pyptp.elements.mv.selection import SelectionMV
    from pyptp.elements.mv.sheet import SheetMV
    from pyptp.elements.mv.shunt_capacitor import ShuntCapacitorMV
    from pyptp.elements.mv.shunt_coil import ShuntCoilMV
    from pyptp.elements.mv.source import SourceMV
    from pyptp.elements.mv.special_transformer import SpecialTransformerMV
    from pyptp.elements.mv.synchronous_generator import SynchronousGeneratorMV
    from pyptp.elements.mv.synchronous_motor import SynchronousMotorMV
    from pyptp.elements.mv.text import TextMV
    from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV
    from pyptp.elements.mv.transformer import TransformerMV
    from pyptp.elements.mv.transformer_load import TransformerLoadMV
    from pyptp.elements.mv.variable import VariableMV
    from pyptp.elements.mv.variant import VariantMV
    from pyptp.elements.mv.windturbine import WindTurbineMV


class NetworkModelError(Exception):
    """Custom exception for network model errors."""


class NetworkMV:
    """Medium-voltage network model supporting symmetrical analysis.

    Manages electrical elements in GUID-indexed collections for efficient
    access and supports balanced three-phase power system modeling using
    sequence components.
    """

    def __init__(self) -> None:
        """Initialize network with element collections and optional type definitions.

        Args:
            default_types: Optional type definitions for network elements.

        """
        self.asynchronous_generators: dict[Guid, AsynchronousGeneratorMV] = {}
        self.asynchronous_motors: dict[Guid, AsynchronousMotorMV] = {}
        self.batteries: dict[Guid, BatteryMV] = {}
        self.cables: dict[Guid, CableMV] = {}
        self.calc_cases: list[CalculationCaseMV] = []
        self.circuit_breakers: dict[Guid, CircuitBreakerMV] = {}
        self.comments: list[CommentMV] = []
        self.earthing_transformers: dict[Guid, EarthingTransformerMV] = {}
        self.frames: dict[Guid, FrameMV] = {}
        self.fuses: dict[Guid, FuseMV] = {}
        self.growths: dict[Guid, GrowthMV] = {}
        self.hyperlinks: list[HyperlinkMV] = []
        self.indicators: dict[Guid, IndicatorMV] = {}
        self.legends: dict[Guid, LegendMV] = {}
        self.lines: dict[Guid, LineMV] = {}
        self.links: dict[Guid, LinkMV] = {}
        self.load_behaviours: dict[Guid, LoadBehaviourMV] = {}
        self.load_switches: dict[Guid, LoadSwitchMV] = {}
        self.loads: dict[Guid, LoadMV] = {}
        self.measure_fields: dict[Guid, MeasureFieldMV] = {}
        self.mutuals: dict[str, MutualMV] = {}
        self.nodes: dict[Guid, NodeMV] = {}
        self.profiles: dict[Guid, ProfileMV] = {}
        self.properties: PropertiesMV = PropertiesMV(system=PropertiesMV.System())
        self.pvs: dict[Guid, PVMV] = {}
        self.rail_systems: dict[Guid, RailSystemMV] = {}
        self.reactance_coils: dict[Guid, ReactanceCoilMV] = {}
        self.scenarios: dict[str, ScenarioMV] = {}
        self.selections: list[SelectionMV] = []
        self.sheets: dict[Guid, SheetMV] = {}
        self.shunt_capacitors: dict[Guid, ShuntCapacitorMV] = {}
        self.shunt_coils: dict[Guid, ShuntCoilMV] = {}
        self.sources: dict[Guid, SourceMV] = {}
        self.special_transformers: dict[Guid, SpecialTransformerMV] = {}
        self.synchronous_generators: dict[Guid, SynchronousGeneratorMV] = {}
        self.synchronous_motors: dict[Guid, SynchronousMotorMV] = {}
        self.texts: dict[Guid, TextMV] = {}
        self.threewinding_transformers: dict[Guid, ThreewindingTransformerMV] = {}
        self.transformer_loads: dict[Guid, TransformerLoadMV] = {}
        self.transformers: dict[Guid, TransformerMV] = {}
        self.variables: list[VariableMV] = []
        self.variants: dict[str, VariantMV] = {}
        self.windturbines: dict[Guid, WindTurbineMV] = {}

    def get_sheet_guid_by_name(self, name: str) -> str:
        """Find sheet GUID by name.

        Args:
            name: Sheet name to search for.

        Returns:
            String representation of sheet GUID.

        Raises:
            NetworkModelError: If no sheet with given name exists.

        """
        for sheet in self.sheets.values():
            if sheet.general.name == name:
                return str(sheet.general.guid)
        logger.warning("Sheet with name %s doesn't exist", name)
        msg = f"Sheet with name {name} not found"
        raise NetworkModelError(msg)

    def get_cable_guid_by_name(self, name: str) -> str:
        """Find cable GUID by name.

        Args:
            name: Cable name to search for.

        Returns:
            String representation of cable GUID.

        Raises:
            NetworkModelError: If no cable with given name exists.

        """
        for cable in self.cables.values():
            if cable.general.name == name:
                return str(cable.general.guid)
        logger.warning("Cable with name %s doesn't exist", name)
        msg = f"Cable with name {name} not found"
        raise NetworkModelError(msg)

    def get_node_guid_by_name(self, name: str) -> str:
        """Find node GUID by name.

        Args:
            name: Node name to search for.

        Returns:
            String representation of node GUID.

        Raises:
            NetworkModelError: If no node with given name exists.

        """
        for node in self.nodes.values():
            if node.general.name == name:
                return str(node.general.guid)
        logger.warning("Node with name %s doesn't exist", name)
        msg = f"Node with name {name} not found"
        raise NetworkModelError(msg)

    @classmethod
    def from_file(cls, path: str | Path) -> NetworkMV:
        """Create MV network from VNF file.

        Args:
            path: Path to VNF file for import.

        Returns:
            Populated NetworkMV instance with all components from file.

        Raises:
            RuntimeError: If file migration fails or content is invalid.
            FileNotFoundError: If specified file does not exist.

        Example:
            >>> network = NetworkMV.from_file("input.vnf")
            >>> print(len(network.nodes))

        """
        from pyptp.IO.importers.vnf_importer import VnfImporter

        return VnfImporter().import_vnf(path)

    def save(self, path: str | Path) -> None:
        """Save network to VNF file.

        Args:
            path: Target file path for VNF output.

        Raises:
            IOError: If output file cannot be written.

        """
        from pyptp.IO.exporters.vnf_exporter import VnfExporter

        VnfExporter.export(self, str(path))
