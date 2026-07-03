import random

LOCATIONS = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Kolkata", "Hyderabad",
             "London", "Manchester", "New York", "Los Angeles", "Chicago",
             "Moscow", "Lagos", "Dubai", "Singapore"]

MERCHANT_CATEGORIES = ["crypto", "gambling", "electronics", "travel", "grocery",
                        "fuel", "jewellery", "utilities", "online_retail"]

PATTERNS = [
    ("geographic_impossibility", "a transaction from {loc2} was recorded only {mins} minutes after a login from {loc1}, transferring funds to {dest}"),
    ("card_testing_pattern", "a series of small purchases under {small_amt} rupees at unrelated merchants within minutes, followed by a larger charge of {amount} rupees"),
    ("structuring_pattern", "{count} transfers of roughly {amount} rupees each were made in short succession, just under common reporting thresholds"),
    ("money_mule_pattern", "an incoming deposit of {amount} rupees was followed within minutes by an outgoing transfer of similar size to {dest}"),
    ("first_transaction", "a first-time transaction of {amount} rupees to a {merchant} merchant was made from a brand new device with no prior account history"),
    ("credential_stuffing_risk", "{count} failed login attempts were followed by a successful login and an immediate transfer of {amount} rupees to {dest}"),
    ("unusual_hour", "a transfer of {amount} rupees was initiated at {hour} local time, well outside the user's typical activity window"),
    ("amount_spike", "a transaction of {amount} rupees was roughly {multiplier}x the user's average transaction size, made to a {merchant} merchant"),
    ("new_device", "a transaction was made from a newly registered device, with amount and pattern otherwise consistent with the user's normal history"),
    ("new_destination_account", "funds were transferred to {dest}, an account with no prior transaction history linked to this user"),
]

OUTCOMES_BY_PATTERN_RISK = {
    "confirmed_fraud": 0.7,   # 70% of generated cases are confirmed fraud
    "false_positive": 0.3,    # 30% are false positives (legitimate explanations)
}

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
        pattern_key, template = random.choice(PATTERNS)
        loc1, loc2 = random.sample(LOCATIONS, 2)
        merchant = random.choice(MERCHANT_CATEGORIES)
        amount = random.randint(500, 300000)
        small_amt = random.randint(100, 500)
        mins = random.randint(2, 90)
        hour = random.choice(["1 AM", "2 AM", "3 AM", "4 AM", "11 PM"])
        count = random.randint(2, 6)
        multiplier = random.randint(3, 8)
        dest = f"account ending in {random.randint(1000,9999)}"

        description = template.format(
            loc1=loc1, loc2=loc2, merchant=merchant, amount=amount,
            small_amt=small_amt, mins=mins, hour=hour, count=count,
            multiplier=multiplier, dest=dest
        )

        is_fraud = random.random() < OUTCOMES_BY_PATTERN_RISK["confirmed_fraud"]
        if is_fraud:
            outcome = "confirmed_fraud"
            full_description = f"A case where {description}."
        else:
            outcome = "false_positive"
            explanation = random.choice(FALSE_POSITIVE_EXPLANATIONS)
            full_description = f"A case where {description}, {explanation}."

        cases.append({
            "case_id": f"case_{i+1:05d}",
            "description": full_description,
            "pattern": pattern_key,
            "outcome": outcome,
        })

    return cases


FRAUD_CASES = generate_fraud_cases(n=3000)