from typing import Final


NORTH: Final[int] = 1
EAST: Final[int] = 2
SOUTH: Final[int] = 4
WEST: Final[int] = 8

ALL_WALLS: Final[int] = NORTH | EAST | SOUTH | WEST

DIRECTIONS: Final[tuple[int, int, int, int]] = (NORTH, EAST, SOUTH, WEST)


DIRECTION_OFFSETS: Final[dict[int, tuple[int, int]]] = {
    NORTH: (0, -1), EAST: (1, 0), SOUTH: (0, 1), WEST: (-1, 0)}


OPPOSITE_DIRECTION: Final[dict[int, int]] = {
    NORTH: SOUTH, EAST: WEST, SOUTH: NORTH, WEST: EAST}


DIRECTION_LETTERS: Final[dict[int, str]] = {
    NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}
