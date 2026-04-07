"""
Network utility helpers used by diagnostic and audit modules.

Provides port checking, ping, DNS resolution, banner grabbing, and HTTP checks.

SOMMAIRE (navigation rapide soutenance) :
─────────────────────────────────────────
- check_port()          : Teste si un port TCP est ouvert sur une machine
- ping_host()           : Ping ICMP cross-platform (Windows/Linux)
- resolve_dns()         : Résolution DNS (via dnspython ou socket standard)
- grab_banner()         : Récupère la bannière d'un service (ex: SSH, SMTP)
- grab_mysql_version()  : Lit la version MySQL depuis le paquet handshake (sans auth)
- http_check()          : Requête HTTP GET + mesure temps de réponse, code HTTP, header Server
"""

import logging
import platform
import socket
import subprocess
import time
from typing import Any

logger = logging.getLogger(__name__)

# Maximum bytes to read from HTTP response body (1 MB)
_MAX_HTTP_BODY = 1024 * 1024

# Common HTTPS ports for automatic scheme detection
_HTTPS_PORTS = {443, 8443, 4443, 9443}


# --- VERIFICATION PORT TCP ---------------------------------------------------
# Ouvre une socket TCP vers host:port. Si la connexion réussit → port ouvert.
# Utilisé par diagnostic pour tester MySQL (3306), SSH (22), HTTP (80), etc.
def check_port(host: str, port: int, timeout: int = 10) -> bool:
    """Check if a TCP port is open on a host.

    Args:
        host: IP address or hostname.
        port: TCP port number.
        timeout: Timeout in seconds.

    Returns:
        True if the port is open, False otherwise.
    """
    if not (1 <= port <= 65535):
        logger.warning("Invalid port number: %d", port)
        return False

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
        logger.debug("Port %d open on %s", port, host)
        return True
    except (OSError, TimeoutError) as exc:
        logger.debug("Port %d closed on %s: %s", port, host, exc)
        return False


# --- PING ICMP (CROSS-PLATFORM) ----------------------------------------------
# Détecte l'OS (Windows vs Linux) pour adapter la commande ping.
# Windows: ping -n 1 -w <ms>  |  Linux: ping -c 1 -W <sec>
# C'est ICI qu'on détecte l'OS pour adapter le comportement.
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


# --- RESOLUTION DNS ----------------------------------------------------------
# Si un serveur DNS est spécifié (ex: DC01 = 192.168.10.10) → utilise dnspython.
# Sinon → résolution standard via socket.gethostbyname() (DNS système).
# Sert à vérifier que le contrôleur de domaine AD répond bien en DNS.
def resolve_dns(
    hostname: str, dns_server: str | None = None
) -> str | None:
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
        except (
            dns.resolver.NXDOMAIN,
            dns.resolver.Timeout,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
            socket.gaierror,
            OSError,
        ) as exc:
            logger.debug("DNS resolution failed for %s via %s: %s", hostname, dns_server, exc)
            return None
        except Exception as exc:
            logger.debug("Unexpected DNS error for %s via %s: %s", hostname, dns_server, exc)
            return None

    try:
        ip = socket.gethostbyname(hostname)
        logger.debug("Resolved %s -> %s", hostname, ip)
        return ip
    except socket.gaierror as exc:
        logger.debug("DNS resolution failed for %s: %s", hostname, exc)
        return None


# --- GRAB BANNER (SERVICE FINGERPRINT) ---------------------------------------
# Se connecte en TCP et lit les premiers octets envoyés par le service.
# Ex: un serveur SSH envoie "SSH-2.0-OpenSSH_8.9" dès la connexion.
# Permet d'identifier le service et sa version sans authentification.
def grab_banner(host: str, port: int, timeout: int = 3) -> str | None:
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


# --- VERSION MYSQL (SANS AUTH) -----------------------------------------------
# MySQL envoie un "handshake packet" dès la connexion TCP.
# On lit les octets à partir de la position 5 jusqu'au premier \x00 (null byte)
# pour extraire la version (ex: "8.0.35"). Aucun mot de passe nécessaire.
def grab_mysql_version(host: str, port: int = 3306, timeout: int = 3) -> str | None:
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


# --- CHECK HTTP/HTTPS --------------------------------------------------------
# Fait un GET sur http(s)://host:port/path et retourne :
# - code HTTP, header Server, taille réponse, temps de réponse en ms
# Détecte auto le schéma (HTTPS si port 443/8443, sinon HTTP).
# SSL non vérifié par défaut (environnement lab).
def http_check(
    host: str, port: int = 80, path: str = "/", timeout: int = 5,
    verify_ssl: bool = False, scheme: str | None = None,
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

    if scheme is None:
        scheme = "https" if port in _HTTPS_PORTS else "http"
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
                "error": None,
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
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, OSError) as exc:
        logger.debug("HTTP check failed %s: %s", url, exc)
        return {
            "ok": False,
            "status_code": 0,
            "server": "",
            "content_length": 0,
            "response_time_ms": 0.0,
            "error": str(exc),
        }
