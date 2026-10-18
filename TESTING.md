# Testing

Use Python >=3.10. Create and activate a clean virtual environment, then run:

```sh
python -m pip install -e '.[dev]'
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

The existing 90% coverage floor remains enforced. CI covers Python 3.10 and 3.14 on Linux, Windows, and macOS. Tests use synthetic inputs and preserve the default command-line workflow. No personal data is required.

## 1.1.2 output and arithmetic failure handling

Create JSON and Markdown reports exclusively; reproduce a destination appearing immediately before open and verify it survives unchanged. Preserve source bytes and retry successfully at a new path. Finite numeric inputs can still exceed Decimal arithmetic or rounding limits; both the public analysis function and CLI must reject those inputs actionably before creating output. Cover rate, remaining-time, rounding and scenario-break failures while retaining the existing estimate semantics. Run formatting, lint, typing, full coverage tests, builds and installed-artifact end-to-end checks before independent review.
