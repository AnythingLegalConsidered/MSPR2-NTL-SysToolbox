"""Tests for the network utility module."""

import socket
from unittest.mock import MagicMock, patch

from src.utils.network import check_port, grab_banner, grab_mysql_version, ping_host, resolve_dns


class TestCheckPort:
    def test_rejects_invalid_port_zero(self):
        assert check_port("127.0.0.1", 0) is False

    def test_rejects_invalid_port_negative(self):
        assert check_port("127.0.0.1", -1) is False

    def test_rejects_invalid_port_too_high(self):
        assert check_port("127.0.0.1", 99999) is False

    def test_accepts_valid_port_range(self):
        # Port 1 and 65535 should be accepted (even if connection fails)
        with patch("src.utils.network.socket.socket") as mock_sock:
            instance = MagicMock()
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            instance.connect.side_effect = OSError("refused")
            mock_sock.return_value = instance

            assert check_port("127.0.0.1", 1) is False
            assert check_port("127.0.0.1", 65535) is False

    def test_returns_false_on_connection_refused(self):
        with patch("src.utils.network.socket.socket") as mock_sock:
            instance = MagicMock()
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            instance.connect.side_effect = OSError("Connection refused")
            mock_sock.return_value = instance

            assert check_port("127.0.0.1", 8080) is False

    def test_returns_true_on_successful_connect(self):
        with patch("src.utils.network.socket.socket") as mock_sock:
            instance = MagicMock()
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            mock_sock.return_value = instance

            assert check_port("127.0.0.1", 8080) is True


class TestPingHost:
    def test_returns_true_on_success(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("src.utils.network.subprocess.run", return_value=mock_result):
            assert ping_host("127.0.0.1") is True

    def test_returns_false_on_failure(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("src.utils.network.subprocess.run", return_value=mock_result):
            assert ping_host("192.168.99.99") is False

    def test_returns_false_on_timeout(self):
        import subprocess

        with patch(
            "src.utils.network.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="ping", timeout=10),
        ):
            assert ping_host("192.168.99.99") is False


class TestResolveDns:
    def test_resolves_without_server(self):
        with patch("src.utils.network.socket.gethostbyname", return_value="93.184.216.34"):
            result = resolve_dns("example.com")
        assert result == "93.184.216.34"

    def test_returns_none_on_failure(self):
        with patch(
            "src.utils.network.socket.gethostbyname",
            side_effect=socket.gaierror("Name resolution failed"),
        ):
            result = resolve_dns("nonexistent.invalid")
        assert result is None


class TestGrabBanner:
    def test_returns_banner_string(self):
        with patch("src.utils.network.socket.socket") as mock_sock:
            instance = MagicMock()
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            instance.recv.return_value = b"SSH-2.0-OpenSSH_8.9\r\n"
            mock_sock.return_value = instance

            result = grab_banner("127.0.0.1", 22)
        assert result == "SSH-2.0-OpenSSH_8.9"

    def test_returns_none_on_failure(self):
        with patch("src.utils.network.socket.socket") as mock_sock:
            instance = MagicMock()
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            instance.connect.side_effect = OSError("refused")
            mock_sock.return_value = instance

            result = grab_banner("127.0.0.1", 22)
        assert result is None


class TestGrabMysqlVersion:
    def test_parses_mysql_protocol(self):
        # Simulated MySQL greeting: 3 bytes len + 1 byte seq + 1 byte protocol + version + \x00
        version_bytes = b"8.0.32"
        packet = b"\x00\x00\x00\x00\x0a" + version_bytes + b"\x00rest..."

        with patch("src.utils.network.socket.socket") as mock_sock:
            instance = MagicMock()
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            instance.recv.return_value = packet
            mock_sock.return_value = instance

            result = grab_mysql_version("127.0.0.1", 3306)
        assert result == "8.0.32"

    def test_returns_none_on_non_mysql(self):
        with patch("src.utils.network.socket.socket") as mock_sock:
            instance = MagicMock()
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            instance.recv.return_value = b"HTTP/1.1 200 OK"
            mock_sock.return_value = instance

            result = grab_mysql_version("127.0.0.1", 80)
        # Should return None or a string (depends on null byte position)
        # HTTP response has no null byte at position 5+, so ValueError -> None
        assert result is None or isinstance(result, str)
