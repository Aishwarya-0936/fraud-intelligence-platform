from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from fastembed import TextEmbedding
import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "fraud_cases"
VECTOR_SIZE = 384  # matches the default fastembed model's output size

client = QdrantClient(url=QDRANT_URL)
embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")


def ensure_collection():
    collections = client.get_collections().collections
    existing_names = [c.name for c in collections]
    if COLLECTION_NAME not in existing_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def embed_text(text: str) -> list:
    embeddings = list(embedder.embed([text]))
    return embeddings[0].tolist()