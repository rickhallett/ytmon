# ytmon — YouTube Monitor

Nightswatch: the CLI that guards the realms of YouTube knowledge.

## Quick Start

```bash
# Check for new videos from watched channels
nightswatch

# Add a channel
nightswatch add "https://youtube.com/@SomeChannel"

# List watched channels
nightswatch list

# Grab transcript from specific video
nightswatch grab "https://youtu.be/xyz"
```

## Config

Config lives at `~/.config/ytmon/config.yaml`

## Tests

Tests use pytest and follow the **Gate Pattern** — see `tests/GATE.md`.

```bash
# Run tests
pytest tests/ -v

# Run with output
pytest tests/ -v -s
```

## Structure

```
~/.local/bin/nightswatch     # The CLI script
~/.config/ytmon/config.yaml  # Channel config
~/.local/share/ytmon/        # Database and transcripts
~/code/ytmon/tests/          # Test suite (Gate)
```
