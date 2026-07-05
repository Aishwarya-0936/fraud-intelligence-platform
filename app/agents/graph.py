import time
import logging
from langgraph.graph import StateGraph, END
from app.agents.state import FraudAnalysisState
from app.agents.transaction_analyst import transaction_analyst_node
from app.agents.behavioral_profiler import behavioral_profiler_node
from app.agents.pattern_detector import pattern_detector_node
from app.agents.case_retriever import case_retriever_node
from app.agents.graph_pattern_analyzer import graph_pattern_analyzer_node
from app.agents.supervisor import supervisor_node

logger = logging.getLogger("fraud_pipeline_timing")

RETRIEVAL_SKIP_THRESHOLD = 30  # below this preliminary score, skip expensive RAG steps


def timed_node(name: str, node_fn):
    async def wrapped(state: FraudAnalysisState) -> dict:
        start = time.perf_counter()
        result = await node_fn(state)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(f"[timing] {name}: {elapsed_ms}ms")
        return result
    return wrapped


def route_after_signals(state: FraudAnalysisState) -> list:
    """
    Decides whether to run the expensive retrieval steps (Qdrant + GraphRAG)
    based on the preliminary score from the fast signal-detection agents.
    Low-scoring transactions skip straight to the supervisor — they won't
    get an LLM summary anyway, so there's no point paying for retrieval.
    """
    preliminary_score = (
        state.get("amount_score", 0)
        + state.get("behavioral_score", 0)
        + state.get("pattern_score", 0)
    )
    if preliminary_score < RETRIEVAL_SKIP_THRESHOLD:
        logger.info(f"[routing] preliminary_score={preliminary_score} < {RETRIEVAL_SKIP_THRESHOLD} — skipping retrieval")
        return ["supervisor"]
    logger.info(f"[routing] preliminary_score={preliminary_score} >= {RETRIEVAL_SKIP_THRESHOLD} — running retrieval")
    return ["case_retriever", "graph_pattern_analyzer"]


def build_fraud_graph():
    workflow = StateGraph(FraudAnalysisState)

    workflow.add_node("transaction_analyst", timed_node("transaction_analyst", transaction_analyst_node))
    workflow.add_node("behavioral_profiler", timed_node("behavioral_profiler", behavioral_profiler_node))
    workflow.add_node("pattern_detector", timed_node("pattern_detector", pattern_detector_node))
    workflow.add_node("case_retriever", timed_node("case_retriever", case_retriever_node))
    workflow.add_node("graph_pattern_analyzer", timed_node("graph_pattern_analyzer", graph_pattern_analyzer_node))
    workflow.add_node("supervisor", timed_node("supervisor", supervisor_node))

    workflow.set_entry_point("transaction_analyst")
    workflow.add_edge("transaction_analyst", "behavioral_profiler")
    workflow.add_edge("behavioral_profiler", "pattern_detector")

    # Conditional fan-out: only pay for retrieval when the transaction looks risky enough to matter
    workflow.add_conditional_edges(
        "pattern_detector",
        route_after_signals,
        ["case_retriever", "graph_pattern_analyzer", "supervisor"]
    )

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

    pipeline_start = time.perf_counter()
    final_state = await fraud_graph.ainvoke(initial_state)
    total_ms = round((time.perf_counter() - pipeline_start) * 1000, 1)
    logger.info(f"[timing] TOTAL pipeline: {total_ms}ms")

    return final_state