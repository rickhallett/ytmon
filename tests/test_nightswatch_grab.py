"""
Tests for nightswatch `grab` command.

Gate Pattern: These tests must pass before changes to nightswatch grab are accepted.
Run with: pytest ~/code/ytmon/tests/ -v
"""
import os
import subprocess
from pathlib import Path

import pytest


class TestGrabTranscript:
    """Tests for the nightswatch grab command."""

    def test_grab_missing_url_shows_usage(self, nightswatch_path, temp_config_dir):
        """Calling grab without a URL should show usage and fail."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        
        result = subprocess.run(
            [str(nightswatch_path), "grab"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should fail with usage message
        assert result.returncode != 0
        assert "usage" in result.stderr.lower()

    def test_grab_valid_url_calls_ytmon(
        self, nightswatch_path, temp_config_dir, mock_ytmon
    ):
        """Grab should call ytmon with the provided URL."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        env["PATH"] = f"{mock_ytmon.parent}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            [str(nightswatch_path), "grab", "https://youtube.com/watch?v=dQw4w9WgXcQ"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Mock ytmon returns success with transcript
        assert result.returncode == 0
        assert "transcript" in result.stdout.lower() or "mock" in result.stdout.lower()

    def test_grab_invalid_url_returns_error(
        self, nightswatch_path, temp_config_dir, mock_ytmon_fail
    ):
        """Grab with invalid URL should return non-zero exit code."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        env["PATH"] = f"{mock_ytmon_fail.parent}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            [str(nightswatch_path), "grab", "not-a-valid-url"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should fail
        assert result.returncode != 0

    def test_grab_short_url_format(
        self, nightswatch_path, temp_config_dir, mock_ytmon
    ):
        """Grab should handle youtu.be short URLs."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        env["PATH"] = f"{mock_ytmon.parent}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            [str(nightswatch_path), "grab", "https://youtu.be/dQw4w9WgXcQ"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0


class TestGrabEdgeCases:
    """Edge case tests for grab command."""

    def test_grab_preserves_url_to_ytmon(
        self, nightswatch_path, temp_config_dir, mock_ytmon_echo_url
    ):
        """URL should be passed correctly to ytmon."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        env["PATH"] = f"{mock_ytmon_echo_url.parent}:{env.get('PATH', '')}"
        
        test_url = "https://youtube.com/watch?v=abc123XYZ_-"
        
        result = subprocess.run(
            [str(nightswatch_path), "grab", test_url],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Mock echoes the URL it received
        assert test_url in result.stdout

    def test_grab_url_with_timestamp(
        self, nightswatch_path, temp_config_dir, mock_ytmon
    ):
        """Grab should handle URLs with timestamps."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        env["PATH"] = f"{mock_ytmon.parent}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            [str(nightswatch_path), "grab", "https://youtube.com/watch?v=dQw4w9WgXcQ&t=120"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Should still succeed
        assert result.returncode == 0

    def test_grab_returns_zero_on_success(
        self, nightswatch_path, temp_config_dir, mock_ytmon
    ):
        """Grab should return exit code 0 on success."""
        env = os.environ.copy()
        env["YTMON_CONFIG"] = str(temp_config_dir)
        env["PATH"] = f"{mock_ytmon.parent}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            [str(nightswatch_path), "grab", "https://youtube.com/watch?v=dQw4w9WgXcQ"],
            env=env,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode == 0
