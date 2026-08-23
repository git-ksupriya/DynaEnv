import os
import numpy as np
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


ENV_PATH = os.path.join(
    os.path.dirname(__file__),
    ".env"
)

load_dotenv(ENV_PATH)


HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN was not found. "
        "Make sure backend/.env contains HF_TOKEN."
    )


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

client = InferenceClient(
    api_key=HF_TOKEN
)

def get_embedding(text: str) -> list[float]:
    embedding = np.asarray(
        client.feature_extraction(
            text,
            model=MODEL_NAME,
        ),
        dtype=np.float32
    )

    norm = np.linalg.norm(embedding)

    if norm == 0:
        return embedding.tolist()

    embedding = embedding / norm

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
