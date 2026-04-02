"""
Centralized validation helpers for NTL-SysToolbox.

Reusable input validation and sanitization functions used across modules.
"""

import ipaddress
import os
import re
from pathlib import Path

_SAFE_FILENAME_RE = re.compile(r"[^a-zA-Z0-9_\-]")


def sanitize_filename_part(name: str) -> str:
    """Sanitize a string for safe use as part of a filename.

    Replaces any character that is not alphanumeric, underscore, or hyphen
    with an underscore. Truncates to 50 characters.

    Args:
        name: Raw string (e.g. module name, function name).

    Returns:
        Safe filename fragment.
    """
    return _SAFE_FILENAME_RE.sub("_", name)[:50]


def validate_network_range(target_range: str) -> str | None:
    """Validate a network target range for nmap scanning.

    Accepts: single IPv4, CIDR notation, nmap-style ranges (192.168.1.1-50).
    Comma-separated lists of the above are also accepted.

    Args:
        target_range: Network range string.

    Returns:
        Error message string if invalid, None if valid.
    """
    if not target_range or not target_range.strip():
        return "Plage réseau vide"

    parts = target_range.replace(",", " ").split()
    for part in parts:
        # Strip nmap range suffix (e.g. "192.168.1.1-50" -> test "192.168.1.1")
        segments = part.split("-", 1)
        base = segments[0]

        # Validate the range suffix if present (must be an integer 0-255)
        if len(segments) == 2:
            try:
                range_end = int(segments[1])
                if not 0 <= range_end <= 255:
                    return f"Suffixe de plage hors limites (0-255): {part!r}"
            except ValueError:
                return f"Suffixe de plage invalide: {part!r}"

        try:
            ipaddress.ip_network(base, strict=False)
            continue
        except ValueError:
            pass
        try:
            ipaddress.ip_address(base)
            continue
        except ValueError:
            return f"Format de plage réseau invalide: {part!r}"

    return None


def validate_port(port: int) -> bool:
    """Check if a port number is within valid TCP/UDP range.

    Args:
        port: Port number to validate.

    Returns:
        True if 1 <= port <= 65535.
    """
    return 1 <= port <= 65535


def validate_path_within(path: str, allowed_dirs: list[str]) -> Path:
    """Validate that a path resolves under one of the allowed directories.

    Prevents path traversal attacks by resolving symlinks and checking
    that the result is a child of an allowed directory.

    Args:
        path: Path to validate.
        allowed_dirs: List of allowed parent directories.

    Raises:
        ValueError: If the path escapes all allowed directories.

    Returns:
        Resolved Path object.
    """
    resolved = Path(os.path.realpath(path))
    for allowed in allowed_dirs:
        allowed_resolved = Path(os.path.realpath(allowed))
        try:
            resolved.relative_to(allowed_resolved)
            return resolved
        except ValueError:
            continue

    raise ValueError(
        f"Chemin non autorisé: {path!r} "
        f"(doit être sous {', '.join(allowed_dirs)})"
    )
