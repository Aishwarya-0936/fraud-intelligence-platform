from app.vectorstore.qdrant_client import client, embedder, COLLECTION_NAME


def retrieve_similar_cases(transaction: dict, signals: list, top_k: int = 3) -> list:
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