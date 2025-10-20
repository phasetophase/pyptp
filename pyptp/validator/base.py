"""Building blocks for implementing validation rules.

Typical workflow for custom rules:

1. Subclass :class:`Validator`.
2. Set a unique ``name`` and the ``applies_to`` network types (``{"LS"}``,
   ``{"MS"}``, or both).
3. Inspect the provided network in :meth:`Validator.validate` and return a list
   of :class:`Issue` instances describing any problems you found.
4. Wrap the returned issues in a :class:`Report` if you need to serialise or
   forward the results.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum, Flag, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class ValidatorCategory(Flag):
    """Categories for organizing and filtering validators.

    Use bitwise OR to combine categories. Validators can belong to multiple categories.

    Attributes:
        CORE: Essential validators that should run in most scenarios.
        ALL: Combination of all available categories (used as default).

    Example:
        >>> # Filter to only core validators
        >>> runner.run(categories=ValidatorCategory.CORE)
        >>> # Run all validators (default)
        >>> runner.run(categories=ValidatorCategory.ALL)

    """

    CORE = auto()
    ALL = CORE  # Currently CORE is all we have


class Severity(str, Enum):
    """Severity levels for validation issues.

    Attributes:
        ERROR: Network is invalid and cannot be safely analyzed or exported.
            Must be fixed before proceeding.
        WARNING: Network has issues that should be reviewed but analysis may
            still be possible. Indicates suboptimal or suspicious conditions.

    """

    ERROR = "error"
    WARNING = "warning"


@dataclass
class Issue:
    """Describe one validation finding including context about the affected asset.

    Fields map directly to the values surfaced in JSON output and user-facing
    tooling:

    - ``code``: short identifier for the rule that fired.
    - ``message``: explanation shown to end users.
    - ``severity``: one of :class:`Severity.ERROR` or :class:`Severity.WARNING`.
    - ``object_type`` / ``object_id``: help consumers locate the offending item.
    - ``validator``: echoes ``Validator.name`` so callers know which rule raised
      the issue.
    - ``details``: optional structured data with extra diagnostics.
    """

    code: str
    message: str
    severity: Severity
    object_type: str
    object_id: Any
    validator: str
    details: dict | None = None

    def to_dict(self) -> dict:
        """Serialize issue for JSON export or API responses."""
        return asdict(self)


@dataclass
class Report:
    """Container around a list of issues with helper serialization methods."""

    issues: list[Issue]

    def to_dict(self) -> dict:
        """Serialize this report to a structure composed of builtin types."""
        return {"issues": [i.to_dict() for i in self.issues]}

    def to_json(self) -> str:
        """Serialize this report to formatted JSON for logging or file output."""
        import json

        return json.dumps(self.to_dict(), indent=2)

    def summary(self) -> str:
        """Return high-level summary of validation results.

        Returns:
            Human-readable string summarizing issue counts by severity.
            Examples: "No issues found", "Found 5 issues: 3 error, 2 warning"

        """
        if not self.issues:
            return "No issues found"

        severity_counts: dict[Severity, int] = {}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        parts = [f"{count} {severity.value}" for severity, count in sorted(severity_counts.items())]
        return f"Found {len(self.issues)} issue{'s' if len(self.issues) != 1 else ''}: {', '.join(parts)}"


class Validator(ABC):
    """Base class that custom validators subclass to perform checks on a network.

    All validators must define:
    - name: Unique identifier for the validator
    - description: Human-readable description of what the validator checks
    - applies_to: Tuple of network types ("LV" for low-voltage, "MV" for medium-voltage, or both)
    - categories: ValidatorCategory flags indicating which validator groups this belongs to

    """

    name: str
    description: str
    applies_to: tuple[str, ...]
    categories: ValidatorCategory = ValidatorCategory.ALL

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate that subclasses define all required class attributes.

        Raises:
            TypeError: If required attributes are missing or empty.
            ValueError: If applies_to contains duplicates.

        """
        super().__init_subclass__(**kwargs)

        # Skip validation for abstract subclasses
        if ABC in cls.__bases__:
            return

        # Validate name
        if not hasattr(cls, "name") or not cls.name:
            msg = f"{cls.__name__} must define 'name' class attribute"
            raise TypeError(msg)

        # Validate description
        if not hasattr(cls, "description") or not cls.description:
            msg = f"{cls.__name__} must define 'description' class attribute"
            raise TypeError(msg)

        # Validate applies_to
        if not hasattr(cls, "applies_to") or not cls.applies_to:
            msg = f"{cls.__name__} must define 'applies_to' class attribute"
            raise TypeError(msg)

        # Check for duplicates in applies_to
        if len(cls.applies_to) != len(set(cls.applies_to)):
            msg = f"{cls.__name__} applies_to contains duplicate values: {cls.applies_to}"
            raise ValueError(msg)

        # Validate categories
        if not hasattr(cls, "categories"):
            msg = f"{cls.__name__} must define 'categories' class attribute"
            raise TypeError(msg)

    @abstractmethod
    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Execute validation analysis on the provided network model.

        Args:
            network: Network model to analyze (LV or MV based on applies_to)

        Returns:
            List of validation issues found, empty if network is valid.

        Raises:
            Should handle internal errors gracefully - framework catches exceptions.

        """
        ...
