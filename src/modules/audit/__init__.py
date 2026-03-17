"""
Module: Audit
Description: Scan réseau, détection EOL, inventaire CSV, rapport d'audit.
Responsable: Zaid
"""

import logging
from typing import Any

from src.interfaces import (
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    build_result,
)

logger = logging.getLogger(__name__)

MODULE_NAME = "audit"


def run(config: dict, target: str, **kwargs: Any) -> dict[str, Any]:
    """Point d'entrée du module audit.

    Args:
        config: Configuration complète (config.yaml).
        target: Plage réseau, chemin CSV, ou "all".
        **kwargs: action= parmi scan_network, list_os_eol,
                  audit_from_csv, generate_report.

    Returns:
        Résultat standardisé (build_result).
    """
    action = kwargs.get("action", "scan_network")
    logger.info("audit.%s sur %s", action, target)

    dispatch = {
        "scan_network": _scan_network,
        "list_os_eol": _list_os_eol,
        "audit_from_csv": _audit_from_csv,
        "generate_report": _generate_report,
    }

    handler = dispatch.get(action)
    if handler:
        return handler(config, target)

    return build_result(
        module=MODULE_NAME,
        function=action,
        status="UNKNOWN",
        exit_code=EXIT_UNKNOWN,
        target=target,
        details={},
        message=f"Action '{action}' non encore implémentée.",
    )


def _scan_network(config: dict, target: str) -> dict[str, Any]:
    """Scanner le réseau et catégoriser les hosts."""
    from .scanner import scan_network

    try:
        default_range = config.get("audit", {}).get("network_range", "172.16.135.0/24")
        network_range = target if target and target != "all" else default_range
        result = scan_network(config, network_range)

        if result.get("error"):
            return build_result(
                module=MODULE_NAME,
                function="scan_network",
                status="UNKNOWN",
                exit_code=EXIT_UNKNOWN,
                target=network_range,
                details=result,
                message=f"Erreur scan: {result['error']}",
            )

        hosts_up = result.get("hosts_up", 0)
        return build_result(
            module=MODULE_NAME,
            function="scan_network",
            status="OK" if hosts_up > 0 else "CRITICAL",
            exit_code=EXIT_OK if hosts_up > 0 else EXIT_CRITICAL,
            target=network_range,
            details=result,
            message=f"Scan terminé: {hosts_up} host(s) trouvé(s) sur {network_range}",
        )
    except Exception as exc:
        logger.error("scan_network failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="scan_network",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(exc)},
            message=f"Erreur lors du scan réseau: {exc}",
        )


def _list_os_eol(config: dict, target: str) -> dict[str, Any]:
    """Lister les dates EOL des systèmes d'exploitation."""
    from .scanner import list_os_eol

    try:
        result = list_os_eol(config)

        if result.get("error"):
            return build_result(
                module=MODULE_NAME,
                function="list_os_eol",
                status="UNKNOWN",
                exit_code=EXIT_UNKNOWN,
                target="eol_database",
                details=result,
                message=f"Erreur lecture EOL: {result['error']}",
            )

        eol_count = result.get("eol_count", 0)
        total = result.get("total", 0)
        return build_result(
            module=MODULE_NAME,
            function="list_os_eol",
            status="WARNING" if eol_count > 0 else "OK",
            exit_code=EXIT_OK,
            target="eol_database",
            details=result,
            message=f"{eol_count}/{total} OS en fin de vie",
        )
    except Exception as exc:
        logger.error("list_os_eol failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="list_os_eol",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target="eol_database",
            details={"error": str(exc)},
            message=f"Erreur EOL: {exc}",
        )


def _audit_from_csv(config: dict, target: str) -> dict[str, Any]:
    """Auditer les hosts depuis un inventaire CSV."""
    from .scanner import audit_from_csv

    try:
        result = audit_from_csv(config, target)

        if result.get("error"):
            return build_result(
                module=MODULE_NAME,
                function="audit_from_csv",
                status="UNKNOWN",
                exit_code=EXIT_UNKNOWN,
                target=target,
                details=result,
                message=f"Erreur lecture CSV: {result['error']}",
            )

        total = result.get("total_hosts", 0)
        reachable = result.get("reachable", 0)
        eol = result.get("eol_hosts", 0)
        return build_result(
            module=MODULE_NAME,
            function="audit_from_csv",
            status="OK",
            exit_code=EXIT_OK,
            target=target or "inventory",
            details=result,
            message=f"Inventaire: {total} hosts, {reachable} joignables, {eol} EOL",
        )
    except Exception as exc:
        logger.error("audit_from_csv failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="audit_from_csv",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(exc)},
            message=f"Erreur audit CSV: {exc}",
        )


def _generate_report(config: dict, target: str) -> dict[str, Any]:
    """Générer un rapport d'audit complet."""
    from .scanner import generate_report

    try:
        result = generate_report(config)
        report_path = result.get("report_path", "")

        return build_result(
            module=MODULE_NAME,
            function="generate_report",
            status="OK",
            exit_code=EXIT_OK,
            target=config.get("audit", {}).get("network_range", "172.16.135.0/24"),
            details=result,
            message=f"Rapport généré: {report_path}",
        )
    except Exception as exc:
        logger.error("generate_report failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="generate_report",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target="all",
            details={"error": str(exc)},
            message=f"Erreur génération rapport: {exc}",
        )
