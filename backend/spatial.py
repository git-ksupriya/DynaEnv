import hashlib
import math


BOARD_WIDTH = 100
BOARD_HEIGHT = 100

MESSAGE_WIDTH = 12
MESSAGE_HEIGHT = 8

MIN_DISTANCE = 10


def get_semantic_position(text: str) -> tuple[float, float]:
    """
    Temporary semantic position.

    This represents where the message WOULD LIKE to be.
    It is not necessarily its final position.
    """

    text = text.lower()

    if any(word in text for word in [
        "database",
        "sql",
        "postgres",
        "schema",
        "table",
    ]):
        return (25, 30)

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

    return (50, 50)


def is_position_free(
    x: float,
    y: float,
    existing_positions: list[dict],
) -> bool:

    for position in existing_positions:

        distance = math.sqrt(
            (x - position["x"]) ** 2
            + (y - position["y"]) ** 2
        )

        if distance < MIN_DISTANCE:
            return False

    return True


def find_free_position(
    preferred_position: tuple[float, float],
    existing_positions: list[dict],
) -> dict[str, float]:

    preferred_x, preferred_y = preferred_position

    # First try the preferred position.
    if is_position_free(
        preferred_x,
        preferred_y,
        existing_positions,
    ):
        return {
            "x": preferred_x,
            "y": preferred_y,
        }

    # Search around the preferred position.
    for radius in range(5, 50, 5):

        for angle in range(0, 360, 30):

            radians = math.radians(angle)

            x = preferred_x + radius * math.cos(radians)
            y = preferred_y + radius * math.sin(radians)

            # Keep message inside board.
            if not (5 <= x <= 95 and 5 <= y <= 95):
                continue

            if is_position_free(
                x,
                y,
                existing_positions,
            ):
                return {
                    "x": x,
                    "y": y,
                }

    # Fallback
    return {
        "x": preferred_x,
        "y": preferred_y,
    }