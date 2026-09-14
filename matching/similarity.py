import math


def cosine_similarity(
    embedding_a: list[float],
    embedding_b: list[float],
) -> float:
    """Calculate cosine similarity between two embedding vectors."""

    if not embedding_a or not embedding_b:
        raise ValueError("Embeddings cannot be empty.")

    if len(embedding_a) != len(embedding_b):
        raise ValueError("Embeddings must have the same dimensions.")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(embedding_a, embedding_b)
    )

    magnitude_a = math.sqrt(sum(value**2 for value in embedding_a))
    magnitude_b = math.sqrt(sum(value**2 for value in embedding_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        raise ValueError("Embeddings cannot have zero magnitude.")

    return dot_product / (magnitude_a * magnitude_b)