"""A lightweight digital twin for a single battery energy storage asset.

Ingests telemetry readings one at a time (as a real BESS data pipeline
would), maintains running state (cycle count, SoH history, safety log),
and exposes summary analytics on demand.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from .safety import SafetyLimits, SafetyReading, check_safety, summarize_safety
from .performance import capacity_fade_rate, state_of_health, CapacityFadeResult


@dataclass
class TelemetryReading:
    timestamp: str
    voltage_v: float
    current_a: float
    temperature_c: float
    energy_charged_kwh: float = 0.0
    energy_discharged_kwh: float = 0.0


class BatteryDigitalTwin:
    """Digital twin of a single BESS asset.

    Mirrors the real asset's state by processing telemetry as it
    arrives, rather than recomputing everything from scratch on
    every reading — the same incremental-update pattern a production
    data pipeline would use.
    """

    def __init__(
        self,
        asset_id: str,
        rated_capacity_kwh: float,
        safety_limits: SafetyLimits | None = None,
    ):
        self.asset_id = asset_id
        self.rated_capacity_kwh = rated_capacity_kwh
        self.safety_limits = safety_limits or SafetyLimits()

        self.cycle_count: int = 0
        self.current_capacity_kwh: float = rated_capacity_kwh
        self.soh_history: list[float] = [100.0]
        self.safety_log: list[SafetyReading] = []
        self._cumulative_charged_kwh: float = 0.0
        self._cumulative_discharged_kwh: float = 0.0

    def ingest(self, reading: TelemetryReading) -> SafetyReading:
        """Process one telemetry reading: update safety log and, if a
        full cycle's worth of energy has passed, update SoH.
        """
        safety_reading = check_safety(
            timestamp=reading.timestamp,
            temperature_c=reading.temperature_c,
            voltage_v=reading.voltage_v,
            current_a=reading.current_a,
            limits=self.safety_limits,
        )
        self.safety_log.append(safety_reading)

        self._cumulative_charged_kwh += reading.energy_charged_kwh
        self._cumulative_discharged_kwh += reading.energy_discharged_kwh

        # A full equivalent cycle = cumulative discharge equal to rated capacity.
        if self._cumulative_discharged_kwh >= self.rated_capacity_kwh:
            self.cycle_count += 1
            self._cumulative_charged_kwh = 0.0
            self._cumulative_discharged_kwh = 0.0

            # Simple degradation model: small capacity loss per completed cycle.
            # (In production this would come from a fitted electrochemical
            # or empirical aging model, not a fixed decrement.)
            degradation_kwh = self.rated_capacity_kwh * 0.0005
            self.current_capacity_kwh = max(0.0, self.current_capacity_kwh - degradation_kwh)
            self.soh_history.append(
                state_of_health(self.current_capacity_kwh, self.rated_capacity_kwh)
            )

        return safety_reading

    def performance_report(self) -> dict:
        if len(self.soh_history) < 2:
            return {
                "asset_id": self.asset_id,
                "cycle_count": self.cycle_count,
                "current_soh_pct": self.soh_history[-1],
                "fade_rate_per_cycle_pct": None,
                "projected_cycles_to_eol": None,
                "note": "Not enough completed cycles yet to estimate fade rate.",
            }

        fade: CapacityFadeResult = capacity_fade_rate(self.soh_history)
        return {
            "asset_id": self.asset_id,
            "cycle_count": self.cycle_count,
            "current_soh_pct": self.soh_history[-1],
            "fade_rate_per_cycle_pct": fade.fade_rate_per_cycle_pct,
            "projected_cycles_to_eol": fade.projected_cycles_to_eol,
        }

    def safety_report(self) -> dict:
        return summarize_safety(self.safety_log)
