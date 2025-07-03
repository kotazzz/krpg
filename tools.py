#!/usr/bin/env python3
"""
Tools for development. Run with `python tools.py --help`.
"""

import argparse
import json
import updater


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
