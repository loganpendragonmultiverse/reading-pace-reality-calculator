from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

PROJECT = "reading-pace-reality-calculator"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _reading_pace(data: dict[str, Any]) -> dict[str, Any]:
    remaining = Decimal(str(_require(data, "remaining_pages")))
    sessions = _require(data, "sessions")
    rates: list[Decimal] = []
    retention: list[Decimal] = []
    for session in sessions:
        minutes = Decimal(str(session.get("minutes", 0)))
        pages = Decimal(str(session.get("pages", 0)))
        if minutes <= 0 or pages < 0:
            raise ValueError("session minutes must be positive and pages non-negative")
        rates.append(pages / minutes * 60)
        retention.append(Decimal(str(session.get("retention", 1))))
    sorted_rates = sorted(rates)
    middle = len(sorted_rates) // 2
    median_rate = (
        sorted_rates[middle]
        if len(sorted_rates) % 2
        else (sorted_rates[middle - 1] + sorted_rates[middle]) / Decimal(2)
    )
    retention_factor = sum(retention, Decimal(0)) / Decimal(len(retention))
    break_factor = Decimal(str(data.get("break_factor", 1)))
    effective = median_rate * retention_factor * break_factor
    if effective <= 0:
        raise ValueError("effective reading pace must be positive")
    hours = remaining / effective
    session_minutes = Decimal(str(data.get("planned_session_minutes", 30)))
    sessions_needed = (hours * 60 / session_minutes).to_integral_value(rounding="ROUND_CEILING")
    return {
        "median_pages_per_hour": round(median_rate, 2),
        "effective_pages_per_hour": round(effective, 2),
        "hours_remaining": round(hours, 2),
        "sessions_remaining": int(sessions_needed),
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_reading_pace(data)}


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
