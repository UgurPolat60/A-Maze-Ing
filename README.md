*This project has been created as part of the 42 curriculum by seraydin, ugpolat.*

# A-Maze-ing

## Description

A-Maze-ing reads a configuration file, generates a random maze from it and
writes the result to a file using one hexadecimal digit per cell. The maze
hides a "42" drawn with fully closed cells and is displayed in the terminal
together with its shortest solution.

Two modes are available:

- **Perfect** (`PERFECT=True`): exactly one path between any two cells.
- **Pac-Man board** (`PERFECT=False`): every corridor is reachable, the four
  corners and the centre are open, there are at least two independent loops
  and very few dead-ends.

The same seed always produces the same maze. The generation logic lives in a
separate package, `mazegen`, that can be installed with pip and reused in
other projects.

## Instructions

### Requirements

- Python 3.10 or later
- `pip`

A virtual environment is recommended:

```bash
python3 -m venv env1
source env1/bin/activate
```

### Makefile

| Command | What it does |
|---|---|
| `make install` | installs the development tools (`flake8`, `mypy`, `build`) |
| `make run` | runs the program with `config.txt` |
| `make debug` | runs the program under the Python debugger (`pdb`) |
| `make clean` | removes caches and build artifacts |
| `make lint` | runs `flake8` and `mypy` with the flags required by the subject |

### Running

```bash
python3 a_maze_ing.py config.txt
```

`config.txt` is the only argument. Any file name can be used.

The maze is drawn in the terminal and saved to `OUTPUT_FILE`. Then the
program waits for a command (type it and press Enter):

| Key | Action |
|---|---|
| `R` | generate a new maze with a new random seed |
| `P` | show or hide the shortest path |
| `C` | change the wall colour |
| `Q` | quit |

Every error (missing file, bad syntax, invalid value, unwritable output file)
is reported as `Error: <message>` and the program exits with status 1.

### Output file

- One line per row of the maze, one hexadecimal digit per cell.
  Bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West.
  A set bit means the wall is closed. Example: `D` = `1101` means only the
  east side is open.
- An empty line.
- The entry coordinates `x,y`.
- The exit coordinates `x,y`.
- The shortest path from entry to exit, written with the letters `N`, `E`,
  `S`, `W`.

```
D539553955553D517913
97C693C69553C53C56AA
...

0,0
19,14
EESENEEESENEEEEESEES...
```

## Configuration file

One `KEY=VALUE` pair per line. Lines starting with `#` and empty lines are
ignored. Spaces around keys and values are ignored.

| Key | Mandatory | Format | Example | Meaning |
|---|---|---|---|---|
| `WIDTH` | yes | integer, at least 2 | `WIDTH=20` | number of columns |
| `HEIGHT` | yes | integer, at least 2 | `HEIGHT=15` | number of rows |
| `ENTRY` | yes | `x,y` | `ENTRY=0,0` | entry cell |
| `EXIT` | yes | `x,y` | `EXIT=19,14` | exit cell |
| `OUTPUT_FILE` | yes | file name | `OUTPUT_FILE=maze.txt` | where the maze is written |
| `PERFECT` | yes | `True` or `False` | `PERFECT=True` | perfect maze or Pac-Man board |
| `SEED` | no | integer | `SEED=42` | same seed gives the same maze; random if missing |

Rules:

- Coordinates start at `0,0` (top-left corner). `x` is the column, `y` is the
  row.
- `ENTRY` and `EXIT` must be inside the maze and different.
- `True` and `False` are case-insensitive.
- An unknown key, a duplicated key or a missing mandatory key is an error.

Default `config.txt`:

```
# Default A-Maze-ing configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

The "42" pattern needs a maze of at least 9 x 7 cells. In a smaller maze, or
when the entry or exit leaves no room for it, a warning is printed and the
maze is generated without the pattern.

## Maze generation algorithm

### Chosen algorithm

**Recursive backtracker** (randomised depth-first search), written with an
explicit stack instead of recursion.

1. Every cell starts with its four walls closed. The cells of the "42"
   pattern are marked as visited from the start, so they are never opened.
2. Start at the entry and push it on the stack.
3. Look at the cell on top of the stack. Pick a random unvisited neighbour,
   remove the wall between them and push the neighbour.
4. If the cell has no unvisited neighbour, pop it (backtrack).
5. Stop when the stack is empty.

Every cell is connected exactly once, so the result is a spanning tree: all
cells are reachable and there is no loop. This is a perfect maze.

For a Pac-Man board (`PERFECT=False`), two steps are added:

- **Dead-end removal**: each cell with only one open side gets one more wall
  opened, in a random direction.
- **Loop check**: the number of independent loops is computed as
  `open passages - (cells - 1)`. If it is below 2, random walls are opened
  until it reaches 2.

Each wall is opened tentatively: if it creates a fully open 3 x 3 area, or
touches the "42" pattern, it is closed again.

The shortest path is found with a **breadth-first search** (BFS). BFS visits
cells in order of distance from the entry, so the first path that reaches the
exit is the shortest one.

### Why this algorithm

- It produces long, winding corridors, which look like a real maze.
- It always gives a spanning tree, so `PERFECT=True` needs no extra work and
  full connectivity is guaranteed in both modes.
- It is short and easy to explain.
- The explicit stack avoids Python's recursion limit on large mazes.
- A private `random.Random(seed)` object is used, so the same seed always
  gives the same maze.

## Reusable module: mazegen

The `mazegen` package (`mazegen/` folder) contains everything needed to
generate and solve a maze: the maze structure, the generator and the solver.
It does not know anything about the configuration file, the terminal display
or the output file, so it can be used in any project. The "42" pattern is not
part of the package: it is passed in as an optional set of closed cells.

The package is built into `mazegen-1.0.0-py3-none-any.whl` at the root of the
repository.

### Building the package

```bash
python3 -m venv build_env
source build_env/bin/activate
pip install build
python3 -m build
cp dist/mazegen-1.0.0-py3-none-any.whl .
```

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic example

```python
from mazegen import MazeGenerator, MazeSettings

settings = MazeSettings(width=20, height=15, entry=(0, 0), exit=(19, 14))
generator = MazeGenerator(settings)
maze = generator.generate()
print(generator.solution())
```

### Custom parameters

All parameters are passed to `MazeSettings`:

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `width` | `int` | required | number of columns |
| `height` | `int` | required | number of rows |
| `entry` | `tuple[int, int]` | required | entry cell `(x, y)` |
| `exit` | `tuple[int, int]` | required | exit cell `(x, y)` |
| `perfect` | `bool` | `False` | `True`: a single path between any two cells. `False`: loops, few dead-ends |
| `seed` | `int \| None` | `None` | same seed gives the same maze. `None` picks a random seed |

Invalid values raise `ValueError`. The seed actually used is available as
`generator.seed`.

`generate()` also accepts an optional set of cells to keep fully closed:

```python
maze = generator.generate({(5, 5), (5, 6)})
```

### Accessing the generated structure

`generate()` returns a `Maze` object:

- `maze.width`, `maze.height`
- `maze.grid[y][x]`: walls of a cell as an integer from 0 to 15, with the
  same bits as the output file (a set bit means the wall is closed).
- `maze.is_wall(x, y, direction)`: `True` if the wall is closed.

```python
from mazegen.constants import EAST

maze.grid[0][0]           # 13
maze.is_wall(0, 0, EAST)  # False
```

### Accessing a solution

- `generator.solve()`: the shortest path as a list of cells, from entry to
  exit.
- `generator.solution()`: the same path as `N`, `E`, `S`, `W` letters.

```python
generator.solve()     # [(0, 0), (1, 0), (2, 0), ...]
generator.solution()  # "EESENEEESE..."
```

## Team and project management

### Roles

- **ugpolat**: the reusable `mazegen` package. Maze data structure,
  generation algorithm (perfect and Pac-Man modes), shortest-path solver.
- **seraydin**: everything outside `mazegen`. Configuration parser,
  validation, "42" pattern placement, terminal display, user interaction,
  output file writer and the main program.

### Planning

The work was split from the start along the package boundary: the generator
on one side, the program around it on the other. The two parts only meet
through `MazeSettings`, `MazeGenerator` and `Maze`, so each member could work
alone. The project was paused for about a month and then finished: lint
fixes, Makefile, packaging and documentation came last.

### What worked well and what could be improved

- Worked well: the clear split between the package and the application.
  Each side could be developed and tested on its own.
- Worked well: an independent validator checks every generated maze before
  it is written, so a generator bug cannot produce an invalid output file.
- Could be improved: the "42" shape leaves two cells with a single opening,
  so a Pac-Man board always keeps two dead-ends next to the pattern.
- Could be improved: packaging and the Makefile should have been set up at
  the start instead of at the end.

### Tools

- Git for version control
- VS Code
- `flake8` and `mypy` for style and type checking
- `pdb` for debugging
- `build` and `setuptools` for packaging

## Resources

- [Maze generation algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Maze Generation: Recursive Backtracking (Jamis Buck)](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Breadth-first search (Wikipedia)](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Spanning tree (Wikipedia)](https://en.wikipedia.org/wiki/Spanning_tree)
- [collections.deque (Python documentation)](https://docs.python.org/3/library/collections.html#collections.deque)
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257: Docstring Conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Choose a License](https://choosealicense.com/)

### Use of AI

AI (Claude) was used as a study and review assistant, not to write the
algorithms:

- explaining parts of the code line by line, so each member understood the
  part written by the other;
- comparing the project with the subject to list missing items;
- explaining flake8 and mypy errors and how to fix them;
- explaining how to write the Makefile, `.gitignore` and `pyproject.toml` and
  how to build the package;
- drafting this README from the code.

Every suggestion was read, tested and adapted by the team before being kept.