"""Handler for parsing GNF GM Type sections.

Uses custom deserialization due to GMType's flattened data structure.
"""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.gm_type import GMTypeLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV
from pyptp.ptp_log import logger


class GMTypeHandler(DeclarativeHandler[NetworkLV]):
    """Handler for GM Type elements using custom deserialization."""

    COMPONENT_CLS = GMTypeLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("gm1", "#GM1 "),
        SectionConfig("gm2", "#GM2 "),
        SectionConfig("gm3", "#GM3 "),
        SectionConfig("gm4", "#GM4 "),
        SectionConfig("workdays1", "#WorkDays1 "),
        SectionConfig("workdays2", "#WorkDays2 "),
        SectionConfig("workdays3", "#WorkDays3 "),
        SectionConfig("workdays4", "#WorkDays4 "),
        SectionConfig("weekenddays1", "#WeekendDays1 "),
        SectionConfig("weekenddays2", "#WeekendDays2 "),
        SectionConfig("weekenddays3", "#WeekendDays3 "),
        SectionConfig("weekenddays4", "#WeekendDays4 "),
        SectionConfig("months1", "#Months1 "),
        SectionConfig("months2", "#Months2 "),
        SectionConfig("months3", "#Months3 "),
        SectionConfig("months4", "#Months4 "),
        SectionConfig("trendworkdays", "#TrendWorkDays "),
        SectionConfig("trendweekenddays", "#TrendWeekendDays "),
        SectionConfig("trendmonths", "#TrendMonths "),
    ]

    def handle(self, model: NetworkLV, raw: str) -> None:
        """Parse and register GM Type components using custom deserialization.

        Overrides base handler to use GMTypeLV's custom deserialize method
        due to its flattened data structure.
        """
        sections = list(self.parse_sections(raw))
        if not sections:
            return

        for section in sections:
            data = {}
            for config in self.COMPONENT_CONFIG:
                raw_data = section.get(config.gnf_tag, [])
                if raw_data:
                    parsed = [self._parse_gnf_line_to_dict(line) for line in raw_data]
                    data[config.kwarg_name] = parsed

            try:
                component = GMTypeLV.deserialize(data)
                component.register(model)
            except (ValueError, TypeError, KeyError) as e:
                msg = f"Failed to process GM Type component: {e}"
                logger.exception(msg)
                logger.debug("Component data that caused failure: %s", data)
                raise type(e)(msg) from e
