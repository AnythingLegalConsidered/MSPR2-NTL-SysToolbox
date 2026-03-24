"""Tests pour le module audit — utilise des mocks, pas de nmap/reseau requis."""

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
