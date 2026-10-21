"""Display a maze in the terminal with square full-block pixels."""

from mazegen import Maze
from mazegen.constants import EAST, SOUTH


RESET = "\033[0m"
COLORS: tuple[str, ...] = (
    "\033[97m",
    "\033[96m",
    "\033[95m",
    "\033[93m",
    "\033[92m",
)
PATH_COLOR = "\033[94m"
PATTERN_COLOR = "\033[90m"
ENTRY_COLOR = "\033[92m"
EXIT_COLOR = "\033[91m"

EMPTY = 0
WALL = 1
PATTERN_BLOCK = 2
PATH = 3
ENTRY = 4
EXIT = 5


class AsciiView:
    """Render a maze using two full blocks for every logical pixel."""

    def __init__(self) -> None:
        self.color_index = 0

    def change_color(self) -> None:
        """Select the next wall colour."""
        self.color_index = (self.color_index + 1) % len(COLORS)

    def _put(
        self,
        canvas: list[list[int]],
        x: int,
        y: int,
        value: int,
    ) -> None:
        """Put a pixel on the canvas if it has higher priority."""
        if value >= canvas[y][x]:
            canvas[y][x] = value

    def _draw_walls(self, maze: Maze, canvas: list[list[int]]) -> None:
        """Draw all walls and intersections."""
        for y in range(maze.height + 1):
            for x in range(maze.width + 1):
                self._put(canvas, x * 2, y * 2, WALL)

        for y in range(maze.height):
            for x in range(maze.width):
                if maze.is_wall(x, y, EAST):
                    self._put(canvas, x * 2 + 2, y * 2 + 1, WALL)
                if maze.is_wall(x, y, SOUTH):
                    self._put(canvas, x * 2 + 1, y * 2 + 2, WALL)
                if y == 0:
                    self._put(canvas, x * 2 + 1, 0, WALL)
                if x == 0:
                    self._put(canvas, 0, y * 2 + 1, WALL)

    def _draw_pattern(self, maze: Maze, canvas: list[list[int]]) -> None:
        """Fill the centre of every closed pattern cell."""
        for x, y in maze.pattern:
            self._put(canvas, x * 2 + 1, y * 2 + 1, PATTERN_BLOCK)

    def _draw_path(
        self,
        path: list[tuple[int, int]],
        canvas: list[list[int]],
    ) -> None:
        """Draw cells and the openings connecting every path step."""
        for index, (x, y) in enumerate(path):
            cx = x * 2 + 1
            cy = y * 2 + 1
            self._put(canvas, cx, cy, PATH)
            if index == 0:
                continue
            old_x, old_y = path[index - 1]
            old_cx = old_x * 2 + 1
            old_cy = old_y * 2 + 1
            self._put(
                canvas,
                (old_cx + cx) // 2,
                (old_cy + cy) // 2,
                PATH,
            )

    def _pixel(self, value: int) -> str:
        """Convert one canvas value to a coloured terminal pixel."""
        if value == EMPTY:
            return "  "
        if value == WALL:
            return COLORS[self.color_index] + "██" + RESET
        if value == PATTERN_BLOCK:
            return PATTERN_COLOR + "██" + RESET
        if value == PATH:
            return PATH_COLOR + "██" + RESET
        if value == ENTRY:
            return ENTRY_COLOR + "EN" + RESET
        return EXIT_COLOR + "EX" + RESET

    def render(
        self,
        maze: Maze,
        path: list[tuple[int, int]] | None = None,
    ) -> str:
        """Return the complete coloured maze as a string."""
        canvas_width = maze.width * 2 + 1
        canvas_height = maze.height * 2 + 1
        canvas = [
            [EMPTY for _ in range(canvas_width)]
            for _ in range(canvas_height)
        ]

        self._draw_walls(maze, canvas)
        self._draw_pattern(maze, canvas)
        if path:
            self._draw_path(path, canvas)
        self._put(
            canvas, maze.entry[0] * 2 + 1, maze.entry[1] * 2 + 1, ENTRY
        )
        self._put(
            canvas, maze.exit[0] * 2 + 1, maze.exit[1] * 2 + 1, EXIT
        )

        lines = [
            "".join(self._pixel(value) for value in row)
            for row in canvas
        ]
        return "\n".join(lines)

    def display(
        self,
        maze: Maze,
        path: list[tuple[int, int]] | None = None,
    ) -> None:
        """Print the maze to the terminal."""
        print(self.render(maze, path))
