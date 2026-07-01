from app.db import redis_client
import json
from datetime import datetime

async def get_user_profile(user_id: str) -> dict:
    profile = await redis_client.get(f"user_profile:{user_id}")
    if profile:
        return json.loads(profile)
    return {
        "avg_amount": 0,
        "transaction_count": 0,
        "known_devices": [],
        "known_locations": [],
        "known_destinations": [],
        "known_merchant_categories": [],
        "failed_logins": 0,
        "account_age_days": 0,
        "recent_transactions": [],
        "last_location": None,
        "last_transaction_time": None
    }

async def update_user_profile(user_id: str, transaction: dict, profile: dict):
    count = profile["transaction_count"]
    avg = profile["avg_amount"]
    new_avg = ((avg * count) + float(transaction["amount"])) / (count + 1)
    profile["avg_amount"] = round(new_avg, 2)
    profile["transaction_count"] = count + 1

    if transaction.get("device_id") and transaction["device_id"] not in profile["known_devices"]:
        profile["known_devices"].append(transaction["device_id"])

    if transaction.get("location") and transaction["location"] not in profile["known_locations"]:
        profile["known_locations"].append(transaction["location"])

    if transaction.get("destination_account") and transaction["destination_account"] not in profile["known_destinations"]:
        profile["known_destinations"].append(transaction["destination_account"])

    if transaction.get("merchant_category") and transaction["merchant_category"] not in profile["known_merchant_categories"]:
        profile["known_merchant_categories"].append(transaction["merchant_category"])

    profile["last_location"] = transaction.get("location")
    profile["last_transaction_time"] = transaction.get("timestamp")

    profile["recent_transactions"].append({
        "amount": float(transaction["amount"]),
        "timestamp": transaction["timestamp"],
        "device_id": transaction.get("device_id"),
        "location": transaction.get("location"),
        "destination_account": transaction.get("destination_account"),
        "merchant_category": transaction.get("merchant_category"),
        "transaction_type": transaction.get("transaction_type")
    })
    profile["recent_transactions"] = profile["recent_transactions"][-20:]

    await redis_client.setex(
        f"user_profile:{user_id}",
        86400,
        json.dumps(profile)
    )
    return profile

def calculate_velocity(profile: dict) -> int:
    return len(profile.get("recent_transactions", []))

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
        except:
            pass
    return False

def check_structuring(profile: dict, amount: float) -> bool:
    recent = profile.get("recent_transactions", [])
    if len(recent) < 2:
        return False
    structuring_count = sum(
        1 for t in recent[-5:]
        if 40000 <= float(t["amount"]) <= 99000
    )
    return structuring_count >= 2 and 40000 <= amount <= 99000

def check_card_testing(profile: dict) -> bool:
    recent = profile.get("recent_transactions", [])
    if len(recent) < 3:
        return False
    recent_amounts = [float(t["amount"]) for t in recent[-5:]]
    small_transactions = [a for a in recent_amounts if a < 500]
    return len(small_transactions) >= 3

def check_money_mule(transaction: dict, profile: dict) -> bool:
    if transaction.get("transaction_type") != "transfer":
        return False
    if not transaction.get("destination_account"):
        return False
    recent = profile.get("recent_transactions", [])
    if not recent:
        return False
    last = recent[-1]
    if last.get("transaction_type") in ["credit", "deposit"]:
        if float(last["amount"]) > 50000 and float(transaction["amount"]) > 30000:
            return True
    return False

async def score_transaction(transaction: dict) -> tuple:
    user_id = transaction["user_id"]
    amount = float(transaction["amount"])
    device_id = transaction.get("device_id")
    location = transaction.get("location")
    merchant_category = transaction.get("merchant_category")
    destination_account = transaction.get("destination_account")
    hour = datetime.utcnow().hour

    profile = await get_user_profile(user_id)
    signals = []
    score = 0

    if profile["avg_amount"] > 0 and amount > profile["avg_amount"] * 3:
        signals.append("amount_spike")
        score += 30

    if amount > 100000:
        signals.append("high_value_transfer")
        score += 20

    velocity = calculate_velocity(profile)
    if velocity >= 4:
        signals.append("rapid_succession")
        score += 35

    if device_id and profile["known_devices"] and device_id not in profile["known_devices"]:
        signals.append("new_device")
        score += 25

    if location and profile["known_locations"] and location not in profile["known_locations"]:
        signals.append("new_location")
        score += 20

    if hour < 6:
        signals.append("unusual_hour")
        score += 15

    if profile["transaction_count"] == 0:
        signals.append("first_transaction")
        score += 10

    if location and check_geographic_impossibility(profile, location):
        signals.append("geographic_impossibility")
        score += 50

    if check_structuring(profile, amount):
        signals.append("structuring_pattern")
        score += 40

    if check_card_testing(profile):
        signals.append("card_testing_pattern")
        score += 40

    if check_money_mule(transaction, profile):
        signals.append("money_mule_pattern")
        score += 45

    if profile.get("failed_logins", 0) >= 3:
        signals.append("credential_stuffing_risk")
        score += 40

    if destination_account and profile["known_destinations"] and destination_account not in profile["known_destinations"]:
        signals.append("new_destination_account")
        score += 20

    if merchant_category in ("crypto", "gambling"):
        signals.append("high_risk_merchant_category")
        score += 25

    await update_user_profile(user_id, transaction, profile)

    return score, signals

def get_risk_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    else:
        return "LOW"

async def update_failed_logins(user_id: str):
    profile = await get_user_profile(user_id)
    profile["failed_logins"] = profile.get("failed_logins", 0) + 1
    await redis_client.setex(
        f"user_profile:{user_id}",
        86400,
        json.dumps(profile)
    )

async def reset_failed_logins(user_id: str):
    profile = await get_user_profile(user_id)
    profile["failed_logins"] = 0
    await redis_client.setex(
        f"user_profile:{user_id}",
        86400,
        json.dumps(profile)
    )