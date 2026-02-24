"""
NTL-SysToolbox — Interactive CLI menu.

Entry point: python src/main.py
"""

import logging
import sys
from typing import Any

from src.config_loader import load_config
from src.interfaces import ModuleConfigError, ModuleExecutionError
from src.utils.output import print_result, save_result_json, setup_logging

logger = logging.getLogger(__name__)

# --- Module imports (graceful if not yet implemented) -----------------------

try:
    from src.modules import diagnostic  # type: ignore[attr-defined]
except ImportError:
    diagnostic = None  # type: ignore[assignment]

try:
    from src.modules import backup  # type: ignore[attr-defined]
except ImportError:
    backup = None  # type: ignore[assignment]

try:
    from src.modules import audit  # type: ignore[attr-defined]
except ImportError:
    audit = None  # type: ignore[assignment]


# --- Menu helpers -----------------------------------------------------------

MAIN_MENU = """
╔══════════════════════════════════╗
║        NTL-SysToolbox           ║
╠══════════════════════════════════╣
║  1. Diagnostic                  ║
║  2. Backup                      ║
║  3. Audit                       ║
║  0. Quitter                     ║
╚══════════════════════════════════╝
"""

DIAGNOSTIC_MENU = """
── Diagnostic ──────────────────────
  1. Vérifier AD/DNS (DC01)
  2. Vérifier MySQL (WMS-DB)
  3. Vérifier Windows Server (métriques)
  4. Vérifier Ubuntu (métriques)
  0. Retour
"""

BACKUP_MENU = """
── Backup ──────────────────────────
  1. Backup base de données (dump SQL)
  2. Export table en CSV
  0. Retour
"""

AUDIT_MENU = """
── Audit ───────────────────────────
  1. Scanner le réseau
  2. Lister les dates EOL
  3. Auditer depuis un CSV
  4. Générer le rapport complet
  0. Retour
"""

# Maps: sub-menu choice -> (function_kwarg_key, default_target_prompt)
DIAGNOSTIC_ACTIONS: dict[str, tuple[str, str]] = {
    "1": ("check_ad_dns", "IP du DC (défaut: dc01) : "),
    "2": ("check_mysql", "IP du serveur MySQL (défaut: wms_db) : "),
    "3": ("check_windows_server", "IP du serveur Windows : "),
    "4": ("check_ubuntu", "IP du serveur Ubuntu : "),
}

BACKUP_ACTIONS: dict[str, tuple[str, str]] = {
    "1": ("backup_database", "Base à sauvegarder (défaut: wms) : "),
    "2": ("export_table_csv", "Table à exporter (ex: shipments) : "),
}

AUDIT_ACTIONS: dict[str, tuple[str, str]] = {
    "1": ("scan_network", "Plage réseau (défaut: config) : "),
    "2": ("list_os_eol", "Appuyez sur Entrée pour continuer : "),
    "3": ("audit_from_csv", "Chemin du CSV (défaut: config) : "),
    "4": ("generate_report", "Appuyez sur Entrée pour continuer : "),
}


def _prompt(text: str) -> str:
    """Read user input, stripping whitespace."""
    try:
        return input(text).strip()
    except EOFError:
        return ""


def _run_module_action(
    module: Any,
    module_name: str,
    action: str,
    config: dict[str, Any],
    target: str,
) -> None:
    """Execute a module action and handle the result."""
    if module is None:
        print(f"\n  Module {module_name} non disponible.\n")
        return

    try:
        result = module.run(config, target, action=action)
        print_result(result)
        output_dir = config.get("general", {}).get("output_dir", "./output")
        saved = save_result_json(result, output_dir)
        logger.info("Result saved to %s", saved)
    except ModuleConfigError as exc:
        logger.error("Erreur de configuration: %s", exc)
        print(f"\n  Erreur config: {exc}\n")
    except ModuleExecutionError as exc:
        logger.error("Erreur d'exécution: %s", exc)
        print(f"\n  Erreur exécution: {exc}\n")


def _handle_submenu(
    menu_text: str,
    actions: dict[str, tuple[str, str]],
    module: Any,
    module_name: str,
    config: dict[str, Any],
) -> None:
    """Display a sub-menu loop for a given module."""
    while True:
        print(menu_text)
        choice = _prompt("  Choix : ")
        if choice == "0":
            return
        if choice not in actions:
            print("\n  Choix invalide.\n")
            continue

        action, target_prompt = actions[choice]
        target = _prompt(f"  {target_prompt}")
        if not target:
            target = _get_default_target(action, config)
        _run_module_action(module, module_name, action, config, target)


def _get_default_target(action: str, config: dict[str, Any]) -> str:
    """Return a sensible default target based on the action and config."""
    targets = config.get("targets", {})
    defaults: dict[str, str] = {
        "check_ad_dns": targets.get("dc01", {}).get("host", "192.168.10.10"),
        "check_mysql": targets.get("wms_db", {}).get("host", "192.168.10.21"),
        "check_windows_server": targets.get("dc01", {}).get("host", "192.168.10.10"),
        "check_ubuntu": targets.get("wms_db", {}).get("host", "192.168.10.21"),
        "backup_database": config.get("mysql", {}).get("database", "wms"),
        "export_table_csv": "shipments",
        "scan_network": config.get("audit", {}).get("network_range", "192.168.10.0/24"),
        "list_os_eol": "all",
        "audit_from_csv": config.get("audit", {}).get("inventory_csv", "./data/sample_inventory.csv"),
        "generate_report": "all",
    }
    return defaults.get(action, "")


# --- Main -------------------------------------------------------------------

def main() -> None:
    """Application entry point."""
    config_path = "config/config.yaml"
    if len(sys.argv) > 1 and sys.argv[1] == "--config" and len(sys.argv) > 2:
        config_path = sys.argv[2]

    try:
        config = load_config(config_path)
    except ModuleConfigError as exc:
        print(f"Erreur: {exc}")
        sys.exit(1)

    setup_logging(
        log_level=config.get("general", {}).get("log_level", "INFO"),
        output_dir=config.get("general", {}).get("output_dir", "./output"),
    )
    logger.info("NTL-SysToolbox started")

    while True:
        print(MAIN_MENU)
        choice = _prompt("  Choix : ")

        if choice == "0":
            print("\nAu revoir!")
            break
        elif choice == "1":
            _handle_submenu(DIAGNOSTIC_MENU, DIAGNOSTIC_ACTIONS, diagnostic, "Diagnostic", config)
        elif choice == "2":
            _handle_submenu(BACKUP_MENU, BACKUP_ACTIONS, backup, "Backup", config)
        elif choice == "3":
            _handle_submenu(AUDIT_MENU, AUDIT_ACTIONS, audit, "Audit", config)
        else:
            print("\n  Choix invalide.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAu revoir!")
        sys.exit(0)
