"""VNF file importer implementing section-based parsing for MV networks.

Provides automatic version migration and dispatches parsed sections to
declarative handlers for component creation and network registration.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pyptp.convert.version_migrator import migrate_and_read
from pyptp.IO.importers._vnf_handlers.async_generator_handler import AsyncGeneratorHandler
from pyptp.IO.importers._vnf_handlers.async_motor_handler import AsyncMotorHandler
from pyptp.IO.importers._vnf_handlers.battery_handler import BatteryHandler
from pyptp.IO.importers._vnf_handlers.cable_handler import CableHandler
from pyptp.IO.importers._vnf_handlers.calc_case_handler import CalcCaseHandler
from pyptp.IO.importers._vnf_handlers.circuit_breaker_handler import CircuitBreakerHandler
from pyptp.IO.importers._vnf_handlers.comment_handler import CommentHandler
from pyptp.IO.importers._vnf_handlers.dynamic_case_handler import DynamicCaseHandler
from pyptp.IO.importers._vnf_handlers.earthing_transformer_handler import EarthingTransformerHandler
from pyptp.IO.importers._vnf_handlers.frame_handler import FrameHandler
from pyptp.IO.importers._vnf_handlers.fuse_handler import FuseHandler
from pyptp.IO.importers._vnf_handlers.growth_handler import GrowthHandler
from pyptp.IO.importers._vnf_handlers.hyperlink_handler import HyperlinkHandler
from pyptp.IO.importers._vnf_handlers.indicator_handler import IndicatorHandler
from pyptp.IO.importers._vnf_handlers.legend_handler import LegendHandler
from pyptp.IO.importers._vnf_handlers.line_handler import LineHandler
from pyptp.IO.importers._vnf_handlers.link_handler import LinkHandler
from pyptp.IO.importers._vnf_handlers.load_behaviour_handler import LoadBehaviourHandler
from pyptp.IO.importers._vnf_handlers.load_handler import LoadHandler
from pyptp.IO.importers._vnf_handlers.load_switch_handler import LoadSwitchHandler
from pyptp.IO.importers._vnf_handlers.measure_field_handler import MeasureFieldHandler
from pyptp.IO.importers._vnf_handlers.mutual_handler import MutualHandler
from pyptp.IO.importers._vnf_handlers.node_handler import NodeHandler
from pyptp.IO.importers._vnf_handlers.profile_handler import ProfileHandler
from pyptp.IO.importers._vnf_handlers.properties_handler import PropertiesHandler
from pyptp.IO.importers._vnf_handlers.pv_handler import PvHandler
from pyptp.IO.importers._vnf_handlers.rails_handler import RailsHandler
from pyptp.IO.importers._vnf_handlers.reactance_coil_handler import ReactanceCoilHandler
from pyptp.IO.importers._vnf_handlers.scenario_handler import ScenarioHandler
from pyptp.IO.importers._vnf_handlers.selection_handler import SelectionHandler
from pyptp.IO.importers._vnf_handlers.sheet_handler import SheetHandler
from pyptp.IO.importers._vnf_handlers.shunt_capacitor_handler import ShuntCapacitorHandler
from pyptp.IO.importers._vnf_handlers.shunt_coil_handler import ShuntCoilHandler
from pyptp.IO.importers._vnf_handlers.source_handler import SourceHandler
from pyptp.IO.importers._vnf_handlers.special_transformer_handler import SpecialTransformerHandler
from pyptp.IO.importers._vnf_handlers.sync_generator_handler import SyncGeneratorHandler
from pyptp.IO.importers._vnf_handlers.sync_motor_handler import SyncMotorHandler
from pyptp.IO.importers._vnf_handlers.text_handler import TextHandler
from pyptp.IO.importers._vnf_handlers.threewinding_transformer_handler import ThreewindingTransformerHandler
from pyptp.IO.importers._vnf_handlers.transformer_handler import TransformerHandler
from pyptp.IO.importers._vnf_handlers.transformer_load_handler import TransformerLoadHandler
from pyptp.IO.importers._vnf_handlers.variable_handler import VariableHandler
from pyptp.IO.importers._vnf_handlers.variant_handler import VariantHandler
from pyptp.IO.importers._vnf_handlers.windturbine_handler import WindTurbineHandler
from pyptp.network_mv import NetworkMV
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from re import Pattern
    from typing import Any

    from pyptp.IO.importers._base_handler import DeclarativeHandler

    VnfHandler = DeclarativeHandler[NetworkMV] | Any


def make_section_pattern(name: str) -> re.Pattern[str]:
    """Create compiled regex pattern for extracting named section content.

    Args:
        name: Section name to match (e.g., "NODE", "TRANSFORMER").

    Returns:
        Compiled regex pattern for section content extraction.

    """
    header = re.escape(name)
    pattern = rf"(?s)(?<=\[{header}\]\s).*?(?=^\[|\Z)"
    return re.compile(pattern, re.MULTILINE)


class VnfImporter:
    """Importer for VNF files supporting automatic version migration and declarative parsing.

    Handles legacy VNF versions through automatic migration and dispatches
    parsed sections to specialized handlers for component creation in MV networks.

    The importer follows a declarative pattern where each section type maps
    to a specific handler, enabling extensible parsing without tight coupling.
    """

    _HANDLERS: ClassVar[dict[str, VnfHandler]] = {
        "CASE": CalcCaseHandler(),
        "PROPERTIES": PropertiesHandler(),
        "COMMENTS": CommentHandler(),
        "SHEET": SheetHandler(),
        "NODE": NodeHandler(),
        "LINK": LinkHandler(),
        "LINE": LineHandler(),
        "CABLE": CableHandler(),
        "TRANSFORMER": TransformerHandler(),
        "SPECIAL TRANSFORMER": SpecialTransformerHandler(),
        "THREEWINDINGSTRANSFORMER": ThreewindingTransformerHandler(),
        "EARTHINGTRANSFORMER": EarthingTransformerHandler(),
        "TRANSFORMERLOAD": TransformerLoadHandler(),
        "SOURCE": SourceHandler(),
        "SYNCHRONOUS GENERATOR": SyncGeneratorHandler(),
        "SYNCHRONOUS MOTOR": SyncMotorHandler(),
        "ASYNCHRONOUS GENERATOR": AsyncGeneratorHandler(),
        "ASYNCHRONOUS MOTOR": AsyncMotorHandler(),
        "LOAD": LoadHandler(),
        "PV": PvHandler(),
        "WINDTURBINE": WindTurbineHandler(),
        "BATTERY": BatteryHandler(),
        "SHUNTCAPACITOR": ShuntCapacitorHandler(),
        "SHUNTCOIL": ShuntCoilHandler(),
        "REACTANCECOIL": ReactanceCoilHandler(),
        "LOAD SWITCH": LoadSwitchHandler(),
        "FUSE": FuseHandler(),
        "CIRCUIT BREAKER": CircuitBreakerHandler(),
        "INDICATOR": IndicatorHandler(),
        "MEASURE FIELD": MeasureFieldHandler(),
        "LOADBEHAVIOUR": LoadBehaviourHandler(),
        "GROWTH": GrowthHandler(),
        "HYPERLINKS": HyperlinkHandler(),
        "VARIABLES": VariableHandler(),
        "PROFILE": ProfileHandler(),
        "SCENARIO": ScenarioHandler(),
        "SELECTION": SelectionHandler(),
        "TEXT": TextHandler(),
        "FRAME": FrameHandler(),
        "LEGEND": LegendHandler(),
        "RAILSYSTEM": RailsHandler(),
        "MUTUAL": MutualHandler(),
        "VARIANT": VariantHandler(),
        "DYNAMIC CASE": DynamicCaseHandler(),
    }

    _SECTION_PATTERNS: ClassVar[dict[str, Pattern[str]]] = {name: make_section_pattern(name) for name in _HANDLERS}

    def _get_and_migrate_vnf_content(self, path: Path) -> str:
        """Load VNF file content with automatic version migration for legacy files.

        Args:
            path: Path to VNF file for import.

        Returns:
            File content as string, either original or migrated to supported version.

        Raises:
            RuntimeError: If version migration fails after retries.

        """
        with Path.open(path, encoding="utf-8", errors="ignore") as f:
            file_version = f.readline().strip()

        supported_versions = {"V9.9", "V9.10a"}

        if file_version not in supported_versions:
            logger.debug(
                "Legacy VNF version '%s' detected. Attempting migration to V9.9...",
                file_version,
            )
            return migrate_and_read(path, version="V9.9", encoding="utf-8")

        return path.read_text(encoding="utf-8", errors="ignore")

    def _dispatch_to_handlers(self, network: NetworkMV, raw_text: str) -> None:
        """Parse file content and dispatch sections to registered handlers.

        Args:
            network: Target MV network for component registration.
            raw_text: Complete file content for section extraction.

        """
        for name, handler in self._HANDLERS.items():
            pattern = self._SECTION_PATTERNS[name]
            for match in pattern.finditer(raw_text):
                chunk = match.group(0).rstrip() + "\n#END"
                handler.handle(network, chunk)

    def import_vnf(self, path: str | Path) -> NetworkMV:
        """Import VNF file into a populated MV network with automatic version migration.

        Args:
            path: Path to VNF file for import.

        Returns:
            Populated TNetworkMS with all components registered from file sections.

        Raises:
            RuntimeError: If file migration fails or content is invalid.

        """
        raw_text = self._get_and_migrate_vnf_content(Path(path))
        network = NetworkMV()
        self._dispatch_to_handlers(network, raw_text)
        return network
