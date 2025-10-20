"""Validate network data quality."""

from pathlib import Path

from pyptp import NetworkMV, configure_logging
from pyptp.ptp_log import logger
from pyptp.validator import CheckRunner, Severity

# Enable logging
configure_logging(level="INFO")

# Load network
network = NetworkMV.from_file("network.vnf")

# Run validation
runner = CheckRunner(network)
report = runner.run()

# Check results
logger.info("Validation: {}", report.summary())

# Count issues by severity
error_count = sum(1 for issue in report.issues if issue.severity == Severity.ERROR)
warning_count = sum(1 for issue in report.issues if issue.severity == Severity.WARNING)
logger.info("  Errors: {}", error_count)
logger.info("  Warnings: {}", warning_count)

# Show critical issues
for issue in report.issues:
    if issue.severity == Severity.ERROR:
        logger.error("ERROR: {}", issue.message)
        logger.error("  Element: {} {}", issue.object_type, issue.object_id)

# Export report
Path("validation_report.txt").write_text(str(report.to_json()), encoding="utf-8")

# Check if network is valid
is_valid = error_count == 0
logger.info("Network valid: {}", is_valid)
