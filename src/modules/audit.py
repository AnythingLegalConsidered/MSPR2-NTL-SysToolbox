"""
Module: [audit]
Description: Network inventory and OS end-of-life audit module
Responsable: Zaid
"""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.interfaces import (  # noqa: F401
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    EXIT_WARNING,
    ModuleConfigError,
    ModuleExecutionError,
    build_result,
)

logger = logging.getLogger(__name__)

MODULE_NAME = "[audit]"

# Days before EOL to trigger WARNING
WARNING_DAYS = 180


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(config: dict, target: str, **kwargs: Any) -> dict[str, Any]:
    logger.info("Starting %s on target: %s", MODULE_NAME, target)

    action = kwargs.get("action", "audit_from_csv")

    try:
        audit_config = config.get("audit", {})
        eol_path = audit_config.get("eol_database", "./data/eol_database.json")
        csv_path = audit_config.get("inventory_csv", "./data/sample_inventory.csv")

        if action == "scan_network":
            network_range = target or audit_config.get("network_range", "192.168.10.0/24")
            return scan_network(network_range)

        elif action == "list_os_eol":
            return list_os_eol_action(eol_path, target)

        elif action == "audit_from_csv":
            path = target if (target and target not in ("all", "")) else csv_path
            return audit_from_csv(path, eol_path)

        elif action == "generate_report":
            return generate_report(csv_path, eol_path, config)

        else:
            raise ModuleConfigError(f"Unknown action: {action}")

    except ModuleConfigError:
        raise
    except Exception as e:
        logger.error("%s execution failed: %s", MODULE_NAME, e)
        raise ModuleExecutionError(str(e)) from e


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_eol_database(eol_path: str) -> dict:
    with open(eol_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_eol_status(eol_info: dict | None) -> tuple[str, int]:
    """Return (status, exit_code) based on EOL info."""
    if eol_info is None:
        return "UNKNOWN", EXIT_UNKNOWN

    today = datetime.today()
    eol_date = datetime.strptime(eol_info["eol_date"], "%Y-%m-%d")

    if today > eol_date:
        return "CRITICAL", EXIT_CRITICAL

    days_left = (eol_date - today).days
    if days_left <= WARNING_DAYS:
        return "WARNING", EXIT_WARNING

    return "OK", EXIT_OK


# ---------------------------------------------------------------------------
# scan_network
# ---------------------------------------------------------------------------

def scan_network(network_range: str) -> dict[str, Any]:
    """
    Scan a network range with nmap. Discovers live hosts and attempts OS detection.
    Requires nmap installed on the system. OS detection requires root/admin privileges.
    """
    try:
        import nmap  # type: ignore[import]
    except ImportError:
        return build_result(
            module=MODULE_NAME,
            function="scan_network",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=network_range,
            details={"error": "python-nmap not installed. Run: pip install python-nmap"},
            message="python-nmap is required for network scanning",
        )

    try:
        nm = nmap.PortScanner()
        logger.info("Scanning network range: %s", network_range)

        # -sn: ping scan only (fast, no port scan)
        # -T4: aggressive timing
        # --osscan-guess: best-effort OS guessing (needs root for full -O)
        try:
            nm.scan(hosts=network_range, arguments="-sn -T4 -O --osscan-guess")
        except Exception:
            # Fallback without OS detection if no admin privileges
            logger.warning("OS detection failed (needs root/admin), falling back to ping scan only")
            nm.scan(hosts=network_range, arguments="-sn -T4")

        hosts = []
        for host in nm.all_hosts():
            host_info = nm[host]
            hostnames = [h["name"] for h in host_info.hostnames() if h["name"]]

            os_guess = ""
            os_accuracy = ""
            if "osmatch" in host_info and host_info["osmatch"]:
                best = host_info["osmatch"][0]
                os_guess = best.get("name", "")
                os_accuracy = best.get("accuracy", "")

            hosts.append({
                "ip": host,
                "hostname": hostnames[0] if hostnames else "",
                "state": host_info.state(),
                "os_guess": os_guess,
                "os_accuracy": f"{os_accuracy}%" if os_accuracy else "",
            })

        return build_result(
            module=MODULE_NAME,
            function="scan_network",
            status="OK",
            exit_code=EXIT_OK,
            target=network_range,
            details={"host_count": len(hosts), "hosts": hosts},
            message=f"Found {len(hosts)} host(s) on {network_range}",
        )

    except Exception as e:
        logger.error("Network scan failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="scan_network",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=network_range,
            details={"error": str(e)},
            message=f"Network scan failed: {e}",
        )


# ---------------------------------------------------------------------------
# list_os_eol
# ---------------------------------------------------------------------------

def list_os_eol_action(eol_path: str, os_filter: str = "all") -> dict[str, Any]:
    """
    List EOL dates for all OSes in the database, or filter by name.
    Called from the CLI menu as action 'list_os_eol'.
    """
    try:
        eol_data = _load_eol_database(eol_path)

        if os_filter and os_filter.lower() not in ("all", ""):
            entries = {k: v for k, v in eol_data.items() if os_filter.lower() in k.lower()}
            if not entries:
                return build_result(
                    module=MODULE_NAME,
                    function="list_os_eol",
                    status="UNKNOWN",
                    exit_code=EXIT_UNKNOWN,
                    target=os_filter,
                    details={"os_filter": os_filter, "entries": {}},
                    message=f"No EOL data found for OS matching: {os_filter}",
                )
        else:
            entries = eol_data

        today = datetime.today()
        result_entries = {}
        for os_name, info in entries.items():
            eol_dt = datetime.strptime(info["eol_date"], "%Y-%m-%d")
            status, _ = _get_eol_status(info)
            result_entries[os_name] = {
                **info,
                "days_until_eol": (eol_dt - today).days,
                "status": status,
            }

        return build_result(
            module=MODULE_NAME,
            function="list_os_eol",
            status="OK",
            exit_code=EXIT_OK,
            target=os_filter or "all",
            details={"entry_count": len(result_entries), "entries": result_entries},
            message=f"EOL data loaded for {len(result_entries)} OS version(s)",
        )

    except Exception as e:
        logger.error("list_os_eol failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="list_os_eol",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=os_filter or "all",
            details={"error": str(e)},
            message=f"Failed to load EOL database: {e}",
        )


# ---------------------------------------------------------------------------
# audit_from_csv
# ---------------------------------------------------------------------------

def audit_from_csv(csv_path: str, eol_path: str) -> dict[str, Any]:
    """
    Compare an inventory CSV (hostname, os_name, os_version, role)
    against the EOL database. Returns per-host status and global severity.
    """
    try:
        eol_data = _load_eol_database(eol_path)
        results = []
        worst_exit = EXIT_OK

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                hostname = row.get("hostname", "")
                os_key = f"{row.get('os_name', '').strip()} {row.get('os_version', '').strip()}".strip()

                eol_info = eol_data.get(os_key)
                status, exit_code = _get_eol_status(eol_info)

                if exit_code > worst_exit:
                    worst_exit = exit_code

                entry: dict[str, Any] = {
                    "hostname": hostname,
                    "os": os_key,
                    "role": row.get("role", ""),
                    "status": status,
                    "eol_date": eol_info["eol_date"] if eol_info else None,
                    "vendor": eol_info["vendor"] if eol_info else None,
                }
                if eol_info:
                    eol_dt = datetime.strptime(eol_info["eol_date"], "%Y-%m-%d")
                    entry["days_until_eol"] = (eol_dt - datetime.today()).days

                results.append(entry)

        counts = {s: sum(1 for r in results if r["status"] == s) for s in ("OK", "WARNING", "CRITICAL", "UNKNOWN")}
        status_map = {EXIT_OK: "OK", EXIT_WARNING: "WARNING", EXIT_CRITICAL: "CRITICAL", EXIT_UNKNOWN: "UNKNOWN"}
        overall_status = status_map.get(worst_exit, "UNKNOWN")

        return build_result(
            module=MODULE_NAME,
            function="audit_from_csv",
            status=overall_status,
            exit_code=worst_exit,
            target=csv_path,
            details={"host_count": len(results), "counts": counts, "results": results},
            message=(
                f"Audit: {counts['CRITICAL']} critical, {counts['WARNING']} warning, "
                f"{counts['OK']} ok, {counts['UNKNOWN']} unknown"
            ),
        )

    except Exception as e:
        logger.error("audit_from_csv failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="audit_from_csv",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=csv_path,
            details={"error": str(e)},
            message=f"Audit failed: {e}",
        )


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------

def generate_report(csv_path: str, eol_path: str, config: dict) -> dict[str, Any]:
    """
    Generate a full obsolescence report. Groups hosts by status,
    highlights critical/warning items, and saves JSON report to output/reports/.
    """
    try:
        audit_result = audit_from_csv(csv_path, eol_path)
        results = audit_result.get("details", {}).get("results", [])

        critical = [r for r in results if r["status"] == "CRITICAL"]
        warning = [r for r in results if r["status"] == "WARNING"]
        ok = [r for r in results if r["status"] == "OK"]
        unknown = [r for r in results if r["status"] == "UNKNOWN"]

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_csv": csv_path,
            "summary": {
                "total": len(results),
                "critical": len(critical),
                "warning": len(warning),
                "ok": len(ok),
                "unknown": len(unknown),
            },
            "critical_hosts": critical,
            "warning_hosts": warning,
            "ok_hosts": ok,
            "unknown_hosts": unknown,
        }

        # Save report
        output_dir = config.get("general", {}).get("output_dir", "./output")
        report_dir = Path(output_dir) / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"{ts}_audit_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("Audit report saved to %s", report_path)

        overall_exit = EXIT_CRITICAL if critical else (EXIT_WARNING if warning else EXIT_OK)
        overall_status = "CRITICAL" if critical else ("WARNING" if warning else "OK")

        return build_result(
            module=MODULE_NAME,
            function="generate_report",
            status=overall_status,
            exit_code=overall_exit,
            target="all",
            details={"report": report, "saved_to": str(report_path)},
            message=(
                f"Report saved: {len(critical)} critical, {len(warning)} warning, "
                f"{len(ok)} ok — {report_path}"
            ),
        )

    except Exception as e:
        logger.error("generate_report failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="generate_report",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target="all",
            details={"error": str(e)},
            message=f"Report generation failed: {e}",
        )


# ---------------------------------------------------------------------------
# Legacy internal helper (kept for backward compatibility)
# ---------------------------------------------------------------------------

def list_os_eol(os_name: str, eol_data: dict) -> dict | None:
    """Direct EOL lookup by exact OS key. Used internally."""
    try:
        return eol_data.get(os_name)
    except Exception as e:
        logger.error("Error retrieving EOL info for %s: %s", os_name, e)
        return None
