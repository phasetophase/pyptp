"""Version migrator utilities.

Convert and validate `.GNF` and `.VNF` network files via the bundled native
libraries (DLL on Windows, SO on Linux), which contain the Gaia and Vision file
loaders. Used by the importers, exporters and the native loader validator.
"""

from __future__ import annotations

import ctypes
import functools
import shutil
import stat
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from pyptp.ptp_log import logger

ERR_SUCCESS: int = 0
ERR_LOAD_FAILURE: int = 1
ERR_SAVE_FAILURE: int = 2
ERR_INVALID_VERSION: int = 3
ERR_NETWORK_INVALID: int = 4

# Human-readable messages mapped to native return codes
MESSAGES: dict[int, str] = {
    ERR_SUCCESS: "Conversion successful",
    ERR_LOAD_FAILURE: "Failed to load the input file.",
    ERR_SAVE_FAILURE: "Failed to save the output file.",
    ERR_INVALID_VERSION: "Invalid version string provided.",
    ERR_NETWORK_INVALID: "The network file contains errors.",
}

# Timing-related failures; version and content errors are deterministic.
_RETRYABLE_CODES: frozenset[int] = frozenset({ERR_LOAD_FAILURE, ERR_SAVE_FAILURE})

_MSG_ERROR: int = 0
_MSG_WARNING: int = 1

__all__ = ["NativeResult", "convert_file", "migrate_and_read", "native_library_available", "save_as", "validate_file"]

LoaderType = Callable[[str], ctypes.CDLL]

_FUNCTYPE = ctypes.WINFUNCTYPE if sys.platform == "win32" else ctypes.CFUNCTYPE
_MessageProc = _FUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)


@dataclass
class NativeResult:
    """Outcome of a native conversion or validation call.

    Attributes:
        code: Native return code, one of the ``ERR_*`` constants.
        errors: Loader errors.
        warnings: Loader warnings.

    """

    code: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether the native call succeeded."""
        return self.code == ERR_SUCCESS

    @property
    def summary(self) -> str:
        """Human-readable meaning of the return code."""
        return MESSAGES.get(self.code, f"Unknown error occurred. Error code: {self.code}")

    def describe(self) -> str:
        """Return the summary followed by every loader error and warning, one per line."""
        lines = [self.summary]
        lines.extend(f"  error: {text}" for text in self.errors)
        lines.extend(f"  warning: {text}" for text in self.warnings)
        return "\n".join(lines)


class _MessageCollector:
    """Receive loader messages from the native library through a ctypes callback."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        # ctypes callbacks must stay referenced while the native call runs
        self.callback = _MessageProc(self._receive)

    def _receive(self, kind: int, text: bytes | None) -> None:
        decoded = (text or b"").decode("utf-8", errors="replace").strip()
        target = {_MSG_ERROR: self.errors, _MSG_WARNING: self.warnings}.get(kind, self.errors)
        target.append(decoded)

    def result(self, code: int) -> NativeResult:
        return NativeResult(code=code, errors=self.errors, warnings=self.warnings)


def _resolve_library(file_type: str) -> tuple[str, LoaderType]:
    """Return the native library filename and loader for this platform."""
    platform = sys.platform

    if file_type not in {"GNF", "VNF"}:
        msg = f"Unsupported file type '{file_type}'"
        raise ValueError(msg)

    if sys.platform == "win32":
        names = {"GNF": "GaiaMigrator.dll", "VNF": "VisionMigrator.dll"}
        loader: LoaderType = ctypes.WinDLL
    elif sys.platform == "linux":
        names = {"GNF": "libGaiaMigrator.so", "VNF": "libVisionMigrator.so"}
        loader = ctypes.CDLL
    else:
        msg = f"Unsupported platform '{platform}'"
        raise RuntimeError(msg)

    return names[file_type], loader


def _file_type_for(path: str | Path) -> str:
    """Return "GNF" or "VNF" based on the file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".gnf":
        return "GNF"
    if suffix == ".vnf":
        return "VNF"
    msg = f"Input file '{path}' is not a .gnf or .vnf file."
    raise ValueError(msg)


@functools.lru_cache(maxsize=2)
def _load_library(file_type: str) -> ctypes.CDLL:
    """Load the native library for the file type and declare its exports.

    Raises:
        ValueError: If the file type is not GNF or VNF.
        RuntimeError: If the platform has no native library.
        FileNotFoundError: If the library is missing from the package.
        OSError: If the library cannot be loaded.

    """
    library_name, loader = _resolve_library(file_type)
    library_path = Path(__file__).with_name(library_name)
    if not library_path.exists():
        msg = f"{library_name} not found at {library_path}"
        raise FileNotFoundError(msg)

    native_lib = loader(str(library_path))
    native_lib.ConvertNetworkFile.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        _MessageProc,
    ]
    native_lib.ConvertNetworkFile.restype = ctypes.c_int
    native_lib.ValidateNetworkFile.argtypes = [ctypes.c_char_p, _MessageProc]
    native_lib.ValidateNetworkFile.restype = ctypes.c_int
    return native_lib


def native_library_available(file_type: str) -> bool:
    """Return whether the native library for "GNF" or "VNF" files can be loaded on this platform."""
    try:
        _load_library(file_type)
    except (ValueError, RuntimeError, OSError):
        return False
    return True


def _log_result(action: str, result: NativeResult) -> None:
    """Log the outcome of a native call, one line per loader message."""
    if result.ok:
        logger.debug("%s finished successfully.", action)
    else:
        logger.error("%s failed: %s", action, result.summary)
    for text in result.errors:
        logger.error("  %s", text)
    for text in result.warnings:
        logger.warning("  %s", text)


def convert_file(
    input_path: str | Path,
    output_dir: str | Path,
    output_file: str,
    version: str = "Latest",
) -> NativeResult:
    """Convert a GNF or VNF file to another version using the native migrator.

    Args:
        input_path: Path to the input `.gnf` or `.vnf` file.
        output_dir: Directory where the converted file should be written.
        output_file: File name for the converted file in the output directory.
        version: Target version (e.g., "G8.9" or "V9.9"). Use "Latest" to pick the
            highest supported version for the file type.

    Returns:
        The native return code together with every loader error and warning.
        A failed conversion leaves no output file.

    """
    logger.debug(
        "Starting migration: input='%s', output_dir='%s', output_file='%s', version='%s'",
        input_path,
        output_dir,
        output_file,
        version,
    )

    try:
        file_type = _file_type_for(input_path)
        native_lib = _load_library(file_type)
    except (ValueError, RuntimeError, OSError) as exc:
        logger.error("Migration failed: %s", exc)
        return NativeResult(code=ERR_LOAD_FAILURE, errors=[str(exc)])

    target_version = version
    if target_version == "Latest":
        target_version = "V9.9" if file_type == "VNF" else "G8.9"

    logger.debug("Using %s library for target version '%s'", file_type, target_version)

    collector = _MessageCollector()
    code = native_lib.ConvertNetworkFile(
        str(input_path).encode("utf-8"),
        str(output_dir).encode("utf-8"),
        output_file.encode("utf-8"),
        target_version.encode("utf-8"),
        collector.callback,
    )
    result = collector.result(code)
    _log_result("Migration", result)
    return result


def validate_file(path: str | Path, *, normalize_encoding: bool = False) -> NativeResult:
    """Load a GNF or VNF file with the Gaia or Vision loader without converting it.

    Args:
        path: Path to the `.gnf` or `.vnf` file.
        normalize_encoding: Validate a UTF-8 copy of the file instead of the file itself.

    Returns:
        The native return code together with every loader error and warning.
        ``ERR_LOAD_FAILURE`` means the file itself could not be read (missing,
        locked, unknown version); ``ERR_NETWORK_INVALID`` means the file was read
        but the loader rejected part of its content.

    """
    logger.debug("Validating network file '%s'", path)

    try:
        file_type = _file_type_for(path)
        native_lib = _load_library(file_type)
    except (ValueError, RuntimeError, OSError) as exc:
        logger.error("Validation failed: %s", exc)
        return NativeResult(code=ERR_LOAD_FAILURE, errors=[str(exc)])

    collector = _MessageCollector()
    if normalize_encoding:
        with tempfile.TemporaryDirectory() as temp_dir:
            normalized = _write_utf8_copy(Path(path), Path(temp_dir))
            code = native_lib.ValidateNetworkFile(str(normalized).encode("utf-8"), collector.callback)
    else:
        code = native_lib.ValidateNetworkFile(str(path).encode("utf-8"), collector.callback)
    result = collector.result(code)
    _log_result("Validation", result)
    return result


def save_as(
    input_path: str,
    output_path: str,
    output_file: str,
    version: str = "Latest",
) -> str:
    """Convert a GNF or VNF file to another version using the native migrator.

    Thin wrapper around :func:`convert_file` that reports the outcome as text.

    Args:
        input_path: Path to the input `.gnf` or `.vnf` file.
        output_path: Directory where the converted file should be written.
        output_file: File name for the converted file in the output directory.
        version: Target version (e.g., "G8.9" or "V9.9"). Use "Latest" to pick the
            highest supported version for the file type.

    Returns:
        Message describing the result. On success: "Conversion successful"; otherwise
        an error description followed by the loader errors and warnings.

    """
    return convert_file(input_path, output_path, output_file, version).describe()


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


def _diagnose_migration_input(original: Path, normalized: Path) -> None:
    """Log diagnostics for a file that failed native migration."""
    # Original file
    if not original.exists():
        logger.warning("  [diagnostic] Original file missing: %s", original)
        return

    orig_size = original.stat().st_size
    logger.warning("  [diagnostic] Original file: %d bytes", orig_size)

    # Normalized file
    if not normalized.exists():
        logger.warning("  [diagnostic] Normalized file missing: %s", normalized)
        return

    norm_stat = normalized.stat()
    norm_size = norm_stat.st_size
    mode = stat.filemode(norm_stat.st_mode)
    logger.warning("  [diagnostic] Normalized file: %d bytes, permissions: %s", norm_size, mode)

    if norm_size == 0:
        logger.warning("  [diagnostic] Normalized file is EMPTY, input may be corrupt")
        return

    # Read first 2 lines to check version and NETWORK marker
    try:
        with normalized.open(encoding="utf-8") as f:
            line1 = f.readline().strip()
            line2 = f.readline().strip()
    except OSError:
        logger.warning("  [diagnostic] Could not read normalized file")
        return

    logger.warning("  [diagnostic] Version line: '%s'", line1)

    if line2 != "NETWORK":
        logger.warning("  [diagnostic] Second line is '%s', expected 'NETWORK'", line2)

    # Check temp dir is writable
    tmp_dir = normalized.parent
    try:
        probe = tmp_dir / "_probe_write_test"
        probe.write_text("test")
        probe.unlink()
    except OSError:
        logger.warning("  [diagnostic] Temp directory not writable: %s", tmp_dir)

    try:
        free_mb = shutil.disk_usage(str(tmp_dir)).free / (1024 * 1024)
        logger.warning("  [diagnostic] Free disk space in temp dir: %.0f MB", free_mb)
    except OSError:
        pass


def _write_utf8_copy(input_path: Path, target_dir: Path) -> Path:
    """Write a UTF-8 copy of a network file that may use a legacy encoding.

    Args:
        input_path: Network file in UTF-8 (with or without BOM), cp1252 or latin-1.
        target_dir: Directory for the copy.

    Returns:
        Path of the UTF-8 copy.

    """
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

    logger.debug("Read input file '%s' with encoding '%s'", input_path.name, detected_encoding)

    normalized_input = target_dir / f"_utf8_{input_path.name}"
    normalized_input.write_text(content, encoding="utf-8")
    return normalized_input


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
    the migration if needed. Version and content errors are not retried.

    Args:
        input_path: Path to the input .gnf or .vnf file.
        version: Target version (e.g., "G8.9" or "V9.9").
        encoding: Encoding to use when reading the migrated file.
        max_retries: Maximum number of migration attempts.
        file_wait_timeout: Seconds to wait for output file per attempt.

    Returns:
        Content of the migrated file as a string.

    Raises:
        RuntimeError: If migration fails. The message includes the loader errors.

    """
    last_error = ""

    for attempt in range(1, max_retries + 1):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            output_file = output_dir / input_path.name

            # Normalize input to UTF-8 for DLL compatibility with legacy encodings
            normalized_input = _write_utf8_copy(input_path, output_dir)

            result = convert_file(
                input_path=normalized_input,
                output_dir=output_dir,
                output_file=input_path.name,
                version=version,
            )

            if not result.ok:
                last_error = result.describe()
                if result.code not in _RETRYABLE_CODES:
                    break
                logger.warning(
                    "Migration attempt %d/%d failed for '%s': %s",
                    attempt,
                    max_retries,
                    input_path.name,
                    result.summary,
                )
                if attempt == 1:
                    _diagnose_migration_input(input_path, normalized_input)
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

    msg = f"Failed to migrate '{input_path.name}': {last_error}"
    raise RuntimeError(msg)
