"""
Tests for nightswatch `list` command.

Gate Pattern: These tests must pass before changes to nightswatch list are accepted.
Run with: pytest ~/code/ytmon/tests/ -v
"""
import os
import subprocess
from pathlib import Path

import pytest
import yaml


class TestListChannels:
    """Tests for the nightswatch list command."""

    def test_list_shows_header(self, temp_config_with_channel, nightswatch_path):
        """List should show a header."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_with_channel)
        
        result = subprocess.run(
            [str(nightswatch_path), "list"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should succeed and show header
        assert result.returncode == 0
        output = result.stdout.lower()
        assert "channel" in output or "watch" in output

    def test_list_shows_configured_channels(
        self, temp_config_with_channels, nightswatch_path
    ):
        """List should display all configured channels."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_with_channels)
        
        result = subprocess.run(
            [str(nightswatch_path), "list"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        output = result.stdout
        
        # Should show both channel names
        assert "Channel Alpha" in output
        assert "Channel Beta" in output

    def test_list_empty_channels(self, temp_config_dir, nightswatch_path):
        """List with no channels should indicate empty."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        result = subprocess.run(
            [str(nightswatch_path), "list"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should succeed (not crash) even with no channels
        # Output might be empty or say "no channels"
        assert result.returncode == 0

    def test_list_shows_channel_ids(
        self, temp_config_with_channels, nightswatch_path
    ):
        """List should display channel IDs."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_with_channels)
        
        result = subprocess.run(
            [str(nightswatch_path), "list"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        output = result.stdout
        
        # Should show channel IDs
        assert "UCaaa" in output
        assert "UCbbb" in output


class TestListEdgeCases:
    """Edge case tests for list command."""

    def test_list_with_special_characters_in_name(
        self, temp_config_dir, nightswatch_path
    ):
        """Channel names with special characters should display correctly."""
        # Create config with special characters
        config = {
            "channels": [
                {"name": "Test & Friends <3", "id": "UCspecial123"},
                {"name": "日本語チャンネル", "id": "UCjapanese123"},
            ],
            "subtitles": {"languages": ["en"], "prefer_manual": True},
        }
        
        with open(temp_config_dir, "w") as f:
            yaml.dump(config, f, allow_unicode=True)
        
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        result = subprocess.run(
            [str(nightswatch_path), "list"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should not crash with special characters
        assert result.returncode == 0

    def test_list_returns_zero_exit_code(
        self, temp_config_with_channel, nightswatch_path
    ):
        """List should always return exit code 0 on success."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_with_channel)
        
        result = subprocess.run(
            [str(nightswatch_path), "list"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
