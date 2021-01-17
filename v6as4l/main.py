import sys

from .game import Game
from .callbacks import ConsoleOut
from .routes import Route, glitchless100perc

def main():
    game = Game(sys.argv[1])
    game.hook(ConsoleOut(Route(glitchless100perc)))

if __name__ == "__main__":
    main()
