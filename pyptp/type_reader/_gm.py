"""Convert rows of the GM type sheet to ``GMTypeLV`` input."""

from __future__ import annotations

DISTRIBUTION_COUNT = 4

QUARTER_HOURS_PER_DAY = 96

MONTHS_PER_YEAR = 12

INDICATOR_BY_SHEET_WORD = {
    "belasting": "Load",
    "belastingprocent": "LoadPercent",
    "wp": "HP",
    "ev": "EV",
    "pv": "PV",
    "apparaat": "Device",
    "koken": "Cooking",
}


def _factors(row: dict[str, object], prefix: str, count: int) -> list[float]:
    """Return one factor series, or an empty list when the row has none.

    A blank cell inside a series counts as zero.
    """
    values = [_number(row.get(f"{prefix}{index}]")) for index in range(1, count + 1)]
    if not any(values):
        return []
    return values


def _number(value: object) -> float:
    if value is None or value == "":
        return 0.0
    return float(str(value))


def _add_distribution(sections: dict[str, list[dict[str, object]]], row: dict[str, object], index: int) -> None:
    average = _number(row.get(f"Average[{index}]"))
    deviation = _number(row.get(f"Deviation[{index}]"))
    if not average and not deviation:
        return
    sections[f"gm{index}"] = [{"Average": average, "StandardDeviation": deviation}]


def _add_factors(
    sections: dict[str, list[dict[str, object]]],
    key: str,
    row: dict[str, object],
    prefix: str,
    count: int,
) -> None:
    values = _factors(row, prefix, count)
    if not values:
        return
    factors: dict[str, object] = {}
    for number, value in enumerate(values, start=1):
        factors[f"f{number}"] = value
    sections[key] = [factors]


def _indicator(value: object) -> str:
    """Return the indicator token for a sheet word. A blank cell counts as load."""
    word = str(value).strip()
    if not word:
        return "Load"
    indicator = INDICATOR_BY_SHEET_WORD.get(word.casefold())
    if indicator is None:
        msg = f"Unknown GM indicator {word!r}"
        raise ValueError(msg)
    return indicator


def gm_row_to_sections(row: dict[str, object]) -> dict[str, list[dict[str, object]]]:
    """Convert one GM sheet row to the dict ``GMTypeLV.deserialize`` takes."""
    name = str(row.get("Name", "")).strip()

    sections: dict[str, list[dict[str, object]]] = {
        "general": [
            {
                "GMtype": name,
                "Indicator": _indicator(row.get("Indicator", "")),
                "CosPhi": _number(row.get("Cos")) or 1.0,
                "Correlation": _number(row.get("Correlation")),
            }
        ],
    }

    for index in range(1, DISTRIBUTION_COUNT + 1):
        _add_distribution(sections, row, index)
        _add_factors(sections, f"workdays{index}", row, f"Workday[{index},", QUARTER_HOURS_PER_DAY)
        _add_factors(sections, f"weekenddays{index}", row, f"Weekend[{index},", QUARTER_HOURS_PER_DAY)
        _add_factors(sections, f"months{index}", row, f"Month[{index},", MONTHS_PER_YEAR)

    _add_factors(sections, "trendworkdays", row, "TrendWorkday[", QUARTER_HOURS_PER_DAY)
    _add_factors(sections, "trendweekenddays", row, "TrendWeekend[", QUARTER_HOURS_PER_DAY)
    _add_factors(sections, "trendmonths", row, "TrendMonth[", MONTHS_PER_YEAR)

    return sections
