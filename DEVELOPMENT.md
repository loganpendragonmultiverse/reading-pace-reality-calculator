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

## 1.1.2 output and arithmetic failure handling

Create JSON and Markdown reports exclusively; reproduce a destination appearing immediately before open and verify it survives unchanged. Preserve source bytes and retry successfully at a new path. Finite numeric inputs can still exceed Decimal arithmetic or rounding limits; both the public analysis function and CLI must reject those inputs actionably before creating output. Cover rate, remaining-time, rounding and scenario-break failures while retaining the existing estimate semantics. Run formatting, lint, typing, full coverage tests, builds and installed-artifact end-to-end checks before independent review.
