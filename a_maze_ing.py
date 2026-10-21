"""Main entry point for A-Maze-ing."""

import sys

from config_parser import ConfigError, config_parser
from controller import Controller
from file_writer import FileWriteError
from validator import ValidationError, validate_config


def main() -> int:
    """Read the configuration and start the maze controller.

    Returns:
        Zero when the program finishes successfully,
        One if anything goes wrong.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>")
        return 1

    try:
        config = config_parser(sys.argv[1])
        settings, output_file = validate_config(config)
        controller = Controller(settings, output_file)
        controller.run()
    except (ConfigError, ValidationError, FileWriteError, ValueError) as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
