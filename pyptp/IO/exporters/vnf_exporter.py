"""VNF file exporter for MV networks with presentation optimization.

Exports TNetworkMS instances to VNF v9.9 format with optional presentation
solving for proper visual layout in electrical design software.
"""

from collections.abc import Iterable
from pathlib import Path

from pyptp.elements.element_utils import Guid
from pyptp.network_mv import NetworkMV


class VnfExporter:
    """Exporter for MV networks supporting presentation optimization and VNF v9.9 format.

    Provides comprehensive export functionality for TNetworkMS instances with
    optional presentation solving to ensure proper visual layout and scaling
    for compatibility with Vision electrical design software.
    """

    @staticmethod
    def __compute_bounds(
        network: NetworkMV,
        sheet_guid: Guid,
    ) -> tuple[float, float, float, float]:
        """Calculate bounding box for all node presentations on specified sheet.

        Args:
            network: MV network containing presentation data.
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
    def __reposition_node_presentations(
        network: NetworkMV,
        sheet_guid: Guid,
        min_x: float,
        min_y: float,
        scale: float,
    ) -> None:
        """Transform node presentations using calculated scale and offset with Y-axis inversion.

        Args:
            network: MV network containing nodes to transform.
            sheet_guid: Target sheet for transformation.
            min_x: X offset for coordinate normalization.
            min_y: Y offset for coordinate normalization.
            scale: Scale factor for coordinate transformation.

        """
        for node in network.nodes.values():
            for pres in node.presentations:
                if pres.sheet == sheet_guid:
                    pres.x = round((pres.x - min_x) * scale)
                    pres.y = round((pres.y - min_y) * scale) * -1

    @staticmethod
    def __reposition_sources(
        network: NetworkMV,
        sheet_guid: Guid,
        min_x: float,
        min_y: float,
        scale: float,
        grid_size: int,
    ) -> None:
        """Transform source presentations with additional vertical offset for visual separation.

        Args:
            network: MV network containing sources to transform.
            sheet_guid: Target sheet for transformation.
            min_x: X offset for coordinate normalization.
            min_y: Y offset for coordinate normalization.
            scale: Scale factor for coordinate transformation.
            grid_size: Grid alignment size for presentation positioning.

        """
        for src in network.sources.values():
            for pres in src.presentations:
                if pres.sheet == sheet_guid:
                    pres.x = round((pres.x - min_x) * scale)
                    pres.y = (round((pres.y - min_y) * scale) * -1) + (grid_size * 4)

    @staticmethod
    def __reposition_transformer_loads(
        network: NetworkMV,
        sheet_guid: Guid,
        min_x: float,
        min_y: float,
        scale: float,
        grid_size: int,
    ) -> None:
        """Transform transformer load presentations with diagonal offset for visual clarity.

        Args:
            network: MV network containing transformer loads to transform.
            sheet_guid: Target sheet for transformation.
            min_x: X offset for coordinate normalization.
            min_y: Y offset for coordinate normalization.
            scale: Scale factor for coordinate transformation.
            grid_size: Grid alignment size for presentation positioning.

        """
        for tl in network.transformer_loads.values():
            for pres in tl.presentations:
                if pres.sheet == sheet_guid:
                    pres.x = round((pres.x - min_x) * scale) + (grid_size * 4)
                    pres.y = (round((pres.y - min_y) * scale) * -1) + (grid_size * 4)

    @staticmethod
    def __reposition_loads(
        network: NetworkMV,
        sheet_guid: Guid,
        min_x: float,
        min_y: float,
        scale: float,
        grid_size: int,
    ) -> None:
        """Transform load presentations with diagonal offset for visual clarity.

        Args:
            network: MV network containing loads to transform.
            sheet_guid: Target sheet for transformation.
            min_x: X offset for coordinate normalization.
            min_y: Y offset for coordinate normalization.
            scale: Scale factor for coordinate transformation.
            grid_size: Grid alignment size for presentation positioning.

        """
        for ld in network.loads.values():
            for pres in ld.presentations:
                if pres.sheet == sheet_guid:
                    pres.x = round((pres.x - min_x) * scale) + (grid_size * 4)
                    pres.y = (round((pres.y - min_y) * scale) * -1) + (grid_size * 4)

    @staticmethod
    def __reposition_cables(
        network: NetworkMV,
        sheet_guid: Guid,
        min_x: float,
        min_y: float,
        scale: float,
    ) -> None:
        """Transform cable corner coordinates using calculated scale and offset.

        Args:
            network: MV network containing cables to transform.
            sheet_guid: Target sheet for transformation.
            min_x: X offset for coordinate normalization.
            min_y: Y offset for coordinate normalization.
            scale: Scale factor for coordinate transformation.

        """
        for cable in network.cables.values():
            for pres in cable.presentations:
                if pres.sheet == sheet_guid:
                    pres.first_corners = [
                        (round((x - min_x) * scale), round((y - min_y) * scale) * -1) for x, y in pres.first_corners
                    ]
                    pres.second_corners = [
                        (round((x - min_x) * scale), round((y - min_y) * scale) * -1) for x, y in pres.second_corners
                    ]

    @staticmethod
    def __vnf_presentation_solver(
        network: NetworkMV,
        sheet_guid: Guid,
        scaling: int = 200,
        grid_size: int = 20,
    ) -> None:
        """Optimize presentation layout for specified sheet using provided scaling.

        Args:
            network: MV network containing presentations to optimize.
            sheet_guid: Target sheet for presentation optimization.
            scaling: Scale factor for coordinate transformation (default: 200).
            grid_size: Grid alignment size for presentation positioning.

        """
        min_x, min_y, __, __ = VnfExporter.__compute_bounds(network, sheet_guid)
        scale: float = float(scaling)

        VnfExporter.__reposition_node_presentations(network, sheet_guid, min_x, min_y, scale)
        VnfExporter.__reposition_sources(network, sheet_guid, min_x, min_y, scale, grid_size)
        VnfExporter.__reposition_transformer_loads(
            network,
            sheet_guid,
            min_x,
            min_y,
            scale,
            grid_size,
        )
        VnfExporter.__reposition_loads(network, sheet_guid, min_x, min_y, scale, grid_size)
        VnfExporter.__reposition_cables(network, sheet_guid, min_x, min_y, scale)

    @staticmethod
    def export(
        network: NetworkMV,
        output_path: str,
    ) -> None:
        """Export MV network to VNF v9.9 format.

        Args:
            network: MV network to export with all registered components.
            output_path: Target file path for VNF output.

        Raises:
            IOError: If output file cannot be written.

        """
        out_path = Path(output_path)
        with out_path.open("w", encoding="utf-8") as fh:
            fh.write("V9.9\nNETWORK\n\n")

            def _write_section(header: str, elements: Iterable) -> None:
                elems = list(elements)
                if not elems:
                    return
                fh.write(f"[{header}]\n")
                for elem in elems:
                    fh.write(elem.serialize() + "\n")
                fh.write("[]\n\n")

            _write_section("PROPERTIES", [network.properties])
            _write_section("COMMENTS", network.comments)
            _write_section("HYPERLINKS", network.hyperlinks)
            _write_section("VARIABLES", network.variables)
            _write_section("SHEET", network.sheets.values())
            _write_section("NODE", network.nodes.values())
            _write_section("RAILSYSTEM", network.rail_systems.values())
            _write_section("LINK", network.links.values())
            _write_section("LINE", network.lines.values())
            _write_section("CABLE", network.cables.values())
            _write_section("TRANSFORMER", network.transformers.values())
            _write_section("SPECIAL TRANSFORMER", network.special_transformers.values())
            _write_section("REACTANCECOIL", network.reactance_coils.values())
            _write_section("THREEWINDINGSTRANSFORMER", network.threewinding_transformers.values())
            _write_section("MUTUAL", network.mutuals.values())
            _write_section("PROFILE", network.profiles.values())
            _write_section("SOURCE", network.sources.values())
            _write_section("SYNCHRONOUS GENERATOR", network.synchronous_generators.values())
            _write_section("SYNCHRONOUS MOTOR", network.synchronous_motors.values())
            _write_section("ASYNCHRONOUS GENERATOR", network.asynchronous_generators.values())
            _write_section("ASYNCHRONOUS MOTOR", network.asynchronous_motors.values())
            _write_section("LOADBEHAVIOUR", network.load_behaviours.values())
            _write_section("GROWTH", network.growths.values())
            _write_section("LOAD", network.loads.values())
            _write_section("TRANSFORMERLOAD", network.transformer_loads.values())
            _write_section("SHUNTCAPACITOR", network.shunt_capacitors.values())
            _write_section("SHUNTCOIL", network.shunt_coils.values())
            _write_section("EARTHINGTRANSFORMER", network.earthing_transformers.values())
            _write_section("WINDTURBINE", network.windturbines.values())
            _write_section("BATTERY", network.batteries.values())
            _write_section("PV", network.pvs.values())
            _write_section("MEASURE FIELD", network.measure_fields.values())
            _write_section("LOAD SWITCH", network.load_switches.values())
            _write_section("FUSE", network.fuses.values())
            _write_section("CIRCUIT BREAKER", network.circuit_breakers.values())
            _write_section("INDICATOR", network.indicators.values())
            _write_section("TEXT", network.texts.values())
            _write_section("FRAME", network.frames.values())
            _write_section("LEGEND", network.legends.values())
            _write_section("SELECTION", network.selections)
            _write_section("VARIANT", network.variants.values())
            _write_section("SCENARIO", network.scenarios.values())
            _write_section("CASE", network.calc_cases)
