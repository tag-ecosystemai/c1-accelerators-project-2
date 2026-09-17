import pytest

from matching.embeddings import EmbeddingModel


@pytest.fixture(scope="module")
def embedding_model() -> EmbeddingModel:
    return EmbeddingModel()


def test_encode_returns_384_dimensions(
    embedding_model: EmbeddingModel,
) -> None:
    embedding = embedding_model.encode("Python backend development")

    assert len(embedding) == 384


def test_encode_returns_normalized_embedding(
    embedding_model: EmbeddingModel,
) -> None:
    embedding = embedding_model.encode("Python backend development")

    magnitude = sum(value**2 for value in embedding) ** 0.5

    assert magnitude == pytest.approx(1.0, abs=1e-5)


def test_encode_rejects_empty_text(
    embedding_model: EmbeddingModel,
) -> None:
    with pytest.raises(ValueError, match="Text cannot be empty"):
        embedding_model.encode("")


def test_encode_rejects_whitespace_only_text(
    embedding_model: EmbeddingModel,
) -> None:
    with pytest.raises(ValueError, match="Text cannot be empty"):
        embedding_model.encode("   ")