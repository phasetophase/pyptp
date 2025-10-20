"""Handler for parsing GNF Legend sections using a declarative recipe."""

from __future__ import annotations

import contextlib
from typing import Any, ClassVar

from pyptp.elements.lv.legend import LegendCell, LegendLV, LegendPresentation
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV as TNetworkLSType
from pyptp.ptp_log import logger


class LegendHandler(DeclarativeHandler[TNetworkLSType]):
    """Parses GNF Legend components using a declarative recipe.

    Handles legends with general properties, merge specifications, cells with text,
    and presentation properties for network documentation.
    """

    COMPONENT_CLS = LegendLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("merges", "#Merge ", required=False),
        SectionConfig("cells", "#Cell ", required=False),
        SectionConfig("_text_lines", "#Text ", required=False),
        SectionConfig("presentations", "#Presentation ", required=False),
    ]
    # Note: _text_lines uses special handling because each Cell has nested Text lines.
    # This parent-child relationship requires custom processing in _process_cells_with_text.

    def __init__(self) -> None:
        """Initialize handler with storage for raw section data."""
        super().__init__()
        self._current_raw_section: str = ""

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Legend-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "general":
            return LegendLV.General
        if kwarg_name == "cells":
            return LegendCell
        if kwarg_name == "presentations":
            return LegendPresentation
        # merges are handled as plain strings
        return None

    def _process_section_data(
        self,
        section: dict[str, list[str]],
        config: SectionConfig,
    ) -> object | list[object] | None:
        """Override section processing for Legend to handle Text-Cell relationships."""
        if config.kwarg_name == "cells":
            # Custom processing for cells: group Text sections with Cell sections
            return self._process_cells_with_text(section)
        if config.kwarg_name == "_text_lines":
            # Skip _text_lines since we handle them in cells processing
            return None
        if config.kwarg_name == "merges":
            # Handle merges as plain strings (remove the #Merge prefix)
            return section.get("#Merge ", [])
        # Use default processing for other sections
        return super()._process_section_data(section, config)

    def _process_cells_with_text(self, _section: dict[str, list[str]]) -> list[LegendCell]:
        """Process Cell sections and associate Text sections with them.

        Parses the raw section to maintain ordering of Cell and Text lines,
        allowing multiple Text lines per Cell.
        """
        cells = []

        # Parse raw section line by line to maintain Cell-Text ordering
        lines = self._current_raw_section.split("\n")

        current_cell_data: dict[str, Any] | None = None
        current_text_lines: list[str] = []

        for raw_line in lines:
            line = raw_line.strip()

            if line.startswith("#Cell "):
                # Save previous cell if it exists
                if current_cell_data is not None:
                    cells.append(
                        LegendCell(
                            row=current_cell_data.get("Row", 1),
                            column=current_cell_data.get("Column", 1),
                            text_size=current_cell_data.get("TextSize", 20),
                            text_lines=current_text_lines.copy(),
                        )
                    )

                # Start new cell
                cell_line = line[6:]  # Remove "#Cell " prefix
                current_cell_data = self._parse_cell_properties(cell_line)
                current_text_lines = []

            elif line.startswith("#Text "):
                # Add text line to current cell
                if current_cell_data is not None:
                    text_content = line[6:]  # Remove "#Text " prefix
                    current_text_lines.append(text_content)

            elif line.startswith("#") and not line.startswith("#Text ") and current_cell_data is not None:
                # Hit a different section type, save current cell
                cells.append(
                    LegendCell(
                        row=current_cell_data.get("Row", 1),
                        column=current_cell_data.get("Column", 1),
                        text_size=current_cell_data.get("TextSize", 20),
                        text_lines=current_text_lines.copy(),
                    )
                )
                current_cell_data = None
                current_text_lines = []

        # Save last cell if exists
        if current_cell_data is not None:
            cells.append(
                LegendCell(
                    row=current_cell_data.get("Row", 1),
                    column=current_cell_data.get("Column", 1),
                    text_size=current_cell_data.get("TextSize", 20),
                    text_lines=current_text_lines.copy(),
                )
            )

        return cells

    def _parse_cell_properties(self, cell_line: str) -> dict[str, Any]:
        """Parse a Cell line into properties dict."""
        properties = {"Row": 1, "Column": 1, "TextSize": 20}

        # Simple parsing: "Row:1 Column:3 TextSize:20"
        parts = cell_line.split()
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                if key in ["Row", "Column", "TextSize"]:
                    with contextlib.suppress(ValueError):
                        properties[key] = int(value)

        return properties

    def handle(self, model: TNetworkLSType, raw: str) -> None:
        """Filter out special parameters during legend processing."""
        handler_name = type(self).__name__
        if not self.COMPONENT_CLS:
            msg = f"Subclass '{handler_name}' must define COMPONENT_CLS"
            raise NotImplementedError(msg)

        # Store raw section for cell-text parsing
        self._current_raw_section = raw

        sections = list(self.parse_sections(raw))
        if not sections:
            return

        for section in sections:
            kwargs: dict[str, Any] = {}
            try:
                for config in self.COMPONENT_CONFIG:
                    value = self._process_section_data(section, config)
                    kwargs[config.kwarg_name] = value

                # Filter out special parameters that shouldn't be passed to the constructor
                filtered_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_")}

                component_to_add = self.COMPONENT_CLS(**filtered_kwargs)
                component_to_add.register(model)

            except Exception as e:
                msg = f"Failed to process component in handler {handler_name}: {e!s}"
                logger.exception(msg)
                logger.debug("Component data that caused failure: %r", kwargs)
                raise type(e)(msg) from e
