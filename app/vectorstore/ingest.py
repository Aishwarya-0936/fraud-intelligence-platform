from qdrant_client.models import PointStruct
from app.vectorstore.qdrant_client import client, embedder, ensure_collection, COLLECTION_NAME
from app.vectorstore.seed_data import FRAUD_CASES
import uuid

BATCH_SIZE = 100


def ingest_fraud_cases():
    ensure_collection()

    total = len(FRAUD_CASES)
    for start in range(0, total, BATCH_SIZE):
        batch = FRAUD_CASES[start:start + BATCH_SIZE]
        texts = [case["description"] for case in batch]
        vectors = list(embedder.embed(texts))

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector.tolist(),
                payload={
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "pattern": case["pattern"],
                    "outcome": case["outcome"],
                },
            )
            for case, vector in zip(batch, vectors)
        ]

        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Ingested {start + len(batch)} / {total}")

    print("Done.")


if __name__ == "__main__":
    ingest_fraud_cases()