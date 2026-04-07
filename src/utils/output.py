"""
Helpers for JSON output formatting, logging setup, and file writing.

Used by all modules. Do not modify without team agreement.

SOMMAIRE (navigation rapide soutenance) :
─────────────────────────────────────────
- setup_logging()     : Configure le logging global (appelé une seule fois dans main.py)
- save_result_json()  : Sauvegarde un résultat JSON horodaté dans output/logs/
- print_result()      : Affiche un résultat JSON en couleur (Rich) ou brut
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# --- CONFIG LOGGING GLOBAL ---------------------------------------------------
# Appelé UNE SEULE FOIS dans main.py. Configure le format des logs :
# "2026-04-07 14:30:00 [INFO] src.modules.backup — Backup action=backup_database..."
# Les modules utilisent ensuite logging.getLogger(__name__) pour loguer.
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


# --- SAUVEGARDE RESULTAT EN JSON HORODATE ------------------------------------
# Écrit le résultat d'un module dans output/logs/YYYYMMDD_HHMMSS_module_func.json
# Permet de garder un historique de toutes les exécutions pour audit/traçabilité.
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

    from src.utils.validation import sanitize_filename_part

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    module = sanitize_filename_part(result.get("module", "unknown"))
    function = sanitize_filename_part(result.get("function", "unknown"))
    filename = f"{timestamp}_{module}_{function}.json"

    filepath = logs_dir / filename
    filepath.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    return filepath


# --- AFFICHAGE RESULTAT (RICH OU BRUT) ---------------------------------------
# Si Rich est installé → affichage JSON coloré et indenté dans le terminal.
# Sinon → fallback json.dumps() en texte brut.
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
