from random import Random, randint
from .constants import DIRECTIONS, EAST, SOUTH
from .maze import Maze
from .settings import DEFAULT_SEED_RANGE, MIN_LOOPS, MazeSettings
from .solver import solve as solve_maze, to_directions


class MazeGenerator:
    """Generate a maze from validated settings."""

    def __init__(self, settings: MazeSettings) -> None:
        """Prepare the generator.

        Args:
            settings: Validated parameters of the maze.
        """
        self.settings: MazeSettings = settings
        self.maze: Maze = Maze(
            settings.width, settings.height, settings.entry, settings.exit)
        self.seed: int = (settings.seed if settings.seed is not None
                          else randint(0, DEFAULT_SEED_RANGE))

    def generate(self, pattern: set[tuple[int, int]] | None = None) -> Maze:
        """Build a new maze.

        Args:
            pattern: Cells to keep fully closed, such as the "42" pattern.

        Returns:
            The generated maze.

        Raises:
            ValueError: If the entry or the exit is in the pattern.
        """
        rng = Random(self.seed)
        self.maze = Maze(
            self.settings.width, self.settings.height,
            self.settings.entry, self.settings.exit)
        if pattern:
            if self.maze.entry in pattern or self.maze.exit in pattern:
                raise ValueError("Entry and exit cant be in the pattern")
            self.maze.pattern = set(pattern)
        self._carve(rng)
        if not self.settings.perfect:
            self._remove_dead_ends(rng)
            self._add_loops(rng)
        return self.maze

    def solve(self) -> list[tuple[int, int]]:
        """Find a shortest path through the maze.

        Returns:
            The cells from entry to exit.
        """
        return solve_maze(self.maze)

    def solution(self) -> str:
        """Give a shortest path as N, E, S, W letters.

        Returns:
            One letter per step from entry to exit.
        """
        return to_directions(self.solve())

    def _carve(self, rng: Random) -> None:
        """Carve a perfect maze with a depth-first search.

        Args:
            rng: Random generator.
        """
        visited: set[tuple[int, int]] = (
            {self.maze.entry} | self.maze.pattern)
        stack: list[tuple[int, int]] = [self.maze.entry]
        while stack:
            x, y = stack[-1]
            options: list[tuple[int, tuple[int, int]]] = []
            for direction in DIRECTIONS:
                cell = self.maze.neighbour(x, y, direction)
                if cell is not None and cell not in visited:
                    options.append((direction, cell))
            if not options:
                stack.pop()
                continue
            direction, cell = rng.choice(options)
            self.maze.open_wall(x, y, direction)
            visited.add(cell)
            stack.append(cell)

    def _try_open(self, x: int, y: int, direction: int) -> bool:
        """Open a wall unless it breaks a rule.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: Side of the cell.

        Returns:
            True if the wall was opened.
        """
        cell = self.maze.neighbour(x, y, direction)
        if cell is None or cell in self.maze.pattern:
            return False
        if (x, y) in self.maze.pattern:
            return False
        if not self.maze.is_wall(x, y, direction):
            return False
        self.maze.open_wall(x, y, direction)
        if self._has_open_area(x, y):
            self.maze.close_wall(x, y, direction)
            return False
        return True

    def _remove_dead_ends(self, rng: Random) -> None:
        """Open a wall of each dead-end when possible.

        Args:
            rng: Random generator.
        """
        cells = [(x, y) for y in range(self.maze.height)
                 for x in range(self.maze.width)
                 if (x, y) not in self.maze.pattern]
        rng.shuffle(cells)
        for x, y in cells:
            if self.maze.open_count(x, y) != 1:
                continue
            directions = list(DIRECTIONS)
            rng.shuffle(directions)
            for direction in directions:
                if self._try_open(x, y, direction):
                    break

    def _count_loops(self) -> int:
        """Count the loops of the maze.

        Returns:
            The number of independent loops.
        """
        cells:int = self.maze.width * self.maze.height - len(self.maze.pattern)
        opened = 0
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if not self.maze.is_wall(x, y, EAST):
                    opened += 1
                if not self.maze.is_wall(x, y, SOUTH):
                    opened += 1
        return opened - (cells - 1)

    def _add_loops(self, rng: Random) -> None:
        """Open walls until the maze has enough loops.

        Args:
            rng: Random generator.
        """
        loops = self._count_loops()
        candidates:list[tuple[int,int,int]] = [(x, y, direction)
                      for y in range(self.maze.height)
                      for x in range(self.maze.width)
                      for direction in (EAST, SOUTH)]
        rng.shuffle(candidates)
        for x, y, direction in candidates:
            if loops >= MIN_LOOPS:
                break
            if self._try_open(x, y, direction):
                loops += 1

    def _is_open_block(self, left: int, top: int) -> bool:
        """Tell whether a 3x3 block of cells is fully open.

        Args:
            left: Column of the block.
            top: Row of the block.

        Returns:
            True if the block is fully open.
        """
        for cy in range(top, top + 3):
            for cx in range(left, left + 3):
                if cx < left + 2 and self.maze.is_wall(cx, cy, EAST):
                    return False
                if cy < top + 2 and self.maze.is_wall(cx, cy, SOUTH):
                    return False
        return True

    def _has_open_area(self, x: int, y: int) -> bool:
        """Tell whether a 3x3 open area contains a cell.

        Args:
            x: Column of the cell.
            y: Row of the cell.

        Returns:
            True if a fully open 3x3 block contains the cell.
        """
        for left in range(x - 2, x + 1):
            for top in range(y - 2, y + 1):
                if (left >= 0 and top >= 0
                        and left + 3 <= self.maze.width
                        and top + 3 <= self.maze.height
                        and self._is_open_block(left, top)):
                    return True
        return False
