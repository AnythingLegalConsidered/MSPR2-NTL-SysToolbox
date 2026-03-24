"""Tests pour le module audit — utilise des mocks, pas de nmap/reseau requis."""

import json
from unittest.mock import patch

from src.interfaces import EXIT_UNKNOWN
from src.modules.audit import run

BASE_CONFIG = {
    "general": {"timeout": 10, "log_level": "INFO", "output_dir": "./output"},
    "audit": {
        "network_range": "172.16.135.0/24",
        "eol_database": "./data/eol_database.json",
        "inventory_csv": "./data/sample_inventory.csv",
    },
    "discovery": {"ports": [22, 80, 443], "timeout": 2},
}


# ---------------------------------------------------------------------------
# run() — dispatcher
# ---------------------------------------------------------------------------


class TestRun:
    def test_dispatches_scan_network(self):
        with patch("src.modules.audit._scan_network") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, "172.16.135.0/24", action="scan_network")
        mock.assert_called_once()
        assert result == {"status": "OK"}

    def test_dispatches_list_os_eol(self):
        with patch("src.modules.audit._list_os_eol") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, "all", action="list_os_eol")
        mock.assert_called_once()
        assert result == {"status": "OK"}

    def test_dispatches_audit_from_csv(self):
        with patch("src.modules.audit._audit_from_csv") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, "inventory.csv", action="audit_from_csv")
        mock.assert_called_once()
        assert result == {"status": "OK"}

    def test_dispatches_generate_report(self):
        with patch("src.modules.audit._generate_report") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, "all", action="generate_report")
        mock.assert_called_once()
        assert result == {"status": "OK"}

    def test_unknown_on_invalid_action(self):
        result = run(BASE_CONFIG, "target", action="foobar")
        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN


# ---------------------------------------------------------------------------
# Scanner validation
# ---------------------------------------------------------------------------


class TestScannerValidation:
    def test_rejects_target_with_spaces(self):
        from src.modules.audit.scanner import _validate_target_range

        err = _validate_target_range("192.168.1.0/24 --script=exploit")
        assert err is not None

    def test_accepts_valid_cidr(self):
        from src.modules.audit.scanner import _validate_target_range

        err = _validate_target_range("192.168.1.0/24")
        assert err is None

    def test_accepts_comma_separated(self):
        from src.modules.audit.scanner import _validate_target_range

        err = _validate_target_range("192.168.1.1,192.168.1.2")
        assert err is None

    def test_accepts_range_notation(self):
        from src.modules.audit.scanner import _validate_target_range

        err = _validate_target_range("192.168.1.1-50")
        assert err is None

    def test_validates_ports(self):
        from src.modules.audit.scanner import _validate_ports

        valid = _validate_ports([22, 80, -1, 99999, "abc"])
        assert valid == [22, 80]

    def test_empty_ports_returns_empty(self):
        from src.modules.audit.scanner import _validate_ports

        valid = _validate_ports([])
        assert valid == []

    def test_rejects_invalid_ip(self):
        from src.modules.audit.scanner import _validate_target_range

        err = _validate_target_range("999.999.999.999")
        assert err is not None

    def test_rejects_empty_range(self):
        from src.modules.audit.scanner import _validate_target_range

        err = _validate_target_range("")
        assert err is not None


# ---------------------------------------------------------------------------
# scan_network() — with mocked nmap
# ---------------------------------------------------------------------------


class TestScanNetwork:
    def test_returns_error_on_invalid_range(self):
        from src.modules.audit.scanner import scan_network

        result = scan_network(BASE_CONFIG, "not a valid range!")
        assert "error" in result
        assert result["hosts_up"] == 0

    def test_returns_error_on_empty_ports(self):
        from src.modules.audit.scanner import scan_network

        config = {**BASE_CONFIG, "discovery": {"ports": [-1, 99999], "timeout": 2}}
        result = scan_network(config, "192.168.1.0/24")
        assert "error" in result


# ---------------------------------------------------------------------------
# list_os_eol()
# ---------------------------------------------------------------------------


class TestListOsEol:
    def test_returns_entries(self, tmp_path):
        from src.modules.audit.scanner import list_os_eol

        eol_db = {
            "Windows Server 2012 R2": {"eol_date": "2023-10-10", "vendor": "Microsoft", "category": "server"},
            "Ubuntu 22.04": {"eol_date": "2027-04-01", "vendor": "Canonical", "category": "server"},
        }
        eol_file = tmp_path / "eol.json"
        eol_file.write_text(json.dumps(eol_db), encoding="utf-8")

        config = {**BASE_CONFIG, "audit": {**BASE_CONFIG["audit"], "eol_database": str(eol_file)}}
        result = list_os_eol(config)

        assert result["total"] == 2
        assert result["eol_count"] >= 1  # Windows Server 2012 R2 is EOL
        assert len(result["entries"]) == 2

    def test_returns_error_on_missing_file(self):
        from src.modules.audit.scanner import list_os_eol

        config = {**BASE_CONFIG, "audit": {**BASE_CONFIG["audit"], "eol_database": "/nonexistent.json"}}
        result = list_os_eol(config)

        assert "error" in result
        assert result["total"] == 0


# ---------------------------------------------------------------------------
# audit_from_csv()
# ---------------------------------------------------------------------------


class TestAuditFromCsv:
    def test_audits_csv_hosts(self, tmp_path):
        from src.modules.audit.scanner import audit_from_csv

        # Create sample CSV
        csv_file = tmp_path / "data" / "inventory.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        csv_file.write_text(
            "hostname,ip,os_name,os_version,role\n"
            "srv1,127.0.0.1,Ubuntu,22.04,web\n",
            encoding="utf-8",
        )
        # Create EOL database
        eol_file = tmp_path / "data" / "eol.json"
        eol_file.write_text("{}", encoding="utf-8")

        config = {
            **BASE_CONFIG,
            "audit": {
                **BASE_CONFIG["audit"],
                "inventory_csv": str(csv_file),
                "eol_database": str(eol_file),
            },
            "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path / "output")},
        }

        with patch("src.modules.audit.scanner.check_port", return_value=True):
            with patch("src.modules.audit.scanner.validate_path_within", return_value=csv_file):
                result = audit_from_csv(config, str(csv_file))

        assert result["total_hosts"] == 1
        assert result["reachable"] == 1
