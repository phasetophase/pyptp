"""Logging Configuration Examples.

Shows how to configure PyPtP logging for different use cases.
"""

from pathlib import Path

from pyptp import NetworkLV
from pyptp.ptp_log import configure_logging, logger

# Example 1: Enable console logging at INFO level
configure_logging(level="INFO")

network = NetworkLV()
logger.info("Created network: {}", network)

# Example 2: Enable DEBUG logging for troubleshooting
configure_logging(level="DEBUG", colorize=True)

logger.debug("This is debug information")
logger.info("This is info")
logger.warning("This is a warning")

# Example 3: Log to file
log_file = Path("pyptp.log")
configure_logging(level="INFO", sink=log_file)

# Example 4: Custom format
configure_logging(
    level="INFO",
    format_string="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

# Example 5: Multiple sinks (console + file)
configure_logging(level="INFO", colorize=True)
configure_logging(level="DEBUG", sink="debug.log", colorize=False)

# Note: PyPtP is silent by default - no logging unless configured
