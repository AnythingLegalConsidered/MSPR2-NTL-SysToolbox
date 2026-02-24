"""
Network utility helpers used by diagnostic and audit modules.

Provides port checking, ping, and DNS resolution.
"""

import logging
import platform
import socket
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def check_port(host: str, port: int, timeout: int = 10) -> bool:
    """Check if a TCP port is open on a host.

    Args:
        host: IP address or hostname.
        port: TCP port number.
        timeout: Timeout in seconds.

    Returns:
        True if the port is open, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
        logger.debug("Port %d open on %s", port, host)
        return True
    except (OSError, TimeoutError) as exc:
        logger.debug("Port %d closed on %s: %s", port, host, exc)
        return False


def ping_host(host: str, timeout: int = 10) -> bool:
    """Check if a host responds to ICMP ping (cross-platform).

    Args:
        host: IP address or hostname.
        timeout: Timeout in seconds.

    Returns:
        True if the host responds, False otherwise.
    """
    try:
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
        else:
            cmd = ["ping", "-c", "1", "-W", str(timeout), host]

        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 5,
        )
        reachable = result.returncode == 0
        logger.debug("Ping %s: %s", host, "OK" if reachable else "FAILED")
        return reachable
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.debug("Ping %s failed: %s", host, exc)
        return False


def resolve_dns(
    hostname: str, dns_server: Optional[str] = None
) -> Optional[str]:
    """Resolve a hostname to an IP address.

    Uses dnspython when a specific DNS server is provided,
    falls back to socket.gethostbyname() otherwise.

    Args:
        hostname: Name to resolve (e.g. "ntl.local").
        dns_server: Optional DNS server IP to query.

    Returns:
        IP address string, or None if resolution fails.
    """
    if dns_server:
        try:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            answers = resolver.resolve(hostname, "A")
            ip = str(answers[0])
            logger.debug("Resolved %s -> %s (via %s)", hostname, ip, dns_server)
            return ip
        except Exception as exc:
            logger.debug("DNS resolution failed for %s via %s: %s", hostname, dns_server, exc)
            return None

    try:
        ip = socket.gethostbyname(hostname)
        logger.debug("Resolved %s -> %s", hostname, ip)
        return ip
    except socket.gaierror as exc:
        logger.debug("DNS resolution failed for %s: %s", hostname, exc)
        return None
