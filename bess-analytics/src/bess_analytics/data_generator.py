"""Synthetic telemetry generator for demo and testing.

Generates a plausible charge/discharge cycle stream for a single BESS
asset, including a small number of injected safety anomalies, so the
pipeline can be exercised end-to-end without requiring a live data feed.
"""

from __future__ import annotations
import random
from datetime import datetime, timedelta

from .digital_twin import TelemetryReading


def generate_cycle_stream(
    num_cycles: int,
    readings_per_cycle: int = 20,
    rated_capacity_kwh: float = 100.0,
    anomaly_probability: float = 0.02,
    seed: int | None = 42,
) -> list[TelemetryReading]:
    """Generate a synthetic stream of telemetry readings spanning
    `num_cycles` charge/discharge cycles.
    """
    rng = random.Random(seed)
    readings: list[TelemetryReading] = []
    t = datetime(2026, 1, 1)

    for _cycle in range(num_cycles):
        # Charge phase
        energy_per_step = rated_capacity_kwh / readings_per_cycle
        for _ in range(readings_per_cycle):
            t += timedelta(minutes=15)
            voltage = rng.uniform(3.6, 4.1)
            current = rng.uniform(20, 40)
            temperature = rng.uniform(15, 30)

            if rng.random() < anomaly_probability:
                temperature = rng.uniform(46, 55)  # inject over-temperature event

            readings.append(
                TelemetryReading(
                    timestamp=t.isoformat(),
                    voltage_v=round(voltage, 3),
                    current_a=round(current, 2),
                    temperature_c=round(temperature, 1),
                    energy_charged_kwh=round(energy_per_step, 3),
                    energy_discharged_kwh=0.0,
                )
            )

        # Discharge phase (round-trip efficiency ~92%)
        discharge_energy_per_step = (rated_capacity_kwh * 0.92) / readings_per_cycle
        for _ in range(readings_per_cycle):
            t += timedelta(minutes=15)
            voltage = rng.uniform(3.2, 3.7)
            current = rng.uniform(-40, -20)
            temperature = rng.uniform(15, 32)

            if rng.random() < anomaly_probability:
                voltage = rng.uniform(2.5, 2.9)  # inject under-voltage event

            readings.append(
                TelemetryReading(
                    timestamp=t.isoformat(),
                    voltage_v=round(voltage, 3),
                    current_a=round(current, 2),
                    temperature_c=round(temperature, 1),
                    energy_charged_kwh=0.0,
                    energy_discharged_kwh=round(discharge_energy_per_step, 3),
                )
            )

    return readings
