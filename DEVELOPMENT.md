# Development contract

Estimate completion time from real sessions, retention, breaks, and reading conditions.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, changelog, README claims, repository metadata, release assets, and the Forge catalog together.

## 1.1.0 - 2026-10-15

Add an optional `scenarios` list to compare session length and time between sessions:

```json
"scenarios": [{"name":"Short evenings","session_minutes":20.5,"break_minutes":5},{"name":"Long weekend","session_minutes":60,"break_minutes":10}]
```

Each scenario uses the same observed median pace and existing retention/break-factor assumptions. `session_minutes` defaults to 30 and must be positive; `break_minutes` defaults to zero and must be non-negative. Names must be non-empty and unique. Results include the assumptions, reading hours, ceiling-rounded session count, and elapsed hours including one break between sessions (no trailing break). Zero remaining pages means zero sessions and breaks. Inputs must be finite numbers; decimal values and numeric strings are supported.

Without scenarios, the report retains its existing fields and defaults. These are arithmetic planning estimates from user-supplied observations and assumptions, **not predictions of comprehension, retention, or reading ability**. Nothing is collected or uploaded.

Changes require independent review before merge or release.
