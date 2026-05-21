from qdrant_client import QdrantClient
from qdrant_client.http import models
from google import genai
from src.config import settings


class VectorDB:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

        self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.collection_name = settings.COLLECTION_NAME

        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Creates the Qdrant collection if it doesn't exist yet."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            print(f"Creating vector collection: '{self.collection_name}'...")
            # Google's text-embedding-004 model generates 768 dimensions.
            # Cosine similarity is perfect for mapping semantic text matches.
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=768,
                    distance=models.Distance.COSINE
                )
            )

    def _get_embedding(self, text: str) -> list[float]:
        """Converts a snippet of text into a 768-dimensional float vector using Gemini."""
        response = self.gemini_client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        # Extract the list of floats from the embedding response object
        return response.embeddings[0].values

    def save_chunks(self, filename: str, chunks: list[str]) -> None:
        """Converts text chunks into vectors and batch-upserts them into Qdrant with metadata."""
        points = []

        for idx, chunk in enumerate(chunks):
            # 1. Generate the semantic vector
            vector = self._get_embedding(chunk)

            # 2. Prepare the payload (metadata) so Gemini can read the text context later
            payload = {
                "source_file": filename,
                "chunk_index": idx,
                "text": chunk
            }

            # 3. Create a unique ID for this point using a simple deterministic hash
            point_id = hash(f"{filename}_{idx}") & 0xFFFFFFFF

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

        # 4. Batch upload everything into Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Successfully vectorized and stored {len(points)} chunks from '{filename}' in Qdrant.")

    def search_similar_chunks(self, query: str, limit: int = 3) -> list[dict]:
        """Converts a user question into a vector and pulls the top N most relevant chunks."""
        query_vector = self._get_embedding(query)

        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        # Return only the payload dictionary which contains the raw text and source filename
        return [result.payload for result in search_results]