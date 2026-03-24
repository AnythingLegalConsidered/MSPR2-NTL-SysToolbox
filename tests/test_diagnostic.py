"""Tests pour le module diagnostic (package) — utilise des mocks, pas de VMs requises."""

from unittest.mock import patch

from src.interfaces import EXIT_CRITICAL, EXIT_OK, EXIT_UNKNOWN, EXIT_WARNING
from src.modules.diagnostic import run

TARGET_DC = "192.168.10.10"
TARGET_DB = "192.168.10.21"
TARGET_LINUX = "192.168.10.21"
TARGET_HTTP = "192.168.10.50"

BASE_CONFIG = {
    "general": {"timeout": 10, "log_level": "INFO", "output_dir": "./output"},
    "targets": {"dc01": {"host": TARGET_DC}, "wms_db": {"host": TARGET_DB}},
    "mysql": {"host": TARGET_DB, "port": 3306, "user": "wms_user", "password": "secret", "database": "wms"},
    "ssh": {"host": TARGET_DB, "port": 22, "user": "sysadmin", "password": "secret"},
    "discovery": {"ports": [22, 80, 3306], "timeout": 2},
}


# ---------------------------------------------------------------------------
# run() — dispatcher
# ---------------------------------------------------------------------------


class TestRun:
    def test_dispatches_check_ad_dns(self):
        with patch("src.modules.diagnostic._check_ad_dns") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_DC, action="check_ad_dns")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_DC)
        assert result == {"status": "OK"}

    def test_dispatches_check_mysql(self):
        with patch("src.modules.diagnostic._check_mysql") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_DB, action="check_mysql")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_DB)
        assert result == {"status": "OK"}

    def test_dispatches_check_linux(self):
        with patch("src.modules.diagnostic._check_linux") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_LINUX, action="check_linux")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_LINUX)
        assert result == {"status": "OK"}

    def test_dispatches_check_http(self):
        with patch("src.modules.diagnostic._check_http") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_HTTP, action="check_http")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_HTTP)
        assert result == {"status": "OK"}

    def test_unknown_on_invalid_action(self):
        result = run(BASE_CONFIG, TARGET_DC, action="foobar")
        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_default_action_is_check_ad_dns(self):
        with patch("src.modules.diagnostic._check_ad_dns") as mock:
            mock.return_value = {"status": "OK"}
            run(BASE_CONFIG, TARGET_DC)
        mock.assert_called_once()


# ---------------------------------------------------------------------------
# _check_ad_dns() via run()
# ---------------------------------------------------------------------------


class TestCheckAdDns:
    def test_ok_when_all_checks_pass_with_winrm(self):
        config = {**BASE_CONFIG, "winrm": {"user": "admin", "password": "pass"}}
        with (
            patch("src.modules.diagnostic.checks.check_dns", return_value=(True, "192.168.10.10")),
            patch("src.modules.diagnostic.checks.check_ports", return_value=("OK", {389: True, 53: True})),
            patch("src.modules.diagnostic.checks.check_ldap", return_value=True),
            patch("src.modules.diagnostic.checks.check_services", return_value=("OK", {"NTDS": "Running"})),
        ):
            result = run(config, TARGET_DC, action="check_ad_dns")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK

    def test_warning_when_winrm_not_configured(self):
        with (
            patch("src.modules.diagnostic.checks.check_dns", return_value=(True, "192.168.10.10")),
            patch("src.modules.diagnostic.checks.check_ports", return_value=("OK", {389: True, 53: True})),
            patch("src.modules.diagnostic.checks.check_ldap", return_value=True),
        ):
            result = run(BASE_CONFIG, TARGET_DC, action="check_ad_dns")

        assert result["status"] == "WARNING"
        assert result["exit_code"] == EXIT_WARNING

    def test_critical_when_dns_fails(self):
        with (
            patch("src.modules.diagnostic.checks.check_dns", return_value=(False, "NXDOMAIN")),
            patch("src.modules.diagnostic.checks.check_ports", return_value=("OK", {389: True})),
            patch("src.modules.diagnostic.checks.check_ldap", return_value=True),
        ):
            result = run(BASE_CONFIG, TARGET_DC, action="check_ad_dns")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_critical_when_ldap_fails(self):
        with (
            patch("src.modules.diagnostic.checks.check_dns", return_value=(True, "192.168.10.10")),
            patch("src.modules.diagnostic.checks.check_ports", return_value=("OK", {389: True})),
            patch("src.modules.diagnostic.checks.check_ldap", return_value=False),
        ):
            result = run(BASE_CONFIG, TARGET_DC, action="check_ad_dns")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_unknown_on_exception(self):
        with patch("src.modules.diagnostic.checks.check_dns", side_effect=OSError("network error")):
            result = run(BASE_CONFIG, TARGET_DC, action="check_ad_dns")

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_result_has_correct_module_and_function(self):
        with (
            patch("src.modules.diagnostic.checks.check_dns", return_value=(True, "192.168.10.10")),
            patch("src.modules.diagnostic.checks.check_ports", return_value=("OK", {389: True})),
            patch("src.modules.diagnostic.checks.check_ldap", return_value=True),
        ):
            result = run(BASE_CONFIG, TARGET_DC, action="check_ad_dns")

        assert result["module"] == "diagnostic"
        assert result["function"] == "check_ad_dns"
        assert result["target"] == TARGET_DC


# ---------------------------------------------------------------------------
# _check_mysql() via run()
# ---------------------------------------------------------------------------


class TestCheckMysql:
    def test_ok_when_reachable(self):
        with patch(
            "src.modules.diagnostic.checks.check_mysql_port",
            return_value={"reachable": True, "port": 3306, "version": "8.0.36", "banner": None},
        ):
            result = run(BASE_CONFIG, TARGET_DB, action="check_mysql")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK

    def test_critical_when_unreachable(self):
        with patch(
            "src.modules.diagnostic.checks.check_mysql_port",
            return_value={"reachable": False, "port": 3306, "version": None, "banner": None},
        ):
            result = run(BASE_CONFIG, TARGET_DB, action="check_mysql")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_unknown_on_exception(self):
        with patch("src.modules.diagnostic.checks.check_mysql_port", side_effect=Exception("timeout")):
            result = run(BASE_CONFIG, TARGET_DB, action="check_mysql")

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_result_has_correct_module_and_function(self):
        with patch(
            "src.modules.diagnostic.checks.check_mysql_port",
            return_value={"reachable": True, "port": 3306, "version": "8.0", "banner": None},
        ):
            result = run(BASE_CONFIG, TARGET_DB, action="check_mysql")

        assert result["module"] == "diagnostic"
        assert result["function"] == "check_mysql"


# ---------------------------------------------------------------------------
# _check_linux() via run()
# ---------------------------------------------------------------------------


class TestCheckLinux:
    def test_ok_when_services_found(self):
        with patch(
            "src.modules.diagnostic.checks.check_host_services",
            return_value={"host": TARGET_LINUX, "open_ports": [], "categories": ["ssh", "mysql"]},
        ):
            result = run(BASE_CONFIG, TARGET_LINUX, action="check_linux")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK

    def test_critical_when_no_services(self):
        with patch(
            "src.modules.diagnostic.checks.check_host_services",
            return_value={"host": TARGET_LINUX, "open_ports": [], "categories": []},
        ):
            result = run(BASE_CONFIG, TARGET_LINUX, action="check_linux")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_unknown_on_exception(self):
        with patch("src.modules.diagnostic.checks.check_host_services", side_effect=Exception("scan error")):
            result = run(BASE_CONFIG, TARGET_LINUX, action="check_linux")

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN


# ---------------------------------------------------------------------------
# _check_http() via run()
# ---------------------------------------------------------------------------


class TestCheckHttp:
    def test_ok_when_http_responds(self):
        with patch(
            "src.modules.diagnostic.checks.check_http",
            return_value={"ok": True, "status_code": 200, "server": "nginx", "response_time_ms": 42},
        ):
            result = run(BASE_CONFIG, TARGET_HTTP, action="check_http")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK

    def test_critical_when_http_fails(self):
        with patch(
            "src.modules.diagnostic.checks.check_http",
            return_value={"ok": False, "error": "Connection refused"},
        ):
            result = run(BASE_CONFIG, TARGET_HTTP, action="check_http")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_unknown_on_exception(self):
        with patch("src.modules.diagnostic.checks.check_http", side_effect=Exception("timeout")):
            result = run(BASE_CONFIG, TARGET_HTTP, action="check_http")

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN
