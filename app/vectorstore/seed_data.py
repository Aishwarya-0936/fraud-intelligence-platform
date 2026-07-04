import random

LOCATIONS = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Kolkata", "Hyderabad",
             "London", "Manchester", "New York", "Los Angeles", "Chicago",
             "Moscow", "Lagos", "Dubai", "Singapore"]

MERCHANT_CATEGORIES = ["crypto", "gambling", "electronics", "travel", "grocery",
                        "fuel", "jewellery", "utilities", "online_retail"]

PATTERN_PHRASES = {
    "geographic_impossibility": "a transaction from {loc2} was recorded only {mins} minutes after a login from {loc1}",
    "card_testing_pattern": "a series of small purchases under {small_amt} rupees at unrelated merchants within minutes",
    "structuring_pattern": "{count} transfers of roughly {amount} rupees each were made in short succession, just under common reporting thresholds",
    "money_mule_pattern": "an incoming deposit of {amount} rupees was followed within minutes by an outgoing transfer of similar size to {dest}",
    "first_transaction": "a first-time transaction of {amount} rupees was made from a brand new device with no prior account history",
    "credential_stuffing_risk": "{count} failed login attempts were followed by a successful login and an immediate transfer",
    "unusual_hour": "the transfer was initiated at {hour} local time, well outside the user's typical activity window",
    "amount_spike": "the transaction of {amount} rupees was roughly {multiplier}x the user's average transaction size",
    "new_device": "the transaction was made from a newly registered device",
    "new_destination_account": "funds were transferred to {dest}, an account with no prior transaction history linked to this user",
    "high_value_transfer": "the transfer exceeded 100000 rupees",
    "high_risk_merchant_category": "the merchant category was flagged as {merchant}, a high risk category",
}

# Realistic co-occurrence groupings — patterns that plausibly appear together
PATTERN_COMBOS = [
    ["geographic_impossibility", "new_device", "high_risk_merchant_category"],
    ["geographic_impossibility", "new_destination_account"],
    ["card_testing_pattern", "amount_spike"],
    ["structuring_pattern", "rapid_succession"] if False else ["structuring_pattern", "high_value_transfer"],
    ["money_mule_pattern", "new_destination_account"],
    ["first_transaction", "high_value_transfer", "high_risk_merchant_category"],
    ["first_transaction", "new_device"],
    ["credential_stuffing_risk", "high_value_transfer"],
    ["credential_stuffing_risk", "new_device", "new_destination_account"],
    ["unusual_hour", "new_device", "high_value_transfer"],
    ["amount_spike", "unusual_hour", "high_risk_merchant_category"],
    ["new_destination_account", "money_mule_pattern"],
    ["new_destination_account", "credential_stuffing_risk"],
    ["new_device"],
    ["unusual_hour"],
    ["amount_spike"],
    ["high_risk_merchant_category"],
]

FALSE_POSITIVE_EXPLANATIONS = [
    "but was later confirmed legitimate after the user explained they were traveling internationally",
    "but was confirmed legitimate as a planned large purchase, verified via follow-up call",
    "but was confirmed legitimate after the user reported recently upgrading their device",
    "but was confirmed legitimate as the user regularly transacts during those hours due to work schedule",
    "but was confirmed legitimate after verifying it as a one-time transfer for a family emergency",
]


def generate_fraud_cases(n: int = 3000, seed: int = 42):
    random.seed(seed)
    cases = []

    for i in range(n):
        combo = random.choice(PATTERN_COMBOS)
        loc1, loc2 = random.sample(LOCATIONS, 2)
        merchant = random.choice(MERCHANT_CATEGORIES)
        amount = random.randint(500, 300000)
        small_amt = random.randint(100, 500)
        mins = random.randint(2, 90)
        hour = random.choice(["1 AM", "2 AM", "3 AM", "4 AM", "11 PM"])
        count = random.randint(2, 6)
        multiplier = random.randint(3, 8)
        dest = f"account ending in {random.randint(1000,9999)}"

        fill = dict(loc1=loc1, loc2=loc2, merchant=merchant, amount=amount,
                    small_amt=small_amt, mins=mins, hour=hour, count=count,
                    multiplier=multiplier, dest=dest)

        phrases = [PATTERN_PHRASES[p].format(**fill) for p in combo]
        combined_text = "; ".join(phrases)

        is_fraud = random.random() < 0.7
        if is_fraud:
            outcome = "confirmed_fraud"
            full_description = f"A case where {combined_text}."
        else:
            outcome = "false_positive"
            explanation = random.choice(FALSE_POSITIVE_EXPLANATIONS)
            full_description = f"A case where {combined_text}, {explanation}."

        cases.append({
            "case_id": f"case_{i+1:05d}",
            "description": full_description,
            "pattern": " + ".join(combo),
            "outcome": outcome,
        })

    return cases


FRAUD_CASES = generate_fraud_cases(n=3000)