"""
Tests unitaires — Module audit
Responsable: Zaid
"""

import csv
import json
from pathlib import Path

import pytest

from src.interfaces import EXIT_CRITICAL, EXIT_OK, EXIT_UNKNOWN, EXIT_WARNING
from src.modules.audit import (
    _get_eol_status,
    audit_from_csv,
    generate_report,
    list_os_eol,
    list_os_eol_action,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EOL_DATA = {
    "Windows Server 2022": {
        "eol_date": "2031-10-14",
        "eol_extended": "2031-10-14",
        "vendor": "Microsoft",
        "category": "server",
    },
    "Windows 7": {
        "eol_date": "2020-01-14",
        "eol_extended": "2023-01-10",
        "vendor": "Microsoft",
        "category": "desktop",
    },
    "Ubuntu 20.04 LTS": {
        "eol_date": "2025-04-02",
        "eol_extended": "2030-04-02",
        "vendor": "Canonical",
        "category": "server",
    },
    "Debian 11": {
        "eol_date": "2026-06-01",
        "eol_extended": None,
        "vendor": "Debian",
        "category": "server",
    },
}

INVENTORY_ROWS = [
    {"hostname": "DC01", "os_name": "Windows Server", "os_version": "2022", "role": "AD/DNS"},
    {"hostname": "PC-OLD", "os_name": "Windows", "os_version": "7", "role": "Workstation"},
    {"hostname": "WMS-DB", "os_name": "Ubuntu", "os_version": "20.04 LTS", "role": "DB"},
    {"hostname": "SRV-INTRANET", "os_name": "Debian", "os_version": "11", "role": "Intranet"},
    {"hostname": "UNKNOWN-HOST", "os_name": "FreeBSD", "os_version": "13", "role": "Unknown"},
]


@pytest.fixture
def eol_file(tmp_path: Path) -> str:
    p = tmp_path / "eol_database.json"
    p.write_text(json.dumps(EOL_DATA), encoding="utf-8")
    return str(p)


@pytest.fixture
def inventory_file(tmp_path: Path) -> str:
    p = tmp_path / "inventory.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["hostname", "os_name", "os_version", "role"])
        writer.writeheader()
        writer.writerows(INVENTORY_ROWS)
    return str(p)


@pytest.fixture
def basic_config(tmp_path: Path) -> dict:
    return {
        "general": {"output_dir": str(tmp_path / "output"), "log_level": "INFO"},
        "audit": {
            "eol_database": str(tmp_path / "eol_database.json"),
            "inventory_csv": str(tmp_path / "inventory.csv"),
        },
    }


# ---------------------------------------------------------------------------
# _get_eol_status
# ---------------------------------------------------------------------------

class TestGetEolStatus:
    def test_none_returns_unknown(self):
        status, code = _get_eol_status(None)
        assert status == "UNKNOWN"
        assert code == EXIT_UNKNOWN

    def test_past_eol_returns_critical(self):
        info = {"eol_date": "2020-01-01", "vendor": "X", "category": "server"}
        status, code = _get_eol_status(info)
        assert status == "CRITICAL"
        assert code == EXIT_CRITICAL

    def test_far_future_eol_returns_ok(self):
        info = {"eol_date": "2099-01-01", "vendor": "X", "category": "server"}
        status, code = _get_eol_status(info)
        assert status == "OK"
        assert code == EXIT_OK

    def test_near_future_eol_returns_warning(self):
        # Debian 11 EOL: 2026-06-01 → ~77 days from 2026-03-16 → WARNING
        info = {"eol_date": "2026-06-01", "vendor": "Debian", "category": "server"}
        status, code = _get_eol_status(info)
        assert status == "WARNING"
        assert code == EXIT_WARNING


# ---------------------------------------------------------------------------
# list_os_eol (internal helper)
# ---------------------------------------------------------------------------

class TestListOsEolInternal:
    def test_known_os_returns_dict(self):
        result = list_os_eol("Windows Server 2022", EOL_DATA)
        assert result is not None
        assert result["vendor"] == "Microsoft"

    def test_unknown_os_returns_none(self):
        result = list_os_eol("AmigaOS 3.1", EOL_DATA)
        assert result is None


# ---------------------------------------------------------------------------
# list_os_eol_action
# ---------------------------------------------------------------------------

class TestListOsEolAction:
    def test_all_returns_all_entries(self, eol_file: str):
        result = list_os_eol_action(eol_file, "all")
        assert result["status"] == "OK"
        assert result["details"]["entry_count"] == len(EOL_DATA)

    def test_filter_returns_matching_entries(self, eol_file: str):
        result = list_os_eol_action(eol_file, "Ubuntu")
        assert result["status"] == "OK"
        entries = result["details"]["entries"]
        assert all("Ubuntu" in k for k in entries)

    def test_unknown_filter_returns_unknown(self, eol_file: str):
        result = list_os_eol_action(eol_file, "AmigaOS")
        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_entries_contain_status_and_days(self, eol_file: str):
        result = list_os_eol_action(eol_file, "Windows Server 2022")
        entry = result["details"]["entries"]["Windows Server 2022"]
        assert "status" in entry
        assert "days_until_eol" in entry
        assert entry["status"] == "OK"

    def test_result_has_standard_keys(self, eol_file: str):
        result = list_os_eol_action(eol_file, "all")
        for key in ("module", "function", "timestamp", "status", "exit_code", "target", "details", "message"):
            assert key in result


# ---------------------------------------------------------------------------
# audit_from_csv
# ---------------------------------------------------------------------------

class TestAuditFromCsv:
    def test_returns_correct_host_count(self, inventory_file: str, eol_file: str):
        result = audit_from_csv(inventory_file, eol_file)
        assert result["details"]["host_count"] == len(INVENTORY_ROWS)

    def test_known_ok_host(self, inventory_file: str, eol_file: str):
        result = audit_from_csv(inventory_file, eol_file)
        hosts = {r["hostname"]: r for r in result["details"]["results"]}
        assert hosts["DC01"]["status"] == "OK"

    def test_known_critical_host(self, inventory_file: str, eol_file: str):
        result = audit_from_csv(inventory_file, eol_file)
        hosts = {r["hostname"]: r for r in result["details"]["results"]}
        assert hosts["PC-OLD"]["status"] == "CRITICAL"
        assert hosts["WMS-DB"]["status"] == "CRITICAL"

    def test_unknown_host(self, inventory_file: str, eol_file: str):
        result = audit_from_csv(inventory_file, eol_file)
        hosts = {r["hostname"]: r for r in result["details"]["results"]}
        assert hosts["UNKNOWN-HOST"]["status"] == "UNKNOWN"

    def test_overall_status_is_critical_when_any_critical(self, inventory_file: str, eol_file: str):
        result = audit_from_csv(inventory_file, eol_file)
        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_results_contain_eol_date(self, inventory_file: str, eol_file: str):
        result = audit_from_csv(inventory_file, eol_file)
        hosts = {r["hostname"]: r for r in result["details"]["results"]}
        assert hosts["DC01"]["eol_date"] == "2031-10-14"

    def test_counts_are_present(self, inventory_file: str, eol_file: str):
        result = audit_from_csv(inventory_file, eol_file)
        counts = result["details"]["counts"]
        assert "OK" in counts
        assert "CRITICAL" in counts
        assert "WARNING" in counts
        assert "UNKNOWN" in counts

    def test_missing_csv_returns_unknown(self, eol_file: str):
        result = audit_from_csv("/nonexistent/path.csv", eol_file)
        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_missing_eol_db_returns_unknown(self, inventory_file: str):
        result = audit_from_csv(inventory_file, "/nonexistent/eol.json")
        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------

class TestGenerateReport:
    def test_report_is_saved_to_disk(self, inventory_file: str, eol_file: str, basic_config: dict, tmp_path: Path):
        basic_config["audit"]["eol_database"] = eol_file
        basic_config["audit"]["inventory_csv"] = inventory_file
        result = generate_report(inventory_file, eol_file, basic_config)
        saved_path = result["details"]["saved_to"]
        assert Path(saved_path).exists()

    def test_report_contains_summary(self, inventory_file: str, eol_file: str, basic_config: dict):
        basic_config["audit"]["eol_database"] = eol_file
        result = generate_report(inventory_file, eol_file, basic_config)
        summary = result["details"]["report"]["summary"]
        assert summary["total"] == len(INVENTORY_ROWS)
        assert "critical" in summary
        assert "warning" in summary
        assert "ok" in summary
        assert "unknown" in summary

    def test_report_groups_by_status(self, inventory_file: str, eol_file: str, basic_config: dict):
        basic_config["audit"]["eol_database"] = eol_file
        result = generate_report(inventory_file, eol_file, basic_config)
        report = result["details"]["report"]
        assert "critical_hosts" in report
        assert "warning_hosts" in report
        assert "ok_hosts" in report
        assert "unknown_hosts" in report

    def test_overall_status_critical(self, inventory_file: str, eol_file: str, basic_config: dict):
        basic_config["audit"]["eol_database"] = eol_file
        result = generate_report(inventory_file, eol_file, basic_config)
        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_report_json_is_valid(self, inventory_file: str, eol_file: str, basic_config: dict):
        basic_config["audit"]["eol_database"] = eol_file
        result = generate_report(inventory_file, eol_file, basic_config)
        saved_path = result["details"]["saved_to"]
        with open(saved_path, encoding="utf-8") as f:
            data = json.load(f)
        assert "summary" in data
        assert "generated_at" in data
