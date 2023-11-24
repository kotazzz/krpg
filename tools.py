#!/usr/bin/env python3
import argparse
import ast
import json
import toml
import updater


def python_set(filename, variable, new_value):
    with open(filename, "r") as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == variable
        ):
            node.value = ast.Str(s=new_value)
    with open(filename, "w") as file:
        file.write(ast.unparse(tree))


def python_get(filename, variable):
    with open(filename, "r") as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == variable
        ):
            return node.value.s


def poetry_set(value):
    filename = "pyproject.toml"
    with open(filename, "r") as file:
        data = toml.load(file)
        # [tool.poetry] - version = value
        data["tool"]["poetry"]["version"] = value
    with open(filename, "w") as file:
        toml.dump(data, file)


def poetry_get():
    file = "pyproject.toml"
    with open(file, "r") as file:
        data = toml.load(file)
        # [tool.poetry] - version = value
        return data["tool"]["poetry"]["version"]


def update_version(args):
    file = "krpg/data/info.py"
    var = "__version__"
    if args.version:
        python_set(file, var, args.version)
        poetry_set(args.version)
    if args.show:
        print("Python:", python_get(file, var))
        print("Poetry:", poetry_get())


def build_hashes(args):
    filename = args.file
    hashes = updater.local_hashes()
    if args.output:
        print(*[f"{i}: {hashes[i]}" for i in hashes], sep="\n")
    else:
        print(f"Writing to {filename}")
        with open(filename, "w") as f:
            json.dump(hashes, f, indent=4)


parser = argparse.ArgumentParser()
parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0")
subparsers = parser.add_subparsers(
    dest="command", help="Action to perform", required=True
)
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
