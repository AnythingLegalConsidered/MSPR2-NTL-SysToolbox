"""
Audit scanner — network scanning, EOL detection, CSV inventory audit.
"""

import csv
import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any

from src.utils.network import check_port, resolve_dns

logger = logging.getLogger(__name__)

# Regex for valid nmap target: IPs, CIDR, ranges (e.g. 192.168.1.0/24, 10.0.0.1-50)
_VALID_TARGET_RE = re.compile(r'^[\d./,:-]+$')

# Valid TCP port range
_MIN_PORT = 1
_MAX_PORT = 65535


def _validate_target_range(target_range: str) -> str | None:
    """Validate that a network range is safe to pass to nmap.

    Returns:
        Error message if invalid, None if valid.
    """
    if not target_range or not _VALID_TARGET_RE.match(target_range):
        return f"Format de plage réseau invalide: {target_range!r}"
    return None


def _validate_ports(ports: list[Any]) -> list[int]:
    """Validate and sanitize a list of port numbers.

    Returns:
        List of valid port integers.
    """
    valid = []
    for p in ports:
        try:
            port = int(p)
            if _MIN_PORT <= port <= _MAX_PORT:
                valid.append(port)
        except (ValueError, TypeError):
            logger.warning("Port invalide ignoré: %s", p)
    return valid


def scan_network(config: dict, target_range: str) -> dict[str, Any]:
    """Scan a network range using python-nmap and categorize hosts.

    Args:
        config: Full configuration dict.
        target_range: Network range (e.g. "172.16.135.0/24").

    Returns:
        Dict with keys: range, hosts_up, hosts (list of host dicts).
    """
    # Validate target range to prevent nmap injection
    err = _validate_target_range(target_range)
    if err:
        logger.error(err)
        return {"range": target_range, "hosts_up": 0, "hosts": [], "error": err}

    try:
        import nmap
    except ImportError:
        logger.error("python-nmap not installed")
        return {"range": target_range, "hosts_up": 0, "hosts": [], "error": "python-nmap non installé"}

    discovery_cfg = config.get("discovery", {})
    raw_ports = discovery_cfg.get("ports", [22, 80, 443, 3306, 5432, 8006, 8080])
    ports = _validate_ports(raw_ports)
    if not ports:
        return {"range": target_range, "hosts_up": 0, "hosts": [], "error": "Aucun port valide configuré"}

    timeout = int(config.get("general", {}).get("timeout", 10))
    if timeout < 1:
        timeout = 10

    port_str = ",".join(str(p) for p in ports)

    nm = nmap.PortScanner()
    logger.info("Scanning %s ports %s ...", target_range, port_str)

    try:
        nm.scan(hosts=target_range, ports=port_str, arguments=f"-T4 --host-timeout {timeout}s")
    except nmap.PortScannerError as exc:
        logger.error("nmap scan failed: %s", exc)
        return {"range": target_range, "hosts_up": 0, "hosts": [], "error": str(exc)}

    hosts = []
    for host in nm.all_hosts():
        if nm[host].state() != "up":
            continue

        open_ports: list[dict[str, Any]] = []
        categories: set[str] = set()

        for proto in nm[host].all_protocols():
            for port in nm[host][proto]:
                state = nm[host][proto][port]["state"]
                service_name = nm[host][proto][port].get("name", "")
                if state == "open":
                    open_ports.append({"port": port, "state": state, "service": service_name})
                    categories.update(_categorize_port(port))

        hosts.append({
            "ip": host,
            "hostname": nm[host].hostname() or "",
            "open_ports": open_ports,
            "categories": sorted(categories),
        })

    logger.info("Scan done: %d hosts up", len(hosts))
    return {
        "range": target_range,
        "hosts_up": len(hosts),
        "hosts": hosts,
    }


def list_os_eol(config: dict) -> dict[str, Any]:
    """Read the EOL database and return all entries with status.

    Args:
        config: Full configuration dict.

    Returns:
        Dict with keys: total, eol_count, supported_count, entries.
    """
    eol_path = config.get("audit", {}).get("eol_database", "./data/eol_database.json")

    try:
        with open(eol_path, encoding="utf-8") as f:
            eol_db = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Cannot read EOL database %s: %s", eol_path, exc)
        return {"total": 0, "eol_count": 0, "supported_count": 0, "entries": [], "error": str(exc)}

    now = datetime.now(timezone.utc).date()
    entries = []
    eol_count = 0

    for os_name, info in eol_db.items():
        eol_date_str = info.get("eol_date", "")
        try:
            eol_date = datetime.strptime(eol_date_str, "%Y-%m-%d").date()
            is_eol = eol_date < now
        except ValueError:
            is_eol = False

        if is_eol:
            eol_count += 1

        entries.append({
            "os_name": os_name,
            "eol_date": eol_date_str,
            "is_eol": is_eol,
            "vendor": info.get("vendor", ""),
            "category": info.get("category", ""),
        })

    return {
        "total": len(entries),
        "eol_count": eol_count,
        "supported_count": len(entries) - eol_count,
        "entries": entries,
    }


def audit_from_csv(config: dict, csv_path: str) -> dict[str, Any]:
    """Audit hosts from a CSV inventory file.

    Reads the CSV, checks connectivity for each host, and crosses with EOL data.
    If the CSV has no 'ip' column, tries to resolve hostname via DNS.

    Args:
        config: Full configuration dict.
        csv_path: Path to inventory CSV file.

    Returns:
        Dict with keys: total_hosts, reachable, unreachable, eol_hosts, hosts.
    """
    if not csv_path or csv_path in ("all", ""):
        csv_path = config.get("audit", {}).get("inventory_csv", "./data/sample_inventory.csv")

    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        logger.error("Cannot read CSV %s: %s", csv_path, exc)
        return {
            "total_hosts": 0, "reachable": 0, "unreachable": 0,
            "eol_hosts": 0, "hosts": [], "error": str(exc),
        }

    # Load EOL data for cross-referencing
    eol_data = list_os_eol(config)
    eol_lookup: dict[str, bool] = {}
    for entry in eol_data.get("entries", []):
        eol_lookup[entry["os_name"]] = entry["is_eol"]

    timeout = config.get("discovery", {}).get("timeout", 2)
    hosts = []
    reachable_count = 0
    eol_count = 0

    for row in rows:
        hostname = row.get("hostname", "")
        ip = row.get("ip", "")
        os_name = row.get("os_name", "")
        os_version = row.get("os_version", "")
        role = row.get("role", "")

        # If no ip column, try to resolve hostname
        if not ip and hostname:
            resolved = resolve_dns(hostname)
            if resolved:
                ip = resolved

        full_os = f"{os_name} {os_version}".strip()
        is_eol = eol_lookup.get(full_os, False)
        if is_eol:
            eol_count += 1

        # Check connectivity via SSH (port 22) then HTTP (port 80) as fallback
        is_reachable = False
        if ip:
            logger.info("Checking connectivity: %s (%s)", hostname, ip)
            is_reachable = check_port(ip, 22, timeout=timeout)
            if not is_reachable:
                is_reachable = check_port(ip, 80, timeout=timeout)

        if is_reachable:
            reachable_count += 1

        hosts.append({
            "hostname": hostname,
            "ip": ip,
            "os": full_os,
            "role": role,
            "reachable": is_reachable,
            "is_eol": is_eol,
        })

    return {
        "total_hosts": len(hosts),
        "reachable": reachable_count,
        "unreachable": len(hosts) - reachable_count,
        "eol_hosts": eol_count,
        "hosts": hosts,
    }


def generate_report(config: dict) -> dict[str, Any]:
    """Generate a comprehensive audit report combining all audit functions.

    Executes scan_network + audit_from_csv + list_os_eol and saves JSON report.

    Args:
        config: Full configuration dict.

    Returns:
        Dict with keys: report_path, scan, inventory, eol, has_errors.
    """
    network_range = config.get("audit", {}).get("network_range", "172.16.135.0/24")

    scan_result = scan_network(config, network_range)
    eol_result = list_os_eol(config)
    inventory_result = audit_from_csv(config, "")

    has_errors = bool(
        scan_result.get("error")
        or eol_result.get("error")
        or inventory_result.get("error")
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "network_range": network_range,
        "has_errors": has_errors,
        "scan": scan_result,
        "eol": eol_result,
        "inventory": inventory_result,
        "summary": {
            "hosts_discovered": scan_result.get("hosts_up", 0),
            "inventory_total": inventory_result.get("total_hosts", 0),
            "inventory_reachable": inventory_result.get("reachable", 0),
            "eol_systems": eol_result.get("eol_count", 0),
        },
    }

    # Save report to output/reports/
    output_dir = config.get("general", {}).get("output_dir", "./output")
    reports_dir = os.path.join(output_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(reports_dir, f"audit_report_{timestamp}.json")

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info("Report saved to %s", report_path)
    except OSError as exc:
        logger.error("Cannot save report: %s", exc)
        report_path = ""
        has_errors = True

    return {
        "report_path": report_path,
        "has_errors": has_errors,
        "scan": scan_result,
        "inventory": inventory_result,
        "eol": eol_result,
    }


def _categorize_port(port: int) -> list[str]:
    """Return service categories for a given port."""
    from src.modules.diagnostic.constant import SERVICE_NAMES

    name = SERVICE_NAMES.get(port)
    return [name] if name else []
