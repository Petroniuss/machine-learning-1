from board import Board
from game import Game
from qtypes import *


def train(board: Board, striga: Striga, witcher: Witcher, initial_state: QState,
          epochs=1000):
    total_hits = 0
    total_wins = 0
    total_turns = 0
    for i in range(epochs):
        game = Game(board, initial_state, striga, witcher)
        while game.game_res is None:
            game.advance()

        total_turns += game.turn
        total_hits += (3 - game.hits)
        if game.game_res == GameResult.WITCHER:
            total_wins += 1

        print(total_hits, total_wins, total_turns)
