from __future__ import annotations

import json
from decimal import Decimal, DecimalException, InvalidOperation, getcontext
from fractions import Fraction
from typing import Any

PROJECT = "reading-pace-reality-calculator"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def number(value: Any, name: str, *, positive: bool = False) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name} must be a finite number") from None
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise ValueError(f"{name} must be finite and {'positive' if positive else 'non-negative'}")
    if result and not getcontext().Etiny() <= result.adjusted() <= getcontext().Emax:
        raise InvalidOperation("numeric exponent exceeds the decimal calculation range")
    return result


def _reading_pace(data: dict[str, Any], *, include_exact: bool = False) -> dict[str, Any]:
    remaining = number(_require(data, "remaining_pages"), "remaining_pages")
    sessions = _require(data, "sessions")
    if not isinstance(sessions, list) or any(not isinstance(s, dict) for s in sessions):
        raise ValueError("sessions must be a non-empty list of objects")
    rates: list[Decimal] = []
    retention: list[Decimal] = []
    observations: list[tuple[Decimal, Decimal]] = []
    for session in sessions:
        minutes = number(session.get("minutes", 0), "session minutes", positive=True)
        pages = number(session.get("pages", 0), "session pages")
        rates.append(pages / minutes * 60)
        observations.append((pages, minutes))
        retention.append(number(session.get("retention", 1), "retention"))
    sorted_rates = sorted(rates)
    middle = len(sorted_rates) // 2
    median_rate = (
        sorted_rates[middle]
        if len(sorted_rates) % 2
        else (sorted_rates[middle - 1] + sorted_rates[middle]) / Decimal(2)
    )
    retention_factor = sum(retention, Decimal(0)) / Decimal(len(retention))
    break_factor = number(data.get("break_factor", 1), "break_factor", positive=True)
    effective = median_rate * retention_factor * break_factor
    if effective <= 0:
        raise ValueError("effective reading pace must be positive")
    hours = remaining / effective
    session_minutes = number(
        data.get("planned_session_minutes", 30), "planned_session_minutes", positive=True
    )
    # Keep Decimal display/range checks before exact finite-ratio conversion.
    displayed = {
        "median_pages_per_hour": round(median_rate, 2),
        "effective_pages_per_hour": round(effective, 2),
        "hours_remaining": round(hours, 2),
    }
    exact_rates = sorted(
        Fraction(pages) / Fraction(minutes) * 60 for pages, minutes in observations
    )
    exact_median = (
        exact_rates[middle]
        if len(exact_rates) % 2
        else (exact_rates[middle - 1] + exact_rates[middle]) / 2
    )
    exact_retention = sum(map(Fraction, retention), Fraction(0)) / len(retention)
    exact_hours = Fraction(remaining) / (exact_median * exact_retention * Fraction(break_factor))
    session_ratio = exact_hours * 60 / Fraction(session_minutes)
    sessions_needed = -(-session_ratio.numerator // session_ratio.denominator)
    return {
        **({"exact_hours": exact_hours} if include_exact else {}),
        **displayed,
        "sessions_remaining": int(sessions_needed),
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    """Reject arithmetic outside Decimal's range with an actionable input error."""
    try:
        return _analyze(data)
    except DecimalException as exc:
        raise ValueError("numeric values exceed the supported decimal calculation range") from exc


def _analyze(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TypeError("input must be an object")
    report = {"version": 1, "project": PROJECT, **_reading_pace(data)}
    if "scenarios" in data:
        scenarios = data["scenarios"]
        if not isinstance(scenarios, list):
            raise ValueError("scenarios must be a list")
        names: set[str] = set()
        results = []
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                raise TypeError("scenario must be an object")
            name = scenario.get("name")
            if not isinstance(name, str) or not name.strip() or name in names:
                raise ValueError("scenario names must be non-empty and unique")
            names.add(name)
            length = number(scenario.get("session_minutes", 30), "session_minutes", positive=True)
            pause = number(scenario.get("break_minutes", 0), "break_minutes")
            estimate = _reading_pace(
                {**data, "planned_session_minutes": length}, include_exact=True
            )
            reading_hours = estimate.pop("exact_hours")
            breaks = max(estimate["sessions_remaining"] - 1, 0)
            # Preserve Decimal range refusal before converting/rounding exact elapsed time.
            round(
                Decimal(reading_hours.numerator) / Decimal(reading_hours.denominator)
                + breaks * pause / 60,
                2,
            )
            elapsed = reading_hours + breaks * Fraction(pause) / 60
            results.append(
                {
                    "name": name,
                    "session_minutes": length,
                    "break_minutes": pause,
                    **estimate,
                    "elapsed_hours": Decimal(round(elapsed * 100)).scaleb(-2),
                }
            )
        report["scenarios"] = results
    return report


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.extend(
                [
                    f"## {key.replace('_', ' ').title()}",
                    "",
                    f"```json\n{json.dumps(value, indent=2, ensure_ascii=False, default=str)}\n```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
