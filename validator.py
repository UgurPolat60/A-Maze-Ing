"""Validate configuration values and generated maze structures."""

from collections import deque
from typing import Any

from mazegen import Maze, MazeSettings
from mazegen.constants import EAST, NORTH, SOUTH, WEST


class ValidationError(Exception):
    """Error raised when settings or a generated maze are invalid."""


def validate_config(
    config: dict[str, Any],
) -> tuple[MazeSettings, str]:
    """Check the config and create maze settings.

    Args:
        config: Values read from the config file.

    Returns:
        Maze settings and output filename.

    Raises:
        ValidationError: If a value is missing or invalid.
    """
    try:
        width = config["WIDTH"]
        height = config["HEIGHT"]
        entry = config["ENTRY"]
        exit_pos = config["EXIT"]
        output_file = config["OUTPUT_FILE"]
        perfect = config["PERFECT"]
        seed = config.get("SEED")
    except KeyError as e:
        raise ValidationError(f"Missing mandatory key: {e.args[0]}")

    if type(width) is not int or type(height) is not int:
        raise ValidationError("WIDTH and HEIGHT must be integers")
    if width < 2 or height < 2:
        raise ValidationError("WIDTH and HEIGHT must be at least 2")
    if not isinstance(entry, tuple) or not isinstance(exit_pos, tuple):
        raise ValidationError("ENTRY and EXIT must be coordinates")
    if type(perfect) is not bool:
        raise ValidationError("PERFECT must be True or False")
    if type(output_file) is not str or not output_file:
        raise ValidationError("OUTPUT_FILE cannot be empty")
    if seed is not None and type(seed) is not int:
        raise ValidationError("SEED must be an integer")

    try:
        settings = MazeSettings(
            width, height, entry, exit_pos, perfect, seed
        )
    except (TypeError, ValueError) as e:
        raise ValidationError(str(e))
    return settings, output_file


def _validate_grid(maze: Maze) -> None:
    """Check the grid, outside borders and shared walls.

    Args:
        maze: Maze to check.

    Raises:
        ValidationError: If the grid or a wall is invalid.
    """
    if len(maze.grid) != maze.height:
        raise ValidationError("Maze grid has an invalid height")
    for row in maze.grid:
        if len(row) != maze.width:
            raise ValidationError("Maze grid has an invalid width")

    for y, row in enumerate(maze.grid):
        for x, cell in enumerate(row):
            if type(cell) is not int or not 0 <= cell <= 15:
                raise ValidationError(f"Invalid cell value at {x},{y}")
            if y == 0 and not maze.is_wall(x, y, NORTH):
                raise ValidationError("North border is open")
            if y == maze.height - 1 and not maze.is_wall(x, y, SOUTH):
                raise ValidationError("South border is open")
            if x == 0 and not maze.is_wall(x, y, WEST):
                raise ValidationError("West border is open")
            if x == maze.width - 1 and not maze.is_wall(x, y, EAST):
                raise ValidationError("East border is open")
            if x + 1 < maze.width:
                east = maze.is_wall(x, y, EAST)
                west = maze.is_wall(x + 1, y, WEST)
                if east != west:
                    raise ValidationError(f"Wall mismatch at {x},{y}")
            if y + 1 < maze.height:
                south = maze.is_wall(x, y, SOUTH)
                north = maze.is_wall(x, y + 1, NORTH)
                if south != north:
                    raise ValidationError(f"Wall mismatch at {x},{y}")


def _reachable(maze: Maze) -> set[tuple[int, int]]:
    """Find all cells that can be reached from the entry.

    Args:
        maze: Maze to search.

    Returns:
        Cells reachable from the entry.
    """
    reached: set[tuple[int, int]] = {maze.entry}
    queue: deque[tuple[int, int]] = deque([maze.entry])
    while queue:
        x, y = queue.popleft()
        for direction in (NORTH, EAST, SOUTH, WEST):
            if maze.is_wall(x, y, direction):
                continue
            neighbour = maze.neighbour(x, y, direction)
            if neighbour is not None and neighbour not in reached:
                reached.add(neighbour)
                queue.append(neighbour)
    return reached


def _count_edges(maze: Maze) -> int:
    """Count passages between cells once.

    Args:
        maze: Maze to check.

    Returns:
        Number of open connections.
    """
    edges = 0
    for y in range(maze.height):
        for x in range(maze.width):
            if x + 1 < maze.width and not maze.is_wall(x, y, EAST):
                edges += 1
            if y + 1 < maze.height and not maze.is_wall(x, y, SOUTH):
                edges += 1
    return edges


def _has_open_area(maze: Maze) -> bool:
    """Check whether the maze contains a fully open 3 by 3 area.

    Args:
        maze: Maze to check.

    Returns:
        True if a fully open 3 by 3 area exists, otherwise False.
    """
    for top in range(maze.height - 2):
        for left in range(maze.width - 2):
            is_open = True
            for y in range(top, top + 3):
                for x in range(left, left + 3):
                    if x < left + 2 and maze.is_wall(x, y, EAST):
                        is_open = False
                    if y < top + 2 and maze.is_wall(x, y, SOUTH):
                        is_open = False
            if is_open:
                return True
    return False


def validate_maze(maze: Maze, perfect: bool) -> None:
    """Check that a generated maze follows the required rules.

    Args:
        maze: Maze to check.
        perfect: True if the maze must not have loops.

    Raises:
        ValidationError: If the maze breaks a rule.
    """
    _validate_grid(maze)
    if maze.entry == maze.exit:
        raise ValidationError("Entry and exit cannot be the same")
    if maze.entry in maze.pattern or maze.exit in maze.pattern:
        raise ValidationError("Entry or exit overlaps the 42 pattern")

    for x, y in maze.pattern:
        if not 0 <= x < maze.width or not 0 <= y < maze.height:
            raise ValidationError("42 pattern is outside the maze")
        if maze.grid[y][x] != 15:
            raise ValidationError("42 pattern cells must be fully closed")

    expected: set[tuple[int, int]] = set()
    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) not in maze.pattern:
                expected.add((x, y))
    reached = _reachable(maze)
    if reached != expected:
        raise ValidationError("Not every corridor is reachable")
    if _has_open_area(maze):
        raise ValidationError("Maze contains an open 3 by 3 area")

    loops = _count_edges(maze) - len(expected) + 1
    if perfect and loops != 0:
        raise ValidationError("Perfect maze contains a loop")
    if not perfect and loops < 2:
        raise ValidationError("Non-perfect maze needs at least two loops")

    if not perfect:
        important: set[tuple[int, int]] = {
            (0, 0),
            (maze.width - 1, 0),
            (0, maze.height - 1),
            (maze.width - 1, maze.height - 1),
            (maze.width // 2, maze.height // 2),
        }
        if important & maze.pattern:
            raise ValidationError("A corner or centre is inside the pattern")
        for x, y in important:
            if maze.open_count(x, y) == 0:
                raise ValidationError("A corner or centre is not open")
