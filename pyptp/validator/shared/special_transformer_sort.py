"""Validator ensuring every special transformer has an explicit sort set."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.elements.enums import SpecialTransformerSort
from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class SpecialTransformerSortValidator(Validator):
    """Flag special transformers whose sort is still ``SpecialTransformerSort.NONE``.

    The NONE sentinel exists so users must pick a sort explicitly; picking a
    default would be a footgun given how strongly the sort influences network
    behaviour. Saving with NONE produces a file Vision/Gaia rejects with a
    cryptic ``geen soort`` load error, so we flag it here and block it at
    serialize time.
    """

    name = "special_transformer_sort"
    description = "Verifies every special transformer has an explicit sort (not NONE)"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Return an ERROR issue for each special transformer with sort=NONE."""
        issues: list[Issue] = []

        special_transformers = getattr(network, "special_transformers", {})

        for special_transformer in special_transformers.values():
            stype = getattr(special_transformer, "type", None)
            if stype is None:
                continue
            if stype.sort != SpecialTransformerSort.NONE:
                continue

            general = special_transformer.general
            name = getattr(general, "name", str(general.guid))
            issues.append(
                Issue(
                    code="special_transformer_sort_none",
                    message=(
                        f"Special transformer '{name}' has no sort set "
                        "(SpecialTransformerSort.NONE). Pick an explicit sort "
                        "before saving; Vision/Gaia cannot load a special "
                        "transformer without one."
                    ),
                    severity=Severity.ERROR,
                    object_type="SpecialTransformer",
                    object_id=general.guid,
                    validator=self.name,
                    details={"sort": int(stype.sort)},
                ),
            )

        return issues
