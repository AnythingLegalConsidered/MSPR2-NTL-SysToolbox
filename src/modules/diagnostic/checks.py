"""
Fonctions de vérification — AD/DNS, MySQL, HTTP, services réseau.
Basé sur le travail de Blaise, étendu pour le réseau école.
"""

import logging
import socket
from typing import Any

from src.utils.network import check_port, grab_banner, grab_mysql_version, http_check

from .constant import CRITICAL_PORTS, DISCOVERY_PORTS, IMPORTANT_PORTS, SERVICE_NAMES, SERVICES

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# AD/DNS checks (nécessitent dnspython, ldap3, pywinrm)
# ---------------------------------------------------------------------------

def check_dns(
    host: str, dns_server: str | None = None, timeout: int = 3
) -> tuple[bool, str]:
    """Resolve hostname via DNS."""
    try:
        if dns_server:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve(host, "A")
            return True, answers[0].to_text()
        else:
            old_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(timeout)
                return True, socket.gethostbyname(host)
            finally:
                socket.setdefaulttimeout(old_timeout)
    except Exception as e:
        return False, str(e)


def check_ports(host: str, timeout: int = 2) -> tuple[str, dict[int, bool]]:
    """Check critical and important AD ports."""
    results: dict[int, bool] = {}
    overall = "OK"

    for port in CRITICAL_PORTS + IMPORTANT_PORTS:
        is_open = check_port(host, port, timeout=timeout)
        results[port] = is_open
        if not is_open:
            if port in CRITICAL_PORTS:
                overall = "CRITICAL"
            elif overall != "CRITICAL":
                overall = "WARNING"

    return overall, results


def check_ldap(host: str) -> bool:
    """Test LDAP connectivity."""
    try:
        from ldap3 import ALL, Connection, Server

        server = Server(host, get_info=ALL, connect_timeout=10)
        conn = Connection(server, auto_bind=True, receive_timeout=10)
        conn.unbind()
        return True
    except Exception:
        return False


def check_services(
    host: str, username: str, password: str
) -> tuple[str, dict[str, Any]]:
    """Check Windows services via WinRM."""
    try:
        import winrm
    except ImportError:
        return "UNKNOWN", {"error": "pywinrm non installé"}

    results: dict[str, Any] = {}
    overall = "OK"

    try:
        session = winrm.Session(
            host,
            auth=(username, password),
            read_timeout_sec=30,
            operation_timeout_sec=20,
        )

        for service in SERVICES:
            ps = f"Get-Service -Name {service} | Select-Object -ExpandProperty Status"
            r = session.run_ps(ps)

            if r.status_code == 0:
                status = r.std_out.decode().strip()
                results[service] = status
                if status != "Running":
                    overall = "CRITICAL"
            else:
                results[service] = "Error"
                overall = "CRITICAL"

    except Exception as e:
        return "UNKNOWN", {"error": str(e)}

    return overall, results


# ---------------------------------------------------------------------------
# Discovery checks (sans authentification)
# ---------------------------------------------------------------------------

def check_mysql_port(host: str, port: int = 3306, timeout: int = 3) -> dict[str, Any]:
    """Check MySQL port and grab server version without credentials.

    Returns:
        Dict with keys: reachable, port, version (or None), banner.
    """
    reachable = check_port(host, port, timeout=timeout)
    result: dict[str, Any] = {"reachable": reachable, "port": port, "version": None, "banner": None}

    if reachable:
        version = grab_mysql_version(host, port, timeout)
        if version:
            result["version"] = version
        else:
            banner = grab_banner(host, port, timeout)
            result["banner"] = banner

    logger.debug("check_mysql_port %s:%d -> %s", host, port, result)
    return result


def check_http(host: str, port: int = 80, timeout: int = 5) -> dict[str, Any]:
    """Check HTTP(S) service and return response metadata.

    Returns:
        Dict from http_check(): ok, status_code, server, content_length, response_time_ms.
    """
    return http_check(host, port, timeout=timeout)


def check_host_services(
    host: str, ports: list[int] | None = None, timeout: int = 2
) -> dict[str, Any]:
    """Scan multiple ports and categorize discovered services.

    Args:
        host: IP address or hostname.
        ports: List of ports to scan (default: DISCOVERY_PORTS).
        timeout: Per-port timeout.

    Returns:
        Dict with keys: host, open_ports (list of {port, service, open}),
        categories (list of service categories found).
    """
    if ports is None:
        ports = DISCOVERY_PORTS

    open_ports: list[dict[str, Any]] = []
    categories: set[str] = set()

    for port in ports:
        is_open = check_port(host, port, timeout=timeout)
        service = SERVICE_NAMES.get(port, f"port-{port}")
        open_ports.append({"port": port, "service": service, "open": is_open})
        if is_open:
            categories.add(service)

    result: dict[str, Any] = {
        "host": host,
        "open_ports": open_ports,
        "categories": sorted(categories),
    }
    logger.debug("check_host_services %s -> %d open", host, len(categories))
    return result
