import json
from pathlib import Path

import pytest

from reading_pace_reality_calculator.cli import main
from reading_pace_reality_calculator.core import analyze


def input_data():
    return {"remaining_pages": 60, "sessions": [{"pages": 30, "minutes": 30}]}


@pytest.mark.parametrize("format_name", ["json", "markdown"])
def test_destination_arriving_during_export_is_preserved(
    tmp_path, monkeypatch, capsys, format_name
):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(input_data()), encoding="utf-8")
    source_bytes = source.read_bytes()
    target = tmp_path / "report.txt"
    original_open = Path.open
    arrived = False

    def open_with_arriving_destination(path, mode="r", *args, **kwargs):
        nonlocal arrived
        if path == target and not arrived and mode in ("w", "x"):
            arrived = True
            with original_open(path, "w", encoding="utf-8") as stream:
                stream.write("concurrent destination")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", open_with_arriving_destination)
    assert main([str(source), "--format", format_name, "--output", str(target)]) == 2
    assert arrived
    assert target.read_text(encoding="utf-8") == "concurrent destination"
    assert source.read_bytes() == source_bytes
    assert "error:" in capsys.readouterr().err
    retry = tmp_path / "retry.txt"
    assert main([str(source), "--format", format_name, "--output", str(retry)]) == 0
    assert retry.read_text(encoding="utf-8").strip()
    assert source.read_bytes() == source_bytes


RANGE_FAILURES = [
    {"remaining_pages": "1e1000000"},
    {"remaining_pages": "1e40"},
    {"sessions": [{"pages": "1e1000000", "minutes": 1}]},
    {"scenarios": [{"name": "Extreme break", "session_minutes": 1, "break_minutes": "1e1000000"}]},
]


@pytest.mark.parametrize("change", RANGE_FAILURES)
def test_public_analysis_rejects_decimal_range_failures(change):
    with pytest.raises(ValueError, match="supported decimal calculation range"):
        analyze({**input_data(), **change})


@pytest.mark.parametrize("change", RANGE_FAILURES)
def test_cli_range_error_preserves_source_and_creates_no_report(tmp_path, capsys, change):
    source = tmp_path / "input.json"
    source.write_text(json.dumps({**input_data(), **change}), encoding="utf-8")
    source_bytes = source.read_bytes()
    target = tmp_path / "report.json"
    assert main([str(source), "--format", "json", "--output", str(target)]) == 2
    captured = capsys.readouterr()
    assert "supported decimal calculation range" in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""
    assert not target.exists()
    assert source.read_bytes() == source_bytes
