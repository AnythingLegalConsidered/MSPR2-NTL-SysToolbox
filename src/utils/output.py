"""
Helpers for JSON output formatting, logging setup, and file writing.

Used by all modules. Do not modify without team agreement.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def setup_logging(log_level: str = "INFO", output_dir: str = "./output") -> None:
    """Configure logging for the entire application.

    Call this ONCE in main.py at startup. Modules use logging.getLogger(__name__).

    Args:
        log_level: One of "DEBUG", "INFO", "WARNING".
        output_dir: Base output directory.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def save_result_json(result: dict[str, Any], output_dir: str = "./output") -> Path:
    """Save a module result dict to a timestamped JSON log file.

    Args:
        result: Standardized result dict from build_result().
        output_dir: Base output directory.

    Returns:
        Path to the written file.
    """
    logs_dir = Path(output_dir) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    module = result.get("module", "unknown")
    function = result.get("function", "unknown")
    filename = f"{timestamp}_{module}_{function}.json"

    filepath = logs_dir / filename
    filepath.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    return filepath


def print_result(result: dict[str, Any]) -> None:
    """Pretty-print a result dict to the console using rich if available.

    Falls back to plain JSON if rich is not installed.

    Args:
        result: Standardized result dict.
    """
    try:
        from rich.console import Console
        from rich.json import JSON

        console = Console()
        console.print(JSON(json.dumps(result, default=str)))
    except ImportError:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
