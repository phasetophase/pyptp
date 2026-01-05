"""Gaussian Mixture (GM) profile types for LV networks.

Stores profile data with up to 4 distributions (GM1-GM4) and temporal factors
for workdays, weekends, and months. Profiles are referenced by network elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dataclasses_json import DataClassJsonMixin

from pyptp.elements.element_utils import string_field
from pyptp.elements.serialization_helpers import (
    serialize_properties,
    write_double,
    write_double_no_skip,
    write_integer,
    write_quote_string,
)
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV


@dataclass
class GMTypeLV:
    """GM profile type with up to 4 distributions and temporal factors.

    Profiles are identified by number and can contain multiple Gaussian mixture
    distributions with workday, weekend, and monthly scaling factors.
    """

    @dataclass
    class General(DataClassJsonMixin):
        """Core properties for GM type profiles.

        Attributes:
            number: Unique profile identifier.
            type: Profile type name (e.g., 'PV', 'EV').
            indicator: Category indicator (e.g., 'Load', 'HP').
            cos_phi: Power factor.
            correlation: Correlation coefficient.

        """

        number: int = 0
        type: str = string_field()
        indicator: str = string_field()
        cos_phi: float = 0.98
        correlation: float = 0.0

        def serialize(self) -> str:
            """Serialize to GNF format."""
            return serialize_properties(
                write_integer("Number", self.number),
                write_quote_string("GMtype", self.type),
                write_quote_string("Indicator", self.indicator),
                write_double_no_skip("CosPhi", self.cos_phi),
                write_double("Correlation", self.correlation, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> GMTypeLV.General:
            """Deserialize from GNF data with defensive type conversion."""
            cos_phi_raw = data.get("CosPhi", 0.98)
            cos_phi = float(str(cos_phi_raw).replace(",", ".")) if isinstance(cos_phi_raw, str) else cos_phi_raw

            correlation_raw = data.get("Correlation", 0.0)
            correlation = (
                float(str(correlation_raw).replace(",", ".")) if isinstance(correlation_raw, str) else correlation_raw
            )

            return cls(
                number=data.get("Number", 0),
                type=data.get("GMtype", ""),
                indicator=data.get("Indicator", ""),
                cos_phi=cos_phi,
                correlation=correlation,
            )

    @dataclass
    class Distribution(DataClassJsonMixin):
        """GM distribution with temporal factors.

        Attributes:
            average: Mean value.
            standard_deviation: Standard deviation.
            work_days: Workday factors (up to 96).
            weekend_days: Weekend factors (up to 96).
            Months: Monthly factors (up to 12).

        """

        average: float = 0.0
        standard_deviation: float = 0.0
        work_days: list[float] = field(default_factory=list)
        weekend_days: list[float] = field(default_factory=list)
        Months: list[float] = field(default_factory=list)

        def serialize(self) -> str:
            """Serialize distribution parameters (not temporal factors)."""
            return serialize_properties(
                write_double("Average", self.average, skip=0.0),
                write_double("StandardDeviation", self.standard_deviation, skip=0.0),
            )

        @classmethod
        def deserialize(cls, data: dict) -> GMTypeLV.Distribution:
            """Deserialize from GNF data (temporal factors set separately)."""
            return cls(
                average=data.get("Average", 0.0),
                standard_deviation=data.get("StandardDeviation", 0.0),
                work_days=[],
                weekend_days=[],
                Months=[],
            )

    @dataclass
    class Trend(DataClassJsonMixin):
        """Trend factors applied across all distributions.

        Attributes:
            work_days: Workday trend factors (up to 96).
            weekend_days: Weekend trend factors (up to 96).
            months: Monthly trend factors (up to 12).

        """

        work_days: list[float] = field(default_factory=list)
        weekend_days: list[float] = field(default_factory=list)
        months: list[float] = field(default_factory=list)

        def serialize(self) -> str:
            """Return empty string (parent handles serialization)."""
            return ""

        @classmethod
        def deserialize(cls, _data: dict) -> GMTypeLV.Trend:
            """Create empty instance (factors set by parent)."""
            return cls(
                work_days=[],
                weekend_days=[],
                months=[],
            )

    general: General

    # Distribution data stored in flattened structure for efficient serialization
    gm1_params: dict[str, Any] = field(default_factory=dict)
    gm1_workdays: list[float] = field(default_factory=list)
    gm1_weekenddays: list[float] = field(default_factory=list)
    gm1_months: list[float] = field(default_factory=list)

    gm2_params: dict[str, Any] = field(default_factory=dict)
    gm2_workdays: list[float] = field(default_factory=list)
    gm2_weekenddays: list[float] = field(default_factory=list)
    gm2_months: list[float] = field(default_factory=list)

    gm3_params: dict[str, Any] = field(default_factory=dict)
    gm3_workdays: list[float] = field(default_factory=list)
    gm3_weekenddays: list[float] = field(default_factory=list)
    gm3_months: list[float] = field(default_factory=list)

    gm4_params: dict[str, Any] = field(default_factory=dict)
    gm4_workdays: list[float] = field(default_factory=list)
    gm4_weekenddays: list[float] = field(default_factory=list)
    gm4_months: list[float] = field(default_factory=list)

    trend_workdays: list[float] = field(default_factory=list)
    trend_weekenddays: list[float] = field(default_factory=list)
    trend_months: list[float] = field(default_factory=list)

    @property
    def gm1(self) -> Distribution:
        """Assemble GM1 distribution from flattened data."""
        return self.Distribution(
            average=self.gm1_params.get("Average", 0.0),
            standard_deviation=self.gm1_params.get("StandardDeviation", 0.0),
            work_days=self.gm1_workdays,
            weekend_days=self.gm1_weekenddays,
            Months=self.gm1_months,
        )

    @property
    def gm2(self) -> Distribution:
        """Assemble GM2 distribution from flattened data."""
        return self.Distribution(
            average=self.gm2_params.get("Average", 0.0),
            standard_deviation=self.gm2_params.get("StandardDeviation", 0.0),
            work_days=self.gm2_workdays,
            weekend_days=self.gm2_weekenddays,
            Months=self.gm2_months,
        )

    @property
    def gm3(self) -> Distribution:
        """Assemble GM3 distribution from flattened data."""
        return self.Distribution(
            average=self.gm3_params.get("Average", 0.0),
            standard_deviation=self.gm3_params.get("StandardDeviation", 0.0),
            work_days=self.gm3_workdays,
            weekend_days=self.gm3_weekenddays,
            Months=self.gm3_months,
        )

    @property
    def gm4(self) -> Distribution:
        """Assemble GM4 distribution from flattened data."""
        return self.Distribution(
            average=self.gm4_params.get("Average", 0.0),
            standard_deviation=self.gm4_params.get("StandardDeviation", 0.0),
            work_days=self.gm4_workdays,
            weekend_days=self.gm4_weekenddays,
            Months=self.gm4_months,
        )

    @property
    def trend(self) -> Trend:
        """Assemble trend data from flattened fields."""
        return self.Trend(
            work_days=self.trend_workdays,
            weekend_days=self.trend_weekenddays,
            months=self.trend_months,
        )

    def register(self, network: NetworkLV) -> None:
        """Register GM type in network by profile number."""
        if self.general.number in network.gmtypes:
            logger.critical("GM type %s already exists, overwriting", self.general.number)
        network.gmtypes[self.general.number] = self

    def serialize(self) -> str:
        """Serialize GM type to GNF format."""
        lines = []
        lines.append(f"#General {self.general.serialize()}")
        for idx, gm in enumerate((self.gm1, self.gm2, self.gm3, self.gm4), start=1):
            has_params = gm.average != 0.0 or gm.standard_deviation != 0.0
            has_factors = any([gm.work_days, gm.weekend_days, gm.Months])
            if not has_params and not has_factors:
                continue
            if has_params:
                lines.append(f"#GM{idx} {gm.serialize()}")
            if gm.work_days:
                workdays_props = serialize_properties(
                    *[write_double_no_skip(f"f{i + 1}", v) for i, v in enumerate(gm.work_days)],
                )
                lines.append(f"#WorkDays{idx} {workdays_props} ")
            if gm.weekend_days:
                weekenddays_props = serialize_properties(
                    *[write_double_no_skip(f"f{i + 1}", v) for i, v in enumerate(gm.weekend_days)],
                )
                lines.append(f"#WeekendDays{idx} {weekenddays_props} ")
            if gm.Months:
                months_props = serialize_properties(
                    *[write_double_no_skip(f"f{i + 1}", v) for i, v in enumerate(gm.Months)],
                )
                lines.append(f"#Months{idx} {months_props} ")
        if self.trend.work_days:
            trend_workdays_props = serialize_properties(
                *[write_double_no_skip(f"f{i + 1}", v) for i, v in enumerate(self.trend.work_days)],
            )
            lines.append(f"#TrendWorkDays {trend_workdays_props}")
        if self.trend.weekend_days:
            trend_weekenddays_props = serialize_properties(
                *[write_double_no_skip(f"f{i + 1}", v) for i, v in enumerate(self.trend.weekend_days)],
            )
            lines.append(f"#TrendWeekendDays {trend_weekenddays_props} ")
        if self.trend.months:
            trend_months_props = serialize_properties(
                *[write_double_no_skip(f"f{i + 1}", v) for i, v in enumerate(self.trend.months)],
            )
            lines.append(f"#TrendMonths {trend_months_props} ")
        return "\n".join(lines)

    @classmethod
    def deserialize(cls, data: dict) -> GMTypeLV:
        """Deserialize GM type from GNF data with defensive type conversion."""
        general_data = data.get("general", [{}])[0] if data.get("general") else {}
        general = cls.General.deserialize(general_data)

        instance = cls(general=general)

        # Process each of the 4 possible Gaussian mixture distributions
        for idx in range(1, 5):
            gm_key = f"gm{idx}"
            gm_data = data.get(gm_key, [{}])[0] if data.get(gm_key) else {}
            if gm_data:
                average_raw = gm_data.get("Average", 0.0)
                average = float(str(average_raw).replace(",", ".")) if isinstance(average_raw, str) else average_raw

                std_dev_raw = gm_data.get("StandardDeviation", 0.0)
                std_dev = float(str(std_dev_raw).replace(",", ".")) if isinstance(std_dev_raw, str) else std_dev_raw

                setattr(
                    instance,
                    f"gm{idx}_params",
                    {
                        "Average": average,
                        "StandardDeviation": std_dev,
                    },
                )

            # Process temporal factors for this distribution
            for factor_type in ["workdays", "weekenddays", "months"]:
                factor_key = f"{factor_type}{idx}"
                factor_data = data.get(factor_key, [{}])[0] if data.get(factor_key) else {}
                if factor_data:
                    factors = []
                    for i in range(1, 97):
                        factor_key = f"f{i}"
                        if factor_key in factor_data:
                            value_raw = factor_data[factor_key]
                            value = float(str(value_raw).replace(",", ".")) if isinstance(value_raw, str) else value_raw
                            factors.append(value)
                        else:
                            break

                    if factor_type == "workdays":
                        setattr(instance, f"gm{idx}_workdays", factors)
                    elif factor_type == "weekenddays":
                        setattr(instance, f"gm{idx}_weekenddays", factors)
                    elif factor_type == "months":
                        setattr(instance, f"gm{idx}_months", factors)

        # Process trend factors that apply to all distributions
        for trend_type in ["workdays", "weekenddays", "months"]:
            trend_key = f"trend{trend_type}"
            trend_data = data.get(trend_key, [{}])[0] if data.get(trend_key) else {}
            if trend_data:
                factors = []
                for i in range(1, 97):
                    factor_key = f"f{i}"
                    if factor_key in trend_data:
                        value_raw = trend_data[factor_key]
                        value = float(str(value_raw).replace(",", ".")) if isinstance(value_raw, str) else value_raw
                        factors.append(value)
                    else:
                        break
                setattr(instance, f"trend_{trend_type}", factors)

        return instance
