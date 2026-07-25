import pytest
from src.bess_analytics.performance import (
    round_trip_efficiency,
    state_of_health,
    capacity_fade_rate,
)


def test_round_trip_efficiency_normal_case():
    assert round_trip_efficiency(100, 92) == pytest.approx(0.92)


def test_round_trip_efficiency_caps_at_one():
    # More energy out than in is non-physical for a real cycle;
    # the function should not report >100% efficiency.
    assert round_trip_efficiency(100, 105) == 1.0


def test_round_trip_efficiency_rejects_invalid_input():
    with pytest.raises(ValueError):
        round_trip_efficiency(0, 50)
    with pytest.raises(ValueError):
        round_trip_efficiency(100, -5)


def test_state_of_health_full_capacity():
    assert state_of_health(100, 100) == 100.0


def test_state_of_health_degraded():
    assert state_of_health(85, 100) == 85.0


def test_state_of_health_rejects_invalid_input():
    with pytest.raises(ValueError):
        state_of_health(50, 0)
    with pytest.raises(ValueError):
        state_of_health(-1, 100)


def test_capacity_fade_rate_detects_degradation():
    soh_history = [100.0, 99.0, 98.0, 97.0]
    result = capacity_fade_rate(soh_history)
    assert result.fade_rate_per_cycle_pct == pytest.approx(1.0, abs=0.01)
    assert result.projected_cycles_to_eol is not None
    assert result.projected_cycles_to_eol > 0


def test_capacity_fade_rate_no_degradation_returns_none_projection():
    soh_history = [100.0, 100.0, 100.0]
    result = capacity_fade_rate(soh_history)
    assert result.projected_cycles_to_eol is None


def test_capacity_fade_rate_requires_at_least_two_points():
    with pytest.raises(ValueError):
        capacity_fade_rate([100.0])
