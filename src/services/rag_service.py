from google import genai
from src.config import settings
from src.database.vector_db import VectorDB


class RAGService:
    def __init__(self):
        # 1. Initialize the vector database connection to query chunks
        self.vector_db = VectorDB()

        # 2. Initialize the official Google GenAI Client
        self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    def answer_question(self, question: str) -> dict:
        """
        Orchestrates the entire RAG pipeline:
        Vector Search -> Context Assembly -> Gemini Generation -> Sourced Response
        """
        # 1. Fetch the most relevant context chunks from Qdrant
        matched_chunks = self.vector_db.search_similar_chunks(question, limit=3)

        if not matched_chunks:
            return {
                "answer": "I couldn't find any relevant regulatory context in my database. Please upload the matching FINMA or legal PDF documents first.",
                "sources": []
            }

        # 2. Extract and compile unique filenames for transparent sourcing
        sources = list(set(chunk.get("source_file", "Unknown Document") for chunk in matched_chunks))

        # 3. Assemble the raw text snippets into a single context block
        context_text = "\n---\n".join([chunk.get("text", "") for chunk in matched_chunks])

        # 4. Construct a strict, Swiss compliance-focused prompt engineering framework
        system_instruction = (
            "You are an expert Swiss Regulatory and Financial Compliance Advisor.\n"
            "Your task is to answer user questions with absolute precision based ONLY on the verified legal "
            "and regulatory context snippets provided below. Keep your tone professional, authoritative, and direct.\n\n"
            f"--- START SYSTEM CONTEXT ---\n{context_text}\n--- END SYSTEM CONTEXT ---\n\n"
            "CRITICAL RULES:\n"
            "1. Base your answer strictly on the context provided above.\n"
            "2. If the context does not explicitly contain the answer, state honestly: 'I cannot verify this information based on the uploaded compliance documents.' Do not hallucinate or guess.\n"
            "3. Reference specific articles, circular numbers, or clauses if they appear in the text."
        )

        # 5. Call Gemini 2.5 Flash
        try:
            response = self.gemini_client.models.generate_content(
                model=self.model_name,
                contents=question,
                config={"system_instruction": system_instruction}
            )

            return {
                "answer": response.text,
                "sources": sources
            }

        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return {
                "answer": f"An error occurred while communicating with the Gemini engine: {str(e)}",
                "sources": sources
            }