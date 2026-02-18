"""
Unit tests for display_server.py module

Tests for display server detection logic.
"""

import os
import pytest
from unittest.mock import patch

from display_server import (
    detect_display_server,
    is_wayland,
    is_x11,
    clear_detection_cache,
    get_display_server_info,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear detection cache before each test"""
    clear_detection_cache()
    yield
    clear_detection_cache()


class TestDetectDisplayServer:
    """Tests for detect_display_server function"""

    def test_manual_override_wayland(self):
        """Test manual override to Wayland"""
        with patch.dict(os.environ, {"DISPLAY_SERVER": "wayland"}, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "wayland"

    def test_manual_override_x11(self):
        """Test manual override to X11"""
        with patch.dict(os.environ, {"DISPLAY_SERVER": "x11"}, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "x11"

    def test_manual_override_case_insensitive(self):
        """Test manual override is case insensitive"""
        with patch.dict(os.environ, {"DISPLAY_SERVER": "WAYLAND"}, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "wayland"

    def test_xdg_session_type_wayland(self):
        """Test detection via XDG_SESSION_TYPE=wayland"""
        env = {"XDG_SESSION_TYPE": "wayland"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "wayland"

    def test_xdg_session_type_x11(self):
        """Test detection via XDG_SESSION_TYPE=x11"""
        env = {"XDG_SESSION_TYPE": "x11"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "x11"

    def test_fallback_wayland_display(self):
        """Test fallback detection via WAYLAND_DISPLAY"""
        env = {"WAYLAND_DISPLAY": "wayland-0"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "wayland"

    def test_fallback_display(self):
        """Test fallback detection via DISPLAY"""
        env = {"DISPLAY": ":0"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "x11"

    def test_unknown_when_no_env(self):
        """Test returns unknown when no display env vars set"""
        with patch.dict(os.environ, {}, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "unknown"

    def test_manual_override_takes_precedence(self):
        """Test manual override takes precedence over XDG_SESSION_TYPE"""
        env = {
            "DISPLAY_SERVER": "x11",
            "XDG_SESSION_TYPE": "wayland",
        }
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "x11"

    def test_xdg_takes_precedence_over_fallback(self):
        """Test XDG_SESSION_TYPE takes precedence over WAYLAND_DISPLAY"""
        env = {
            "XDG_SESSION_TYPE": "x11",
            "WAYLAND_DISPLAY": "wayland-0",
        }
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "x11"

    def test_wayland_display_takes_precedence_over_display(self):
        """Test WAYLAND_DISPLAY takes precedence over DISPLAY"""
        env = {
            "WAYLAND_DISPLAY": "wayland-0",
            "DISPLAY": ":0",
        }
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result = detect_display_server()
            assert result == "wayland"

    def test_caching(self):
        """Test that result is cached"""
        env = {"XDG_SESSION_TYPE": "wayland"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result1 = detect_display_server()
            # Change env but cache should return old value
            os.environ["XDG_SESSION_TYPE"] = "x11"
            result2 = detect_display_server()
            assert result1 == "wayland"
            assert result2 == "wayland"

    def test_cache_clear(self):
        """Test that clear_detection_cache clears the cache"""
        env = {"XDG_SESSION_TYPE": "wayland"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            result1 = detect_display_server()
            assert result1 == "wayland"
            
            # Clear cache and change env
            clear_detection_cache()
            os.environ["XDG_SESSION_TYPE"] = "x11"
            result2 = detect_display_server()
            assert result2 == "x11"


class TestIsWayland:
    """Tests for is_wayland function"""

    def test_returns_true_on_wayland(self):
        """Test returns True when on Wayland"""
        env = {"XDG_SESSION_TYPE": "wayland"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            assert is_wayland() is True

    def test_returns_false_on_x11(self):
        """Test returns False when on X11"""
        env = {"XDG_SESSION_TYPE": "x11"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            assert is_wayland() is False

    def test_returns_false_on_unknown(self):
        """Test returns False when unknown"""
        with patch.dict(os.environ, {}, clear=True):
            clear_detection_cache()
            assert is_wayland() is False


class TestIsX11:
    """Tests for is_x11 function"""

    def test_returns_true_on_x11(self):
        """Test returns True when on X11"""
        env = {"XDG_SESSION_TYPE": "x11"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            assert is_x11() is True

    def test_returns_false_on_wayland(self):
        """Test returns False when on Wayland"""
        env = {"XDG_SESSION_TYPE": "wayland"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            assert is_x11() is False

    def test_returns_false_on_unknown(self):
        """Test returns False when unknown"""
        with patch.dict(os.environ, {}, clear=True):
            clear_detection_cache()
            assert is_x11() is False


class TestGetDisplayServerInfo:
    """Tests for get_display_server_info function"""

    def test_returns_all_env_info(self):
        """Test returns dictionary with all env info"""
        env = {
            "XDG_SESSION_TYPE": "wayland",
            "WAYLAND_DISPLAY": "wayland-0",
            "DISPLAY": ":0",
            "DISPLAY_SERVER": "",
        }
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            info = get_display_server_info()
            assert info["detected"] == "wayland"
            assert info["XDG_SESSION_TYPE"] == "wayland"
            assert info["WAYLAND_DISPLAY"] == "wayland-0"
            assert info["DISPLAY"] == ":0"

    def test_includes_override(self):
        """Test includes manual override value"""
        env = {"DISPLAY_SERVER": "x11"}
        with patch.dict(os.environ, env, clear=True):
            clear_detection_cache()
            info = get_display_server_info()
            assert info["DISPLAY_SERVER_OVERRIDE"] == "x11"
            assert info["detected"] == "x11"
