# Reading Pace Reality Calculator

[![CI](https://github.com/loganpendragonmultiverse/reading-pace-reality-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/reading-pace-reality-calculator/actions/workflows/ci.yml)

Estimate completion time from real sessions, retention, breaks, and reading conditions. The command uses explicit UTF-8 JSON input and produces reviewable JSON or Markdown output.

## Release 1.1.2 — 2026-10-18

Reports use exclusive file creation. If another process creates the destination during export, the command returns an error and preserves that file and the source input.

Finite numeric inputs must also fit the decimal calculation range. Values that overflow arithmetic or cannot be rounded to the report precision return an actionable error before any output file is created. These limits do not change ordinary reading estimates.

## Three-minute start

```bash
python -m pip install .
reading-pace examples/sample.json
reading-pace examples/sample.json --format json --output report.json
```

The example documents the v1 input shape. Existing report files are never overwritten. Source inputs are read-only except where the documented purpose explicitly creates a new output artifact.

## Privacy and platforms

The tool runs locally and does not upload input or include telemetry. Python 3.10 or newer is supported on Windows, macOS, and Linux.

## Interpretation boundary

Results are planning estimates based on supplied sessions; they do not predict comprehension or enforce a reading schedule.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

The project is feature-complete for its documented v1 scope. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Named session scenarios

Add an optional `scenarios` list to compare session length and time between sessions:

```json
"scenarios": [{"name":"Short evenings","session_minutes":20.5,"break_minutes":5},{"name":"Long weekend","session_minutes":60,"break_minutes":10}]
```

Each scenario uses the same observed median pace and existing retention/break-factor assumptions. `session_minutes` defaults to 30 and must be positive; `break_minutes` defaults to zero and must be non-negative. Names must be non-empty and unique. Results include the assumptions, reading hours, ceiling-rounded session count, and elapsed hours including one break between sessions (no trailing break). Zero remaining pages means zero sessions and breaks. Inputs must be finite numbers; decimal values and numeric strings are supported.

Without scenarios, the report retains its existing fields and defaults. These are arithmetic planning estimates from user-supplied observations and assumptions, **not predictions of comprehension, retention, or reading ability**. Nothing is collected or uploaded.

### Changes prepared for 1.1.3 — 2026-10-18

Session counts use exact finite ratios before rounding up. For example, three pages at one page per 13 minutes require three 13-minute sessions; with ten-minute breaks between sessions, elapsed time is 0.98 hours. A value just above three pages still requires a fourth session. Reading hours and scenario elapsed hours use the same exact half-even rounding to two decimal places. Scenario elapsed hours include no trailing break. Unsupported decimal ranges remain input errors. Failed stdout writes return exit status 2.
