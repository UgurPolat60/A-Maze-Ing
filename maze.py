from constants import (
    ALL_WALLS, DIRECTION_OFFSETS, DIRECTIONS, OPPOSITE_DIRECTION)


class Maze:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.grid: list[list[int]] = [
            [ALL_WALLS] * width for _ in range(height)]
        self.pattern: set[tuple[int, int]] = set()

    def is_wall(self, x: int, y: int, direction: int) -> bool:
        return bool(self.grid[y][x] & direction)

    def neighbour(self, x: int, y: int,
                  direction: int) -> tuple[int, int] | None:
        dx, dy = DIRECTION_OFFSETS[direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.width and 0 <= ny < self.height:
            return (nx, ny)
        return None

    def open_count(self, x: int, y: int) -> int:
        return sum(1 for d in DIRECTIONS if not self.is_wall(x, y, d))

    def close_wall(self, x: int, y: int, direction: int) -> None:
        dx, dy = DIRECTION_OFFSETS[direction]
        opposite = OPPOSITE_DIRECTION[direction]
        self.grid[y][x] |= direction
        self.grid[y + dy][x + dx] |= opposite

    def open_wall(self, x: int, y: int, direction: int) -> None:
        dx, dy = DIRECTION_OFFSETS[direction]
        opposite = OPPOSITE_DIRECTION[direction]
        self.grid[y][x] &= ~direction
        self.grid[y + dy][x + dx] &= ~opposite
