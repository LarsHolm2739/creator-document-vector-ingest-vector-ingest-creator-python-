from src.creator_ingest import chunk_document


def test_chunk_document_preserves_order_and_bounds():
    text = "one two three four five"
    assert chunk_document(text, size=2) == ["one two", "three four", "five"]

