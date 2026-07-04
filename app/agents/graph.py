from langgraph.graph import StateGraph, END
from app.agents.state import FraudAnalysisState
from app.agents.transaction_analyst import transaction_analyst_node
from app.agents.behavioral_profiler import behavioral_profiler_node
from app.agents.pattern_detector import pattern_detector_node
from app.agents.case_retriever import case_retriever_node
from app.agents.graph_pattern_analyzer import graph_pattern_analyzer_node
from app.agents.supervisor import supervisor_node


def build_fraud_graph():
    workflow = StateGraph(FraudAnalysisState)

    workflow.add_node("transaction_analyst", transaction_analyst_node)
    workflow.add_node("behavioral_profiler", behavioral_profiler_node)
    workflow.add_node("pattern_detector", pattern_detector_node)
    workflow.add_node("case_retriever", case_retriever_node)
    workflow.add_node("graph_pattern_analyzer", graph_pattern_analyzer_node)
    workflow.add_node("supervisor", supervisor_node)

    workflow.set_entry_point("transaction_analyst")
    workflow.add_edge("transaction_analyst", "behavioral_profiler")
    workflow.add_edge("behavioral_profiler", "pattern_detector")

    # Both retrieval paths run after signals are known, in parallel
    workflow.add_edge("pattern_detector", "case_retriever")
    workflow.add_edge("pattern_detector", "graph_pattern_analyzer")

    # Supervisor waits for both to finish before running
    workflow.add_edge("case_retriever", "supervisor")
    workflow.add_edge("graph_pattern_analyzer", "supervisor")

    workflow.add_edge("supervisor", END)

    return workflow.compile()


fraud_graph = build_fraud_graph()


async def run_fraud_analysis(transaction: dict, user_profile: dict) -> dict:
    initial_state: FraudAnalysisState = {
        "transaction": transaction,
        "user_profile": user_profile,
        "amount_signals": [],
        "amount_score": 0,
        "behavioral_signals": [],
        "behavioral_score": 0,
        "pattern_signals": [],
        "pattern_score": 0,
        "similar_cases": [],
        "related_patterns": [],
        "all_signals": [],
        "total_score": 0,
        "risk_level": "LOW",
        "summary": None,
    }
    final_state = await fraud_graph.ainvoke(initial_state)
    return final_state