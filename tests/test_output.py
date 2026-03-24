"""Tests for the output utility module."""

import json

from src.interfaces import EXIT_OK, build_result
from src.utils.output import print_result, save_result_json, setup_logging


def _make_result(**overrides):
    defaults = {
        "module": "diagnostic",
        "function": "check_dns",
        "status": "OK",
        "exit_code": EXIT_OK,
        "target": "192.168.1.1",
        "details": {},
        "message": "test",
    }
    defaults.update(overrides)
    return build_result(**defaults)


class TestSaveResultJson:
    def test_creates_file(self, tmp_path):
        result = _make_result()
        filepath = save_result_json(result, str(tmp_path))

        assert filepath.exists()
        assert filepath.suffix == ".json"

    def test_correct_content(self, tmp_path):
        result = _make_result(message="hello world")
        filepath = save_result_json(result, str(tmp_path))

        data = json.loads(filepath.read_text(encoding="utf-8"))
        assert data["message"] == "hello world"
        assert data["module"] == "diagnostic"

    def test_sanitizes_module_name(self, tmp_path):
        result = _make_result()
        # Inject path traversal attempt in module name
        result["module"] = "../../../etc/passwd"
        result["function"] = "normal"

        filepath = save_result_json(result, str(tmp_path))
        # Filename should not contain path separators
        assert "/" not in filepath.name
        assert "\\" not in filepath.name
        assert ".." not in filepath.name

    def test_sanitizes_function_name(self, tmp_path):
        result = _make_result()
        result["function"] = "../../tmp/evil"

        filepath = save_result_json(result, str(tmp_path))
        assert ".." not in filepath.name


class TestPrintResult:
    def test_no_crash(self, capsys):
        result = _make_result()
        print_result(result)
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestSetupLogging:
    def test_no_crash(self):
        setup_logging("DEBUG")

    def test_invalid_level_falls_back(self):
        setup_logging("NONEXISTENT")
