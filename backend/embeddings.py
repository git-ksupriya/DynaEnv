from sentence_transformers import SentenceTransformer
import numpy as np


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def get_embedding(text: str) -> list[float]:
    """
    Convert text into a semantic embedding.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:

    a = np.array(a)
    b = np.array(b)

    return float(np.dot(a, b))


def get_most_similar_and_dissimilar(
    embedding: list[float],
    active_messages: list[dict],
):
    scored = []

    for message in active_messages:

        if "embedding" not in message:
            continue

        similarity = cosine_similarity(
            embedding,
            message["embedding"],
        )

        scored.append(
            (similarity, message)
        )

        print(
            f"{message['text'][:40]!r} "
            f"-> similarity = {similarity:.4f}"
        )

    if not scored:
        return None, None

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    most_similar = scored[0][1]

    if len(scored) >= 2:
        most_dissimilar = scored[-1][1]
    else:
        most_dissimilar = None

    print(
        f"Most similar: {most_similar['text']!r}"
    )

    if most_dissimilar:
        print(
            f"Most dissimilar: "
            f"{most_dissimilar['text']!r}"
        )

    return most_similar, most_dissimilar
