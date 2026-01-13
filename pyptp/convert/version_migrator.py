"""Version migrator utilities.

Convert `.GNF` and `.VNF` network files to a target version via bundled native
libraries (DLL on Windows, SO on Linux). Used internally by importers; may also
be called directly.
"""

from __future__ import annotations

import ctypes
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from pyptp.ptp_log import logger

ERR_SUCCESS: int = 0
ERR_LOAD_FAILURE: int = 1
ERR_SAVE_FAILURE: int = 2
ERR_INVALID_VERSION: int = 3

# Human-readable messages mapped to native return codes
MESSAGES: dict[int, str] = {
    ERR_SUCCESS: "Conversion successful",
    ERR_LOAD_FAILURE: "Failed to load the input file.",
    ERR_SAVE_FAILURE: "Failed to save the output file.",
    ERR_INVALID_VERSION: "Invalid version string provided.",
}

__all__ = ["migrate_and_read", "save_as"]

LoaderType = Callable[[str], ctypes.CDLL]


def _resolve_library(file_type: str) -> tuple[str, LoaderType]:
    """Return the native library filename and loader for this platform."""
    platform = sys.platform

    if file_type not in {"GNF", "VNF"}:
        msg = f"Unsupported file type '{file_type}'"
        raise ValueError(msg)

    if platform.startswith("win"):
        names = {"GNF": "GaiaMigrator.dll", "VNF": "VisionMigrator.dll"}
        loader: LoaderType = ctypes.WinDLL
    elif platform.startswith("linux"):
        names = {"GNF": "libGaiaMigrator.so", "VNF": "libVisionMigrator.so"}
        loader = ctypes.CDLL
    else:
        msg = f"Unsupported platform '{platform}'"
        raise RuntimeError(msg)

    return names[file_type], loader


def save_as(
    input_path: str,
    output_path: str,
    output_file: str,
    version: str = "Latest",
) -> str:
    """Convert a GNF or VNF file to another version using the native migrator.

    Args:
        input_path: Path to the input `.gnf` or `.vnf` file.
        output_path: Directory where the converted file should be written.
        output_file: File name for the converted file in the output directory.
        version: Target version (e.g., "G8.9" or "V9.9"). Use "Latest" to pick the
            highest supported version for the file type.

    Returns:
        Message describing the result. On success: "Conversion successful"; otherwise
        an error description.

    """
    logger.debug(
        "Starting migration: input='%s', output_dir='%s', output_file='%s', version='%s'",
        input_path,
        output_path,
        output_file,
        version,
    )

    # Determine file type and select appropriate native library
    input_lower = input_path.lower()
    if input_lower.endswith(".gnf"):
        file_type = "GNF"
    elif input_lower.endswith(".vnf"):
        file_type = "VNF"
    else:
        logger.error("Migration failed: Input file '%s' is not a .gnf or .vnf file.", input_path)
        return MESSAGES[ERR_LOAD_FAILURE]

    try:
        library_name, loader = _resolve_library(file_type)
    except (ValueError, RuntimeError):
        logger.exception("Migration failed while resolving library")
        return MESSAGES[ERR_LOAD_FAILURE]

    library_path = Path(__file__).with_name(library_name)

    if not library_path.exists():
        logger.error("Migration failed: %s not found at %s", library_name, library_path)
        return MESSAGES[ERR_LOAD_FAILURE]

    # Set target version based on file type
    target_version = version
    if target_version == "Latest":
        if file_type == "VNF":
            target_version = "V9.9"
        elif file_type == "GNF":
            target_version = "G8.9"
        else:
            logger.error("Migration failed: Could not determine target version for file type '%s'", file_type)
            return MESSAGES[ERR_LOAD_FAILURE]

    logger.debug("Using %s for %s file, resolved target version to: '%s'", library_name, file_type, target_version)

    try:
        native_lib = loader(str(library_path))
    except OSError:
        logger.exception("Failed to load library at '%s'", library_path)
        return MESSAGES[ERR_LOAD_FAILURE]

    native_lib.ConvertNetworkFile.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
    ]
    native_lib.ConvertNetworkFile.restype = ctypes.c_int

    # Use encoding that matches the file type's importer/exporter
    encoding = "utf-8"

    input_path_arg = ctypes.create_string_buffer(input_path.encode(encoding))
    output_path_arg = ctypes.create_string_buffer(output_path.encode(encoding))
    output_file_arg = ctypes.create_string_buffer(output_file.encode(encoding))
    version_target_arg = ctypes.create_string_buffer(target_version.encode(encoding))

    logger.debug("Calling ConvertNetworkFile with final arguments")
    logger.debug("  -> Library: %s", library_name)
    logger.debug("  -> File Type: %s", file_type)
    logger.debug("  -> Input Path: %s", input_path_arg.value)
    logger.debug("  -> Output Dir: %s", output_path_arg.value)
    logger.debug("  -> Output File: %s", output_file_arg.value)
    logger.debug("  -> Target Version: %s", version_target_arg.value)

    result_code = native_lib.ConvertNetworkFile(
        input_path_arg,
        output_path_arg,
        output_file_arg,
        version_target_arg,
    )

    logger.debug("Library returned result code: %d", result_code)

    return_message = MESSAGES.get(result_code, f"Unknown error occurred. Error code: {result_code}")

    if result_code == ERR_SUCCESS:
        logger.debug("Migration finished successfully.")
    else:
        # Errors are already logged by the native library; we log a concise summary
        logger.error("Migration failed: %s", return_message)

    return return_message


def _wait_for_file(
    path: Path,
    timeout: float = 2.0,
    poll_interval: float = 0.1,
) -> bool:
    """Wait for a file to exist and be readable.

    Args:
        path: Path to the file to wait for.
        timeout: Maximum time to wait in seconds.
        poll_interval: Time between existence checks in seconds.

    Returns:
        True if file became available, False if timeout exceeded.

    """
    elapsed = 0.0
    while elapsed < timeout:
        if path.exists():
            try:
                # Try to open and read a byte to confirm it's accessible
                with path.open("rb") as f:
                    f.read(1)
                return True
            except OSError:
                pass
        time.sleep(poll_interval)
        elapsed += poll_interval
    return False


def migrate_and_read(
    input_path: Path,
    version: str,
    encoding: str = "utf-8",
    *,
    max_retries: int = 3,
    file_wait_timeout: float = 2.0,
) -> str:
    """Migrate a network file and return its content with retry logic.

    Handles potential race conditions with antivirus software or file system
    delays by waiting for the output file to become available and retrying
    the migration if needed.

    Args:
        input_path: Path to the input .gnf or .vnf file.
        version: Target version (e.g., "G8.9" or "V9.9").
        encoding: Encoding to use when reading the migrated file.
        max_retries: Maximum number of migration attempts.
        file_wait_timeout: Seconds to wait for output file per attempt.

    Returns:
        Content of the migrated file as a string.

    Raises:
        RuntimeError: If migration fails after all retries.

    """
    last_error = ""

    for attempt in range(1, max_retries + 1):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            output_file = output_dir / input_path.name

            # Normalize input to UTF-8 for DLL compatibility with legacy encodings
            content = None
            detected_encoding = None
            for enc in ("utf-8-sig", "cp1252", "latin-1"):
                try:
                    content = input_path.read_text(encoding=enc, errors="strict")
                    detected_encoding = enc
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                # Should not happen since latin-1 accepts all bytes
                content = input_path.read_text(encoding="latin-1", errors="replace")
                detected_encoding = "latin-1"

            logger.debug(
                "Read input file '%s' with encoding '%s'",
                input_path.name,
                detected_encoding,
            )

            normalized_input = output_dir / f"_utf8_{input_path.name}"
            normalized_input.write_text(content, encoding="utf-8")

            result = save_as(
                input_path=str(normalized_input),
                output_path=str(output_dir),
                output_file=input_path.name,
                version=version,
            )

            if "successful" not in str(result).lower():
                last_error = result
                logger.warning(
                    "Migration attempt %d/%d failed for '%s': %s",
                    attempt,
                    max_retries,
                    input_path.name,
                    result,
                )
                if attempt < max_retries:
                    time.sleep(0.5 * attempt)  # Exponential backoff
                continue

            # Wait for file to be available (handles AV scans, flush delays)
            if not _wait_for_file(output_file, timeout=file_wait_timeout):
                last_error = "Output file not available after migration reported success"
                logger.warning(
                    "Migration attempt %d/%d: file not ready for '%s'",
                    attempt,
                    max_retries,
                    input_path.name,
                )
                if attempt < max_retries:
                    time.sleep(0.5 * attempt)
                continue

            logger.debug("Migration successful on attempt %d.", attempt)
            return output_file.read_text(encoding=encoding, errors="ignore")

    msg = f"Failed to migrate '{input_path.name}' after {max_retries} attempts. Last error: {last_error}"
    raise RuntimeError(msg)
