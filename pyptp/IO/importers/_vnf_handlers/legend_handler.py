"""Handler for parsing VNF Legend sections using a declarative recipe."""

from __future__ import annotations

import contextlib
from typing import Any, ClassVar

from pyptp.elements.mv.legend import LegendCell, LegendMV, LegendPresentation
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType
from pyptp.ptp_log import logger


class LegendHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Legend components using a declarative recipe.

    Handles legends with general properties, merge specifications, cells with text,
    and presentation properties for network documentation.
    """

    COMPONENT_CLS = LegendMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("merges", "#Merge ", required=False),
        SectionConfig("cells", "#Cell ", required=False),
        SectionConfig("_text_lines", "#Text ", required=False),  # Underscore means we handle it specially
        # TODO this is ugly and should be made uniform with the rest of the lib.
        SectionConfig("presentations", "#Presentation ", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Legend-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "general":
            return LegendMV.General
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

    def _process_cells_with_text(self, section: dict[str, list[str]]) -> list[LegendCell]:
        """Process Cell sections and associate Text sections with them."""
        cells = []
        cell_lines = section.get("#Cell ", [])
        text_lines = section.get("#Text ", [])

        # Associate each text line with the preceding cell
        # This assumes Text sections follow their corresponding Cell sections
        text_index = 0

        for cell_line in cell_lines:
            # Parse cell properties
            cell_data = self._parse_cell_properties(cell_line)

            # Collect text lines for this cell
            # In the VNF format, text lines appear after their cell
            # We'll collect text lines until we hit the next cell or end
            cell_text_lines = []

            # For now, assume 1:1 relationship (each cell has one text line)
            # This is a simplification - in reality we'd need more complex logic
            if text_index < len(text_lines):
                cell_text_lines.append(text_lines[text_index])
                text_index += 1

            # Create LegendCell with text lines
            cell = LegendCell(
                row=cell_data.get("Row", 1),
                column=cell_data.get("Column", 1),
                text_size=cell_data.get("TextSize", 20),
                text_lines=cell_text_lines,
            )
            cells.append(cell)

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

    def handle(self, model: TNetworkMSType, raw: str) -> None:
        """Filter out special parameters during legend processing."""
        handler_name = type(self).__name__
        if not self.COMPONENT_CLS:
            msg = f"Subclass '{handler_name}' must define COMPONENT_CLS"
            raise NotImplementedError(msg)

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
