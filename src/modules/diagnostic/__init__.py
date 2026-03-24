"""
Module: Diagnostic
Description: Vérification de l'état des services AD/DNS, MySQL, Linux et HTTP.
Responsable: Blaise
"""

import logging
from typing import Any

from src.interfaces import (
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    EXIT_WARNING,
    build_result,
)

logger = logging.getLogger(__name__)

MODULE_NAME = "diagnostic"


def run(config: dict, target: str, **kwargs: Any) -> dict[str, Any]:
    """Point d'entrée du module diagnostic.

    Args:
        config: Configuration complète (config.yaml).
        target: IP ou hostname de la cible.
        **kwargs: action= parmi check_ad_dns, check_mysql,
                  check_linux, check_http.

    Returns:
        Résultat standardisé (build_result).
    """
    action = kwargs.get("action", "check_ad_dns")
    logger.info("diagnostic.%s sur %s", action, target)

    dispatch = {
        "check_ad_dns": _check_ad_dns,
        "check_mysql": _check_mysql,
        "check_linux": _check_linux,
        "check_http": _check_http,
    }

    handler = dispatch.get(action)
    if handler:
        return handler(config, target)

    # Action pas encore implémentée
    return build_result(
        module=MODULE_NAME,
        function=action,
        status="UNKNOWN",
        exit_code=EXIT_UNKNOWN,
        target=target,
        details={},
        message=f"Action '{action}' non encore implémentée.",
    )


def _check_ad_dns(config: dict, target: str) -> dict[str, Any]:
    """Exécute les checks AD/DNS (DNS, ports, LDAP, services WinRM)."""
    from .checks import check_dns, check_ldap, check_ports, check_services

    try:
        details: dict[str, Any] = {}

        # DNS
        dns_server = config.get("targets", {}).get("dc01", {}).get("host")
        dns_ok, dns_info = check_dns(target, dns_server)
        details["dns"] = {"ok": dns_ok, "info": dns_info}

        # Ports
        port_status, port_results = check_ports(target)
        details["ports"] = {"status": port_status, "results": {str(k): v for k, v in port_results.items()}}

        # LDAP
        ldap_ok = check_ldap(target)
        details["ldap"] = {"ok": ldap_ok}

        # Services WinRM (optionnel, nécessite credentials)
        # Credentials resolved from env vars via config_loader._resolve_env_vars()
        # Config should use ${NTL_WINRM_USER} / ${NTL_WINRM_PASSWORD} placeholders
        winrm_user = config.get("winrm", {}).get("user", "")
        winrm_pass = config.get("winrm", {}).get("password", "")
        if winrm_user and winrm_pass:
            svc_status, svc_results = check_services(target, winrm_user, winrm_pass)
            details["services"] = {"status": svc_status, "results": svc_results}
        else:
            svc_status = "UNKNOWN"
            details["services"] = {"status": "UNKNOWN", "results": "Credentials WinRM non configurés"}

        # Status global
        statuses = [
            "OK" if dns_ok else "CRITICAL",
            port_status,
            "OK" if ldap_ok else "CRITICAL",
            svc_status,
        ]

        if "CRITICAL" in statuses:
            overall, code = "CRITICAL", EXIT_CRITICAL
        elif "UNKNOWN" in statuses:
            overall, code = "WARNING", EXIT_WARNING  # Couverture partielle (WinRM non configure)
        else:
            overall, code = "OK", EXIT_OK

        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status=overall,
            exit_code=code,
            target=target,
            details=details,
            message=f"AD/DNS check {overall} sur {target}",
        )
    except Exception as exc:
        logger.error("check_ad_dns failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(exc)},
            message=f"Erreur lors du check AD/DNS sur {target}: {exc}",
        )


def _check_mysql(config: dict, target: str) -> dict[str, Any]:
    """Check MySQL port and version (sans authentification)."""
    from .checks import check_mysql_port as _check_mysql_port

    try:
        port = config.get("mysql", {}).get("port", 3306)
        result = _check_mysql_port(target, port)

        if result["reachable"]:
            status, code = "OK", EXIT_OK
            msg = f"MySQL accessible sur {target}:{port}"
            if result.get("version"):
                msg += f" (version {result['version']})"
        else:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"MySQL injoignable sur {target}:{port}"

        return build_result(
            module=MODULE_NAME,
            function="check_mysql",
            status=status,
            exit_code=code,
            target=target,
            details=result,
            message=msg,
        )
    except Exception as exc:
        logger.error("check_mysql failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="check_mysql",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(exc)},
            message=f"Erreur lors du check MySQL sur {target}: {exc}",
        )


def _check_linux(config: dict, target: str) -> dict[str, Any]:
    """Check services ouverts sur un host Linux (scan multi-ports)."""
    from .checks import check_host_services

    try:
        discovery_cfg = config.get("discovery", {})
        ports = discovery_cfg.get("ports")
        timeout = discovery_cfg.get("timeout", 2)
        result = check_host_services(target, ports=ports, timeout=timeout)

        open_count = len(result["categories"])
        if open_count > 0:
            status, code = "OK", EXIT_OK
            msg = f"{open_count} service(s) trouvé(s) sur {target}: {', '.join(result['categories'])}"
        else:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"Aucun service détecté sur {target}"

        return build_result(
            module=MODULE_NAME,
            function="check_linux",
            status=status,
            exit_code=code,
            target=target,
            details=result,
            message=msg,
        )
    except Exception as exc:
        logger.error("check_linux failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="check_linux",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(exc)},
            message=f"Erreur lors du check Linux sur {target}: {exc}",
        )


def _check_http(config: dict, target: str) -> dict[str, Any]:
    """Check HTTP(S) service on a host."""
    from .checks import check_http as _http_check

    try:
        # NOTE: IPv6 addresses like [::1]:8080 are not supported.
        # To support IPv6, use urllib.parse.urlsplit() instead.
        port = 80
        if ":" in target:
            parts = target.rsplit(":", 1)
            try:
                port = int(parts[1])
                target = parts[0]
            except ValueError:
                pass  # Not a port suffix, keep target as-is

        result = _http_check(target, port)

        if result.get("ok"):
            status, code = "OK", EXIT_OK
            msg = (
                f"HTTP {result['status_code']} sur {target}:{port}"
                f" — {result['response_time_ms']}ms"
            )
            if result.get("server"):
                msg += f" (Server: {result['server']})"
        else:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"HTTP échoué sur {target}:{port}"
            if result.get("error"):
                msg += f" — {result['error']}"

        return build_result(
            module=MODULE_NAME,
            function="check_http",
            status=status,
            exit_code=code,
            target=target,
            details=result,
            message=msg,
        )
    except Exception as exc:
        logger.error("check_http failed: %s", exc)
        return build_result(
            module=MODULE_NAME,
            function="check_http",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(exc)},
            message=f"Erreur lors du check HTTP sur {target}: {exc}",
        )
