from app.agents.state import FraudAnalysisState
from app.vectorstore.retriever import retrieve_similar_cases


async def case_retriever_node(state: FraudAnalysisState) -> dict:
    combined_signals = (
        state.get("amount_signals", [])
        + state.get("behavioral_signals", [])
        + state.get("pattern_signals", [])
    )
    similar_cases = retrieve_similar_cases(state["transaction"], combined_signals)
    return {"similar_cases": similar_cases}