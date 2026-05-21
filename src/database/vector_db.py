from qdrant_client import QdrantClient
from qdrant_client.http import models
from google import genai
from src.config import settings
import time

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
            # gemini-embedding-001 generates 3,072 dimensions.
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=3072,
                    distance=models.Distance.COSINE
                )
            )

    def _get_embedding(self, text: str) -> list[float]:
        """Converts a snippet of text into a 3072-dimensional float vector using Gemini."""
        response = self.gemini_client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return response.embeddings[0].values


    def save_chunks(self, filename: str, chunks: list[str]) -> None:
        """
        Converts text chunks into vectors and batch-upserts them into Qdrant.
        Introduces throttling to prevent hitting Gemini API 429 rate limits.
        """
        points = []
        total_chunks = len(chunks)

        print(f"Starting vector generation for {total_chunks} chunks...")

        for idx, chunk in enumerate(chunks):
            retry_attempts = 3
            vector = None

            for attempt in range(retry_attempts):
                try:
                    vector = self._get_embedding(chunk)
                    break  # Success: break out of the retry loop
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        # Calculate an increasing backoff wait time (e.g., 2s, 4s, 8s)
                        wait_time = (attempt + 1) * 2
                        print(f"Rate limit hit at chunk {idx + 1}/{total_chunks}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        # Re-raise any non-rate-limit unexpected exceptions
                        raise e

            # Guard clause if all retries failed to return a vector
            if vector is None:
                print(f"Failed to embed chunk {idx} after multiple attempts due to rate limits.")
                continue

            # Build the metadata payload for Qdrant storage
            payload = {
                "source_file": filename,
                "chunk_index": idx,
                "text": chunk
            }

            # Use a deterministic hash to prevent duplicate points across runs
            point_id = hash(f"{filename}_{idx}") & 0xFFFFFFFF

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

            # Introduce a short defensive pause between requests.
            # This keeps our Requests Per Minute safely under the free tier threshold.
            time.sleep(1.2)

        # Batch upload everything into Qdrant once all vectors are processed
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Successfully stored {len(points)} chunks from '{filename}' in Qdrant.")

    def search_similar_chunks(self, query: str, limit: int = 3) -> list[dict]:
        """Converts a user question into a vector and pulls the top N most relevant chunks."""
        query_vector = self._get_embedding(query)

        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )

        # Return only the payload dictionary which contains the raw text and source filename
        return [point.payload for point in search_results.points if point.payload is not None]