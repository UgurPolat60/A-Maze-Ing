"""Control generation, saving and terminal interaction."""

from random import randint

from ascii_view import AsciiView
from file_writer import write_maze
from mazegen import Maze, MazeGenerator, MazeSettings
from mazegen.settings import DEFAULT_SEED_RANGE
from pattern import create_pattern
from validator import validate_maze


class Controller:
    """Keep the current maze and handle user commands."""

    def __init__(self, settings: MazeSettings, output_file: str) -> None:
        """Set up the controller.

        Args:
            settings: Settings to use for maze generation.
            output_file: File to save the maze in.
        """
        self.settings = settings
        self.output_file = output_file
        self.view = AsciiView()
        self.maze: Maze | None = None
        self.path: list[tuple[int, int]] = []
        self.show_path = False
        self.seed = settings.seed
        self.message: str = ""

    def generate(self, new_seed: bool = False) -> None:
        """Generate, validate and save a maze.

        Args:
            new_seed: Generate with a new seed when True.

        Raises:
            ValueError: If generation fails.
            ValidationError: If the maze is invalid.
            FileWriteError: If the output cannot be saved.
        """
        if new_seed or self.seed is None:
            self.seed = randint(0, DEFAULT_SEED_RANGE)
        settings = MazeSettings(
            self.settings.width,
            self.settings.height,
            self.settings.entry,
            self.settings.exit,
            self.settings.perfect,
            self.seed,
        )
        generator = MazeGenerator(settings)
        blocked: set[tuple[int, int]] = {settings.entry, settings.exit}
        if not settings.perfect:
            blocked.add((settings.width // 2, settings.height // 2))
        pattern = create_pattern(settings.width, settings.height, blocked)
        self.maze = generator.generate(pattern)
        self.path = generator.solve()
        validate_maze(self.maze, settings.perfect)
        write_maze(self.maze, self.path, self.output_file)

    def display(self) -> None:
        """Clear the terminal and display current state and controls."""
        if self.maze is None:
            return
        print("\033[2J\033[H", end="")
        path: list[tuple[int, int]] | None = None
        if self.show_path:
            path = self.path
        self.view.display(self.maze, path)
        print()
        print(f"Seed: {self.seed} | Output: {self.output_file}")
        print("[R]egenerate  [P]ath  [C]olour  [Q]uit")
        if self.message:
            print(self.message)
        self.message = ""

    def run(self) -> None:
        """Generate the first maze and start the interaction loop."""
        self.generate()
        while True:
            self.display()
            try:
                command = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if command in ("q", "quit"):
                return
            elif command in ("r", "regenerate"):
                self.generate(True)
            elif command in ("p", "path"):
                self.show_path = not self.show_path
            elif command in ("c", "colour", "color"):
                self.view.change_color()
            else:
                self.message = "Unknown command. Use R, P, C or Q."
