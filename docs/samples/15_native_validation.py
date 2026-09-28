"""Check networks and files with the Gaia or Vision loader."""

from pathlib import Path

from pyptp import NetworkMV, configure_logging
from pyptp.convert.version_migrator import validate_file
from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.ptp_log import logger
from pyptp.validator import CheckRunner, ValidatorCategory

# Enable logging
configure_logging(level="INFO")

# A measure field without an in-object: Vision refuses to load it
network = NetworkMV()
MeasureFieldMV(general=MeasureFieldMV.General(), presentations=[]).register(network)

# The native_loader validator reports what the loader rejects
report = CheckRunner(network).run()
for issue in report.issues:
    if issue.validator == "native_loader":
        logger.error("%s %s: %s", issue.object_type, issue.object_id, issue.message)

# Python validators only
report = CheckRunner(network).run(categories=ValidatorCategory.CORE)

# save() runs the same check and raises when the loader rejects the network
try:
    network.save("draft.vnf")
except RuntimeError as exc:
    logger.error("%s", exc)

# Skip the check to write the file anyway
network.save("draft.vnf", native_check=False)

# Check an existing file without building a network
result = validate_file("draft.vnf")
if not result.ok:
    logger.error("%s", result.describe())

# parse the file without the check
network = NetworkMV.from_file("draft.vnf", native_check=False)

Path("draft.vnf").unlink()
