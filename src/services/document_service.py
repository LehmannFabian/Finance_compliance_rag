from src.database.vector_db import VectorDB

# Instantiate the DB connector
vector_db = VectorDB()


def process_regulatory_document(filename: str, pdf_content: bytes) -> int:
    """
    The orchestrator function for document ingestion.
    Extracts text, splits it into chunks, and saves it to Qdrant.
    """
    print(f"Processing started for file: {filename}")

    # 1. Extract raw text
    raw_text = extract_text_from_pdf(pdf_content)
    if not raw_text.strip():
        raise ValueError("The uploaded PDF does not contain any extractable text.")

    # 2. Break into semantic chunks
    chunks = chunk_text(raw_text)
    print(f"Successfully split '{filename}' into {len(chunks)} chunks.")

    # 3. Save directly to Qdrant Vector Database (Connected!)
    vector_db.save_chunks(filename, chunks)

    return len(chunks)