"""GNF file exporter for LV networks with presentation optimization.

Exports NetworkLV instances to GNF format with version migration support.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from pyptp.convert.version_migrator import NativeResult, convert_file, native_library_available, validate_file
from pyptp.elements.element_utils import Guid, guid_to_string
from pyptp.elements.enums import GnfVersion
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyptp.network_lv import NetworkLV


class GnfExporter:
    """Exporter for LV networks supporting presentation optimization and GNF v8.12 format.

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
    def _write_gnf(network: NetworkLV, fh: TextIO) -> None:
        """Write network content in G8.12 format to file handle."""
        fh.write("G8.12\nNETWORK\n\n")

        def _write_section(header: str, elements: Iterable, *, always: bool = False) -> None:
            """Write one [HEADER] ... [] block, skipping it when there are no elements.

            Gaia omits empty sections. COMMENTS is written even when empty with
            always=True to keep the output identical to earlier pyptp versions.
            """
            elems = list(elements)
            if not elems and not always:
                return
            fh.write(f"[{header}]\n")
            fh.writelines(elem.serialize() + "\n" for elem in elems)
            fh.write("[]\n\n")

        _write_section("PROPERTIES", [network.properties])
        _write_section("COMMENTS", network.comments, always=True)
        _write_section("HYPERLINKS", network.hyperlinks)
        _write_section("PROFILEFILES", network.profile_files)
        _write_section("MEASUREMENTFILES", network.measurement_files)
        _write_section("PROFILE", network.profiles.values())
        _write_section("GM TYPE", network.gmtypes.values())
        _write_section("SHEET", network.sheets.values())
        _write_section("NODE", network.nodes.values())
        _write_section("LINK", network.links.values())
        _write_section("CABLE", network.cables.values())
        _write_section("TRANSFORMER", network.transformers.values())
        _write_section("SPECIAL TRANSFORMER", network.special_transformers.values())
        _write_section("REACTANCECOIL", network.reactance_coils.values())
        _write_section("SOURCE", network.sources.values())
        _write_section("SYNCHRONOUS GENERATOR", network.syn_generators.values())
        _write_section("ASYNCHRONOUS GENERATOR", network.async_generators.values())
        _write_section("ASYNCHRONOUS MOTOR", network.async_motors.values())
        _write_section("LOAD", network.loads.values())
        _write_section("SHUNTCAPACITOR", network.shunt_capacitors.values())
        _write_section("EARTHINGTRANSFORMER", network.earthing_transformers.values())
        _write_section("HOME", network.homes.values())
        _write_section("BATTERY", network.batteries.values())
        _write_section("PV", network.pvs.values())
        _write_section("MEASURE FIELD", network.measure_fields.values())
        _write_section("FUSE", network.fuses.values())
        _write_section("CIRCUIT BREAKER", network.circuit_breakers.values())
        _write_section("LOAD SWITCH", network.load_switches.values())
        _write_section("TEXT", network.texts.values())
        _write_section("FRAME", network.frames.values())
        _write_section("LEGEND", network.legends.values())
        _write_section("SELECTION", network.selections)

    @staticmethod
    def export(
        network: NetworkLV,
        output_path: str,
        version: GnfVersion = GnfVersion.G8_12,
        *,
        validate_on_migration_failure: bool = True,
        native_check: bool = True,
    ) -> None:
        """Export LV network to GNF format with version migration.

        The network is always serialized as native G8.12. When an older target
        version is requested, the G8.12 output is written to a temporary file and
        down-converted by the migrator.

        Args:
            network: LV network to export.
            output_path: Target file path for GNF output.
            version: Target GNF version (default: G8.12).
            validate_on_migration_failure: Run validators and include diagnostics
                in the error message when the native loader rejects the network
                (default: True).
            native_check: Check the written file with the native loader and raise
                if it rejects the network (default: True).

        Raises:
            IOError: If output file cannot be written.
            RuntimeError: If the native loader rejects the network or version
                migration fails. No output file is left behind.

        """
        out_path = Path(output_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / out_path.name
            with temp_file.open("w", encoding="utf-8") as fh:
                GnfExporter._write_gnf(network, fh)

            if version == GnfVersion.G8_12:
                if native_check and native_library_available("GNF"):
                    GnfExporter._raise_if_rejected(
                        network,
                        validate_file(temp_file),
                        f"Failed to save as {version}",
                        diagnostics=validate_on_migration_failure,
                    )
                shutil.copyfile(temp_file, out_path)
            else:
                result = convert_file(
                    input_path=temp_file,
                    output_dir=out_path.parent,
                    output_file=out_path.name,
                    version=version,
                )
                GnfExporter._raise_if_rejected(
                    network,
                    result,
                    f"Failed to convert to {version}",
                    diagnostics=validate_on_migration_failure,
                )

    @staticmethod
    def _raise_if_rejected(network: NetworkLV, result: NativeResult, what: str, *, diagnostics: bool) -> None:
        """Raise RuntimeError with the loader messages when a native call failed."""
        if result.ok:
            return
        msg = f"{what}: {result.describe()}"
        if diagnostics:
            msg = GnfExporter._append_validation_diagnostics(network, msg)
        raise RuntimeError(msg)

    @staticmethod
    def _append_validation_diagnostics(network: NetworkLV, msg: str) -> str:
        """Run validators and append ERROR-level issues to the error message."""
        from pyptp.validator.base import Severity, ValidatorCategory
        from pyptp.validator.runner import CheckRunner

        try:
            report = CheckRunner(network).run(categories=ValidatorCategory.CORE)
            errors = [i for i in report.issues if i.severity == Severity.ERROR]
            if errors:
                lines = [
                    f"\n\nValidation found {len(errors)} error(s) that may explain the failure:",
                    *[f"  - [{issue.object_type}] '{issue.message}'" for issue in errors],
                ]
                msg += "\n".join(lines)
        except Exception:  # noqa: BLE001
            logger.debug("Validation diagnostics failed during migration error reporting", exc_info=True)
        return msg
