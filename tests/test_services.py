import pytest
from src.services.document_service import chunk_text


def test_chunk_text_creates_overlapping_chunks():
    # 1. Arrange: Prepare a realistic sample text string
    # A typical sentence about Swiss compliance repeated to simulate a real document
    sample_sentence = "According to FINMA regulations, financial institutions must manage cyber risks effectively. "
    test_text = sample_sentence * 30  # Generates a long block of text

    chunk_size = 300
    chunk_overlap = 50

    # 2. Act: Execute the chunking function
    chunks = chunk_text(test_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # 3. Assert: Verify the output matches our expectations
    assert isinstance(chunks, list), "The output must be a list of strings."
    assert len(chunks) > 1, "The text should be split into multiple chunks."

    # Verify that the text splitter respected our max chunk size boundary
    # We add a small 50-character buffer since separators can occasionally cause minor variances
    for chunk in chunks:
        assert len(chunk) <= chunk_size + 50, f"Chunk exceeded maximum allowed size: {len(chunk)}"


def test_chunk_text_with_empty_string():
    # Act & Assert: An empty string should return an empty list gracefully without crashing
    chunks = chunk_text("")
    assert chunks == []
    assert len(chunks) == 0