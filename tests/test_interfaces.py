"""Tests for the shared interfaces module."""

from datetime import datetime

from src.interfaces import (
    EXIT_CRITICAL,
    EXIT_OK,
    EXIT_UNKNOWN,
    EXIT_WARNING,
    ModuleConfigError,
    ModuleExecutionError,
    build_result,
)


class TestExitCodes:
    def test_exit_ok_is_zero(self):
        assert EXIT_OK == 0

    def test_exit_warning_is_one(self):
        assert EXIT_WARNING == 1

    def test_exit_critical_is_two(self):
        assert EXIT_CRITICAL == 2

    def test_exit_unknown_is_three(self):
        assert EXIT_UNKNOWN == 3


class TestBuildResult:
    def test_returns_dict_with_all_keys(self):
        result = build_result(
            module="diagnostic",
            function="check_dns",
            status="OK",
            exit_code=EXIT_OK,
            target="192.168.1.10",
            details={"resolved": True},
            message="DNS resolution successful",
        )
        expected_keys = {
            "module", "function", "timestamp", "status",
            "exit_code", "target", "details", "message",
        }
        assert set(result.keys()) == expected_keys

    def test_preserves_values(self):
        result = build_result(
            module="backup",
            function="backup_database",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target="wms-db",
            details={"error": "connection refused"},
            message="MySQL backup failed",
        )
        assert result["module"] == "backup"
        assert result["function"] == "backup_database"
        assert result["status"] == "CRITICAL"
        assert result["exit_code"] == EXIT_CRITICAL
        assert result["target"] == "wms-db"
        assert result["details"] == {"error": "connection refused"}
        assert result["message"] == "MySQL backup failed"

    def test_timestamp_is_iso_format(self):
        result = build_result(
            module="audit",
            function="scan_network",
            status="OK",
            exit_code=EXIT_OK,
            target="10.0.0.0/24",
            details={},
            message="Scan complete",
        )
        # Should not raise ValueError if valid ISO format
        datetime.fromisoformat(result["timestamp"])

    def test_empty_details_allowed(self):
        result = build_result(
            module="diagnostic",
            function="check_ad",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target="dc01",
            details={},
            message="Target unreachable",
        )
        assert result["details"] == {}


class TestCustomExceptions:
    def test_module_config_error_is_exception(self):
        with __import__("pytest").raises(ModuleConfigError):
            raise ModuleConfigError("Missing MySQL password")

    def test_module_execution_error_is_exception(self):
        with __import__("pytest").raises(ModuleExecutionError):
            raise ModuleExecutionError("SSH timeout")

    def test_config_error_message(self):
        err = ModuleConfigError("bad config")
        assert str(err) == "bad config"

    def test_execution_error_message(self):
        err = ModuleExecutionError("timeout")
        assert str(err) == "timeout"
