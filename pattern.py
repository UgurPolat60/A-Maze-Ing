"""Create the closed cells used to draw the number 42."""


PATTERN: tuple[str, ...] = (
    "1000111",
    "1000001",
    "1110111",
    "0010100",
    "0010111",
)


def create_pattern(
    width: int,
    height: int,
    blocked: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    """Return a centred 42 pattern, or an empty set if it cannot fit."""
    pattern_width = len(PATTERN[0])
    pattern_height = len(PATTERN)
    if width < pattern_width + 2 or height < pattern_height + 2:
        print("Warning: maze is too small to display the 42 pattern")
        return set()

    if blocked is None:
        blocked = set()
    wanted_left = (width - pattern_width + 1) // 2
    wanted_top = (height - pattern_height) // 2
    positions = [
        (left, top)
        for top in range(1, height - pattern_height)
        for left in range(1, width - pattern_width)
    ]
    positions.sort(
        key=lambda pos: (
            abs(pos[0] - wanted_left) + abs(pos[1] - wanted_top),
            pos[1],
            pos[0],
        )
    )

    for left, top in positions:
        cells: set[tuple[int, int]] = set()
        for y, row in enumerate(PATTERN):
            for x, value in enumerate(row):
                if value == "1":
                    cells.add((left + x, top + y))
        if not cells & blocked:
            return cells

    print("Warning: entry and exit leave no room for the 42 pattern")
    return set()
