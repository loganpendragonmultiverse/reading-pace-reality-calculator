from decimal import Decimal

import pytest

from reading_pace_reality_calculator.core import analyze


def data():
    return {"remaining_pages": "60.5", "sessions": [{"pages": "30.25", "minutes": "30"}]}


def test_named_scenarios_decimal_breaks_and_unchanged_default():
    original = analyze(data())
    assert "scenarios" not in original
    report = analyze(
        {
            **data(),
            "scenarios": [
                {"name": "Short", "session_minutes": "15.5", "break_minutes": "5.5"},
                {"name": "Long", "session_minutes": 60, "break_minutes": 10},
            ],
        }
    )
    assert {k: v for k, v in report.items() if k != "scenarios"} == original
    short, long = report["scenarios"]
    assert short["sessions_remaining"] == 4 and short["elapsed_hours"] == Decimal("1.28")
    assert long["sessions_remaining"] == 1 and long["elapsed_hours"] == Decimal("1.00")


def test_zero_remaining_has_no_sessions_or_breaks():
    report = analyze(
        {
            **data(),
            "remaining_pages": 0,
            "scenarios": [{"name": "Zero", "session_minutes": 10, "break_minutes": 10}],
        }
    )
    assert report["scenarios"][0]["elapsed_hours"] == 0
    assert report["scenarios"][0]["sessions_remaining"] == 0


@pytest.mark.parametrize(
    "change",
    [
        {"remaining_pages": -1},
        {"remaining_pages": "NaN"},
        {"remaining_pages": "Infinity"},
        {"planned_session_minutes": 0},
        {"break_factor": "NaN"},
        {"sessions": []},
        {"sessions": [1]},
        {"sessions": [{"pages": 1, "minutes": "Infinity"}]},
        {"sessions": [{"pages": "x", "minutes": 5}]},
        {"sessions": [{"pages": 0, "minutes": 5}]},
        {"scenarios": [{"name": "A"}, {"name": "A"}]},
        {"scenarios": [1]},
        {"scenarios": [{"name": "A", "session_minutes": 0}]},
        {"scenarios": [{"name": "A", "break_minutes": "NaN"}]},
        {"scenarios": {}},
        {"scenarios": [{"name": ""}]},
    ],
)
def test_invalid_inputs_are_rejected(change):
    with pytest.raises((ValueError, TypeError)):
        analyze({**data(), **change})
