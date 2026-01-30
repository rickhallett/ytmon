"""
Tests for nightswatch `add` command.

Gate Pattern: These tests must pass before changes to nightswatch are accepted.
Run with: pytest ~/code/ytmon/tests/ -v
"""
import os
import subprocess
from pathlib import Path

import pytest
import yaml


class TestAddChannel:
    """Tests for the nightswatch add command."""

    def test_add_channel_by_url(self, temp_config_dir, mock_yt_dlp, nightswatch_path):
        """Adding a channel by URL should add it to config."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        result = subprocess.run(
            [str(nightswatch_path), "add", "https://youtube.com/@TestChannel"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should succeed
        assert result.returncode == 0
        assert "Added" in result.stdout or "✓" in result.stdout
        
        # Verify config was updated
        with open(temp_config_dir) as f:
            config = yaml.safe_load(f)
        
        assert len(config["channels"]) == 1
        assert config["channels"][0]["id"] == "UCmock123456789abcdefgh"
        assert config["channels"][0]["name"] == "Mock Channel Name"

    def test_add_duplicate_channel_no_duplicate(
        self, temp_config_with_channel, nightswatch_path
    ):
        """Adding an already-existing channel should not duplicate it."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_with_channel)
        
        # Read original config
        with open(temp_config_with_channel) as f:
            original_config = yaml.safe_load(f)
        original_count = len(original_config["channels"])
        original_id = original_config["channels"][0]["id"]
        
        # Try to add the same channel (mock a scenario where yt-dlp returns same ID)
        # We need to create a custom mock for this test
        mock_dir = Path(temp_config_with_channel).parent / "mock_bin"
        mock_dir.mkdir(exist_ok=True)
        mock_uvx = mock_dir / "uvx"
        mock_uvx.write_text(f'''#!/bin/bash
if [[ "$*" == *"--print channel_id"* ]]; then
    echo "{original_id}"
elif [[ "$*" == *"--print channel"* ]]; then
    echo "Test Channel"
fi
''')
        mock_uvx.chmod(0o755)
        
        env["PATH"] = f"{mock_dir}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            [str(nightswatch_path), "add", "https://youtube.com/@TestChannel"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should succeed but indicate already exists
        assert result.returncode == 0
        assert "already" in result.stdout.lower()
        
        # Verify no duplicate was added
        with open(temp_config_with_channel) as f:
            new_config = yaml.safe_load(f)
        
        assert len(new_config["channels"]) == original_count

    def test_add_invalid_url_handling(self, temp_config_dir, nightswatch_path):
        """Invalid URLs should produce a clear error."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        # Create mock that fails for invalid URLs
        mock_dir = Path(temp_config_dir).parent / "mock_bin"
        mock_dir.mkdir(exist_ok=True)
        mock_uvx = mock_dir / "uvx"
        mock_uvx.write_text('''#!/bin/bash
# Simulate yt-dlp failing for invalid URLs
if [[ "$*" == *"not-a-valid-url"* ]]; then
    exit 1
fi
echo "UCvalid123"
''')
        mock_uvx.chmod(0o755)
        env["PATH"] = f"{mock_dir}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            [str(nightswatch_path), "add", "not-a-valid-url"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should fail with error
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "could not" in result.stderr.lower()

    def test_add_missing_url_shows_usage(self, temp_config_dir, nightswatch_path):
        """Calling add without a URL should show usage."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        result = subprocess.run(
            [str(nightswatch_path), "add"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode != 0
        assert "usage" in result.stderr.lower()


class TestConfigIntegrity:
    """Tests ensuring config file integrity after add operations."""

    def test_config_remains_valid_yaml(self, temp_config_dir, mock_yt_dlp, nightswatch_path):
        """Config should remain valid YAML after add."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        subprocess.run(
            [str(nightswatch_path), "add", "https://youtube.com/@TestChannel"],
            env=env,
            capture_output=True,
        )
        
        # Should parse without errors
        with open(temp_config_dir) as f:
            config = yaml.safe_load(f)
        
        assert isinstance(config, dict)
        assert "channels" in config
        assert isinstance(config["channels"], list)

    def test_config_preserves_other_settings(
        self, temp_config_dir, mock_yt_dlp, nightswatch_path
    ):
        """Adding a channel should not clobber other config settings."""
        # Add custom settings to config
        with open(temp_config_dir) as f:
            config = yaml.safe_load(f)
        
        config["custom_setting"] = "preserve_me"
        config["subtitles"]["languages"] = ["en", "de", "fr"]
        
        with open(temp_config_dir, "w") as f:
            yaml.dump(config, f)
        
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        subprocess.run(
            [str(nightswatch_path), "add", "https://youtube.com/@TestChannel"],
            env=env,
            capture_output=True,
        )
        
        # Verify settings preserved
        with open(temp_config_dir) as f:
            new_config = yaml.safe_load(f)
        
        assert new_config.get("custom_setting") == "preserve_me"
        assert new_config["subtitles"]["languages"] == ["en", "de", "fr"]

    def test_config_channel_format_correct(
        self, temp_config_dir, mock_yt_dlp, nightswatch_path
    ):
        """Added channels should have correct format (name and id)."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        subprocess.run(
            [str(nightswatch_path), "add", "https://youtube.com/@TestChannel"],
            env=env,
            capture_output=True,
        )
        
        with open(temp_config_dir) as f:
            config = yaml.safe_load(f)
        
        channel = config["channels"][0]
        assert "name" in channel
        assert "id" in channel
        assert isinstance(channel["name"], str)
        assert isinstance(channel["id"], str)
        assert channel["id"].startswith("UC")  # YouTube channel IDs start with UC


class TestEdgeCases:
    """Edge case tests for robustness."""

    def test_add_to_empty_channels_list(
        self, temp_config_dir, mock_yt_dlp, nightswatch_path
    ):
        """Should handle config with empty channels list."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        result = subprocess.run(
            [str(nightswatch_path), "add", "https://youtube.com/@TestChannel"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
        
        with open(temp_config_dir) as f:
            config = yaml.safe_load(f)
        
        assert len(config["channels"]) == 1

    def test_add_multiple_channels_sequentially(
        self, temp_config_dir, nightswatch_path
    ):
        """Should correctly add multiple channels in sequence."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        channels = [
            ("UC111111111111111111111", "Channel One"),
            ("UC222222222222222222222", "Channel Two"),
            ("UC333333333333333333333", "Channel Three"),
        ]
        
        for channel_id, channel_name in channels:
            mock_dir = Path(temp_config_dir).parent / f"mock_{channel_id[:6]}"
            mock_dir.mkdir(exist_ok=True)
            mock_uvx = mock_dir / "uvx"
            mock_uvx.write_text(f'''#!/bin/bash
if [[ "$*" == *"--print channel_id"* ]]; then
    echo "{channel_id}"
elif [[ "$*" == *"--print channel"* ]]; then
    echo "{channel_name}"
fi
''')
            mock_uvx.chmod(0o755)
            
            test_env = env.copy()
            test_env["PATH"] = f"{mock_dir}:{env.get('PATH', '')}"
            
            subprocess.run(
                [str(nightswatch_path), "add", f"https://youtube.com/@test{channel_id[:6]}"],
                env=test_env,
                capture_output=True,
            )
        
        with open(temp_config_dir) as f:
            config = yaml.safe_load(f)
        
        assert len(config["channels"]) == 3
        ids = [c["id"] for c in config["channels"]]
        assert "UC111111111111111111111" in ids
        assert "UC222222222222222222222" in ids
        assert "UC333333333333333333333" in ids
