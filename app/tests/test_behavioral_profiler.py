import pytest
from datetime import datetime, timezone, timedelta
from app.agents.behavioral_profiler import check_geographic_impossibility, behavioral_profiler_node


def make_profile(last_location=None, last_transaction_time=None, **overrides):
    profile = {
        "known_devices": [],
        "known_locations": [],
        "known_destinations": [],
        "last_location": last_location,
        "last_transaction_time": last_transaction_time,
        "failed_logins": 0,
    }
    profile.update(overrides)
    return profile


def test_geographic_impossibility_detects_recent_cross_region_transaction():
    """This is the exact bug we hit today — timezone-aware vs naive datetime comparison."""
    recent_time = datetime.now(timezone.utc).isoformat()
    profile = make_profile(last_location="Chennai", last_transaction_time=recent_time)

    result = check_geographic_impossibility(profile, "Moscow")

    assert result is True


def test_geographic_impossibility_false_when_same_location():
    profile = make_profile(last_location="Chennai", last_transaction_time=datetime.now(timezone.utc).isoformat())
    result = check_geographic_impossibility(profile, "Chennai")
    assert result is False


def test_geographic_impossibility_false_when_enough_time_elapsed():
    old_time = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    profile = make_profile(last_location="Chennai", last_transaction_time=old_time)
    result = check_geographic_impossibility(profile, "Moscow")
    assert result is False


def test_geographic_impossibility_false_with_no_history():
    profile = make_profile(last_location=None, last_transaction_time=None)
    result = check_geographic_impossibility(profile, "Moscow")
    assert result is False


@pytest.mark.asyncio
async def test_behavioral_profiler_node_flags_new_device_and_crypto():
    state = {
        "transaction": {
            "device_id": "device_new",
            "location": "Chennai",
            "destination_account": "acc_new",
            "merchant_category": "crypto",
        },
        "user_profile": make_profile(
            known_devices=["device_old"],
            known_locations=["Chennai"],
            known_destinations=["acc_old"],
        ),
    }

    result = await behavioral_profiler_node(state)

    assert "new_device" in result["behavioral_signals"]
    assert "high_risk_merchant_category" in result["behavioral_signals"]
    assert result["behavioral_score"] > 0