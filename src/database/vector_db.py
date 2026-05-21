from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.config import settings


class VectorDB:
    def __init__(self):
        # This client automatically handles local memory AND your live Qdrant Cloud cluster
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.collection_name = settings.COLLECTION_NAME
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Creates the collection in Qdrant if it doesn't exist yet."""
        # Check if the collection already exists
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            # 1536 dimensions as a safe default for standard embeddings
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE
                )
            )

    def search_similar_chunks(self, query_text: str, limit: int = 3) -> list[dict]:
        """
        Placeholder for searching Qdrant.
        We will pass our query text here to get the most relevant document matches.
        """
        # For now, we return an empty list until we build the embedding pipeline
        return []