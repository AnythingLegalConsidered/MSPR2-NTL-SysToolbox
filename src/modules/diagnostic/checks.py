"""
Fonctions de vérification — AD/DNS, MySQL, HTTP, services réseau.
Basé sur le travail de Blaise, étendu pour le réseau école.
"""

import logging
import socket

import dns.resolver
import winrm
from ldap3 import ALL, Connection, Server

from src.utils.network import check_port, grab_banner, grab_mysql_version, http_check

from .constant import CRITICAL_PORTS, DISCOVERY_PORTS, IMPORTANT_PORTS, SERVICE_NAMES, SERVICES

logger = logging.getLogger(__name__)


# DNS
def check_dns(host, dns_server=None, timeout=3):
    try:
        if dns_server:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve(host, "A")
            return True, answers[0].to_text()
        else:
            socket.setdefaulttimeout(timeout)
            return True, socket.gethostbyname(host)
    except Exception as e:
        return False, str(e)


# Ports
def check_ports(host, timeout=2):
    results = {}
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


# LDAP
def check_ldap(host):
    try:
        server = Server(host, get_info=ALL)
        conn = Connection(server, auto_bind=True)
        conn.unbind()
        return True
    except Exception:
        return False


# WinRM Services
def check_services(host, username, password):
    results = {}
    overall = "OK"

    try:
        session = winrm.Session(host, auth=(username, password))

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

def check_mysql_port(host: str, port: int = 3306, timeout: int = 3) -> dict:
    """Check MySQL port and grab server version without credentials.

    Returns:
        Dict with keys: reachable, port, version (or None), banner.
    """
    reachable = check_port(host, port, timeout=timeout)
    result: dict = {"reachable": reachable, "port": port, "version": None, "banner": None}

    if reachable:
        version = grab_mysql_version(host, port, timeout)
        if version:
            result["version"] = version
        else:
            banner = grab_banner(host, port, timeout)
            result["banner"] = banner

    logger.debug("check_mysql_port %s:%d -> %s", host, port, result)
    return result


def check_http(host: str, port: int = 80, timeout: int = 5) -> dict:
    """Check HTTP(S) service and return response metadata.

    Returns:
        Dict from http_check(): ok, status_code, server, content_length, response_time_ms.
    """
    return http_check(host, port, timeout=timeout)


def check_host_services(host: str, ports: list[int] | None = None, timeout: int = 2) -> dict:
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

    open_ports = []
    categories: set[str] = set()

    for port in ports:
        is_open = check_port(host, port, timeout=timeout)
        service = SERVICE_NAMES.get(port, f"port-{port}")
        open_ports.append({"port": port, "service": service, "open": is_open})
        if is_open:
            categories.add(service)

    result = {
        "host": host,
        "open_ports": open_ports,
        "categories": sorted(categories),
    }
    logger.debug("check_host_services %s -> %d open", host, len(categories))
    return result
