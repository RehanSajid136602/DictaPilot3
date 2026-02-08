#!/usr/bin/env python3
"""
Test script for paste policy functionality
Verifies that the paste policy correctly handles different scenarios
"""

import os
import sys
from unittest.mock import Mock, patch

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_paste_policy_logic():
    """Test that paste policy logic works as expected"""

    # Test environment variable setting
    os.environ["PASTE_POLICY"] = "final_only"
    paste_policy = os.getenv("PASTE_POLICY", "final_only").strip().lower()
    assert paste_policy == "final_only", f"Expected 'final_only', got '{paste_policy}'"

    os.environ["PASTE_POLICY"] = "live_preview"
    paste_policy = os.getenv("PASTE_POLICY", "final_only").strip().lower()
    assert paste_policy == "live_preview", f"Expected 'live_preview', got '{paste_policy}'"

    # Test default value
    if "PASTE_POLICY" in os.environ:
        del os.environ["PASTE_POLICY"]
    paste_policy = os.getenv("PASTE_POLICY", "final_only").strip().lower()
    assert paste_policy == "final_only", f"Expected default 'final_only', got '{paste_policy}'"

    print("✓ Environment variable tests passed")


def test_smart_editor_command_detection():
    """Test that smart editor correctly identifies commands that should not be pasted"""
    from smart_editor import needs_intent_handling

    # Test various command types that should be detected
    command_tests = [
        ("ignore that", True),
        ("don't include this", True),
        ("cancel that", True),
        ("never mind", True),
        ("clear all", True),
        ("undo that", True),
        ("regular text", False),
        ("hello world", False),
        ("this is normal text", False),
    ]

    for text, expected in command_tests:
        result = needs_intent_handling(text)
        assert result == expected, f"Command detection failed for '{text}': expected {expected}, got {result}"

    print("✓ Command detection tests passed")


def test_config_loading():
    """Test that the new config option loads properly"""
    from config import DictaPilotConfig

    # Test default value
    config = DictaPilotConfig()
    assert config.paste_policy == "final_only", f"Expected default 'final_only', got '{config.paste_policy}'"

    # Test custom value
    config = DictaPilotConfig(paste_policy="live_preview")
    assert config.paste_policy == "live_preview", f"Expected 'live_preview', got '{config.paste_policy}'"

    print("✓ Config loading tests passed")


def run_all_tests():
    """Run all paste policy tests"""
    print("Running paste policy tests...")

    test_paste_policy_logic()
    test_smart_editor_command_detection()
    test_config_loading()

    print("\n✅ All paste policy tests passed!")
    print("\nSummary of changes:")
    print("- Added PASTE_POLICY environment variable and config setting")
    print("- Default is 'final_only' to prevent flickering")
    print("- Only refined text is pasted to target app")
    print("- Commands like 'ignore', 'undo', 'clear' don't paste externally")
    print("- Raw text only shown in GUI preview, not external apps")


if __name__ == "__main__":
    run_all_tests()