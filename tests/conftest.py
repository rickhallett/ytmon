"""
Pytest configuration and fixtures for nightswatch tests.
"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory with a clean config file."""
    temp_dir = tempfile.mkdtemp(prefix="ytmon_test_")
    config_path = Path(temp_dir) / "config.yaml"
    
    # Minimal valid config
    initial_config = {
        "channels": [],
        "subtitles": {"languages": ["en"], "prefer_manual": True},
    }
    
    with open(config_path, "w") as f:
        yaml.dump(initial_config, f)
    
    yield config_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_config_with_channel(temp_config_dir):
    """Config with one pre-existing channel."""
    # Write in the exact format nightswatch expects (quoted strings)
    # nightswatch's duplicate check uses: grep -q 'id: "$channel_id"'
    config_content = '''channels:
  - name: "Test Channel"
    id: "UCtest123456789abcdefgh"
subtitles:
  languages:
    - en
  prefer_manual: true
'''
    with open(temp_config_dir, "w") as f:
        f.write(config_content)
    
    return temp_config_dir


@pytest.fixture
def temp_config_with_channels(temp_config_dir):
    """Config with multiple pre-existing channels."""
    config_content = '''channels:
  - name: "Channel Alpha"
    id: "UCaaa111111111111111111"
  - name: "Channel Beta"
    id: "UCbbb222222222222222222"
subtitles:
  languages:
    - en
  prefer_manual: true
'''
    with open(temp_config_dir, "w") as f:
        f.write(config_content)
    
    return temp_config_dir


@pytest.fixture
def nightswatch_path():
    """Path to the nightswatch script."""
    path = Path.home() / ".local" / "bin" / "nightswatch"
    if not path.exists():
        pytest.skip("nightswatch not installed at ~/.local/bin/nightswatch")
    return path


@pytest.fixture
def mock_yt_dlp(monkeypatch, tmp_path):
    """
    Mock uvx yt-dlp for testing without network calls.
    Creates a fake uvx script that returns predictable values.
    """
    mock_script = tmp_path / "uvx"
    mock_script.write_text('''#!/bin/bash
# Mock uvx for testing
if [[ "$*" == *"--print channel_id"* ]]; then
    echo "UCmock123456789abcdefgh"
elif [[ "$*" == *"--print channel"* ]]; then
    echo "Mock Channel Name"
fi
''')
    mock_script.chmod(0o755)
    
    # Prepend mock to PATH
    new_path = f"{tmp_path}:{os.environ.get('PATH', '')}"
    monkeypatch.setenv("PATH", new_path)
    
    return mock_script
