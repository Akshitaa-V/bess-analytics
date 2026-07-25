"""Performance metrics for battery energy storage systems (BESS).

These functions compute standard battery health and efficiency
metrics from operational telemetry, the same kind of derived
metrics used to evaluate BESS performance in the field.
"""

from __future__ import annotations
from dataclasses import dataclass


def round_trip_efficiency(energy_charged_kwh: float, energy_discharged_kwh: float) -> float:
    """Round-trip efficiency: fraction of charged energy recovered on discharge.

    Returns a value in [0, 1]. Raises ValueError for non-physical inputs.
    """
    if energy_charged_kwh <= 0:
        raise ValueError("energy_charged_kwh must be positive")
    if energy_discharged_kwh < 0:
        raise ValueError("energy_discharged_kwh cannot be negative")

    efficiency = energy_discharged_kwh / energy_charged_kwh
    return min(efficiency, 1.0)


def state_of_health(current_capacity_kwh: float, rated_capacity_kwh: float) -> float:
    """State of Health (SoH) as a percentage of rated capacity remaining.

    SoH = 100% at beginning of life, degrades toward the industry-standard
    end-of-life threshold (commonly 80%) over the asset's lifetime.
    """
    if rated_capacity_kwh <= 0:
        raise ValueError("rated_capacity_kwh must be positive")
    if current_capacity_kwh < 0:
        raise ValueError("current_capacity_kwh cannot be negative")

    soh = (current_capacity_kwh / rated_capacity_kwh) * 100
    return round(soh, 2)


@dataclass
class CapacityFadeResult:
    fade_rate_per_cycle_pct: float
    projected_cycles_to_eol: float | None  # cycles remaining to 80% SoH


def capacity_fade_rate(
    soh_history_pct: list[float],
    eol_threshold_pct: float = 80.0,
) -> CapacityFadeResult:
    """Estimate capacity fade rate per cycle from a SoH history, and
    project remaining cycles to the end-of-life (EoL) threshold.

    Uses a simple linear fit across the provided SoH readings (one
    reading per cycle), which is standard for a first-pass degradation
    estimate before more sophisticated modeling.
    """
    n = len(soh_history_pct)
    if n < 2:
        raise ValueError("Need at least 2 SoH readings to estimate fade rate")

    # Simple linear regression slope (fade per cycle), cycle index as x.
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(soh_history_pct) / n

    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, soh_history_pct))
    denominator = sum((x - mean_x) ** 2 for x in xs)

    if denominator == 0:
        slope = 0.0
    else:
        slope = numerator / denominator

    fade_rate_per_cycle = -slope  # positive fade rate = degrading
    current_soh = soh_history_pct[-1]

    if fade_rate_per_cycle <= 0:
        projected_cycles = None  # not degrading (or improving) — cannot project
    else:
        projected_cycles = max(0.0, (current_soh - eol_threshold_pct) / fade_rate_per_cycle)

    return CapacityFadeResult(
        fade_rate_per_cycle_pct=round(fade_rate_per_cycle, 4),
        projected_cycles_to_eol=(
            round(projected_cycles, 1) if projected_cycles is not None else None
        ),
    )
