"""
NTL-SysToolbox — Contrat d'interface entre modules.

Ce fichier definit les structures communes que TOUS les modules doivent respecter.
Ne pas modifier sans accord de l'equipe.
"""

from datetime import datetime, timezone  # noqa: I001
from typing import Any


# ---------------------------------------------------------------------------
# Exit codes
# ---------------------------------------------------------------------------

EXIT_OK = 0        # Everything works
EXIT_WARNING = 1   # Degradation (CPU > threshold, disk > threshold...)
EXIT_CRITICAL = 2  # Service down, backup failed, fatal error
EXIT_UNKNOWN = 3   # Target unreachable, timeout


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class ModuleConfigError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class ModuleExecutionError(Exception):
    """Raised when a module function fails during execution."""
    pass


# ---------------------------------------------------------------------------
# Result builder
# ---------------------------------------------------------------------------

_VALID_STATUSES = {"OK", "WARNING", "CRITICAL", "UNKNOWN"}
_VALID_EXIT_CODES = {EXIT_OK, EXIT_WARNING, EXIT_CRITICAL, EXIT_UNKNOWN}


def build_result(
    module: str,
    function: str,
    status: str,
    exit_code: int,
    target: str,
    details: dict[str, Any],
    message: str,
) -> dict[str, Any]:
    """Build a standardized result dict.

    Every module function MUST return a dict built with this helper.

    Args:
        module: One of "diagnostic", "backup", "audit".
        status: One of "OK", "WARNING", "CRITICAL", "UNKNOWN".
        exit_code: One of EXIT_OK, EXIT_WARNING, EXIT_CRITICAL, EXIT_UNKNOWN.
        target: IP, hostname, database name, network range...
        details: Free-form dict with module-specific data.
        message: Human-readable description of the result.

    Returns:
        Standardized result dict.

    Raises:
        ValueError: If status or exit_code is invalid.
    """
    if status not in _VALID_STATUSES:
        raise ValueError(f"Invalid status {status!r}, must be one of {_VALID_STATUSES}")
    if exit_code not in _VALID_EXIT_CODES:
        raise ValueError(f"Invalid exit_code {exit_code!r}, must be one of {_VALID_EXIT_CODES}")

    return {
        "module": module,
        "function": function,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "exit_code": exit_code,
        "target": target,
        "details": details,
        "message": message,
    }
