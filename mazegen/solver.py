from collections import deque

from .constants import DIRECTION_LETTERS, DIRECTION_OFFSETS, DIRECTIONS
from .maze import Maze


def solve(maze: Maze) -> list[tuple[int, int]]:
    """Find a shortest path with a breadth-first search.

    Args:
        maze: A generated maze.

    Returns:
        The cells from entry to exit, empty if there is no path.
    """
    previous: dict[tuple[int, int], tuple[int, int]] = {maze.entry: maze.entry}
    queue: deque[tuple[int, int]] = deque([maze.entry])
    while queue:
        x, y = queue.popleft()
        if (x, y) == maze.exit:
            break
        for direction in DIRECTIONS:
            if maze.is_wall(x, y, direction):
                continue
            cell = maze.neighbour(x, y, direction)
            if cell is not None and cell not in previous:
                previous[cell] = (x, y)
                queue.append(cell)
    if maze.exit not in previous:
        return []
    path = [maze.exit]
    while path[-1] != maze.entry:
        path.append(previous[path[-1]])
    path.reverse()
    return path


def to_directions(path: list[tuple[int, int]]) -> str:
    """Convert a path of cells to N, E, S, W letters.

    Args:
        path: Cells of the path, one step apart.

    Returns:
        One letter per step.
    """
    moves = {DIRECTION_OFFSETS[d]: DIRECTION_LETTERS[d] for d in DIRECTIONS}
    letters = ""
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        letters += moves[(x2 - x1, y2 - y1)]
    return letters
