"""Create the closed cells used to draw the number 42."""


PATTERN: tuple[str, ...] = (
    "1000111",
    "1000001",
    "1110111",
    "0010100",
    "0010111",
)

PATTERN_CELLS: set[tuple[int, int]] = {
    (x, y)
    for y, row in enumerate(PATTERN)
    for x, value in enumerate(row)
    if value == "1"
}


def create_pattern(
    width: int,
    height: int,
    blocked: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    """Create the 42 pattern inside the maze.

    Args:
        width: Maze width.
        height: Maze height.
        blocked: Cells that cannot be part of the pattern.

    Returns:
        Pattern cells, or an empty set if the pattern cannot fit.
    """
    pattern_width = len(PATTERN[0])
    pattern_height = len(PATTERN)
    if width < pattern_width + 2 or height < pattern_height + 2:
        print("Warning: maze is too small to display the 42 pattern")
        return set()

    if blocked is None:
        blocked = set()
    wanted_left = (width - pattern_width + 1) // 2
    wanted_top = (height - pattern_height) // 2
    positions: list[tuple[int, int]] = [
        (left, top)
        for top in range(1, height - pattern_height)
        for left in range(1, width - pattern_width)
    ]

    def position_priority(pos: tuple[int, int]) -> tuple[int, int, int]:
        """Order positions by distance from the center, then row and column."""
        return (
            abs(pos[0] - wanted_left) + abs(pos[1] - wanted_top),
            pos[1],
            pos[0],
        )

    positions.sort(key=position_priority)

    for left, top in positions:
        overlaps = any(
            (left + x, top + y) in blocked for x, y in PATTERN_CELLS
        )
        if not overlaps:
            return {
                (left + x, top + y)
                for x, y in PATTERN_CELLS
            }

    print("Warning: entry and exit leave no room for the 42 pattern")
    return set()
