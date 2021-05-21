from board import Board
from env import Env
from qtypes import *


def train(board: Board, striga: Striga, witcher: Witcher, initial_state: QState,
          epochs=1000):
    total_wins = 0

    hits = []
    win_p = []
    lifetime = []
    rewards = []
    time = []

    heatmap_start = board.to_numpy()
    heatmap = board.to_numpy()

    for i in range(epochs):
        game = Env(board, initial_state, striga, witcher)
        while game.game_res is None:
            game.advance()

        if game.game_res == GameResult.WITCHER:
            total_wins += 1

        if i == epochs // 100:
            heatmap_start = heatmap.copy()

        heatmap += game.witcher_positions
        time.append(i + 1)
        hits.append(float(game.hits))
        win_p.append(total_wins / (i + 1))
        lifetime.append(game.turn)
        rewards.append(game.rewards)

    return hits, win_p, lifetime, rewards, time, heatmap, heatmap_start

