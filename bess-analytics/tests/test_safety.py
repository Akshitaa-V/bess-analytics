from src.bess_analytics.safety import check_safety, summarize_safety, SafetyFlag, SafetyLimits


def test_normal_reading_has_no_flags():
    reading = check_safety("t1", temperature_c=25.0, voltage_v=3.8, current_a=30.0)
    assert reading.is_safe
    assert reading.flags == []


def test_over_temperature_flagged():
    reading = check_safety("t1", temperature_c=50.0, voltage_v=3.8, current_a=30.0)
    assert SafetyFlag.OVER_TEMPERATURE in reading.flags
    assert not reading.is_safe


def test_under_voltage_flagged():
    reading = check_safety("t1", temperature_c=25.0, voltage_v=2.5, current_a=30.0)
    assert SafetyFlag.UNDER_VOLTAGE in reading.flags


def test_over_current_flagged_for_negative_current_too():
    reading = check_safety("t1", temperature_c=25.0, voltage_v=3.8, current_a=-150.0)
    assert SafetyFlag.OVER_CURRENT in reading.flags


def test_custom_limits_are_respected():
    tight_limits = SafetyLimits(max_temp_c=30.0)
    reading = check_safety("t1", temperature_c=35.0, voltage_v=3.8, current_a=30.0, limits=tight_limits)
    assert SafetyFlag.OVER_TEMPERATURE in reading.flags


def test_summarize_safety_counts_correctly():
    readings = [
        check_safety("t1", 25.0, 3.8, 30.0),
        check_safety("t2", 50.0, 3.8, 30.0),  # over temp
        check_safety("t3", 25.0, 2.5, 30.0),  # under voltage
    ]
    summary = summarize_safety(readings)
    assert summary["total_readings"] == 3
    assert summary["unsafe_readings"] == 2
    assert summary["flag_counts"]["over_temperature"] == 1
    assert summary["flag_counts"]["under_voltage"] == 1
