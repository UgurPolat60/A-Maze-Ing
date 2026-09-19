DEFAULT_SEED_RANGE = 99999
MIN_LOOPS = 2


class MazeSettings:
    """Validated parameters of a maze."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool = False,
        seed: int | None = None,
    ) -> None:
        """Check and store the parameters.

        Args:
            width: Number of columns.
            height: Number of rows.
            entry: Entry cell (x, y).
            exit: Exit cell (x, y).
            perfect: True for a perfect maze, False for a Pac-Man board.
            seed: Random seed, None to choose one.

        Raises:
            ValueError: If a parameter is invalid.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Enter valid values")
        for name, position in (("Entrance", entry), ("ExitLocation", exit),):
            x, y = position
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"{name} Out of borders")
        if entry == exit:
            raise ValueError("Entry and exit cant be on the same block")
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed
