import pytest

from matching.similarity import cosine_similarity


def test_identical_vectors_have_similarity_one() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)


def test_orthogonal_vectors_have_similarity_zero() -> None:
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_opposite_vectors_have_similarity_negative_one() -> None:
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)


def test_different_dimensions_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="same dimensions",
    ):
        cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])


def test_empty_embeddings_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        cosine_similarity([], [1.0])


def test_zero_magnitude_embeddings_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="zero magnitude",
    ):
        cosine_similarity([0.0, 0.0], [1.0, 0.0])