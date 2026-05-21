import pytest

from src.services.document_service import chunk_text


def test_chunk_text_splits_text_with_overlap():
    chunks = chunk_text("abcdefghij", chunk_size=5, overlap=2)

    assert chunks == ["abcde", "defgh", "ghij", "j"]


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=5, overlap=5)
