"""Read the maze configuration file."""

import typing


class ConfigError(Exception):
    """Error raised when the configuration file is not valid."""


KEY_LIST: dict[str, type] = {
    "WIDTH": int,
    "HEIGHT": int,
    "ENTRY": tuple,
    "EXIT": tuple,
    "OUTPUT_FILE": str,
    "PERFECT": bool,
    "SEED": int,
}

REQUIRED_KEYS: set[str] = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
}


def val_type(input_type: type, check_value: str) -> typing.Any:
    """Convert one configuration value to the requested type."""
    if input_type is int:
        try:
            return int(check_value)
        except ValueError as e:
            raise ConfigError(f"Cannot convert to int: {check_value}") from e

    if input_type is bool:
        if check_value.lower() == "false":
            return False
        if check_value.lower() == "true":
            return True
        raise ConfigError(f"Invalid boolean representation: {check_value}")

    if input_type is str:
        if check_value:
            return check_value
        raise ConfigError("String cannot be empty")

    if input_type is tuple:
        values = check_value.split(",")
        if len(values) != 2:
            raise ConfigError(f"Invalid coordinates: {check_value}")
        try:
            return (int(values[0].strip()), int(values[1].strip()))
        except ValueError as e:
            raise ConfigError(f"Invalid coordinates: {check_value}") from e

    raise ConfigError("Unsupported configuration type")


def config_parser(path: str) -> dict[str, typing.Any]:
    """Read a KEY=VALUE configuration file."""
    config: dict[str, typing.Any] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"Invalid syntax on line {line_number}: {line}"
                    )
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key not in KEY_LIST:
                    raise ConfigError(
                        f"Unknown key on line {line_number}: {key}"
                    )
                if key in config:
                    raise ConfigError(
                        f"Duplicate key on line {line_number}: {key}"
                    )
                try:
                    config[key] = val_type(KEY_LIST[key], value)
                except ConfigError as e:
                    raise ConfigError(f"Line {line_number}: {e}") from e
    except OSError as e:
        raise ConfigError(f"Cannot read configuration file: {e}") from e

    missing = REQUIRED_KEYS - set(config)
    if missing:
        names = ", ".join(sorted(missing))
        raise ConfigError(f"Missing mandatory keys: {names}")
    return config
