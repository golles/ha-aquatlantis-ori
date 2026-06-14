# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About

Home Assistant custom integration for controlling Aquatlantis Ori smart aquarium controllers via their cloud API. The Ori API was reverse-engineered; functionality may break if Aquatlantis changes their API.

## Commands

All Python tooling is managed via `uv`. Node/npm is used for Prettier formatting only.

```sh
# Install dependencies
./scripts/setup_env.sh

# Run all tests
pytest tests

# Run a single test file
pytest tests/test_light.py

# Run a single test
pytest tests/test_light.py::test_function_name

# Linting and type checking
uv run ruff check .          # Linter
uv run ruff format .         # Formatter
uv run mypy custom_components/ori
uv run pylint custom_components/ori tests
npm run prettier -- --write . # Format JSON/YAML

# Run all CI checks locally (requires jq and yq)
./scripts/local_ci_checks.sh

# Run Home Assistant locally against ./config for manual testing
./scripts/develop.sh
```

Python version: **3.14** (enforced in `pyproject.toml`).

## Architecture

### Integration structure

The integration lives in `custom_components/ori/` and wraps the external `aquatlantis_ori` Python library. The library handles the cloud WebSocket connection and exposes `AquatlantisOriClient` and `Device` objects.

**Entry points:**

- `__init__.py` — sets up `AquatlantisOriClient` on `config_entry.runtime_data`, forwards to all platforms, and calls `client.connect()` / `client.wait_for_data()` before platforms are loaded.
- `config_flow.py` — UI-only config flow using email + password credentials.
- `services.py` — registers the `ori.set_schedule` service at `async_setup` time (not per entry).

**Platforms:** `binary_sensor`, `button`, `light`, `number`, `sensor`, `update`.

### Entity pattern

All entities follow the same descriptor pattern:

- `OriEntityDescription` (in `entity.py`) extends `EntityDescription` with four optional callables:
  - `available_fn(device)` — controls `available` property
  - `entity_registry_enabled_default_fn(device)` — disables entities that are off by default
  - `is_supported_fn(device)` — filters which entities get created per device
  - `state_attributes_fn(device)` — returns extra state attributes dict

- `OriEntity` base class stores `_device: Device` and `_config_entry`. The `available` property requires `device.availability_state == AvailabilityType.AVAILABLE` **and** the description's `available_fn(device)`.

Each platform defines a `DESCRIPTIONS` list of platform-specific entity description subclasses (e.g., `OriLightEntityDescription`) and iterates over `client.get_devices()` to create entities, filtering with `is_supported_fn`.

### Light specifics

The light entity maps HA effects to Ori modes:

- `manual` → `ModeType.MANUAL` + `DynamicModeType.OFF`
- `automatic` → `ModeType.AUTOMATIC` (returns early, no RGBW sent)
- `dynamic` → `ModeType.MANUAL` + `DynamicModeType.ON`

Color values are converted between HA's 0–255 range and the Ori API's 0–100 range via `_convert_255_to_100` / `_convert_100_to_255`.

### Testing

Tests use `pytest-homeassistant-custom-component`. Key fixtures in `conftest.py`:

- `mock_aquatlantis_client` (autouse) — patches `AquatlantisOriClient` with an `AsyncMock`; override `mock_aquatlantis_client.get_devices.return_value` to inject test devices.
- `enable_all_entities` — opt-in fixture that overrides `entity_registry_enabled_default` to `True` for testing disabled-by-default entities.
- `mock_async_get_clientsession` (autouse) — prevents real aiohttp sessions.

### PR contributions from agents

Add `🤖🤖🤖` to the end of the PR title to fast-track merging of automated agent PRs.
