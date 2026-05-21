import io
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.database.vector_db import VectorDB

# Instantiate the DB connector singleton
vector_db = VectorDB()


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Takes the raw binary bytes of a PDF file and extracts all readable text.
    """
    # Wrap the raw bytes in an in-memory file stream (avoids writing to disk)
    pdf_file = io.BytesIO(pdf_content)
    reader = PdfReader(pdf_file)
    extracted_text = ""

    # Loop through every page and pull out the raw characters
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            extracted_text += page_text + "\n"

    return extracted_text


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Splits a long string of text into smaller, overlapping chunks.
    The overlap ensures context cut off at boundaries isn't lost.
    """
    # RecursiveCharacterTextSplitter tries to split by paragraphs (\n\n),
    # then sentences (\n), then words ( ) to keep structural meaning together.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    return text_splitter.split_text(text)


def process_regulatory_document(filename: str, pdf_content: bytes) -> int:
    """
    The orchestrator function for document ingestion.
    Extracts text, splits it into chunks, and saves it to Qdrant.
    """
    print(f"Processing started for file: {filename}")

    # 1. Extract raw text from the file stream
    raw_text = extract_text_from_pdf(pdf_content)
    if not raw_text.strip():
        raise ValueError("The uploaded PDF does not contain any extractable text (it might be a scanned image).")

    # 2. Break into semantic chunks
    chunks = chunk_text(raw_text)
    print(f"Successfully split '{filename}' into {len(chunks)} chunks.")

    # 3. Save directly to Qdrant Vector Database (Connected!)
    vector_db.save_chunks(filename, chunks)

    return len(chunks)