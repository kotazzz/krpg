#!/usr/bin/env python3
"""
Tools for development. Run with `python tools.py --help`.
"""

import argparse
import ast
import json

import toml

import updater


def python_set(filename: str, variable: str, new_value: str):
    """Set variable value in python file

    Parameters
    ----------
    filename : str
        Path to python file
    variable : str
        Variable name
    new_value : str
        New value for variable
    """
    with open(filename, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == variable:
            node.value = ast.Constant(value=new_value)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(ast.unparse(tree))


def python_get(filename: str, variable: str):
    """Get variable value from python file

    Parameters
    ----------
    filename : str
        Path to python file
    variable : str
        Variable name

    Returns
    -------
    Any
        Variable value
    """
    with open(filename, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == variable:
            return node.value  # FIXME: What?
    raise NameError(f"Variable {variable} not found")


def poetry_set(value: str):
    """Set version in pyproject.toml

    Parameters
    ----------
    value : str
        New version
    """

    filename = "pyproject.toml"
    with open(filename, "r", encoding="utf-8") as file:
        data = toml.load(file)
        # [tool.poetry] - version = value
        data["tool"]["poetry"]["version"] = value
    with open(filename, "w", encoding="utf-8") as file:
        toml.dump(data, file)


def poetry_get() -> str:
    """Get version from pyproject.toml

    Returns
    -------
    str
        Version
    """
    filename = "pyproject.toml"
    with open(filename, "r", encoding="utf-8") as file:
        data = toml.load(file)
        # [tool.poetry] - version = value
        return data["tool"]["poetry"]["version"]


def update_version(update_args: argparse.Namespace):
    """Update version

    Parameters
    ----------
    args : argparse.Namespace
        Arguments
    """
    file = "krpg/data/info.py"
    var = "__version__"
    if update_args.version:
        if update_args.version == "1.0.0":
            raise ValueError("Change version to something other than 1.0.0")
        python_set(file, var, update_args.version)
        poetry_set(update_args.version)
    if update_args.show:
        print("Python:", python_get(file, var))
        print("Poetry:", poetry_get())


def build_hashes(build_args: argparse.Namespace):
    """Build hashes file

    Parameters
    ----------
    args : argparse.Namespace
        Arguments
    """
    filename = build_args.file
    hashes = updater.local_hashes()
    if build_args.output:
        for i, j in hashes.items():  # noqa
            print(f"{i}: {j}")
    else:
        print(f"Writing to {filename}")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=4)


parser = argparse.ArgumentParser()
parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0")
subparsers = parser.add_subparsers(dest="command", help="Action to perform", required=True)
update_sub = subparsers.add_parser("version", help="Update version")
update_sub.add_argument("version", action="store", nargs="?", help="New version name")
update_sub.add_argument("--show", action="store_true", help="Show the new version")
update_sub.set_defaults(func=update_version)
build_sub = subparsers.add_parser("hashes", help="Build hashes file for a given file")
build_sub.add_argument(
    "file",
    action="store",
    nargs="?",
    default="hashes.json",
    help="File to write hashes to",
)
build_sub.add_argument("--output", "-o", action="store_true", help="Output to console")
build_sub.set_defaults(func=build_hashes)
if __name__ == "__main__":
    args = parser.parse_args()
    args.func(args)
