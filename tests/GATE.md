# Gate Pattern — nightswatch Tests

## What is a Gate?

A **Gate** is a set of tests that **must pass** before any change to the guarded code is accepted. It's a quality checkpoint that prevents regressions and enforces contracts.

## Gate for `nightswatch add`

These tests guard the `add` command in `~/.local/bin/nightswatch`:

```bash
# Run the gate
pytest ~/code/ytmon/tests/ -v

# Or with coverage
pytest ~/code/ytmon/tests/ --cov=nightswatch -v
```

### Gate Rules

1. **All tests must pass** before merging changes to nightswatch
2. **New features require new tests** — no shipping untested code
3. **Breaking changes require gate updates** — if behavior changes, tests change first
4. **Failed gate = blocked change** — no exceptions, no "I'll fix it later"

## Test Coverage

| Test Class | Description |
|------------|-------------|
| `TestAddChannel` | Core add functionality |
| `TestConfigIntegrity` | Config file safety |
| `TestEdgeCases` | Edge cases and robustness |
| `TestListChannels` | Core list functionality |
| `TestListEdgeCases` | List edge cases |

### `add` Command Tests

- `test_add_channel_by_url` — Happy path: add works
- `test_add_duplicate_channel_no_duplicate` — Idempotency: no duplicates
- `test_add_invalid_url_handling` — Error handling: bad URLs fail gracefully
- `test_add_missing_url_shows_usage` — UX: helpful errors
- `test_config_remains_valid_yaml` — Safety: output is valid YAML
- `test_config_preserves_other_settings` — Safety: doesn't clobber config
- `test_config_channel_format_correct` — Contract: channel format is correct
- `test_add_to_empty_channels_list` — Edge: empty list handled
- `test_add_multiple_channels_sequentially` — Edge: sequential adds work

### `list` Command Tests

- `test_list_shows_header` — Output has descriptive header
- `test_list_shows_configured_channels` — Shows channel names
- `test_list_empty_channels` — Handles empty config gracefully
- `test_list_shows_channel_ids` — Shows channel IDs
- `test_list_with_special_characters_in_name` — Unicode/special chars work
- `test_list_returns_zero_exit_code` — Exits cleanly

## Extending the Gate

When modifying nightswatch:

1. **Write the test first** (TDD encouraged)
2. **Run the gate** to see it fail
3. **Implement the change**
4. **Run the gate** to see it pass
5. **Commit both test and change together**

## Dependencies

```bash
# Install test dependencies
pip install pytest pyyaml
```

## Philosophy

> "If it's not tested, it's broken."

Gates are not bureaucracy — they're insurance. The 5 minutes spent running tests saves hours debugging production issues.
