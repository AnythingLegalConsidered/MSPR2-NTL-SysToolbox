"""
NTL-SysToolbox — Configuration loader.

Loads YAML config and resolves ${VAR} placeholders from environment variables.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from src.interfaces import ModuleConfigError

logger = logging.getLogger(__name__)

_ENV_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_MAX_RESOLVE_DEPTH = 20


def _resolve_env_vars(
    data: Any, unresolved: list[str] | None = None, _depth: int = 0,
) -> Any:
    """Recursively replace ${VAR} placeholders with environment variables.

    If a variable is not set, logs a warning and keeps the raw placeholder.
    When unresolved list is provided, collects unresolved variable names.

    Raises:
        ModuleConfigError: If recursion depth exceeds _MAX_RESOLVE_DEPTH.
    """
    if _depth > _MAX_RESOLVE_DEPTH:
        raise ModuleConfigError(
            f"Config nesting too deep (>{_MAX_RESOLVE_DEPTH} levels). "
            "Check for circular references in config."
        )

    if isinstance(data, str):
        def _replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            value = os.environ.get(var_name)
            if value is None:
                logger.warning("Environment variable %s is not set", var_name)
                if unresolved is not None:
                    unresolved.append(var_name)
                return match.group(0)
            return value
        return _ENV_VAR_PATTERN.sub(_replacer, data)

    if isinstance(data, dict):
        return {
            key: _resolve_env_vars(val, unresolved, _depth + 1)
            for key, val in data.items()
        }

    if isinstance(data, list):
        return [_resolve_env_vars(item, unresolved, _depth + 1) for item in data]

    return data


def load_config(config_path: str = "config/config.yaml", strict: bool = False) -> dict[str, Any]:
    """Load YAML configuration and resolve environment variable placeholders.

    1. Loads .env file (if present) via python-dotenv
    2. Reads the YAML config file
    3. Replaces ${VAR} placeholders with actual env var values

    Args:
        config_path: Path to the YAML config file.
        strict: If True, raise ModuleConfigError when env vars are unresolved.

    Returns:
        Configuration dict with resolved values.

    Raises:
        ModuleConfigError: If the config file does not exist, is invalid,
            or has unresolved env vars in strict mode.
    """
    # Load .env relative to the config file location (not CWD)
    config_dir = Path(config_path).parent
    env_file = config_dir / ".env"
    if env_file.is_file():
        load_dotenv(env_file)
    else:
        load_dotenv()

    path = Path(config_path)
    if not path.is_file():
        raise ModuleConfigError(
            f"Config file not found: {path.resolve()}. "
            f"Copy config/config.example.yaml to {config_path} and fill in your values."
        )

    try:
        raw = path.read_text(encoding="utf-8")
        config = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ModuleConfigError(f"Invalid YAML in {config_path}: {exc}") from exc

    if not isinstance(config, dict):
        raise ModuleConfigError(f"Config file {config_path} must contain a YAML mapping, got {type(config).__name__}")

    unresolved: list[str] = []
    resolved = _resolve_env_vars(config, unresolved)

    if strict and unresolved:
        raise ModuleConfigError(
            f"Variables d'environnement non definies: {', '.join(sorted(set(unresolved)))}. "
            "Verifiez votre fichier .env."
        )

    logger.debug("Configuration loaded from %s", path.resolve())
    return resolved
