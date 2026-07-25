"""Run the BESS analytics pipeline end to end on synthetic telemetry.

Usage:
    python run_analysis.py
"""

from src.bess_analytics.data_generator import generate_cycle_stream
from src.bess_analytics.digital_twin import BatteryDigitalTwin


def main() -> None:
    twin = BatteryDigitalTwin(asset_id="BESS-MUC-001", rated_capacity_kwh=100.0)

    readings = generate_cycle_stream(num_cycles=50, readings_per_cycle=20, seed=42)
    print(f"Ingesting {len(readings)} telemetry readings across 50 cycles...\n")

    for reading in readings:
        twin.ingest(reading)

    perf = twin.performance_report()
    safety = twin.safety_report()

    print("=== Performance Report ===")
    for key, value in perf.items():
        print(f"  {key}: {value}")

    print("\n=== Safety Report ===")
    for key, value in safety.items():
        print(f"  {key}: {value}")

    if safety["unsafe_readings"] > 0:
        print(
            f"\n{safety['unsafe_readings']} unsafe reading(s) detected out of "
            f"{safety['total_readings']} total readings."
        )
    else:
        print("\nNo safety violations detected across the full telemetry stream.")


if __name__ == "__main__":
    main()
