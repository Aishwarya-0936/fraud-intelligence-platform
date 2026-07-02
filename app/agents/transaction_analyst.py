from app.agents.state import FraudAnalysisState


def calculate_velocity(profile: dict) -> int:
    return len(profile.get("recent_transactions", []))


async def transaction_analyst_node(state: FraudAnalysisState) -> FraudAnalysisState:
    transaction = state["transaction"]
    profile = state["user_profile"]

    amount = float(transaction["amount"])
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

    if profile["transaction_count"] == 0:
        signals.append("first_transaction")
        score += 10

    state["amount_signals"] = signals
    state["amount_score"] = score
    return state