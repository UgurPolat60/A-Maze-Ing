"""Display a maze in the terminal."""

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
    """Render a maze using two full blocks for every pixel."""

    def __init__(self) -> None:
        """Create a view using the first available wall color."""
        self.color_index = 0

    def change_color(self) -> None:
        """Select the next wall color."""
        self.color_index = (self.color_index + 1) % len(COLORS)

    def _draw_walls(self, maze: Maze, canvas: list[list[int]]) -> None:
        """Draw all walls and intersections.

        Args:
            maze: Maze to draw.
            canvas: Canvas to draw on.
        """
        for y in range(maze.height + 1):
            for x in range(maze.width + 1):
                canvas[y * 2][x * 2] = WALL

        for y in range(maze.height):
            for x in range(maze.width):
                if maze.is_wall(x, y, EAST):
                    canvas[y * 2 + 1][x * 2 + 2] = WALL
                if maze.is_wall(x, y, SOUTH):
                    canvas[y * 2 + 2][x * 2 + 1] = WALL
                if y == 0:
                    canvas[0][x * 2 + 1] = WALL
                if x == 0:
                    canvas[y * 2 + 1][0] = WALL

    def _draw_pattern(self, maze: Maze, canvas: list[list[int]]) -> None:
        """Fill the center of every 42 pattern cell.

        Args:
            maze: Maze containing the 42 pattern.
            canvas: Canvas to draw on.
        """
        for x, y in maze.pattern:
            canvas[y * 2 + 1][x * 2 + 1] = PATTERN_BLOCK

    def _draw_path(
        self,
        path: list[tuple[int, int]],
        canvas: list[list[int]],
    ) -> None:
        """Draw cells and the openings connecting every path step.

        Args:
            path: Path from the entry to the exit.
            canvas: Canvas to draw on.
        """
        previous: tuple[int, int] | None = None
        for x, y in path:
            cx = x * 2 + 1
            cy = y * 2 + 1
            canvas[cy][cx] = PATH
            if previous is not None:
                old_x, old_y = previous
                canvas[y + old_y + 1][x + old_x + 1] = PATH
            previous = (x, y)

    def _pixel(self, value: int) -> str:
        """Convert a canvas value to colored text.

        Args:
            value: Canvas value to convert.

        Returns:
            Two characters with the correct color.
        """
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
        """Turn the maze into a string for the terminal.

        Args:
            maze: Maze to render.
            path: Path to display, or None to hide it.

        Returns:
            Colored maze ready to be printed.
        """
        canvas_width = maze.width * 2 + 1
        canvas_height = maze.height * 2 + 1
        canvas: list[list[int]] = []
        for _ in range(canvas_height):
            canvas.append([EMPTY] * canvas_width)

        self._draw_walls(maze, canvas)
        self._draw_pattern(maze, canvas)
        if path:
            self._draw_path(path, canvas)
        entry_x, entry_y = maze.entry
        exit_x, exit_y = maze.exit
        canvas[entry_y * 2 + 1][entry_x * 2 + 1] = ENTRY
        canvas[exit_y * 2 + 1][exit_x * 2 + 1] = EXIT

        lines: list[str] = []
        for row in canvas:
            line = ""
            for value in row:
                line += self._pixel(value)
            lines.append(line)
        return "\n".join(lines)

    def display(
        self,
        maze: Maze,
        path: list[tuple[int, int]] | None = None,
    ) -> None:
        """Print the maze in the terminal.

        Args:
            maze: Maze to display.
            path: Optional solution path to display.
        """
        print(self.render(maze, path))
