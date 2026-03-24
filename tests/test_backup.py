"""Tests pour le module backup — utilise des mocks, pas de MySQL requis."""

import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.interfaces import EXIT_CRITICAL, EXIT_OK, EXIT_UNKNOWN, ModuleConfigError, ModuleExecutionError
from src.modules.backup import backup_database, export_table_csv, run

TARGET_DB = "wms"
TARGET_TABLE = "shipments"

BASE_CONFIG = {
    "general": {"timeout": 10, "log_level": "INFO", "output_dir": "./output"},
    "mysql": {"host": "192.168.10.21", "port": 3306, "user": "wms_user", "password": "secret", "database": "wms"},
}


# ---------------------------------------------------------------------------
# run() — dispatcher
# ---------------------------------------------------------------------------


class TestRun:
    def test_dispatches_backup_database(self):
        with patch("src.modules.backup.backup_database") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_DB, action="backup_database")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_DB)
        assert result == {"status": "OK"}

    def test_dispatches_export_table_csv(self):
        with patch("src.modules.backup.export_table_csv") as mock:
            mock.return_value = {"status": "OK"}
            result = run(BASE_CONFIG, TARGET_TABLE, action="export_table_csv")
        mock.assert_called_once_with(BASE_CONFIG, TARGET_TABLE)
        assert result == {"status": "OK"}

    def test_raises_on_unknown_action(self):
        with pytest.raises(ModuleExecutionError, match="Action inconnue"):
            run(BASE_CONFIG, TARGET_DB, action="foobar")

    def test_default_action_raises(self):
        with pytest.raises(ModuleExecutionError):
            run(BASE_CONFIG, TARGET_DB)


# ---------------------------------------------------------------------------
# backup_database()
# ---------------------------------------------------------------------------


class TestBackupDatabase:
    def test_ok_on_successful_dump(self, tmp_path):
        config = {**BASE_CONFIG, "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path)}}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "-- MySQL dump\nCREATE TABLE..."
        mock_result.stderr = ""

        with patch("src.modules.backup.subprocess.run", return_value=mock_result):
            result = backup_database(config, "wms")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK
        assert result["details"]["database"] == "wms"
        assert result["details"]["size_bytes"] > 0

    def test_critical_on_access_denied(self, tmp_path):
        config = {**BASE_CONFIG, "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path)}}
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Access denied for user 'wms_user'"

        with patch("src.modules.backup.subprocess.run", return_value=mock_result):
            result = backup_database(config, "wms")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_critical_on_mysqldump_error(self, tmp_path):
        config = {**BASE_CONFIG, "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path)}}
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stdout = ""
        mock_result.stderr = "Unknown database 'nope'"

        with patch("src.modules.backup.subprocess.run", return_value=mock_result):
            result = backup_database(config, "nope")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_critical_when_mysqldump_not_found(self):
        with patch("src.modules.backup.subprocess.run", side_effect=FileNotFoundError):
            result = backup_database(BASE_CONFIG, "wms")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL
        assert "mysqldump" in result["message"]

    def test_unknown_on_timeout(self):
        with patch("src.modules.backup.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="mysqldump", timeout=10)):
            result = backup_database(BASE_CONFIG, "wms")

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_raises_config_error_when_no_mysql_section(self):
        config_no_mysql = {"general": BASE_CONFIG["general"]}
        with pytest.raises(ModuleConfigError, match="mysql"):
            backup_database(config_no_mysql, "wms")

    def test_uses_default_database_from_config(self, tmp_path):
        config = {**BASE_CONFIG, "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path)}}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "-- dump"
        mock_result.stderr = ""

        with patch("src.modules.backup.subprocess.run", return_value=mock_result):
            result = backup_database(config, "")

        assert result["details"]["database"] == "wms"

    def test_result_has_correct_module_and_function(self, tmp_path):
        config = {**BASE_CONFIG, "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path)}}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "-- dump"
        mock_result.stderr = ""

        with patch("src.modules.backup.subprocess.run", return_value=mock_result):
            result = backup_database(config, "wms")

        assert result["module"] == "backup"
        assert result["function"] == "backup_database"


# ---------------------------------------------------------------------------
# export_table_csv()
# ---------------------------------------------------------------------------


def _make_mysql_mock(columns=None, rows=None):
    """Construit un mock mysql.connector.connect() pour l'export CSV."""
    if columns is None:
        columns = [("id",), ("name",), ("status",)]
    if rows is None:
        rows = [(1, "Colis A", "shipped"), (2, "Colis B", "pending")]

    cursor = MagicMock()
    cursor.description = columns
    cursor.fetchall.return_value = rows

    conn = MagicMock()
    conn.cursor.return_value = cursor

    return conn


class TestExportTableCsv:
    def test_ok_on_successful_export(self, tmp_path):
        config = {**BASE_CONFIG, "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path)}}
        conn = _make_mysql_mock()

        with patch("mysql.connector.connect", return_value=conn):
            result = export_table_csv(config, "shipments")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK
        assert result["details"]["row_count"] == 2
        assert result["details"]["table"] == "shipments"
        assert result["details"]["columns"] == ["id", "name", "status"]

    def test_critical_on_access_denied(self):
        with patch("mysql.connector.connect", side_effect=Exception("Access denied for user")):
            result = export_table_csv(BASE_CONFIG, "shipments")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL

    def test_critical_on_table_not_found(self):
        with patch("mysql.connector.connect", side_effect=Exception("Table 'wms.nope' doesn't exist")):
            result = export_table_csv(BASE_CONFIG, "nope")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL
        assert "introuvable" in result["message"]

    def test_unknown_on_connection_refused(self):
        with patch("mysql.connector.connect", side_effect=Exception("Can't connect to MySQL server")):
            result = export_table_csv(BASE_CONFIG, "shipments")

        assert result["status"] == "UNKNOWN"
        assert result["exit_code"] == EXIT_UNKNOWN

    def test_raises_config_error_when_no_mysql_section(self):
        config_no_mysql = {"general": BASE_CONFIG["general"]}
        with pytest.raises(ModuleConfigError, match="mysql"):
            export_table_csv(config_no_mysql, "shipments")

    def test_raises_config_error_when_no_table_name(self):
        with pytest.raises(ModuleConfigError, match="table"):
            export_table_csv(BASE_CONFIG, "")

    def test_result_has_correct_module_and_function(self, tmp_path):
        config = {**BASE_CONFIG, "general": {**BASE_CONFIG["general"], "output_dir": str(tmp_path)}}
        conn = _make_mysql_mock()

        with patch("mysql.connector.connect", return_value=conn):
            result = export_table_csv(config, "shipments")

        assert result["module"] == "backup"
        assert result["function"] == "export_table_csv"
