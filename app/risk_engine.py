from app.db import redis_client
import json
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger("fraud_risk_engine")

REDIS_TIMEOUT_SECONDS = 2

DEFAULT_PROFILE = {
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


async def get_user_profile(user_id: str) -> dict:
    try:
        profile = await asyncio.wait_for(
            redis_client.get(f"user_profile:{user_id}"),
            timeout=REDIS_TIMEOUT_SECONDS
        )
        if profile:
            return json.loads(profile)
        return DEFAULT_PROFILE.copy()
    except (asyncio.TimeoutError, Exception) as e:
        # Redis is down/slow — degrade gracefully instead of failing the whole request.
        # The transaction still gets scored, just without historical context this one time.
        logger.warning(f"[degraded mode] Could not fetch profile for {user_id}: {e}")
        return DEFAULT_PROFILE.copy()


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

    try:
        await asyncio.wait_for(
            redis_client.setex(f"user_profile:{user_id}", 86400, json.dumps(profile)),
            timeout=REDIS_TIMEOUT_SECONDS
        )
    except (asyncio.TimeoutError, Exception) as e:
        # If we can't persist the updated profile, log it but don't fail the request —
        # the transaction was already scored correctly; we just lose this one profile update.
        logger.warning(f"[degraded mode] Could not persist profile for {user_id}: {e}")

    return profile


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
    try:
        await asyncio.wait_for(
            redis_client.setex(f"user_profile:{user_id}", 86400, json.dumps(profile)),
            timeout=REDIS_TIMEOUT_SECONDS
        )
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning(f"[degraded mode] Could not update failed_logins for {user_id}: {e}")


async def reset_failed_logins(user_id: str):
    profile = await get_user_profile(user_id)
    profile["failed_logins"] = 0
    try:
        await asyncio.wait_for(
            redis_client.setex(f"user_profile:{user_id}", 86400, json.dumps(profile)),
            timeout=REDIS_TIMEOUT_SECONDS
        )
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning(f"[degraded mode] Could not reset failed_logins for {user_id}: {e}")