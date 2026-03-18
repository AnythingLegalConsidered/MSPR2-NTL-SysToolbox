"""
Network utility helpers used by diagnostic and audit modules.

Provides port checking, ping, DNS resolution, banner grabbing, and HTTP checks.
"""

import logging
import platform
import socket
import subprocess
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Maximum bytes to read from HTTP response body (1 MB)
_MAX_HTTP_BODY = 1024 * 1024


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


def grab_banner(host: str, port: int, timeout: int = 3) -> Optional[str]:
    """Read the initial banner sent by a service (SSH version, MySQL greeting, etc.).

    Args:
        host: IP address or hostname.
        port: TCP port number.
        timeout: Timeout in seconds.

    Returns:
        Banner string (decoded, stripped), or None on failure.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            data = sock.recv(1024)
            if data:
                banner = data.decode("utf-8", errors="replace").strip()
                logger.debug("Banner on %s:%d -> %s", host, port, banner[:80])
                return banner
    except (OSError, TimeoutError) as exc:
        logger.debug("Banner grab failed on %s:%d: %s", host, port, exc)
    return None


def grab_mysql_version(host: str, port: int = 3306, timeout: int = 3) -> Optional[str]:
    """Read the MySQL greeting packet and extract the server version.

    The MySQL protocol sends a handshake packet upon connection.
    No authentication is needed to read the version string.

    Args:
        host: IP address or hostname.
        port: MySQL port (default 3306).
        timeout: Timeout in seconds.

    Returns:
        MySQL version string, or None on failure.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            data = sock.recv(1024)
            if len(data) < 5:
                return None
            # MySQL packet: 3 bytes length + 1 byte seq + 1 byte protocol + null-terminated version
            version_start = 5
            # ValueError raised if no null byte found (service is not MySQL)
            version_end = data.index(b"\x00", version_start)
            version = data[version_start:version_end].decode("utf-8", errors="replace")
            logger.debug("MySQL version on %s:%d -> %s", host, port, version)
            return version
    except (OSError, TimeoutError, ValueError) as exc:
        logger.debug("MySQL version grab failed on %s:%d: %s", host, port, exc)
    return None


def http_check(
    host: str, port: int = 80, path: str = "/", timeout: int = 5,
    verify_ssl: bool = False,
) -> dict[str, Any]:
    """Perform an HTTP GET request and return response metadata.

    Args:
        host: IP address or hostname.
        port: HTTP port (default 80).
        path: URL path to request.
        timeout: Timeout in seconds.
        verify_ssl: If False, disable certificate verification (default for lab use).

    Returns:
        Dict with keys: ok, status_code, server, content_length, response_time_ms.
    """
    import ssl
    import urllib.error
    import urllib.request

    scheme = "https" if port == 443 else "http"
    url = f"{scheme}://{host}:{port}{path}"

    try:
        if verify_ssl:
            ctx = ssl.create_default_context()
        else:
            logger.debug("SSL verification disabled for %s", url)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "NTL-SysToolbox/1.0")

        start = time.monotonic()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read(_MAX_HTTP_BODY)
            elapsed = (time.monotonic() - start) * 1000

            result: dict[str, Any] = {
                "ok": True,
                "status_code": resp.status,
                "server": resp.headers.get("Server", ""),
                "content_length": len(body),
                "response_time_ms": round(elapsed, 1),
            }
            logger.debug("HTTP check %s -> %s", url, result)
            return result

    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status_code": exc.code,
            "server": exc.headers.get("Server", "") if exc.headers else "",
            "content_length": 0,
            "response_time_ms": 0.0,
            "error": str(exc),
        }
    except Exception as exc:
        logger.debug("HTTP check failed %s: %s", url, exc)
        return {
            "ok": False,
            "status_code": 0,
            "server": "",
            "content_length": 0,
            "response_time_ms": 0.0,
            "error": str(exc),
        }
