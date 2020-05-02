"""Parses the configuration files."""

from yaml import load


def load_config(filename: str) -> dict:
    """Loads the configuration file."""

    with open(filename, "r") as file:
        res = load(file)
    return res
