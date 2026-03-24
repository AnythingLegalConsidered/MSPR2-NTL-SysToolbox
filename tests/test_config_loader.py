"""Tests for the configuration loader module."""

import os
from unittest.mock import patch

import pytest

from src.config_loader import _resolve_env_vars, load_config
from src.interfaces import ModuleConfigError


class TestLoadConfig:
    def test_loads_valid_yaml(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("general:\n  timeout: 10\n", encoding="utf-8")

        config = load_config(str(cfg_file))
        assert config["general"]["timeout"] == 10

    def test_raises_on_missing_file(self):
        with pytest.raises(ModuleConfigError, match="not found"):
            load_config("nonexistent/config.yaml")

    def test_raises_on_invalid_yaml(self, tmp_path):
        cfg_file = tmp_path / "bad.yaml"
        cfg_file.write_text(":\n  bad: [yaml\n", encoding="utf-8")

        with pytest.raises(ModuleConfigError, match="Invalid YAML"):
            load_config(str(cfg_file))

    def test_raises_on_non_dict_yaml(self, tmp_path):
        cfg_file = tmp_path / "list.yaml"
        cfg_file.write_text("- item1\n- item2\n", encoding="utf-8")

        with pytest.raises(ModuleConfigError, match="mapping"):
            load_config(str(cfg_file))


class TestResolveEnvVars:
    def test_resolves_env_var(self):
        with patch.dict(os.environ, {"TEST_VAR": "hello"}):
            result = _resolve_env_vars("value is ${TEST_VAR}")
        assert result == "value is hello"

    def test_keeps_placeholder_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("NONEXISTENT_VAR", None)
            result = _resolve_env_vars("${NONEXISTENT_VAR}")
        assert result == "${NONEXISTENT_VAR}"

    def test_collects_unresolved_vars(self):
        unresolved: list[str] = []
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MISSING_VAR", None)
            _resolve_env_vars("${MISSING_VAR}", unresolved=unresolved)
        assert "MISSING_VAR" in unresolved

    def test_resolves_nested_dicts(self):
        with patch.dict(os.environ, {"DB_HOST": "localhost"}):
            data = {"mysql": {"host": "${DB_HOST}"}}
            result = _resolve_env_vars(data)
        assert result["mysql"]["host"] == "localhost"

    def test_resolves_lists(self):
        with patch.dict(os.environ, {"PORT": "3306"}):
            result = _resolve_env_vars(["${PORT}", "other"])
        assert result == ["3306", "other"]

    def test_passes_through_non_string_types(self):
        assert _resolve_env_vars(42) == 42
        assert _resolve_env_vars(True) is True
        assert _resolve_env_vars(None) is None


class TestRecursionDepth:
    def test_raises_on_deep_nesting(self):
        # Build a deeply nested dict (25 levels, exceeds _MAX_RESOLVE_DEPTH=20)
        data: dict = {"key": "value"}
        for _ in range(25):
            data = {"nested": data}

        with pytest.raises(ModuleConfigError, match="too deep"):
            _resolve_env_vars(data)


class TestStrictMode:
    def test_strict_raises_on_unresolved(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("db:\n  host: '${UNSET_VAR}'\n", encoding="utf-8")

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("UNSET_VAR", None)
            with pytest.raises(ModuleConfigError, match="non definies"):
                load_config(str(cfg_file), strict=True)
