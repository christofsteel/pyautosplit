import json
import os.path
from argparse import ArgumentParser
from collections import OrderedDict

from .game import Game
from .callbacks import ConsoleOut, LiveSplitServer, LiveSplitOne


def main():
    parser = ArgumentParser()
    parser.add_argument("--front-ends", "-f", nargs="+", default=["livesplit"],
                        help="Choose one or multiple of `console', "
                        "`livesplit', `livesplitone' (default livesplit)")
    parser.add_argument("--livesplit-host", default="localhost",
                        help="Host that runs the livesplit server component "
                        "(default localhost)")
    parser.add_argument("--livesplit-port", type=int, default=16834,
                        help="Port the livesplit server component listens on "
                        "(default 16834)")
    parser.add_argument("--livesplitone-bind", default="localhost",
                        help="Bind the livesplitone websocket server to this "
                        "host (default localhost)")
    parser.add_argument("--livesplitone-port", type=int, default=5000,
                        help="Bind the livesplitone websocket server to this "
                        "port (default 5000)")
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

    if 'console' in args.front_ends:
        callback_handlers.append(ConsoleOut())
    if 'livesplitone' in args.front_ends:
        callback_handlers.append(
            LiveSplitOne(args.livesplitone_bind, args.livesplitone_port))
    if 'livesplit' in args.front_ends:
        callback_handlers.append(
            LiveSplitServer(args.livesplit_host, args.livesplit_port))

    game = Game(gamedata, rundata, callback_handlers)
    game.hook()


if __name__ == "__main__":
    main()
