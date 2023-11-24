import argparse
from krpg.game import Game

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="KRPG", description="Консольная рпг игра", epilog="Ы :)"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true"
    )  # option that takes a value
    parser.add_argument("-v", "--version", action="version", version=__version__)

    args = parser.parse_args()
    game = Game(args.debug)
