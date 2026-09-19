from .constants import (
    ALL_WALLS, DIRECTION_OFFSETS, DIRECTIONS, OPPOSITE_DIRECTION)


class Maze:
    """Grid of cells, each cell stores its four walls as bits."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        """Create a maze with every wall closed.

        Args:
            width: Number of columns.
            height: Number of rows.
            entry: Entry cell (x, y).
            exit: Exit cell (x, y).
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.grid: list[list[int]] = [
            [ALL_WALLS] * width for _ in range(height)]
        self.pattern: set[tuple[int, int]] = set()

    def is_wall(self, x: int, y: int, direction: int) -> bool:
        """Tell whether a wall is closed.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Side of the cell.

        Returns:
            True if the wall is closed.
        """
        return bool(self.grid[y][x] & direction)

    def neighbour(self, x: int, y: int,
                  direction: int) -> tuple[int, int] | None:
        """Give the neighbour cell in a direction.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Side of the cell.

        Returns:
            The neighbour (x, y), or None outside the maze.
        """
        dx, dy = DIRECTION_OFFSETS[direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.width and 0 <= ny < self.height:
            return (nx, ny)
        return None

    def open_count(self, x: int, y: int) -> int:
        """Count the open sides of a cell.

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            The number of open walls.
        """
        return sum(1 for d in DIRECTIONS if not self.is_wall(x, y, d))

    def close_wall(self, x: int, y: int, direction: int) -> None:
        """Close a wall of a cell and of its neighbour.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Side of the cell.
        """
        dx, dy = DIRECTION_OFFSETS[direction]
        opposite = OPPOSITE_DIRECTION[direction]
        self.grid[y][x] |= direction
        self.grid[y + dy][x + dx] |= opposite

    def open_wall(self, x: int, y: int, direction: int) -> None:
        """Open a wall of a cell and of its neighbour.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Side of the cell.
        """
        dx, dy = DIRECTION_OFFSETS[direction]
        opposite = OPPOSITE_DIRECTION[direction]
        self.grid[y][x] &= ~direction
        self.grid[y + dy][x + dx] &= ~opposite
