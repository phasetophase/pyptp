"""Native loader validator for both LV and MV networks.

Saves the network and runs the Gaia or Vision loader on the file. The loader's
own errors and warnings are reported as issues.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from pyptp.convert.version_migrator import NativeResult, native_library_available, validate_file
from pyptp.elements.element_utils import Guid
from pyptp.ptp_log import logger
from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV

# Loader messages start with the object description, e.g. "Meetveld {GUID} in Station 1: ..."
_OBJECT_PATTERN = re.compile(r"^(?P<type>[^{:]+?)\s*\{(?P<guid>[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12})\}")


def _object_reference(text: str) -> tuple[str, Guid | None]:
    """Extract the object type and GUID a loader message refers to, if any."""
    match = _OBJECT_PATTERN.match(text)
    if match is None:
        return "Network", None
    return match.group("type").strip(), Guid(match.group("guid"))


def issues_from_native_result(result: NativeResult, validator_name: str) -> list[Issue]:
    """Translate loader errors and warnings into validation issues.

    Args:
        result: Outcome of a native validation or conversion call.
        validator_name: Value for the ``validator`` field of each issue.

    Returns:
        One issue per loader message. Messages that name an object carry its
        type and GUID; file-level messages use object type "Network".

    """
    issues: list[Issue] = []
    groups = (
        (Severity.ERROR, "native_load_error", result.errors),
        (Severity.WARNING, "native_load_warning", result.warnings),
    )
    for severity, code, texts in groups:
        for text in texts:
            object_type, object_id = _object_reference(text)
            issues.append(
                Issue(
                    code=code,
                    message=text,
                    severity=severity,
                    object_type=object_type,
                    object_id=object_id,
                    validator=validator_name,
                    details={"native_code": result.code},
                ),
            )
    return issues


class NativeLoaderValidator(Validator):
    """Checks that the Gaia or Vision loader accepts the network as saved."""

    name = "native_loader"
    description = "Runs the Gaia or Vision loader on the saved network and reports its errors and warnings"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.NATIVE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Save the network to a temporary file and load it with the native loader.

        Args:
            network: Network model to validate (LV or MV)

        Returns:
            One issue per loader message. Empty when no native library exists for this platform.

        """
        from pyptp.network_lv import NetworkLV

        file_type = "GNF" if isinstance(network, NetworkLV) else "VNF"
        if not native_library_available(file_type):
            logger.warning("Validator '%s' skipped: no native %s library for this platform", self.name, file_type)
            return []

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / f"{self.name}.{file_type.lower()}"
            network.save(path, native_check=False)
            result = validate_file(path)

        return issues_from_native_result(result, self.name)
