from datetime import datetime
from app.agents.state import FraudAnalysisState


def check_geographic_impossibility(profile: dict, current_location: str) -> bool:
    if not profile.get("last_location") or not profile.get("last_transaction_time"):
        return False
    if profile["last_location"] == current_location:
        return False

    known_city_regions = {
        "Chennai": "India", "Mumbai": "India", "Delhi": "India",
        "Bangalore": "India", "Kolkata": "India", "Hyderabad": "India",
        "London": "UK", "Manchester": "UK",
        "New York": "USA", "Los Angeles": "USA", "Chicago": "USA",
        "Moscow": "Russia", "Lagos": "Nigeria",
        "Dubai": "UAE", "Singapore": "Singapore"
    }

    last_region = known_city_regions.get(profile["last_location"])
    current_region = known_city_regions.get(current_location)

    if last_region and current_region and last_region != current_region:
        try:
            last_time = datetime.fromisoformat(profile["last_transaction_time"])
            now = datetime.utcnow()
            minutes_elapsed = (now - last_time).total_seconds() / 60
            if minutes_elapsed < 120:
                return True
        except Exception:
            pass
    return False


async def behavioral_profiler_node(state: FraudAnalysisState) -> FraudAnalysisState:
    transaction = state["transaction"]
    profile = state["user_profile"]

    device_id = transaction.get("device_id")
    location = transaction.get("location")
    destination_account = transaction.get("destination_account")
    merchant_category = transaction.get("merchant_category")
    hour = datetime.utcnow().hour

    signals = []
    score = 0

    if device_id and profile["known_devices"] and device_id not in profile["known_devices"]:
        signals.append("new_device")
        score += 25

    if location and profile["known_locations"] and location not in profile["known_locations"]:
        signals.append("new_location")
        score += 20

    if hour < 6:
        signals.append("unusual_hour")
        score += 15

    if location and check_geographic_impossibility(profile, location):
        signals.append("geographic_impossibility")
        score += 50

    if destination_account and profile["known_destinations"] and destination_account not in profile["known_destinations"]:
        signals.append("new_destination_account")
        score += 20

    if merchant_category in ("crypto", "gambling"):
        signals.append("high_risk_merchant_category")
        score += 25

    if profile.get("failed_logins", 0) >= 3:
        signals.append("credential_stuffing_risk")
        score += 40

    state["behavioral_signals"] = signals
    state["behavioral_score"] = score
    return {"behavioral_signals": signals, "behavioral_score": score}