import random

from constants import DIRECTIONS, EAST, SOUTH
from maze import Maze
from settings import DEFAULT_SEED_RANGE, MazeSettings


class MazeGenerator:
    def __init__(self, settings: MazeSettings) -> None:
        self.settings: MazeSettings = settings
        self.maze: Maze = Maze(
            settings.width, settings.height, settings.entry, settings.exit)
        self.seed: int = (settings.seed if settings.seed is not None
                           else random.randint(0, DEFAULT_SEED_RANGE))

    def generate(self) -> Maze:
        rng = random.Random(self.seed)
        self.maze = Maze(
            self.settings.width, self.settings.height,
            self.settings.entry, self.settings.exit)
        self._carve(rng)
        return self.maze

    def _carve(self, rng: random.Random) -> None:
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
        cell = self.maze.neighbour(x, y, direction)
        if cell is None or cell in self.maze.pattern:
            return False
        if not self.maze.is_wall(x, y, direction):
            return False
        self.maze.open_wall(x, y, direction)
        if self._has_open_area(x, y):
            self.maze.close_wall(x, y, direction)
            return False
        return True

    def _remove_dead_ends(self, rng: random.Random) -> None:
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

    def _is_open_block(self, left: int, top: int) -> bool:
        for cy in range(top, top + 3):
            for cx in range(left, left + 3):
                if cx < left + 2 and self.maze.is_wall(cx, cy, EAST):
                    return False
                if cy < top + 2 and self.maze.is_wall(cx, cy, SOUTH):
                    return False
        return True

    def _has_open_area(self, x: int, y: int) -> bool:
        for left in range(x - 2, x + 1):
            for top in range(y - 2, y + 1):
                if (left >= 0 and top >= 0
                        and left + 3 <= self.maze.width
                        and top + 3 <= self.maze.height
                        and self._is_open_block(left, top)):
                    return True
        return False
