"""
Module: Diagnostic
Description: Verification de l'etat des services critiques NTL (AD/DNS, MySQL, metriques serveurs)
Responsable: Blaise
"""

import logging
import subprocess
from typing import Any

from src.interfaces import (
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    EXIT_WARNING,
    ModuleConfigError,
    ModuleExecutionError,
    build_result,
)
from src.utils.network import check_port, ping_host, resolve_dns

logger = logging.getLogger(__name__)

MODULE_NAME = "diagnostic"

_WARN_THRESHOLD = 80  # Pourcentage au-dela duquel on passe en WARNING


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(config: dict, target: str, **kwargs: Any) -> dict[str, Any]:
    """Point d'entree principal du module diagnostic.

    Appele par main.py. Delegue vers la fonction selon le kwarg 'action'.

    Args:
        config: Config complete chargee depuis config.yaml.
        target: IP ou hostname saisi par l'utilisateur.
        **kwargs: action = "check_ad_dns" | "check_mysql" | "check_windows_server" | "check_ubuntu"

    Raises:
        ModuleExecutionError: Si l'action est inconnue.
    """
    action = kwargs.get("action", "")
    logger.info("Diagnostic action=%s sur cible: %s", action, target)

    if action == "check_ad_dns":
        return check_ad_dns(config, target)
    elif action == "check_mysql":
        return check_mysql(config, target)
    elif action == "check_windows_server":
        return check_windows_server(config, target)
    elif action == "check_ubuntu":
        return check_ubuntu(config, target)
    else:
        raise ModuleExecutionError(f"Action inconnue: {action}")


# ---------------------------------------------------------------------------
# check_ad_dns
# ---------------------------------------------------------------------------


def check_ad_dns(config: dict, target: str) -> dict[str, Any]:
    """Verifie que l'Active Directory (LDAP port 389) et le DNS (ntl.local) sont operationnels.

    Args:
        config: Config complete (utilise general.timeout).
        target: IP du controleur de domaine (ex: 192.168.10.10).

    Returns:
        Resultat standardise via build_result().
    """
    timeout = config.get("general", {}).get("timeout", 10)

    try:
        if not ping_host(target, timeout=timeout):
            return build_result(
                module=MODULE_NAME,
                function="check_ad_dns",
                status="UNKNOWN",
                exit_code=EXIT_UNKNOWN,
                target=target,
                details={"error": "Host injoignable"},
                message=f"DC01 injoignable: {target}",
            )

        ldap_ok = check_port(target, 389, timeout=timeout)
        dns_result = resolve_dns("ntl.local", dns_server=target)
        dns_ok = dns_result is not None

        if ldap_ok and dns_ok:
            status, code = "OK", EXIT_OK
            msg = "AD et DNS operationnels"
        elif not ldap_ok:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"LDAP injoignable sur {target}:389"
        else:
            status, code = "WARNING", EXIT_WARNING
            msg = "DNS ne resout pas ntl.local"

        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status=status,
            exit_code=code,
            target=target,
            details={"ldap": ldap_ok, "dns": dns_ok, "dns_result": dns_result},
            message=msg,
        )

    except Exception as e:
        logger.error("check_ad_dns failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(e)},
            message=f"Impossible de verifier {target}: {e}",
        )


# ---------------------------------------------------------------------------
# check_mysql
# ---------------------------------------------------------------------------


def check_mysql(config: dict, target: str) -> dict[str, Any]:
    """Verifie la connexion MySQL et la presence de la base wms.

    Args:
        config: Config complete (utilise mysql.* et general.timeout).
        target: IP du serveur MySQL (ex: 192.168.10.21).

    Returns:
        Resultat standardise via build_result().

    Raises:
        ModuleConfigError: Si la section 'mysql' est absente du config.
    """
    mysql_cfg = config.get("mysql", {})
    timeout = config.get("general", {}).get("timeout", 10)

    if not mysql_cfg:
        raise ModuleConfigError("Section 'mysql' manquante dans config.yaml")

    try:
        import mysql.connector  # type: ignore[import]

        conn = mysql.connector.connect(
            host=target,
            port=mysql_cfg.get("port", 3306),
            user=mysql_cfg.get("user", ""),
            password=mysql_cfg.get("password", ""),
            connection_timeout=timeout,
        )
        cursor = conn.cursor()

        cursor.execute("SHOW DATABASES")
        databases = [row[0] for row in cursor.fetchall()]  # type: ignore[index]
        wms_exists = "wms" in databases

        cursor.execute("SHOW STATUS LIKE 'Uptime'")
        uptime_row = cursor.fetchone()
        uptime = str(uptime_row[1]) if uptime_row else "unknown"  # type: ignore[index]

        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        threads_row = cursor.fetchone()
        threads = int(str(threads_row[1])) if threads_row else 0  # type: ignore[index]

        cursor.execute("SHOW STATUS LIKE 'Questions'")
        questions_row = cursor.fetchone()
        questions = int(str(questions_row[1])) if questions_row else 0  # type: ignore[index]

        cursor.close()
        conn.close()

        if wms_exists:
            status, code = "OK", EXIT_OK
            msg = "MySQL operationnel, base wms presente"
        else:
            status, code = "WARNING", EXIT_WARNING
            msg = "MySQL connecte mais base 'wms' absente"

        return build_result(
            module=MODULE_NAME,
            function="check_mysql",
            status=status,
            exit_code=code,
            target=target,
            details={
                "connected": True,
                "databases": databases,
                "wms_exists": wms_exists,
                "uptime": uptime,
                "threads": threads,
                "questions": questions,
            },
            message=msg,
        )

    except Exception as e:
        err = str(e).lower()
        if "access denied" in err or "authentication" in err:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"Connexion MySQL refusee: {e}"
        elif any(kw in err for kw in ("can't connect", "connection refused", "timed out", "unreachable")):
            status, code = "UNKNOWN", EXIT_UNKNOWN
            msg = f"Serveur MySQL injoignable: {e}"
        else:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"Erreur MySQL: {e}"

        logger.error("check_mysql failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="check_mysql",
            status=status,
            exit_code=code,
            target=target,
            details={"connected": False, "error": str(e)},
            message=msg,
        )


# ---------------------------------------------------------------------------
# check_windows_server
# ---------------------------------------------------------------------------


def _wmic_get(node_args: list[str], wmi_class: str, properties: str, timeout: int) -> str:
    """Execute une commande wmic et retourne la sortie brute."""
    result = subprocess.run(
        ["wmic"] + node_args + wmi_class.split() + ["get"] + properties.split(",") + ["/value"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout


def check_windows_server(config: dict, target: str) -> dict[str, Any]:
    """Verifie les metriques (CPU, RAM, Disque C:) d'un serveur Windows via wmic.

    Args:
        config: Config complete (utilise general.timeout).
        target: IP ou hostname du serveur Windows.

    Returns:
        Resultat standardise via build_result().
    """
    timeout = config.get("general", {}).get("timeout", 10)

    try:
        if not ping_host(target, timeout=timeout):
            return build_result(
                module=MODULE_NAME,
                function="check_windows_server",
                status="UNKNOWN",
                exit_code=EXIT_UNKNOWN,
                target=target,
                details={"error": "Host injoignable"},
                message=f"Serveur Windows injoignable: {target}",
            )

        node_args = [f"/node:{target}"] if target not in ("localhost", "127.0.0.1") else []

        # CPU
        cpu_output = _wmic_get(node_args, "cpu", "LoadPercentage", timeout)
        cpu_percent = 0
        for line in cpu_output.splitlines():
            if "LoadPercentage=" in line:
                val = line.split("=")[1].strip()
                cpu_percent = int(val) if val.isdigit() else 0
                break

        # RAM
        ram_output = _wmic_get(node_args, "OS", "FreePhysicalMemory,TotalVisibleMemorySize", timeout)
        free_ram_kb = 0
        total_ram_kb = 0
        for line in ram_output.splitlines():
            if "FreePhysicalMemory=" in line:
                val = line.split("=")[1].strip()
                free_ram_kb = int(val) if val.isdigit() else 0
            elif "TotalVisibleMemorySize=" in line:
                val = line.split("=")[1].strip()
                total_ram_kb = int(val) if val.isdigit() else 0

        ram_used_kb = total_ram_kb - free_ram_kb
        ram_percent = round((ram_used_kb / total_ram_kb) * 100, 1) if total_ram_kb > 0 else 0
        ram_total_mb = int(total_ram_kb / 1024)

        # Disk C:
        disk_output = _wmic_get(node_args, "logicaldisk where DeviceID='C:'", "Size,FreeSpace", timeout)
        disk_free = 0
        disk_size = 0
        for line in disk_output.splitlines():
            if "FreeSpace=" in line:
                val = line.split("=")[1].strip()
                disk_free = int(val) if val.isdigit() else 0
            elif "Size=" in line:
                val = line.split("=")[1].strip()
                disk_size = int(val) if val.isdigit() else 0

        disk_used = disk_size - disk_free
        disk_percent = round((disk_used / disk_size) * 100, 1) if disk_size > 0 else 0
        disk_total_gb = round(disk_size / (1024**3), 1)

        # Status
        issues = []
        if cpu_percent > _WARN_THRESHOLD:
            issues.append(f"CPU {cpu_percent}%")
        if ram_percent > _WARN_THRESHOLD:
            issues.append(f"RAM {ram_percent}%")
        if disk_percent > _WARN_THRESHOLD:
            issues.append(f"Disk {disk_percent}%")

        if issues:
            status, code = "WARNING", EXIT_WARNING
            msg = f"Seuil 80% depasse: {', '.join(issues)}"
        else:
            status, code = "OK", EXIT_OK
            msg = f"Serveur Windows OK — CPU {cpu_percent}%, RAM {ram_percent}%, Disk {disk_percent}%"

        return build_result(
            module=MODULE_NAME,
            function="check_windows_server",
            status=status,
            exit_code=code,
            target=target,
            details={
                "cpu_percent": cpu_percent,
                "ram_percent": ram_percent,
                "disk_percent": disk_percent,
                "ram_total_mb": ram_total_mb,
                "disk_total_gb": disk_total_gb,
            },
            message=msg,
        )

    except FileNotFoundError:
        logger.error("wmic non disponible sur ce systeme")
        return build_result(
            module=MODULE_NAME,
            function="check_windows_server",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=target,
            details={"error": "wmic non disponible"},
            message="wmic non disponible — diagnostic Windows impossible depuis ce poste",
        )
    except subprocess.TimeoutExpired:
        return build_result(
            module=MODULE_NAME,
            function="check_windows_server",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": "Timeout wmic"},
            message=f"Timeout lors de la connexion wmic a {target}",
        )
    except Exception as e:
        logger.error("check_windows_server failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="check_windows_server",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=target,
            details={"error": str(e)},
            message=f"Erreur lors du diagnostic Windows: {e}",
        )


# ---------------------------------------------------------------------------
# check_ubuntu
# ---------------------------------------------------------------------------


def check_ubuntu(config: dict, target: str) -> dict[str, Any]:
    """Verifie l'etat d'un serveur Ubuntu via SSH (OS, uptime, RAM, disque, MySQL).

    Args:
        config: Config complete (utilise ssh.* et general.timeout).
        target: IP du serveur Ubuntu (ex: 192.168.10.21).

    Returns:
        Resultat standardise via build_result().

    Raises:
        ModuleConfigError: Si la section 'ssh' est absente du config.
    """
    ssh_cfg = config.get("ssh", {})
    timeout = config.get("general", {}).get("timeout", 10)

    if not ssh_cfg:
        raise ModuleConfigError("Section 'ssh' manquante dans config.yaml")

    try:
        import paramiko  # type: ignore[import]

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=target,
            port=ssh_cfg.get("port", 22),
            username=ssh_cfg.get("user", ""),
            password=ssh_cfg.get("password", ""),
            timeout=timeout,
        )

        def run_cmd(cmd: str) -> str:
            _, stdout, _ = client.exec_command(cmd, timeout=timeout)
            return stdout.read().decode("utf-8", errors="replace").strip()

        os_cmd = "lsb_release -d 2>/dev/null | cut -f2 || grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"'"
        os_version = run_cmd(os_cmd)
        uptime = run_cmd("uptime -p 2>/dev/null || uptime")

        # RAM: free -m => "Mem: total used free ..."
        ram_raw = run_cmd("free -m | awk 'NR==2{print $2,$3}'")
        ram_parts = ram_raw.split()
        ram_total = int(ram_parts[0]) if len(ram_parts) >= 2 and ram_parts[0].isdigit() else 0
        ram_used = int(ram_parts[1]) if len(ram_parts) >= 2 and ram_parts[1].isdigit() else 0
        ram_percent = round((ram_used / ram_total) * 100, 1) if ram_total > 0 else 0

        # Disk /
        disk_raw = run_cmd("df / | awk 'NR==2{print $3,$4}'")
        disk_parts = disk_raw.split()
        disk_used_kb = int(disk_parts[0]) if len(disk_parts) >= 2 and disk_parts[0].isdigit() else 0
        disk_free_kb = int(disk_parts[1]) if len(disk_parts) >= 2 and disk_parts[1].isdigit() else 0
        disk_total_kb = disk_used_kb + disk_free_kb
        disk_percent = round((disk_used_kb / disk_total_kb) * 100, 1) if disk_total_kb > 0 else 0

        # MySQL service
        mysql_status = run_cmd(
            "systemctl is-active mysql 2>/dev/null || systemctl is-active mysqld 2>/dev/null || echo inactive"
        ).split("\n")[0].strip()

        client.close()

        issues = []
        if ram_percent > _WARN_THRESHOLD:
            issues.append(f"RAM {ram_percent}%")
        if disk_percent > _WARN_THRESHOLD:
            issues.append(f"Disk {disk_percent}%")

        if issues:
            status, code = "WARNING", EXIT_WARNING
            msg = f"Seuil 80% depasse: {', '.join(issues)}"
        else:
            status, code = "OK", EXIT_OK
            msg = f"Serveur Ubuntu OK — RAM {ram_percent}%, Disk {disk_percent}%"

        return build_result(
            module=MODULE_NAME,
            function="check_ubuntu",
            status=status,
            exit_code=code,
            target=target,
            details={
                "os_version": os_version,
                "uptime": uptime,
                "ram_percent": ram_percent,
                "disk_percent": disk_percent,
                "mysql_status": mysql_status,
            },
            message=msg,
        )

    except Exception as e:
        err = str(e).lower()
        if "authentication" in err or "no authentication" in err:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"SSH: authentification refusee sur {target}"
        elif any(kw in err for kw in ("connection refused", "timed out", "no route", "network")):
            status, code = "UNKNOWN", EXIT_UNKNOWN
            msg = f"SSH: impossible de joindre {target}"
        else:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"SSH echoue: {e}"

        logger.error("check_ubuntu failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="check_ubuntu",
            status=status,
            exit_code=code,
            target=target,
            details={"error": str(e)},
            message=msg,
        )
