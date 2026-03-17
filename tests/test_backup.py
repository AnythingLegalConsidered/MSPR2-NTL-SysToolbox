"""
Tests unitaires – Module backup
Responsable: ojvind
"""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.interfaces import EXIT_CRITICAL, EXIT_OK, ModuleConfigError
from src.modules.backup import _sha256, backup_database, export_table_csv, run

# ---------------------------------------------------------------------------
# Config fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def config(tmp_path: Path) -> dict:
    return {
        "general": {"output_dir": str(tmp_path / "output"), "log_level": "INFO"},
        "ssh": {
            "host": "192.168.10.21",
            "port": 22,
            "user": "ntl",
            "password": "secret",
        },
        "mysql": {
            "host": "192.168.10.21",
            "port": 3306,
            "user": "ntl_user",
            "password": "dbpass",
            "database": "wms",
        },
    }


# ---------------------------------------------------------------------------
# Test 1 – backup_database crée un fichier .sql avec SHA256
# ---------------------------------------------------------------------------

class TestBackupDatabase:
    def test_creates_sql_file_with_sha256(self, config: dict, tmp_path: Path):
        """Le fichier .sql est créé localement et son SHA256 est renvoyé."""
        fake_dump = b"-- MySQL dump\nCREATE TABLE orders (\n);\nCREATE TABLE shipments (\n);\n"

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = fake_dump
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""

        with patch("paramiko.SSHClient") as MockSSH:
            mock_client = MockSSH.return_value
            mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

            result = backup_database(config, "wms")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK

        saved_path = Path(result["details"]["file"])
        assert saved_path.exists()
        assert saved_path.suffix == ".sql"
        assert saved_path.read_bytes() == fake_dump

        expected_sha = hashlib.sha256(fake_dump).hexdigest()
        assert result["details"]["sha256"] == expected_sha

    def test_table_count_reported(self, config: dict):
        """Le nombre de tables est compté via CREATE TABLE dans le dump."""
        fake_dump = b"CREATE TABLE a ();\nCREATE TABLE b ();\nCREATE TABLE c ();\n"

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = fake_dump
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""

        with patch("paramiko.SSHClient") as MockSSH:
            mock_client = MockSSH.return_value
            mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

            result = backup_database(config, "wms")

        assert result["details"]["table_count"] == 3


# ---------------------------------------------------------------------------
# Test 2 – Calcul SHA256 correct
# ---------------------------------------------------------------------------

class TestSha256:
    def test_sha256_matches_known_value(self, tmp_path: Path):
        """_sha256 renvoie le bon hash pour un contenu connu."""
        data = b"NTL-SysToolbox backup integrity check"
        f = tmp_path / "test.bin"
        f.write_bytes(data)

        expected = hashlib.sha256(data).hexdigest()
        assert _sha256(f) == expected

    def test_sha256_differs_for_different_content(self, tmp_path: Path):
        """Deux fichiers différents produisent des hashes différents."""
        f1 = tmp_path / "a.bin"
        f2 = tmp_path / "b.bin"
        f1.write_bytes(b"content-one")
        f2.write_bytes(b"content-two")

        assert _sha256(f1) != _sha256(f2)


# ---------------------------------------------------------------------------
# Test 3 – Échec SSH → statut CRITICAL
# ---------------------------------------------------------------------------

class TestSshFailure:
    def test_ssh_connection_error_returns_critical(self, config: dict):
        """Une erreur SSH retourne status CRITICAL (pas de crash)."""
        with patch("paramiko.SSHClient") as MockSSH:
            mock_client = MockSSH.return_value
            mock_client.connect.side_effect = Exception("Connection refused")

            result = backup_database(config, "wms")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL
        assert "error" in result["details"]

    def test_empty_dump_returns_critical(self, config: dict):
        """Un dump vide (mysqldump sans données) retourne CRITICAL."""
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"Access denied"

        with patch("paramiko.SSHClient") as MockSSH:
            mock_client = MockSSH.return_value
            mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

            result = backup_database(config, "wms")

        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL


# ---------------------------------------------------------------------------
# Test 4 – export_table_csv contient les bonnes colonnes et lignes
# ---------------------------------------------------------------------------

class TestExportTableCsv:
    def test_csv_contains_correct_columns_and_rows(self, config: dict, tmp_path: Path):
        """Le CSV exporté contient les bons en-têtes et toutes les lignes."""
        fake_rows = [
            (1, "ORD-001", "Lens", "2026-01-10"),
            (2, "ORD-002", "Arras", "2026-01-11"),
        ]
        fake_columns = [("id",), ("order_ref",), ("warehouse",), ("date",)]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = fake_rows
        mock_cursor.description = fake_columns

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("mysql.connector.connect", return_value=mock_conn):
            result = export_table_csv(config, "orders")

        assert result["status"] == "OK"
        assert result["exit_code"] == EXIT_OK
        assert result["details"]["row_count"] == 2
        assert result["details"]["columns"] == ["id", "order_ref", "warehouse", "date"]

        # Verify CSV file on disk
        csv_path = Path(result["details"]["file"])
        assert csv_path.exists()
        lines = csv_path.read_text(encoding="utf-8").splitlines()
        assert lines[0] == "id,order_ref,warehouse,date"
        assert len(lines) == 3  # header + 2 rows

    def test_csv_sha256_is_present(self, config: dict):
        """Le SHA256 du fichier CSV est inclus dans le résultat."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "data")]
        mock_cursor.description = [("id",), ("value",)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("mysql.connector.connect", return_value=mock_conn):
            result = export_table_csv(config, "shipments")

        assert "sha256" in result["details"]
        assert len(result["details"]["sha256"]) == 64  # SHA256 hex = 64 chars


# ---------------------------------------------------------------------------
# Test 5 – Action invalide → ModuleConfigError
# ---------------------------------------------------------------------------

class TestRunDispatcher:
    def test_invalid_action_raises_module_config_error(self, config: dict):
        """Une action inconnue lève ModuleConfigError, sans crash silencieux."""
        with pytest.raises(ModuleConfigError, match="Unknown action"):
            run(config, "wms", action="nonexistent_action")

    def test_export_without_table_raises_module_config_error(self, config: dict):
        """export_table_csv sans nom de table lève ModuleConfigError."""
        with pytest.raises(ModuleConfigError, match="table name"):
            run(config, "", action="export_table_csv")
