from app.agents.state import FraudAnalysisState
from app.graphrag.pattern_graph import get_related_patterns


async def graph_pattern_analyzer_node(state: FraudAnalysisState) -> FraudAnalysisState:
    combined_signals = (
        state.get("amount_signals", [])
        + state.get("behavioral_signals", [])
        + state.get("pattern_signals", [])
    )
    related = get_related_patterns(combined_signals, top_k=5)
    state["related_patterns"] = related
    return state