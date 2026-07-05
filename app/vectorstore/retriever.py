import asyncio
import logging
from app.vectorstore.qdrant_client import client, embedder, COLLECTION_NAME

logger = logging.getLogger("fraud_retriever")

QDRANT_TIMEOUT_SECONDS = 3


def _blocking_retrieve(transaction: dict, signals: list, top_k: int) -> list:
    query_text = (
        f"Transaction of {transaction.get('amount')} rupees "
        f"to a {transaction.get('merchant_category', 'unknown')} merchant, "
        f"signals detected: {', '.join(signals) if signals else 'none'}."
    )

    query_vector = list(embedder.embed([query_text]))[0].tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points

    return [
        {
            "case_id": r.payload["case_id"],
            "description": r.payload["description"],
            "pattern": r.payload["pattern"],
            "outcome": r.payload["outcome"],
            "similarity_score": round(r.score, 3),
        }
        for r in results
    ]


async def retrieve_similar_cases(transaction: dict, signals: list, top_k: int = 3) -> list:
    loop = asyncio.get_event_loop()
    try:
        results = await asyncio.wait_for(
            loop.run_in_executor(None, _blocking_retrieve, transaction, signals, top_k),
            timeout=QDRANT_TIMEOUT_SECONDS
        )
        return results
    except (asyncio.TimeoutError, Exception) as e:
        # Qdrant is slow/down — degrade gracefully. The fraud score still stands on its
        # own signals; we just lose the "similar historical cases" context this one time.
        logger.warning(f"[degraded mode] Qdrant retrieval failed or timed out: {e}")
        return []