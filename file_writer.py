"""Write a generated maze in the required hexadecimal format."""

from mazegen import Maze
from mazegen.solver import to_directions


class FileWriteError(Exception):
    """Error raised when a maze cannot be written."""


def write_maze(
    maze: Maze,
    path: list[tuple[int, int]],
    output_file: str,
) -> None:
    """Write the grid, entry, exit and solution to a file.
    
    Args:
        maze: The maze to write.
        path: The path to write.
        output_file: File path to write to.

    Raises:
        FileWriteError if maze is invalid or it cannot write to file
    """
    if not path or path[0] != maze.entry or path[-1] != maze.exit:
        raise FileWriteError("Cannot write maze without a valid solution")

    lines: list[str] = []
    for row in maze.grid:
        if len(row) != maze.width:
            raise FileWriteError("Maze row has an invalid width")
        if any(type(cell) is not int or not 0 <= cell <= 15 for cell in row):
            raise FileWriteError("Maze contains an invalid cell value")
        lines.append("".join(format(cell, "X") for cell in row))

    if len(maze.grid) != maze.height:
        raise FileWriteError("Maze grid has an invalid height")
    
    lines.append("")
    lines.append(f"{maze.entry[0]},{maze.entry[1]}")
    lines.append(f"{maze.exit[0]},{maze.exit[1]}")
    lines.append(to_directions(path))

    try:
        with open(output_file, "w") as f:
            f.write("\n".join(lines) + "\n")
    except OSError as e:
        raise FileWriteError(f"Cannot write output file: {e}")
