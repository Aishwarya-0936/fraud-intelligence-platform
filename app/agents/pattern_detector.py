from app.agents.state import FraudAnalysisState


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


async def pattern_detector_node(state: FraudAnalysisState) -> FraudAnalysisState:
    transaction = state["transaction"]
    profile = state["user_profile"]
    amount = float(transaction["amount"])

    signals = []
    score = 0

    if check_structuring(profile, amount):
        signals.append("structuring_pattern")
        score += 40

    if check_card_testing(profile):
        signals.append("card_testing_pattern")
        score += 40

    if check_money_mule(transaction, profile):
        signals.append("money_mule_pattern")
        score += 45

    state["pattern_signals"] = signals
    state["pattern_score"] = score
    return state