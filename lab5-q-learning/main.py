from board import Board
from game import Game
from qtypes import *
from striga_scheme import StrigaDeterministicMovementScheme
from train import train
from witcher_scheme import WitcherMovementSchemeSARSA


def main():
    width = 7
    height = 7
    walls = [
        Position(width - 2, 0),
        Position(width - 2, 1),
        Position(width - 1, 1)
    ]
    castle_position = Position(width - 1, 0)
    board = Board(width, height, castle_position, walls)
    striga = Striga(StrigaDeterministicMovementScheme(board, 3))
    witcher = Witcher(WitcherMovementSchemeSARSA(board))
    initial_state = QState(Position(0, 0), Position(3, 3))

    # train(board, striga, witcher, initial_state)

    game = Game(board, initial_state, striga, witcher)
    game.visualize()


if __name__ == '__main__':
    main()
