"""Low-voltage network model for unbalanced electrical system analysis.

Supports GNF format networks with up to 9 conductors per connection,
complex impedance modeling, and unbalanced load flow analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.lv.properties import PropertiesLV
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pathlib import Path

    from pyptp.elements.element_utils import Guid
    from pyptp.elements.lv.async_generator import AsynchronousGeneratorLV
    from pyptp.elements.lv.async_motor import AsynchronousMotorLV
    from pyptp.elements.lv.battery import BatteryLV
    from pyptp.elements.lv.cable import CableLV
    from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV
    from pyptp.elements.lv.comment import CommentLV
    from pyptp.elements.lv.connection import ConnectionLV
    from pyptp.elements.lv.earthing_transformer import EarthingTransformerLV
    from pyptp.elements.lv.frame import FrameLV
    from pyptp.elements.lv.fuse import FuseLV
    from pyptp.elements.lv.gm_type import GMTypeLV
    from pyptp.elements.lv.legend import LegendLV
    from pyptp.elements.lv.link import LinkLV
    from pyptp.elements.lv.load import LoadLV
    from pyptp.elements.lv.load_switch import LoadSwitchLV
    from pyptp.elements.lv.measure_field import MeasureFieldLV
    from pyptp.elements.lv.node import NodeLV
    from pyptp.elements.lv.profile import ProfileLV
    from pyptp.elements.lv.pv import PVLV
    from pyptp.elements.lv.reactance_coil import ReactanceCoilLV
    from pyptp.elements.lv.selection import SelectionLV
    from pyptp.elements.lv.sheet import SheetLV
    from pyptp.elements.lv.shunt_capacitor import ShuntCapacitorLV
    from pyptp.elements.lv.source import SourceLV
    from pyptp.elements.lv.special_transformer import SpecialTransformerLV
    from pyptp.elements.lv.syn_generator import SynchronousGeneratorLV
    from pyptp.elements.lv.transformer import TransformerLV


class NetworkModelError(Exception):
    """Custom exception for network model errors."""


class NetworkLV:
    """Low-voltage network model supporting unbalanced analysis."""

    def __init__(self) -> None:
        """Initialize network with element collections and optional type definitions.

        Args:
            default_types: Optional type definitions for network elements.

        """
        self.properties: PropertiesLV = PropertiesLV(system=PropertiesLV.System())
        self.comments: list[CommentLV] = []
        self.frames: dict[Guid, FrameLV] = {}
        self.profiles: dict[Guid, ProfileLV] = {}
        self.gmtypes: dict[int, GMTypeLV] = {}
        self.sheets: dict[Guid, SheetLV] = {}
        self.nodes: dict[Guid, NodeLV] = {}
        self.cables: dict[Guid, CableLV] = {}
        self.links: dict[Guid, LinkLV] = {}
        self.homes: dict[Guid, ConnectionLV] = {}
        self.legends: dict[Guid, LegendLV] = {}
        self.sources: dict[Guid, SourceLV] = {}
        self.fuses: dict[Guid, FuseLV] = {}
        self.transformers: dict[Guid, TransformerLV] = {}
        self.special_transformers: dict[Guid, SpecialTransformerLV] = {}
        self.reactance_coils: dict[Guid, ReactanceCoilLV] = {}
        self.syn_generators: dict[Guid, SynchronousGeneratorLV] = {}
        self.async_generators: dict[Guid, AsynchronousGeneratorLV] = {}
        self.async_motors: dict[Guid, AsynchronousMotorLV] = {}
        self.earthing_transformers: dict[Guid, EarthingTransformerLV] = {}
        self.shunt_capacitors: dict[Guid, ShuntCapacitorLV] = {}
        self.batteries: dict[Guid, BatteryLV] = {}
        self.loads: dict[Guid, LoadLV] = {}
        self.circuit_breakers: dict[Guid, CircuitBreakerLV] = {}
        self.pvs: dict[Guid, PVLV] = {}
        self.load_switches: dict[Guid, LoadSwitchLV] = {}
        self.measure_fields: dict[Guid, MeasureFieldLV] = {}
        self.selections: list[SelectionLV] = []

    def get_transformer(self, guid: str) -> TransformerLV | None:
        """Find transformer by GUID string.

        Args:
            guid: String representation of transformer GUID.

        Returns:
            Transformer element or None if not found.

        Note:
            Logs warning if transformer not found.

        """
        for transformer in self.transformers.values():
            if guid == transformer.general.guid:
                return transformer
        logger.warning("Transformer with GUID %s not found", guid)
        return None

    def delete_transformer(self, guid: str) -> bool:
        """Remove transformer from network by GUID string.

        Args:
            guid: String representation of transformer GUID.

        Returns:
            True if transformer was found and removed, False otherwise.

        Note:
            Logs warning if transformer not found.

        """
        for key, transformer in list(self.transformers.items()):
            if guid == transformer.general.guid:
                del self.transformers[key]
                return True
        logger.warning("Delete failed: Transformer with GUID %s not found", guid)
        return False

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

    def get_link(self, guid: Guid) -> LinkLV | None:
        """Find link by GUID.

        Args:
            guid: Link GUID to search for.

        Returns:
            Link element or None if not found.

        Note:
            Logs warning if link not found.

        """
        for link in self.links.values():
            if guid == link.general.guid:
                return link

        logger.warning("Link with GUID %s not found", guid)
        return None

    @classmethod
    def from_file(cls, path: str | Path) -> NetworkLV:
        """Create LV network from GNF file.

        Args:
            path: Path to GNF file for import.

        Returns:
            Populated NetworkLV instance with all components from file.

        Raises:
            RuntimeError: If file migration fails or content is invalid.
            FileNotFoundError: If specified file does not exist.

        Example:
            >>> network = NetworkLV.from_file("input.gnf")
            >>> print(len(network.nodes))

        """
        from pyptp.IO.importers.gnf_importer import GnfImporter

        return GnfImporter().import_gnf(path)

    def save(self, path: str | Path) -> None:
        """Save network to GNF file.

        Args:
            path: Target file path for GNF output.

        Raises:
            IOError: If output file cannot be written.

        """
        from pyptp.IO.exporters.gnf_exporter import GnfExporter

        GnfExporter.export(self, str(path))
