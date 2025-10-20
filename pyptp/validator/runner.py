"""Runtime glue that discovers validators and executes them against a network."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Issue, Report, Severity, ValidatorCategory
from .registry import discover_validators

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class CheckRunner:
    """Discover validators for the requested network type and run them."""

    def __init__(self, network: NetworkLV | NetworkMV, network_type: str | None = None) -> None:
        """Initialize validation runner for the specified network and type.

        Args:
            network: Network model to validate (LV or MV)
            network_type: Type identifier ('LV' for low-voltage/Gaia, 'MV' for medium-voltage/Vision).
                If not provided, automatically detected from network class name.

        Raises:
            ValueError: If network_type cannot be auto-detected from network class.

        """
        self.network = network

        # Auto-detect network type if not provided
        if network_type is None:
            class_name = network.__class__.__name__
            if "LV" in class_name or class_name.endswith("LS"):
                network_type = "LV"
            elif "MV" in class_name or class_name.endswith("MS"):
                network_type = "MV"
            else:
                msg = (
                    f"Cannot auto-detect network type from class '{class_name}'. "
                    "Please specify network_type explicitly."
                )
                raise ValueError(msg)

        self.network_type = network_type

        raw = discover_validators()
        self.validators = [v() for v in raw if network_type in getattr(v, "applies_to", ())]

    def run(
        self,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        categories: ValidatorCategory = ValidatorCategory.ALL,
    ) -> Report:
        """Run validators filtered by optional include/exclude lists and categories.

        Args:
            include: Only run validators with these names (None = all)
            exclude: Skip validators with these names (None = skip none)
            categories: Only run validators in these categories (default: ALL)

        Returns:
            Report containing all validation issues found.

        """
        to_run = [
            v
            for v in self.validators
            if (include is None or v.name in include)
            and (exclude is None or v.name not in exclude)
            and (v.categories & categories)  # Check if validator matches any of the requested categories
        ]

        issues = []
        for validator in to_run:
            try:
                issues.extend(validator.validate(self.network))
            except (RuntimeError, ValueError) as e:
                issues.append(
                    Issue(
                        code="validator_crash",
                        message=f"{validator.name} crashed: {e}",
                        severity=Severity.ERROR,
                        object_type="-",
                        object_id="-",
                        validator=validator.name,
                    ),
                )
        return Report(issues)

    def run_all(self) -> Report:
        """Run every validator compatible with the network type."""
        return self.run()

    def list_available(self) -> list[dict]:
        """List available validators for this network type with metadata.

        Returns:
            List of dicts containing validator metadata:
            - name: Validator identifier
            - description: Human-readable description
            - applies_to: Tuple of network types this validator supports

        Note:
            Users can filter the returned list themselves using list comprehensions
            or standard Python filtering techniques.

        """
        return [
            {
                "name": v.name,
                "description": v.description,
                "applies_to": v.applies_to,
            }
            for v in self.validators
        ]
