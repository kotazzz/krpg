"""Module of game"""

import argparse

from krpg.game import main
from krpg.data.consts import __version__

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="KRPG", description="Консольная рпг игра", epilog="Ы :)")
    parser.add_argument("-d", "--debug", action="store_true")  # option that takes a value
    parser.add_argument("-v", "--version", action="version", version=__version__)

    args = parser.parse_args()
    main(debug=args.debug)
