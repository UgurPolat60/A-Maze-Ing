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
    warnings: list[str],
    blocked: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    """Create the 42 pattern inside the maze.

    Args:
        width: Maze width.
        height: Maze height.
        warnings: List to collect warning messages for the controller.
        blocked: Cells that cannot be part of the pattern.

    Returns:
        Pattern cells, or an empty set if the pattern cannot fit.
    """
    pattern_width = len(PATTERN[0])
    pattern_height = len(PATTERN)
    if width < pattern_width + 2 or height < pattern_height + 2:
        warnings.append(
            "Warning: maze is too small to display the 42 pattern"
        )
        return set()

    if blocked is None:
        blocked = set()
    center = (
        (width - pattern_width + 1) // 2,
        (height - pattern_height) // 2,
    )
    positions: list[tuple[int, int]] = []
    for top in range(1, height - pattern_height):
        for left in range(1, width - pattern_width):
            positions.append((left, top))

    def distance_to_center(position: tuple[int, int]) -> int:
        """Return the horizontal and vertical distance from the center."""
        x, y = position
        center_x, center_y = center
        return abs(x - center_x) + abs(y - center_y)

    positions.sort(key=distance_to_center)

    for left, top in positions:
        overlaps = any(
            (left + x, top + y) in blocked for x, y in PATTERN_CELLS
        )
        if not overlaps:
            return {
                (left + x, top + y)
                for x, y in PATTERN_CELLS
            }

    warnings.append(
        "Warning: entry and exit leave no room for the 42 pattern"
    )
    return set()
