"""
Module: [NOM DU MODULE]
Description: [DESCRIPTION]
Responsable: [PRENOM]

Instructions:
    1. Copier ce fichier sous le nom de votre module (diagnostic.py, backup.py, audit.py)
    2. Remplacer les placeholders [...]
    3. Implementer chaque fonction
    4. Chaque fonction DOIT utiliser build_result() pour son retour
    5. Chaque fonction DOIT catch ses exceptions (jamais de crash non gere)
"""

import logging
from typing import Any

from src.interfaces import (  # noqa: F401
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    EXIT_WARNING,
    ModuleConfigError,
    ModuleExecutionError,
    build_result,
)

logger = logging.getLogger(__name__)

MODULE_NAME = "[nom]"  # "diagnostic", "backup", or "audit"


def run(config: dict, target: str, **kwargs: Any) -> dict[str, Any]:
    """Main entry point for this module.

    Called by main.py menu. Delegates to specific functions based on kwargs.

    Args:
        config: Full config dict loaded from config.yaml.
        target: Target to operate on (IP, hostname, DB name, network range...).
        **kwargs: Module-specific arguments (e.g., table_name for CSV export).

    Returns:
        Standardized result dict (see interfaces.py).

    Raises:
        ModuleConfigError: Required config keys are missing.
        ModuleExecutionError: Execution failed.
    """
    logger.info("Starting %s on target: %s", MODULE_NAME, target)

    try:
        # --- Your module logic here ---
        result = build_result(
            module=MODULE_NAME,
            function="run",
            status="OK",
            exit_code=EXIT_OK,
            target=target,
            details={},
            message=f"{MODULE_NAME} completed successfully on {target}",
        )
        return result

    except ModuleConfigError:
        raise  # Let it propagate — main.py handles it

    except Exception as e:
        logger.error("%s execution failed: %s", MODULE_NAME, e)
        raise ModuleExecutionError(str(e)) from e


# ---------------------------------------------------------------------------
# Module-specific functions — implement below
# ---------------------------------------------------------------------------
# Each function should:
# 1. Accept (config, target, **kwargs) or specific args
# 2. Return build_result(...)
# 3. Catch its own exceptions and return UNKNOWN/CRITICAL, never crash
#
# Example:
#
# def check_something(config: dict, target: str) -> dict[str, Any]:
#     try:
#         # ... logic ...
#         return build_result(
#             module=MODULE_NAME,
#             function="check_something",
#             status="OK",
#             exit_code=EXIT_OK,
#             target=target,
#             details={"key": "value"},
#             message="Check passed",
#         )
#     except ConnectionError as e:
#         return build_result(
#             module=MODULE_NAME,
#             function="check_something",
#             status="UNKNOWN",
#             exit_code=EXIT_UNKNOWN,
#             target=target,
#             details={"error": str(e)},
#             message=f"Cannot reach {target}: {e}",
#         )
