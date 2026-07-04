from mcp.server.fastmcp import FastMCP
from app.vectorstore.retriever import retrieve_similar_cases
from app.graphrag.pattern_graph import get_related_patterns

mcp = FastMCP("fraud-intelligence-tools")


@mcp.tool()
def retrieve_similar_fraud_cases(amount: float, merchant_category: str, signals: str) -> list:
    """
    Retrieve historically similar fraud cases from the vector store.

    Args:
        amount: Transaction amount
        merchant_category: Merchant category (e.g. crypto, gambling, grocery)
        signals: Comma-separated list of detected fraud signals
    """
    transaction = {"amount": amount, "merchant_category": merchant_category}
    signal_list = [s.strip() for s in signals.split(",") if s.strip()]
    return retrieve_similar_cases(transaction, signal_list, top_k=3)


@mcp.tool()
def get_related_fraud_patterns(signals: str) -> list:
    """
    Given a comma-separated list of fraud signals, return related signals
    that historically co-occur, along with their historical fraud rate.

    Args:
        signals: Comma-separated list of detected fraud signals
    """
    signal_list = [s.strip() for s in signals.split(",") if s.strip()]
    return get_related_patterns(signal_list, top_k=5)


if __name__ == "__main__":
    mcp.run(transport="stdio")