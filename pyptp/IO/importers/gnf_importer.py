"""GNF file importer implementing section-based parsing for LV networks.

Provides automatic version migration and dispatches parsed sections to
declarative handlers for component creation and network registration.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pyptp.convert.version_migrator import migrate_and_read
from pyptp.IO.importers._gnf_handlers.async_generator_handler import AsyncGeneratorHandler
from pyptp.IO.importers._gnf_handlers.async_motor_handler import AsyncMotorHandler
from pyptp.IO.importers._gnf_handlers.battery_handler import BatteryHandler
from pyptp.IO.importers._gnf_handlers.cable_handler import CableHandler
from pyptp.IO.importers._gnf_handlers.circuit_breaker_handler import CircuitBreakerHandler
from pyptp.IO.importers._gnf_handlers.comment_handler import CommentHandler
from pyptp.IO.importers._gnf_handlers.earthing_transformer_handler import EarthingTransformerHandler
from pyptp.IO.importers._gnf_handlers.frame_handler import FrameHandler
from pyptp.IO.importers._gnf_handlers.fuse_handler import FuseHandler
from pyptp.IO.importers._gnf_handlers.gm_type_handler import GMTypeHandler
from pyptp.IO.importers._gnf_handlers.home_handler import HomeHandler
from pyptp.IO.importers._gnf_handlers.legend_handler import LegendHandler
from pyptp.IO.importers._gnf_handlers.link_handler import LinkHandler
from pyptp.IO.importers._gnf_handlers.load_handler import LoadHandler
from pyptp.IO.importers._gnf_handlers.load_switch_handler import LoadSwitchHandler
from pyptp.IO.importers._gnf_handlers.measure_field_handler import MeasureFieldHandler
from pyptp.IO.importers._gnf_handlers.node_handler import NodeHandler
from pyptp.IO.importers._gnf_handlers.profile_handler import ProfileHandler
from pyptp.IO.importers._gnf_handlers.properties_handler import PropertiesHandler
from pyptp.IO.importers._gnf_handlers.pv_handler import PvHandler
from pyptp.IO.importers._gnf_handlers.reactance_coil_handler import ReactanceCoilHandler
from pyptp.IO.importers._gnf_handlers.selection_handler import SelectionHandler
from pyptp.IO.importers._gnf_handlers.sheet_handler import SheetHandler
from pyptp.IO.importers._gnf_handlers.shunt_capacitor_handler import ShuntCapacitorHandler
from pyptp.IO.importers._gnf_handlers.source_handler import SourceHandler
from pyptp.IO.importers._gnf_handlers.special_transformer_handler import SpecialTransformerHandler
from pyptp.IO.importers._gnf_handlers.sync_generator_handler import SyncGeneratorHandler
from pyptp.IO.importers._gnf_handlers.transformer_handler import TransformerHandler
from pyptp.network_lv import NetworkLV
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from re import Pattern
    from typing import Any

    from pyptp.IO.importers._base_handler import DeclarativeHandler

    GnfHandler = DeclarativeHandler[NetworkLV] | Any


def make_section_pattern(name: str) -> re.Pattern[str]:
    """Create compiled regex pattern for extracting named section content.

    Args:
        name: Section name to match (e.g., "NODE", "CABLE").

    Returns:
        Compiled regex pattern for section content extraction.

    """
    header = re.escape(name)
    pattern = rf"(?s)(?<=\[{header}\]\s).*?(?=^\[|\Z)"
    return re.compile(pattern, re.MULTILINE)


class GnfImporter:
    """Importer for GNF files supporting automatic version migration and declarative parsing.

    Handles legacy GNF versions through automatic migration and dispatches
    parsed sections to specialized handlers for component creation in LV networks.

    The importer follows a declarative pattern where each section type maps
    to a specific handler, enabling extensible parsing without tight coupling.
    """

    _HANDLERS: ClassVar[dict[str, GnfHandler]] = {
        "COMMENTS": CommentHandler(),
        "PROPERTIES": PropertiesHandler(),
        "SHEET": SheetHandler(),
        "SELECTION": SelectionHandler(),
        "PROFILE": ProfileHandler(),
        "GM TYPE": GMTypeHandler(),
        "NODE": NodeHandler(),
        "LINK": LinkHandler(),
        "CABLE": CableHandler(),
        "FUSE": FuseHandler(),
        "HOME": HomeHandler(),
        "LEGEND": LegendHandler(),
        "TRANSFORMER": TransformerHandler(),
        "SPECIAL TRANSFORMER": SpecialTransformerHandler(),
        "REACTANCECOIL": ReactanceCoilHandler(),
        "SYNCHRONOUS GENERATOR": SyncGeneratorHandler(),
        "ASYNCHRONOUS GENERATOR": AsyncGeneratorHandler(),
        "ASYNCHRONOUS MOTOR": AsyncMotorHandler(),
        "EARTHINGTRANSFORMER": EarthingTransformerHandler(),
        "SHUNTCAPACITOR": ShuntCapacitorHandler(),
        "LOAD": LoadHandler(),
        "SOURCE": SourceHandler(),
        "BATTERY": BatteryHandler(),
        "PV": PvHandler(),
        "CIRCUIT BREAKER": CircuitBreakerHandler(),
        "FRAME": FrameHandler(),
        "LOAD SWITCH": LoadSwitchHandler(),
        "MEASURE FIELD": MeasureFieldHandler(),
    }

    _SECTION_PATTERNS: ClassVar[dict[str, Pattern[str]]] = {name: make_section_pattern(name) for name in _HANDLERS}

    def _get_and_migrate_gnf_content(self, path: Path) -> str:
        """Load GNF file content with automatic version migration for legacy files.

        Args:
            path: Path to GNF file for import.

        Returns:
            File content as string, either original or migrated to supported version.

        Raises:
            RuntimeError: If version migration fails after retries.

        """
        with Path.open(path, encoding="utf-8-sig", errors="ignore") as f:
            file_version = f.readline().strip()

        supported_versions = {"G8.9", "G8.9a"}

        if file_version not in supported_versions:
            logger.debug(
                "Legacy GNF version '%s' detected. Attempting migration to G8.9...",
                file_version,
            )
            return migrate_and_read(path, version="G8.9", encoding="utf-8-sig")

        return path.read_text(encoding="utf-8-sig", errors="ignore")

    def _dispatch_to_handlers(self, network: NetworkLV, raw_text: str) -> None:
        """Parse file content and dispatch sections to registered handlers.

        Args:
            network: Target LV network for component registration.
            raw_text: Complete file content for section extraction.

        """
        for name, handler in self._HANDLERS.items():
            pattern = self._SECTION_PATTERNS[name]
            for match in pattern.finditer(raw_text):
                chunk = match.group(0).rstrip() + "\n#END"
                handler.handle(network, chunk)

    def import_gnf(self, path: str | Path) -> NetworkLV:
        """Import GNF file into a populated LV network with automatic version migration.

        Args:
            path: Path to GNF file for import.

        Returns:
            Populated TNetworkLS with all components registered from file sections.

        Raises:
            RuntimeError: If file migration fails or content is invalid.

        """
        raw_text = self._get_and_migrate_gnf_content(Path(path))
        network = NetworkLV()
        self._dispatch_to_handlers(network, raw_text)
        return network
