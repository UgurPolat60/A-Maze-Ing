import typing

KEY_LIST: dict[str, type] = {
    "WIDTH": int,
    "HEIGHT": int,
    "ENTRY": tuple,
    "EXIT": tuple,
    "OUTPUT_FILE": str,
    "PERFECT": bool,
}


def val_type(input_type: type, check_value: str) -> typing.Any:
    if input_type is int:
        try:
            ret: int = int(check_value)
            return ret
        except ValueError:
            raise ValueError(f"Cannot convert to int: {check_value}")
    elif input_type is bool:
        if check_value == "False" or check_value == "false":
            return False
        elif check_value == "True" or check_value == "true":
            return True
        raise ValueError(f"Invalid boolean representation: {check_value}")
    elif input_type is str:
        if check_value:
            return check_value
        else:
            raise ValueError("String cannot be empty")
    elif input_type is tuple:
        val1, val2 = check_value.split(",")
        return (int(val1), int(val2))


def config_parser(path: str) -> dict[str, typing.Any]:
    config: dict[str, typing.Any] = {}
    try:
        with open(path, "r") as f:
            for line in f:
                try:
                    line = line.strip()
                    if not line or line[0] == "#":
                        continue
                    key, value = line.split("=")
                    key = key.strip()
                    value = value.strip()
                except ValueError as e:
                    print(f"Invalid syntax on {e}")
                    continue

                if key in KEY_LIST and key not in config:
                    config[key] = val_type(KEY_LIST[key], value)
                else:
                    print(f"Bad input: {key}:{value}")

    except OSError as e:
        print(f"An error occured: {e}")

    return config
