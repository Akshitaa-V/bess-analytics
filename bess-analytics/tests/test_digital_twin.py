from src.bess_analytics.digital_twin import BatteryDigitalTwin, TelemetryReading


def test_twin_starts_at_full_health():
    twin = BatteryDigitalTwin(asset_id="TEST-001", rated_capacity_kwh=100.0)
    assert twin.soh_history == [100.0]
    assert twin.cycle_count == 0


def test_twin_ingest_logs_safety_reading():
    twin = BatteryDigitalTwin(asset_id="TEST-001", rated_capacity_kwh=100.0)
    reading = TelemetryReading(
        timestamp="2026-01-01T00:00:00",
        voltage_v=3.8,
        current_a=30.0,
        temperature_c=25.0,
    )
    result = twin.ingest(reading)
    assert result.is_safe
    assert len(twin.safety_log) == 1


def test_twin_completes_a_cycle_and_degrades_soh():
    twin = BatteryDigitalTwin(asset_id="TEST-001", rated_capacity_kwh=100.0)

    # Simulate a full discharge in one reading to trigger a cycle completion.
    reading = TelemetryReading(
        timestamp="2026-01-01T00:00:00",
        voltage_v=3.5,
        current_a=-30.0,
        temperature_c=25.0,
        energy_discharged_kwh=100.0,
    )
    twin.ingest(reading)

    assert twin.cycle_count == 1
    assert twin.soh_history[-1] < 100.0  # some degradation should have occurred


def test_twin_performance_report_has_expected_keys():
    twin = BatteryDigitalTwin(asset_id="TEST-001", rated_capacity_kwh=100.0)
    reading = TelemetryReading(
        timestamp="2026-01-01T00:00:00",
        voltage_v=3.8,
        current_a=30.0,
        temperature_c=25.0,
    )
    twin.ingest(reading)
    report = twin.performance_report()

    assert report["asset_id"] == "TEST-001"
    assert "cycle_count" in report
    assert "current_soh_pct" in report
    assert "fade_rate_per_cycle_pct" in report
    assert "projected_cycles_to_eol" in report


def test_twin_safety_report_reflects_unsafe_readings():
    twin = BatteryDigitalTwin(asset_id="TEST-001", rated_capacity_kwh=100.0)
    twin.ingest(
        TelemetryReading(
            timestamp="t1", voltage_v=3.8, current_a=30.0, temperature_c=50.0
        )
    )
    report = twin.safety_report()
    assert report["unsafe_readings"] == 1
