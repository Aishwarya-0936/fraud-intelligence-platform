from app.agents.state import FraudAnalysisState
from app.llm import generate_fraud_summary


def get_risk_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    else:
        return "LOW"


async def supervisor_node(state: FraudAnalysisState) -> FraudAnalysisState:
    all_signals = (
        state.get("amount_signals", [])
        + state.get("behavioral_signals", [])
        + state.get("pattern_signals", [])
    )
    total_score = (
        state.get("amount_score", 0)
        + state.get("behavioral_score", 0)
        + state.get("pattern_score", 0)
    )
    risk_level = get_risk_level(total_score)

    summary = await generate_fraud_summary(
        state["transaction"], total_score, risk_level, all_signals, state.get("similar_cases", [])
    )

    state["all_signals"] = all_signals
    state["total_score"] = total_score
    state["risk_level"] = risk_level
    state["summary"] = summary
    return {
        "all_signals": all_signals,
        "total_score": total_score,
        "risk_level": risk_level,
        "summary": summary,
    }