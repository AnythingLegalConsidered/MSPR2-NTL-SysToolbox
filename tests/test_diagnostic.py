"""Tests pour le module diagnostic — utilise des mocks, pas de VMs requises."""

from unittest.mock import MagicMock, patch

import pytest

from src.interfaces import EXIT_CRITICAL, EXIT_OK, EXIT_UNKNOWN, EXIT_WARNING, ModuleConfigError, ModuleExecutionError
from src.modules.diagnostic import check_ad_dns, check_mysql, check_ubuntu, check_windows_server, run

TARGET_DC = "192.168.10.10"
TARGET_DB = "192.168.10.21"

BASE_CONFIG = {
    "general": {"timeout": 10, "log_level": "INFO", "output_dir": "./output"},
    "mysql": {"host": TARGET_DB, "port": 3306, "user": "wms_user", "password": "secret", "database": "wms"},
    "ssh": {"host": TARGET_DB, "port": 22, "user": "sysadmin", "password": "secret"},
}


# ---------------------------------------------------------------------------
# run() — dispatcher
# ---------------------------------------------------------------------------


class TestRun:
    def test_dispatches_check_ad_dns(self):
        with patch("src.modules.diagnostic.check_ad_dns") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_DC, action="check_ad_dns")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_DC)
        assert result == {"status": "OK"}

    def test_dispatches_check_mysql(self):
        with patch("src.modules.diagnostic.check_mysql") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_DB, action="check_mysql")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_DB)
        assert result == {"status": "OK"}

    def test_dispatches_check_windows_server(self):
        with patch("src.modules.diagnostic.check_windows_server") as mock:
            mock.return_value = {"status": "OK"}
            run(BASE_CONFIG, TARGET_DC, action="check_windows_server")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_DC)

    def test_dispatches_check_ubuntu(self):
        with patch("src.modules.diagnostic.check_ubuntu") as mock:
            mock.return_value = {"status": "OK"}
            run(BASE_CONFIG, TARGET_DB, action="check_ubuntu")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_DB)

    def test_raises_on_unknown_action(self):
        with pytest.raises(ModuleExecutionError, match="Action inconnue"):
            run(BASE_CONFIG, TARGET_DC, action="foobar")

    def test_default_action_raises(self):
        with pytest.raises(ModuleExecutionError):
            run(BASE_CONFIG, TARGET_DC)


# ---------------------------------------------------------------------------
# check_ad_dns()
# ---------------------------------------------------------------------------


class TestCheckAdDns:
    def test_ok_when_ldap_and_dns_up(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.check_port", return_value=True),
            patch("src.modules.diagnostic.resolve_dns", return_value="192.168.10.10"),
        ):
            result = check_ad_dns(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK
        assert result["details"]["ldap"] is True
        assert result["details"]["dns"] is True

    def test_warning_when_ldap_up_dns_down(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.check_port", return_value=True),
            patch("src.modules.diagnostic.resolve_dns", return_value=None),
        ):
            result = check_ad_dns(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "WARNING"
        assert result["exit_code"] == EXIT_WARNING
        assert result["details"]["dns"] is False

    def test_critical_when_ldap_down(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.check_port", return_value=False),
            patch("src.modules.diagnostic.resolve_dns", return_value=None),
        ):
            result = check_ad_dns(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL
        assert result["details"]["ldap"] is False

    def test_unknown_when_host_unreachable(self):
        with patch("src.modules.diagnostic.ping_host", return_value=False):
            result = check_ad_dns(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_unknown_on_unexpected_exception(self):
        with patch("src.modules.diagnostic.ping_host", side_effect=OSError("network error")):
            result = check_ad_dns(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_result_has_correct_module_and_function(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.check_port", return_value=True),
            patch("src.modules.diagnostic.resolve_dns", return_value="192.168.10.10"),
        ):
            result = check_ad_dns(BASE_CONFIG, TARGET_DC)

        assert result["module"] == "diagnostic"
        assert result["function"] == "check_ad_dns"
        assert result["target"] == TARGET_DC


# ---------------------------------------------------------------------------
# check_mysql()
# ---------------------------------------------------------------------------


def _make_mysql_mock(databases=None, uptime="3600", threads="2", questions="100"):
    """Construit un mock mysql.connector.connect() complet."""
    if databases is None:
        databases = [("information_schema",), ("wms",), ("mysql",)]

    cursor = MagicMock()
    cursor.fetchall.return_value = databases
    cursor.fetchone.side_effect = [
        ("Uptime", uptime),
        ("Threads_connected", threads),
        ("Questions", questions),
    ]

    conn = MagicMock()
    conn.cursor.return_value = cursor

    return conn


class TestCheckMysql:
    def test_ok_when_connected_and_wms_exists(self):
        conn = _make_mysql_mock()
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("mysql.connector.connect", return_value=conn),
        ):
            result = check_mysql(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK
        assert result["details"]["connected"] is True
        assert result["details"]["wms_exists"] is True

    def test_warning_when_wms_missing(self):
        conn = _make_mysql_mock(databases=[("information_schema",), ("mysql",)])
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("mysql.connector.connect", return_value=conn),
        ):
            result = check_mysql(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "WARNING"
        assert result["exit_code"] == EXIT_WARNING
        assert result["details"]["wms_exists"] is False

    def test_critical_on_access_denied(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("mysql.connector.connect", side_effect=Exception("Access denied for user")),
        ):
            result = check_mysql(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL
        assert result["details"]["connected"] is False

    def test_unknown_when_server_unreachable(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("mysql.connector.connect", side_effect=Exception("Can't connect to MySQL server")),
        ):
            result = check_mysql(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_raises_config_error_when_no_mysql_section(self):
        config_no_mysql = {"general": BASE_CONFIG["general"]}
        with pytest.raises(ModuleConfigError, match="mysql"):
            check_mysql(config_no_mysql, TARGET_DB)

    def test_result_contains_db_details(self):
        conn = _make_mysql_mock()
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("mysql.connector.connect", return_value=conn),
        ):
            result = check_mysql(BASE_CONFIG, TARGET_DB)

        details = result["details"]
        assert "databases" in details
        assert "uptime" in details
        assert "threads" in details
        assert "questions" in details


# ---------------------------------------------------------------------------
# check_windows_server()
# ---------------------------------------------------------------------------


def _make_wmic_output(cpu=30, free_ram=2097152, total_ram=4194304, disk_free=10737418240, disk_size=53687091200):
    """Retourne une fonction side_effect pour subprocess.run qui simule wmic."""
    def side_effect(cmd, **kwargs):
        mock = MagicMock()
        cmd_str = " ".join(str(c) for c in cmd)
        if "LoadPercentage" in cmd_str:
            mock.stdout = f"\nLoadPercentage={cpu}\n\n"
        elif "FreePhysicalMemory" in cmd_str:
            mock.stdout = f"\nFreePhysicalMemory={free_ram}\nTotalVisibleMemorySize={total_ram}\n\n"
        elif "FreeSpace" in cmd_str:
            mock.stdout = f"\nFreeSpace={disk_free}\nSize={disk_size}\n\n"
        else:
            mock.stdout = ""
        mock.returncode = 0
        return mock

    return side_effect


class TestCheckWindowsServer:
    def test_ok_when_all_metrics_below_threshold(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.subprocess.run", side_effect=_make_wmic_output()),
        ):
            result = check_windows_server(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK
        assert result["details"]["cpu_percent"] == 30

    def test_warning_when_cpu_above_threshold(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.subprocess.run", side_effect=_make_wmic_output(cpu=90)),
        ):
            result = check_windows_server(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "WARNING"
        assert result["exit_code"] == EXIT_WARNING
        assert result["details"]["cpu_percent"] == 90

    def test_warning_when_ram_above_threshold(self):
        # free_ram proche de 0 → RAM % proche de 100%
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.subprocess.run", side_effect=_make_wmic_output(free_ram=100000)),
        ):
            result = check_windows_server(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "WARNING"
        assert result["details"]["ram_percent"] > 80

    def test_unknown_when_host_unreachable(self):
        with patch("src.modules.diagnostic.ping_host", return_value=False):
            result = check_windows_server(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_critical_when_wmic_not_found(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.subprocess.run", side_effect=FileNotFoundError),
        ):
            result = check_windows_server(BASE_CONFIG, TARGET_DC)

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_result_has_all_metric_keys(self):
        with (
            patch("src.modules.diagnostic.ping_host", return_value=True),
            patch("src.modules.diagnostic.subprocess.run", side_effect=_make_wmic_output()),
        ):
            result = check_windows_server(BASE_CONFIG, TARGET_DC)

        for key in ("cpu_percent", "ram_percent", "disk_percent", "ram_total_mb", "disk_total_gb"):
            assert key in result["details"], f"Cle manquante: {key}"


# ---------------------------------------------------------------------------
# check_ubuntu()
# ---------------------------------------------------------------------------


def _make_ssh_mock(ram_total=4096, ram_used=2048, disk_used=5000000, disk_free=10000000, mysql_active=True):
    """Construit un mock paramiko.SSHClient avec des reponses predefinies."""
    responses = {
        "lsb_release": "Ubuntu 20.04.6 LTS",
        "uptime": "up 3 hours, 42 minutes",
        "free": f"{ram_total} {ram_used}",
        "df": f"{disk_used} {disk_free}",
        "systemctl": "active" if mysql_active else "inactive",
    }

    def exec_command(cmd, **kwargs):
        stdout = MagicMock()
        if "lsb_release" in cmd or "os-release" in cmd:
            stdout.read.return_value = responses["lsb_release"].encode()
        elif "uptime" in cmd:
            stdout.read.return_value = responses["uptime"].encode()
        elif "free" in cmd:
            stdout.read.return_value = responses["free"].encode()
        elif "df" in cmd:
            stdout.read.return_value = responses["df"].encode()
        elif "systemctl" in cmd:
            stdout.read.return_value = responses["systemctl"].encode()
        else:
            stdout.read.return_value = b""
        return MagicMock(), stdout, MagicMock()

    client = MagicMock()
    client.exec_command.side_effect = exec_command
    return client


class TestCheckUbuntu:
    def test_ok_when_metrics_below_threshold(self):
        ssh_client = _make_ssh_mock()
        with patch("paramiko.SSHClient", return_value=ssh_client):
            result = check_ubuntu(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK

    def test_warning_when_ram_above_threshold(self):
        # ram_used = 3900, ram_total = 4096 → ~95%
        ssh_client = _make_ssh_mock(ram_total=4096, ram_used=3900)
        with patch("paramiko.SSHClient", return_value=ssh_client):
            result = check_ubuntu(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "WARNING"
        assert result["exit_code"] == EXIT_WARNING
        assert result["details"]["ram_percent"] > 80

    def test_critical_on_auth_failure(self):
        with patch("paramiko.SSHClient") as mock_cls:
            mock_cls.return_value.connect.side_effect = Exception("Authentication failed")
            result = check_ubuntu(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_unknown_on_connection_refused(self):
        with patch("paramiko.SSHClient") as mock_cls:
            mock_cls.return_value.connect.side_effect = Exception("Connection refused")
            result = check_ubuntu(BASE_CONFIG, TARGET_DB)

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_raises_config_error_when_no_ssh_section(self):
        config_no_ssh = {"general": BASE_CONFIG["general"]}
        with pytest.raises(ModuleConfigError, match="ssh"):
            check_ubuntu(config_no_ssh, TARGET_DB)

    def test_result_has_all_detail_keys(self):
        ssh_client = _make_ssh_mock()
        with patch("paramiko.SSHClient", return_value=ssh_client):
            result = check_ubuntu(BASE_CONFIG, TARGET_DB)

        for key in ("os_version", "uptime", "ram_percent", "disk_percent", "mysql_status"):
            assert key in result["details"], f"Cle manquante: {key}"

    def test_mysql_status_captured(self):
        ssh_client = _make_ssh_mock(mysql_active=False)
        with patch("paramiko.SSHClient", return_value=ssh_client):
            result = check_ubuntu(BASE_CONFIG, TARGET_DB)

        assert result["details"]["mysql_status"] == "inactive"
