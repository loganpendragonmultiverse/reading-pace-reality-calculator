import json
import os
import subprocess
import sys
from decimal import Decimal
from fractions import Fraction

import pytest

from reading_pace_reality_calculator.cli import main
from reading_pace_reality_calculator.core import analyze


@pytest.mark.parametrize("minutes", [13, 38, 39, 45, 53, 59])
def test_exact_session_boundary_has_no_extra_session_or_break(minutes):
    data = {
        "remaining_pages": 3,
        "sessions": [{"pages": 1, "minutes": minutes}],
        "planned_session_minutes": minutes,
        "scenarios": [{"name": "Boundary", "session_minutes": minutes, "break_minutes": 10}],
    }
    report = analyze(data)
    assert report["sessions_remaining"] == 3
    scenario = report["scenarios"][0]
    assert scenario["sessions_remaining"] == 3
    expected = Decimal(round(Fraction(3 * minutes + 20, 60) * 100)).scaleb(-2)
    assert scenario["elapsed_hours"] == expected
    data["remaining_pages"] = "3.000000000000000000000000001"
    report = analyze(data)
    assert report["sessions_remaining"] == 4
    assert report["scenarios"][0]["sessions_remaining"] == 4


def test_multiple_observations_retention_and_break_factor_are_exact():
    data = {
        "remaining_pages": "2.25",
        "sessions": [{"pages": 1, "minutes": 13, "retention": "0.75"}] * 2,
        "break_factor": "0.5",
        "planned_session_minutes": 13,
    }
    assert analyze(data)["sessions_remaining"] == 6


@pytest.mark.parametrize("value", ["1e999999999", "1e-999999999"])
def test_unbounded_exponent_is_refused_before_ratio_conversion(value):
    with pytest.raises(ValueError, match="supported decimal calculation range"):
        analyze({"remaining_pages": value, "sessions": [{"pages": 1, "minutes": 13}]})


def test_closed_stdout_pipe_returns_documented_error(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps({"remaining_pages": 3, "sessions": [{"pages": 1, "minutes": 13}]}))
    read_end, write_end = os.pipe()
    os.close(read_end)
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reading_pace_reality_calculator",
                str(source),
                "--format",
                "json",
            ],
            stdout=write_end,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    finally:
        os.close(write_end)
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert "Exception ignored" not in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("zero_write", [False, True])
def test_stdout_short_and_zero_writes(tmp_path, monkeypatch, capsys, zero_write):
    source = tmp_path / "input.json"
    source.write_text(json.dumps({"remaining_pages": 3, "sessions": [{"pages": 1, "minutes": 13}]}))

    class Output:
        encoding = "utf-8"
        errors = "strict"

        def fileno(self):
            return 123

    output = bytearray()

    def write(descriptor, pending):
        assert descriptor == 123
        if zero_write:
            return 0
        output.extend(pending[:7])
        return min(7, len(pending))

    monkeypatch.setattr(sys, "stdout", Output())
    monkeypatch.setattr(os, "write", write)
    assert main([str(source), "--format", "json"]) == (2 if zero_write else 0)
    if zero_write:
        assert "error:" in capsys.readouterr().err
    else:
        assert json.loads(output)["sessions_remaining"] == 2


def test_balanced_extreme_exponents_are_refused_before_fraction_allocation(monkeypatch):
    from reading_pace_reality_calculator import core

    def forbidden_fraction(*args, **kwargs):
        pytest.fail("unsupported raw exponent reached ratio conversion")

    monkeypatch.setattr(core, "Fraction", forbidden_fraction)
    with pytest.raises(ValueError, match="supported decimal calculation range"):
        analyze(
            {
                "remaining_pages": 3,
                "sessions": [{"pages": "1e1000000000", "minutes": "1e1000000000"}],
            }
        )


def test_even_median_with_different_rates_keeps_exact_ceiling():
    # Median(1/13, 3/13) pages per minute = 2/13; six pages need 39 minutes.
    report = analyze(
        {
            "remaining_pages": 6,
            "sessions": [{"pages": 1, "minutes": 13}, {"pages": 3, "minutes": 13}],
            "planned_session_minutes": 13,
        }
    )
    assert report["sessions_remaining"] == 3


@pytest.mark.parametrize("minutes, expected", [(7, "0.04"), (13, "0.06"), (45, "0.22")])
def test_exact_half_cent_hours_match_zero_break_elapsed_hours(minutes, expected):
    report = analyze(
        {
            "remaining_pages": 3,
            "sessions": [{"pages": 10, "minutes": minutes}],
            "scenarios": [{"name": "No breaks", "session_minutes": 30, "break_minutes": 0}],
        }
    )
    scenario = report["scenarios"][0]
    assert report["hours_remaining"] == Decimal(expected)
    assert scenario["hours_remaining"] == Decimal(expected)
    assert scenario["elapsed_hours"] == Decimal(expected)
