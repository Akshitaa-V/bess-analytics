# BESS Analytics

A Python toolkit for evaluating the **performance and safety** of Battery Energy Storage Systems (BESS), built around a lightweight digital twin that ingests telemetry incrementally, the way a real operational data pipeline would.

## What it does
- **Digital twin (`digital_twin.py`)** — models a single BESS asset, ingesting telemetry readings one at a time and maintaining running state: cycle count, State of Health (SoH) history, and a safety event log
- **Performance metrics (`performance.py`)** — round-trip efficiency, State of Health, and capacity fade rate with projected cycles to end-of-life (80% SoH threshold)
- **Safety monitoring (`safety.py`)** — flags telemetry outside safe operating limits (over/under-temperature, over/under-voltage, over-current), with configurable thresholds per asset
- **Synthetic data generator (`data_generator.py`)** — produces a realistic charge/discharge telemetry stream with injected anomalies, so the pipeline can be exercised end-to-end without a live data feed

## Why I built it
Battery performance and safety evaluation sits at the intersection of data engineering and domain-specific analytics — exactly the kind of problem where a clean data model and correct incremental processing matter as much as the underlying formulas. This project also directly reuses patterns from my other backend/data work: incremental state updates instead of full recomputation, dataclasses for typed domain models, and explicit input validation.

## Tech stack
Python, pytest

## Project structure
```
src/bess_analytics/
  digital_twin.py       # BatteryDigitalTwin — the core stateful model
  performance.py        # SoH, round-trip efficiency, capacity fade projection
  safety.py             # Safe operating envelope checks + summary reporting
  data_generator.py     # Synthetic telemetry stream generator
tests/
  test_digital_twin.py
  test_performance.py
  test_safety.py
run_analysis.py          # CLI entry point — runs the full pipeline end to end
```

## Running it
```bash
pip install -r requirements.txt
python run_analysis.py       # runs the full pipeline on synthetic telemetry
python -m pytest tests/ -v   # runs the test suite (20 tests)
```

## Example output
```
=== Performance Report ===
  asset_id: BESS-MUC-001
  cycle_count: 45
  current_soh_pct: 97.75
  fade_rate_per_cycle_pct: 0.05
  projected_cycles_to_eol: 355.0

=== Safety Report ===
  total_readings: 2000
  unsafe_readings: 48
  flag_counts: {'over_temperature': 16, 'under_voltage': 32, ...}
```

## Notes
Degradation is modeled with a fixed per-cycle capacity loss for simplicity; a production system would fit this from an electrochemical or empirical aging model instead. Telemetry is synthetic (see `data_generator.py`) — this project is a data-pipeline and analytics exercise, not a claim of access to real BESS operational data.
