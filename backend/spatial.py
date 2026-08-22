import math
import random


BOARD_WIDTH = 100
BOARD_HEIGHT = 100


def mock_vector(text: str) -> tuple[float, float]:
    """
    Temporary semantic representation.

    This is NOT real NLP.
    It just gives similar text a deterministic
    location in a 2D semantic space.
    """

    text = text.lower()

    if any(word in text for word in [
        "database",
        "sql",
        "postgres",
        "schema",
        "table",
    ]):
        return (20, 30)

    if any(word in text for word in [
        "ai",
        "model",
        "machine",
        "learning",
        "neural",
    ]):
        return (70, 30)

    if any(word in text for word in [
        "football",
        "cricket",
        "match",
        "sport",
    ]):
        return (50, 75)

    return (
        random.uniform(10, 90),
        random.uniform(10, 90),
    )


def get_position(text: str) -> dict[str, float]:
    x, y = mock_vector(text)

    return {
        "x": x,
        "y": y,
    }