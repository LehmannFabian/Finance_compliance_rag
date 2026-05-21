from qdrant_client import QdrantClient

from src.config import settings


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)
