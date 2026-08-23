import math


BOARD_WIDTH = 100
BOARD_HEIGHT = 100

MIN_WIDTH = 8
MAX_WIDTH = 30

MIN_HEIGHT = 6
MAX_HEIGHT = 18

PADDING = 2


def get_semantic_position(text: str) -> tuple[float, float]:
    """
    Temporary semantic anchor.

    This is the preferred region for the message.
    It is not necessarily the final position.
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


def get_message_size(text: str) -> dict[str, float]:
    """
    Estimate the visual size of a message from its length.
    """

    length = len(text.strip())

    width = 8 + length / 2
    width = max(MIN_WIDTH, min(MAX_WIDTH, width))

    if length <= 20:
        height = MIN_HEIGHT
    elif length <= 50:
        height = 10
    else:
        height = MAX_HEIGHT

    return {
        "width": width,
        "height": height,
    }


def rectangles_overlap(
    a_position: dict,
    a_size: dict,
    b_position: dict,
    b_size: dict,
) -> bool:

    a_left = a_position["x"] - a_size["width"] / 2
    a_right = a_position["x"] + a_size["width"] / 2
    a_top = a_position["y"] - a_size["height"] / 2
    a_bottom = a_position["y"] + a_size["height"] / 2

    b_left = b_position["x"] - b_size["width"] / 2
    b_right = b_position["x"] + b_size["width"] / 2
    b_top = b_position["y"] - b_size["height"] / 2
    b_bottom = b_position["y"] + b_size["height"] / 2

    return not (
        a_right + PADDING < b_left
        or a_left - PADDING > b_right
        or a_bottom + PADDING < b_top
        or a_top - PADDING > b_bottom
    )


def inside_board(
    position: dict,
    size: dict,
) -> bool:

    half_width = size["width"] / 2
    half_height = size["height"] / 2

    return (
        half_width <= position["x"] <= BOARD_WIDTH - half_width
        and
        half_height <= position["y"] <= BOARD_HEIGHT - half_height
    )


def is_position_valid(
    candidate_position: dict,
    candidate_size: dict,
    existing_messages: list[dict],
) -> bool:

    if not inside_board(
        candidate_position,
        candidate_size,
    ):
        return False

    for existing in existing_messages:

        if rectangles_overlap(
            candidate_position,
            candidate_size,
            existing["position"],
            existing["size"],
        ):
            return False

    return True


def find_free_position(
    preferred_position: tuple[float, float],
    size: dict,
    existing_messages: list[dict],
) -> dict | None:

    preferred_x, preferred_y = preferred_position

    candidates = []

    # How far we search from the semantic center.
    MAX_RADIUS = 45

    # Distance between candidate points.
    STEP = 2

    for x_offset in range(
        -MAX_RADIUS,
        MAX_RADIUS + 1,
        STEP,
    ):

        for y_offset in range(
            -MAX_RADIUS,
            MAX_RADIUS + 1,
            STEP,
        ):

            candidate = {
                "x": preferred_x + x_offset,
                "y": preferred_y + y_offset,
            }

            if not is_position_valid(
                candidate,
                size,
                existing_messages,
            ):
                continue

            # Euclidean distance from semantic center.
            distance = math.sqrt(
                x_offset ** 2 +
                y_offset ** 2
            )

            candidates.append(
                (distance, candidate)
            )

    if not candidates:
        return None

    # Closest valid position wins.
    candidates.sort(
        key=lambda item: item[0]
    )

    return candidates[0][1]

def get_semantic_center(
    similar_messages: list[tuple[float, dict]],
) -> tuple[float, float]:

    if not similar_messages:
        return (50, 50)

    total_weight = 0.0
    weighted_x = 0.0
    weighted_y = 0.0

    for similarity, message in similar_messages:

        position = message["position"]

        # Ignore very weak semantic relationships.
        weight = max(similarity, 0.0)

        weighted_x += (
            position["x"] * weight
        )

        weighted_y += (
            position["y"] * weight
        )

        total_weight += weight

    if total_weight == 0:
        return (50, 50)

    return (
        weighted_x / total_weight,
        weighted_y / total_weight,
    )

def get_dynamic_position(
    similar_message: dict | None,
    dissimilar_message: dict | None,
    existing_messages: list[dict],
    size: dict,
) -> dict | None:

    # No existing messages.
    # Start in the center.
    if similar_message is None:

        return find_free_position(
            (50, 50),
            size,
            existing_messages,
        )


    # Position of most similar message.
    sx = similar_message["position"]["x"]
    sy = similar_message["position"]["y"]


    # If there is no dissimilar message,
    # simply prefer the similar message's region.

    if dissimilar_message is None:

        preferred = (
            sx,
            sy,
        )

    else:

        # Position of most dissimilar message.

        dx = dissimilar_message["position"]["x"]
        dy = dissimilar_message["position"]["y"]


        # Vector from dissimilar → similar.

        vx = sx - dx
        vy = sy - dy


        distance = math.sqrt(
            vx ** 2 +
            vy ** 2
        )


        if distance == 0:

            preferred = (
                sx,
                sy,
            )

        else:

            # Continue in the direction
            # away from the dissimilar message.

            PUSH_DISTANCE = 12

            preferred = (
                sx + (vx / distance) * PUSH_DISTANCE,
                sy + (vy / distance) * PUSH_DISTANCE,
            )


    # Now use the rectangle-aware
    # placement algorithm to find the
    # closest valid position.

    return find_free_position(
        preferred,
        size,
        existing_messages,
    )