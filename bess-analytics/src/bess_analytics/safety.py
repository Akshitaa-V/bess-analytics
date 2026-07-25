"""Safety monitoring for battery energy storage systems (BESS).

Flags telemetry readings that fall outside safe operating envelopes —
the kind of checks that matter for safe, scalable BESS operation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class SafetyFlag(str, Enum):
    OVER_TEMPERATURE = "over_temperature"
    UNDER_TEMPERATURE = "under_temperature"
    OVER_VOLTAGE = "over_voltage"
    UNDER_VOLTAGE = "under_voltage"
    OVER_CURRENT = "over_current"
    OK = "ok"


@dataclass
class SafetyLimits:
    min_temp_c: float = -10.0
    max_temp_c: float = 45.0
    min_voltage_v: float = 3.0
    max_voltage_v: float = 4.2
    max_current_a: float = 100.0


@dataclass
class SafetyReading:
    timestamp: str
    temperature_c: float
    voltage_v: float
    current_a: float
    flags: list[SafetyFlag] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return len(self.flags) == 0


def check_safety(
    timestamp: str,
    temperature_c: float,
    voltage_v: float,
    current_a: float,
    limits: SafetyLimits | None = None,
) -> SafetyReading:
    """Check a single telemetry reading against safe operating limits."""
    limits = limits or SafetyLimits()
    flags: list[SafetyFlag] = []

    if temperature_c > limits.max_temp_c:
        flags.append(SafetyFlag.OVER_TEMPERATURE)
    elif temperature_c < limits.min_temp_c:
        flags.append(SafetyFlag.UNDER_TEMPERATURE)

    if voltage_v > limits.max_voltage_v:
        flags.append(SafetyFlag.OVER_VOLTAGE)
    elif voltage_v < limits.min_voltage_v:
        flags.append(SafetyFlag.UNDER_VOLTAGE)

    if abs(current_a) > limits.max_current_a:
        flags.append(SafetyFlag.OVER_CURRENT)

    return SafetyReading(
        timestamp=timestamp,
        temperature_c=temperature_c,
        voltage_v=voltage_v,
        current_a=current_a,
        flags=flags,
    )


def summarize_safety(readings: list[SafetyReading]) -> dict:
    """Summarize a batch of safety readings: total flags by type, unsafe count."""
    summary: dict[str, int] = {flag.value: 0 for flag in SafetyFlag if flag != SafetyFlag.OK}
    unsafe_count = 0

    for reading in readings:
        if not reading.is_safe:
            unsafe_count += 1
        for flag in reading.flags:
            summary[flag.value] += 1

    return {
        "total_readings": len(readings),
        "unsafe_readings": unsafe_count,
        "flag_counts": summary,
    }
