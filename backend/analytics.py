"""Water consumption analytics for smart house monitoring."""

import os
from collections import defaultdict
from datetime import datetime

import config  # noqa: F401 — loads .env from project root
from database import get_all_readings

WATER_TARIFF = float(os.getenv("WATER_TARIFF_PER_KL", "50"))
LEAK_THRESHOLD = float(os.getenv("LEAK_FLOW_THRESHOLD", "0.5"))


def _parse_time(iso_str: str) -> datetime:
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))


def consumption_summary(readings: list[dict] | None = None) -> dict:
    readings = readings or get_all_readings()
    if not readings:
        return {"message": "No data yet. Run the simulator first."}

    latest = readings[-1]
    first = readings[0]

    total_liters = latest.get("water_consumption") or 0
    period_used = total_liters - (first.get("water_consumption") or 0)

    flow_rates = [r["flow_rate"] for r in readings if r.get("flow_rate") is not None]
    pressures = [r["water_pressure"] for r in readings if r.get("water_pressure") is not None]
    ph_values = [r["ph"] for r in readings if r.get("ph") is not None]
    turbidity_values = [r["turbidity"] for r in readings if r.get("turbidity") is not None]
    leak_events = sum(1 for r in readings if r.get("leak_status") == 1)

    cost_inr = (period_used / 1000) * WATER_TARIFF

    return {
        "total_consumption_liters": round(total_liters, 1),
        "period_usage_liters": round(max(period_used, 0), 1),
        "avg_flow_rate_lpm": round(sum(flow_rates) / len(flow_rates), 2) if flow_rates else 0,
        "max_flow_rate_lpm": round(max(flow_rates), 2) if flow_rates else 0,
        "avg_pressure_bar": round(sum(pressures) / len(pressures), 2) if pressures else 0,
        "avg_ph": round(sum(ph_values) / len(ph_values), 2) if ph_values else 0,
        "avg_turbidity_ntu": round(sum(turbidity_values) / len(turbidity_values), 2) if turbidity_values else 0,
        "leak_events": leak_events,
        "estimated_cost_inr": round(cost_inr, 2),
        "readings_count": len(readings),
        "latest_reading": latest,
    }


def hourly_peak_usage(readings: list[dict] | None = None) -> list[dict]:
    readings = readings or get_all_readings()
    hourly: dict[int, list[float]] = defaultdict(list)

    for r in readings:
        if r.get("flow_rate") is None:
            continue
        hour = _parse_time(r["created_at"]).hour
        hourly[hour].append(r["flow_rate"])

    return [
        {
            "hour": h,
            "avg_flow_rate": round(sum(vals) / len(vals), 2),
            "label": f"{h:02d}:00",
        }
        for h, vals in sorted(hourly.items())
    ]


def quality_status(readings: list[dict] | None = None) -> dict:
    readings = readings or get_all_readings()
    if not readings:
        return {"status": "unknown", "issues": []}

    latest = readings[-1]
    issues = []

    ph = latest.get("ph")
    turbidity = latest.get("turbidity")
    leak = latest.get("leak_status")

    if ph is not None and (ph < 6.5 or ph > 8.5):
        issues.append(f"pH {ph} is outside safe range (6.5–8.5)")
    if turbidity is not None and turbidity > 5:
        issues.append(f"Turbidity {turbidity} NTU is high (safe: < 5)")
    if leak == 1:
        issues.append("Active leak detected")

    return {
        "status": "critical" if leak == 1 else ("warning" if issues else "good"),
        "ph": ph,
        "turbidity": turbidity,
        "leak_status": leak,
        "issues": issues,
    }


def roi_estimate(monthly_savings_liters: float = 500) -> dict:
    """ROI for 1-house smart water system (for report)."""
    hardware_cost = 4500
    software_cost = 0  # ThingSpeak free tier
    monthly_savings_inr = (monthly_savings_liters / 1000) * WATER_TARIFF
    payback_months = hardware_cost / monthly_savings_inr if monthly_savings_inr else 0

    return {
        "hardware_cost_inr": hardware_cost,
        "software_cost_inr": software_cost,
        "total_investment_inr": hardware_cost + software_cost,
        "estimated_monthly_savings_liters": monthly_savings_liters,
        "estimated_monthly_savings_inr": round(monthly_savings_inr, 2),
        "payback_period_months": round(payback_months, 1),
    }
