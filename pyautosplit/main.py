import json
import os.path
from argparse import ArgumentParser
from collections import OrderedDict

from .game import Game
from .callbacks import ConsoleOut, LiveSplitServer


def main():
    parser = ArgumentParser()
    parser.add_argument("--no-livesplit", "-L", action="store_true")
    parser.add_argument("--console-out", "-c", action="store_true")
    parser.add_argument("--livesplit-port", "-p", type=int, default=16834)
    parser.add_argument("--livesplit-host", "-H", default="localhost")
    parser.add_argument("runfile")

    args = parser.parse_args()

    with open(args.runfile) as jsonfile:
        rundata = json.load(jsonfile, object_pairs_hook=OrderedDict)

    if os.path.isabs(rundata["gamefile"]):
        abs_gamefilename = rundata["gamefile"]
    else:
        relative_base = os.path.dirname(args.runfile)
        abs_gamefilename = os.path.join(relative_base, rundata["gamefile"])

    with open(abs_gamefilename) as jsonfile:
        gamedata = json.load(jsonfile, object_pairs_hook=OrderedDict)

    callback_handlers = []

    if not args.no_livesplit:
        callback_handlers.append(
            LiveSplitServer(
                args.livesplit_host,
                args.livesplit_port))

    if args.console_out:
        callback_handlers.append(ConsoleOut())

    game = Game(gamedata, rundata, callback_handlers)
    game.hook()


if __name__ == "__main__":
    main()
