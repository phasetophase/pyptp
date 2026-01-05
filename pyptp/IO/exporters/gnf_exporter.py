"""GNF file exporter for LV networks with presentation optimization.

Exports TNetworkLS instances to GNF v8.9 format with optional presentation
solving for proper visual layout in electrical design software.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pyptp.elements.element_utils import Guid, guid_to_string
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyptp.network_lv import NetworkLV


class GnfExporter:
    """Exporter for LV networks supporting presentation optimization and GNF v8.9 format.

    Provides comprehensive export functionality for TNetworkLS instances with
    optional presentation solving to ensure proper visual layout and scaling
    for compatibility with Gaia electrical design software.
    """

    @staticmethod
    def __compute_bounds(
        network: NetworkLV,
        sheet_guid: Guid,
    ) -> tuple[float, float, float, float]:
        """Calculate bounding box for all node presentations on specified sheet.

        Args:
            network: LV network containing presentation data.
            sheet_guid: Target sheet for bounds calculation.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y) coordinate bounds.

        """
        min_x: float = float("inf")
        min_y: float = float("inf")
        max_x: float = float("-inf")
        max_y: float = float("-inf")

        for node in network.nodes.values():
            for pres in node.presentations:
                if pres.sheet == sheet_guid:
                    min_x = min(min_x, pres.x)
                    min_y = min(min_y, pres.y)
                    max_x = max(max_x, pres.x)
                    max_y = max(max_y, pres.y)

        return min_x, min_y, max_x, max_y

    @staticmethod
    def __calculate_scale(
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float,
    ) -> float:
        """Calculate scale factor for presentation normalization based on content bounds.

        Args:
            min_x: Minimum X coordinate from bounds calculation.
            min_y: Minimum Y coordinate from bounds calculation.
            max_x: Maximum X coordinate from bounds calculation.
            max_y: Maximum Y coordinate from bounds calculation.

        Returns:
            Scale factor for coordinate transformation.

        """
        delta_x: float = abs(max_x - min_x)
        delta_y: float = abs(max_y - min_y)
        scale: float = 120.0
        max_delta: float = max(delta_x, delta_y)
        if max_delta > 0.0:
            scale = (800.0 / max_delta) + 120.0
        return scale

    @staticmethod
    def __reposition_nodes(
        network: NetworkLV,
        sheet_guid: Guid,
        min_x: float,
        min_y: float,
        scale: float,
        grid_size: int,
    ) -> None:
        """Transform node, home, and source presentations using calculated scale and offset.

        Args:
            network: LV network containing elements to transform.
            sheet_guid: Target sheet for transformation.
            min_x: X offset for coordinate normalization.
            min_y: Y offset for coordinate normalization.
            scale: Scale factor for coordinate transformation.
            grid_size: Grid alignment size for presentation snap.

        """
        for node in network.nodes.values():
            for pres in node.presentations:
                if pres.sheet == sheet_guid:
                    pres.x = grid_size * round(((pres.x - min_x) * scale) / grid_size)
                    pres.y = (grid_size * round(((pres.y - min_y) * scale) / grid_size)) * -1

        for home in network.homes.values():
            for pres in home.presentations:
                if pres.sheet == sheet_guid:
                    pres.x = grid_size * round(((pres.x - min_x) * scale) / grid_size)
                    pres.y = (grid_size * round(((pres.y - min_y) * scale) / grid_size)) * -1

        for src in network.sources.values():
            for pres in src.presentations:
                if pres.sheet == sheet_guid:
                    pres.x = grid_size * round(((pres.x - min_x) * scale) / grid_size)
                    pres.y = (grid_size * round(((pres.y - min_y) * scale) / grid_size)) * -1

    @staticmethod
    def __reposition_cables(
        network: NetworkLV,
        sheet_guid: Guid,
        min_x: float,
        min_y: float,
        scale: float,
        grid_size: int,
    ) -> None:
        """Transform cable corner coordinates using calculated scale and offset.

        Args:
            network: LV network containing cables to transform.
            sheet_guid: Target sheet for transformation.
            min_x: X offset for coordinate normalization.
            min_y: Y offset for coordinate normalization.
            scale: Scale factor for coordinate transformation.
            grid_size: Grid alignment size for presentation snap.

        """
        for cable in network.cables.values():
            for pres in cable.presentations:
                if pres.sheet == sheet_guid:
                    pres.first_corners = [
                        (
                            grid_size * round(((x - min_x) * scale) / grid_size),
                            (grid_size * round(((y - min_y) * scale) / grid_size)) * -1,
                        )
                        for x, y in pres.first_corners
                    ]
                    pres.second_corners = [
                        (
                            grid_size * round(((x - min_x) * scale) / grid_size),
                            (grid_size * round(((y - min_y) * scale) / grid_size)) * -1,
                        )
                        for x, y in pres.second_corners
                    ]

    @staticmethod
    def __gnf_presentation_solver(
        network: NetworkLV,
        sheet_guid: Guid,
    ) -> None:
        """Optimize presentation layout for specified sheet using automatic scaling.

        Args:
            network: LV network containing presentations to optimize.
            sheet_guid: Target sheet for presentation optimization.

        Raises:
            KeyError: If specified sheet GUID not found in network.
            ValueError: If no valid presentation coordinates found for sheet.

        """
        grid_size: int = 20

        if sheet_guid not in network.sheets:
            available: list[Guid] = list(network.sheets.keys())
            msg: str = f"Sheet '{guid_to_string(sheet_guid)}' not found. Available sheets: {available}"
            logger.error(msg)
            raise KeyError(msg)

        min_x, min_y, max_x, max_y = GnfExporter.__compute_bounds(network, sheet_guid)
        if min_x == float("inf") or min_y == float("inf") or max_x == float("-inf") or max_y == float("-inf"):
            msg = f"No valid presentation coordinates found for sheet: {guid_to_string(sheet_guid)}"
            raise ValueError(msg)

        scale: float = GnfExporter.__calculate_scale(min_x, min_y, max_x, max_y)
        GnfExporter.__reposition_nodes(network, sheet_guid, min_x, min_y, scale, grid_size)
        GnfExporter.__reposition_cables(network, sheet_guid, min_x, min_y, scale, grid_size)

    @staticmethod
    def export(
        network: NetworkLV,
        output_path: str,
    ) -> None:
        """Export LV network to GNF v8.9 format.

        Args:
            network: LV network to export with all registered components.
            output_path: Target file path for GNF output.

        Raises:
            IOError: If output file cannot be written.

        """
        out_path: Path = Path(output_path)
        with out_path.open("w", encoding="utf-8") as fh:
            fh.write("G8.9\nNETWORK\n\n")

            fh.write("[PROPERTIES]\n")
            fh.write(network.properties.serialize() + "\n")
            fh.write("[]\n\n")

            fh.write("[COMMENTS]\n")
            for comment in network.comments:
                fh.write(comment.serialize() + "\n")
            fh.write("[]\n\n")

            sections: list[tuple[str, Iterable]] = [
                ("PROFILE", network.profiles.values()),
                ("GM TYPE", network.gmtypes.values()),
                ("SHEET", network.sheets.values()),
                ("NODE", network.nodes.values()),
                ("LINK", network.links.values()),
                ("CABLE", network.cables.values()),
                ("TRANSFORMER", network.transformers.values()),
                ("SPECIAL TRANSFORMER", network.special_transformers.values()),
                ("REACTANCECOIL", network.reactance_coils.values()),
                ("SOURCE", network.sources.values()),
                ("SYNCHRONOUS GENERATOR", network.syn_generators.values()),
                ("ASYNCHRONOUS GENERATOR", network.async_generators.values()),
                ("ASYNCHRONOUS MOTOR", network.async_motors.values()),
                ("LOAD", network.loads.values()),
                ("SHUNTCAPACITOR", network.shunt_capacitors.values()),
                ("EARTHINGTRANSFORMER", network.earthing_transformers.values()),
                ("HOME", network.homes.values()),
                ("BATTERY", network.batteries.values()),
                ("PV", network.pvs.values()),
                ("MEASURE FIELD", network.measure_fields.values()),
                ("FUSE", network.fuses.values()),
                ("CIRCUIT BREAKER", network.circuit_breakers.values()),
                ("LOAD SWITCH", network.load_switches.values()),
                ("FRAME", network.frames.values()),
                ("LEGEND", network.legends.values()),
                ("SELECTION", network.selections),
            ]

            for header, elements in sections:
                if elements:
                    fh.write(f"[{header}]\n")
                    for elem in elements:
                        fh.write(elem.serialize() + "\n")
                    fh.write("[]\n\n")
